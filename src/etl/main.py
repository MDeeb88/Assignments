"""Command-line entry point for the Steam Games ETL pipeline."""

import argparse
import sqlite3
import sys
from pathlib import Path

import psycopg2

from .extract import extract_data
from .load import load_data
from .transform import transform_data
from .validate import validate_data


def main() -> None:
    """Run the complete ETL pipeline."""

    parser = argparse.ArgumentParser(
        description="Extract, transform, validate, and load Steam games."
    )

    parser.add_argument(
        "--table",
        required=True,
        help="Destination PostgreSQL table (e.g. deebm).",
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("datasets/games.parquet"),
        help="Path to the source Parquet dataset.",
    )

    parser.add_argument(
        "--creds",
        type=Path,
        default=Path("creds.db"),
        help="Path to the local SQLite credentials database.",
    )

    args = parser.parse_args()

    print("Starting Steam Games ETL pipeline...\n")

    try:
        raw = extract_data(args.dataset)
        transformed = transform_data(raw)
        validated = validate_data(transformed)

        count = load_data(
            validated,
            creds_path=args.creds,
            table_name=args.table,
        )

    except (
        FileNotFoundError,
        ValueError,
        TypeError,
        RuntimeError,
        OSError,
        sqlite3.Error,
        psycopg2.Error,
    ) as exc:
        print(f"\nETL failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None

    print("\nETL completed successfully.")
    print(f"Destination: homeworks.{args.table}")
    print(f"Verified records: {count}")


if __name__ == "__main__":
    main()
