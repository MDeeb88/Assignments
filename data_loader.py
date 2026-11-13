from pathlib import Path

import pandas as pd


def load_dataset():
    """Load the Steam games dataset and display the first 10 rows."""

    data_path = Path(__file__).resolve().parent / "datasets" / "games.csv"

    df = pd.read_csv(data_path, index_col=False)

    print("First 10 rows of the Steam games dataset:")
    print(df.head(10))


if __name__ == "__main__":
    load_dataset()