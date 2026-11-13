"""Validate transformed Steam game records before database loading."""

import pandas as pd

from .extract import REQUIRED_COLUMNS


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Check schema, types, completeness, uniqueness, and value ranges."""

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    if df.empty:
        raise ValueError("Validation failed: no records to upload.")

    if len(df) > 100:
        raise ValueError("Validation failed: maximum 100 records allowed.")

    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Validation failed: missing values detected.")

    if df["AppID"].duplicated().any():
        raise ValueError("Validation failed: duplicate AppIDs detected.")

    if df["Name"].astype("string").str.strip().eq("").any():
        raise ValueError("Validation failed: blank game names detected.")

    for column in ["AppID", "Price", "Positive", "Negative"]:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError(f"Validation failed: {column} must be numeric.")

        if (df[column] < 0).any():
            raise ValueError(f"Validation failed: negative {column} values.")

    for column in ["AppID", "Positive", "Negative"]:
        if not pd.api.types.is_integer_dtype(df[column]):
            raise TypeError(f"Validation failed: {column} must be integer.")

    print(f"VALIDATE: {len(df)} records passed all checks.")

    return df
