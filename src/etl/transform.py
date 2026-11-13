"""Clean and transform Steam game records for PostgreSQL."""

import pandas as pd

from .extract import REQUIRED_COLUMNS


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean records and select up to 100 valid games."""
    data = df.copy()
    original_count = len(data)

    # Convert numeric columns
    numeric_columns = ["AppID", "Price", "Positive", "Negative"]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Normalize game names
    data["Name"] = data["Name"].astype("string").str.strip()

    # Remove records containing missing required values
    data = data.dropna(subset=list(REQUIRED_COLUMNS))

    # Remove blank names
    data = data[data["Name"].str.len() > 0]

    # Exclude invalid negative values
    data = data[
        (data["AppID"] >= 0)
        & (data["Price"] >= 0)
        & (data["Positive"] >= 0)
        & (data["Negative"] >= 0)
    ]

    # Ensure integer fields contain whole numbers
    for column in ["AppID", "Positive", "Negative"]:
        data = data[data[column] % 1 == 0]
        data[column] = data[column].astype("int64")

    # Prepare prices for NUMERIC(12, 2)
    data["Price"] = data["Price"].round(2)

    # Remove duplicate games and enforce a stable ordering
    data = (
        data.drop_duplicates(subset="AppID")
        .sort_values("AppID")
        .head(100)
        .reset_index(drop=True)
    )

    print(f"TRANSFORM: {original_count:,} source rows processed.")
    print(f"TRANSFORM: {len(data)} clean records selected.")

    return data
