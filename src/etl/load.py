"""Load validated Steam game records into PostgreSQL."""

import sqlite3
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


def get_credentials(creds_path: str | Path) -> dict:
    """Read homeworks credentials from the local SQLite database."""
    path = Path(creds_path)

    if not path.is_file():
        raise FileNotFoundError("Local creds.db was not found.")

    with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        record = conn.execute(
            'SELECT url, port, "user", "pass", db_name FROM access WHERE db_name = ?',
            ("homeworks",),
        ).fetchone()

    if record is None:
        raise RuntimeError("No homeworks credentials found.")

    return dict(record)


def load_data(
    df: pd.DataFrame,
    creds_path: str | Path,
    table_name: str = "deebm",
) -> int:
    """Upsert at most 100 validated records into PostgreSQL."""
    if df.empty or len(df) > 100:
        raise ValueError("Expected between 1 and 100 records.")

    credentials = get_credentials(creds_path)

    records = [
        (
            int(appid),
            str(name),
            round(float(price), 2),
            int(positive),
            int(negative),
        )
        for appid, name, price, positive, negative in df[
            ["AppID", "Name", "Price", "Positive", "Negative"]
        ].itertuples(index=False, name=None)
    ]

    with (
        psycopg2.connect(
            host=credentials["url"],
            port=credentials["port"],
            user=credentials["user"],
            password=credentials["pass"],
            dbname=credentials["db_name"],
            connect_timeout=10,
        ) as conn,
        conn.cursor() as cursor,
    ):
        cursor.execute(
            sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {} (
                        appid BIGINT PRIMARY KEY,
                        name TEXT NOT NULL,
                        price NUMERIC(12, 2),
                        positive INTEGER,
                        negative INTEGER
                    )
                """).format(sql.Identifier(table_name))
        )

        query = sql.SQL("""
                INSERT INTO {} (
                    appid, name, price, positive, negative
                )
                VALUES %s
                ON CONFLICT (appid)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    positive = EXCLUDED.positive,
                    negative = EXCLUDED.negative
            """).format(sql.Identifier(table_name))

        execute_values(
            cursor,
            query.as_string(conn),
            records,
        )

        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
        )
        final_count = cursor.fetchone()[0]

        if final_count > 100:
            raise RuntimeError(
                f"Table contains {final_count} records; maximum permitted is 100."
            )

    print(f"LOAD: {len(records)} records uploaded to homeworks.{table_name}.")
    print(f"LOAD: {final_count} records verified.")

    return final_count
