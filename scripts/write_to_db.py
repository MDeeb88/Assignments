
"""Upload 100 Steam game records to the homework PostgreSQL database."""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CREDS_PATH = PROJECT_ROOT / "creds.db"

DATA_PATH = PROJECT_ROOT / "datasets" / "games.parquet"

COLUMNS = ["AppID", "Name", "Price", "Positive", "Negative"]


def load_steam_data():
    """Select exactly 100 valid Steam game records."""

    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_parquet(DATA_PATH, columns=COLUMNS)

    for column in ["AppID", "Price", "Positive", "Negative"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Name"] = df["Name"].astype("string").str.strip()

    df = df.dropna(subset=COLUMNS)
    df = df[df["Name"].str.len() > 0]

    df = df[
        (df["AppID"] >= 0)
        & (df["Price"] >= 0)
        & (df["Positive"] >= 0)
        & (df["Negative"] >= 0)
    ]

    df = (
        df.drop_duplicates(subset="AppID")
        .sort_values("AppID")
        .head(100)
    )

    if len(df) != 100:
        raise ValueError("The dataset has fewer than 100 valid records.")

    return [
        (
            int(appid),
            str(name),
            round(float(price), 2),
            int(positive),
            int(negative),
        )
        for appid, name, price, positive, negative
        in df[COLUMNS].itertuples(index=False, name=None)
    ]


def get_credentials():
    """Read homeworks credentials locally without displaying them."""

    if not CREDS_PATH.is_file():
        raise FileNotFoundError("Local creds.db file not found.")

    with sqlite3.connect(
        f"file:{CREDS_PATH}?mode=ro", uri=True
    ) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            'SELECT url, port, "user", "pass", db_name '
            "FROM access WHERE db_name = ?",
            ("homeworks",),
        ).fetchone()

    if row is None:
        raise RuntimeError("No homeworks database credentials found.")

    return dict(row)


def upload_records(table_name):
    """Create the homework table and upload exactly 100 records."""

    records = load_steam_data()
    credentials = get_credentials()

    with psycopg2.connect(
        host=credentials["url"],
        port=credentials["port"],
        user=credentials["user"],
        password=credentials["pass"],
        dbname=credentials["db_name"],
        connect_timeout=10,
    ) as conn:

        with conn.cursor() as cursor:
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

            cursor.execute(
                sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table_name)
                )
            )
            existing_count = cursor.fetchone()[0]

            if existing_count not in (0, 100):
                raise RuntimeError(
                    f"Table already has {existing_count} records. "
                    "Refusing to modify unexpected existing data."
                )

            insert_query = sql.SQL("""
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
                insert_query.as_string(conn),
                records,
            )

            cursor.execute(
                sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table_name)
                )
            )
            final_count = cursor.fetchone()[0]

            if final_count != 100:
                raise RuntimeError(
                    f"Expected 100 records, found {final_count}. "
                    "Transaction will be rolled back."
                )

    print("Database: homeworks")
    print("Table:", table_name)
    print("Records uploaded:", len(records))
    print("Records verified:", final_count)
    print("Upload successful.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--table",
        required=True,
        help="Lowercase surname followed by initials",
    )

    args = parser.parse_args()

    if not args.table.isascii() or not args.table.isalnum() \
            or not args.table.islower():
        parser.error("Table name must contain lowercase letters and digits.")

    upload_records(args.table)
