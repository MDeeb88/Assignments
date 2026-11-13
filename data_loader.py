
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "datasets"


def load_dataset() -> pd.DataFrame:
    """Read the Steam dataset and correct the missing CSV header."""
    csv_path = DATA_DIR / "games.csv"

    # The original CSV combines "Discount" and "DLC count".
    columns = pd.read_csv(csv_path, nrows=0).columns.tolist()
    index = columns.index("DiscountDLC count")
    columns[index:index + 1] = ["Discount", "DLC count"]

    return pd.read_csv(
        csv_path,
        header=0,
        names=columns,
        index_col=False,
        low_memory=False,
    )


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Steam dataset columns to appropriate data types."""
    df = df.copy()

    # Dates
    df["Release date"] = pd.to_datetime(
        df["Release date"], format="mixed", errors="coerce"
    )

    # Integer columns
    integer_columns = [
        "AppID", "Peak CCU", "Required age", "Discount",
        "DLC count", "Metacritic score", "User score",
        "Positive", "Negative", "Score rank", "Achievements",
        "Recommendations", "Average playtime forever",
        "Average playtime two weeks", "Median playtime forever",
        "Median playtime two weeks",
    ]

    for col in integer_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        ).astype("Int64")

    # Decimal columns
    df["Price"] = pd.to_numeric(
        df["Price"], errors="coerce"
    ).astype("Float64")

    # Boolean columns
    for col in ["Windows", "Mac", "Linux"]:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .str.lower()
            .map({"true": True, "false": False})
            .astype("boolean")
        )

    # Remaining columns are text
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype("string")

    # Movies column
    df["Movies"] = df["Movies"].astype("string")

    return df


def save_parquet(df: pd.DataFrame) -> None:
    """Save the converted dataset in Parquet format."""
    output_path = DATA_DIR / "games.parquet"

    df.to_parquet(output_path, engine="pyarrow", index=False)

    print(f"\nSaved Parquet file: {output_path}")


if __name__ == "__main__":
    df = load_dataset()
    df = convert_types(df)

    print("First 10 rows:")
    print(df.head(10))

    print("\nData types:")
    print(df.dtypes.to_string())

    save_parquet(df)
