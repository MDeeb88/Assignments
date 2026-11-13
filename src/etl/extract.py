"""Extract Steam game records from a local Parquet dataset."""

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REQUIRED_COLUMNS = (
    "AppID",
    "Name",
    "Price",
    "Positive",
    "Negative",
)


def extract_data(dataset_path: str | Path) -> pd.DataFrame:
    """Read the source dataset after checking its schema."""

    path = Path(dataset_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    if path.suffix.lower() != ".parquet":
        raise ValueError("Expected a Parquet dataset (.parquet).")

    try:
        available_columns = pq.read_schema(path).names
    except (pa.ArrowException, OSError) as exc:
        raise ValueError(f"Could not read Parquet dataset: {exc}") from exc

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in available_columns
    ]

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing_columns)
        )

    try:
        df = pd.read_parquet(
            path,
            columns=list(REQUIRED_COLUMNS),
        )
    except (pa.ArrowException, OSError, ValueError) as exc:
        raise ValueError(f"Could not load Parquet dataset: {exc}") from exc

    if df.empty:
        raise ValueError("The source dataset is empty.")

    print(f"EXTRACT: {len(df):,} rows and {len(df.columns)} columns loaded.")

    return df
