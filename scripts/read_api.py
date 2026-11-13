from pathlib import Path

import pandas as pd
import requests


API_URL = "https://archive-api.open-meteo.com/v1/archive"

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "datasets" / "weather.csv"


def fetch_weather() -> pd.DataFrame:
    """Fetch hourly historical weather data from Open-Meteo."""

    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "start_date": "2025-10-01",
        "end_date": "2025-10-07",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Europe/Berlin",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data["hourly"])

    df["time"] = pd.to_datetime(df["time"])

    return df


def main():
    df = fetch_weather()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("First 15 rows of the weather dataset:")
    print(df.head(15).to_string(index=False))

    print(f"\nDataset shape: {df.shape}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()