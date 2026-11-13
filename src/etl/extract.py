"""Extract Steam game records from a local Parquet dataset."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = (
    "AppID",
    "Name",
    "Price",
    "Positive",
    "Negative",
)


def extract_data(dataset_path: str | Path) -> pd.DataFrame:
    """Read the source dataset without modifying its records."""
    path = Path(dataset_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    if path.suffix.lower() != ".parquet":
        raise ValueError("Expected a Parquet dataset (.parquet).")

    df = pd.read_parquet(path, columns=list(REQUIRED_COLUMNS))

    if df.empty:
        raise ValueError("The source dataset is empty.")

    print(f"EXTRACT: {len(df):,} rows and {len(df.columns)} columns loaded.")

    return df
