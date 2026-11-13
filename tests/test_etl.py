"""Automated tests for the Steam Games ETL package."""

import pandas as pd
import pytest

from etl.transform import transform_data
from etl.validate import validate_data


@pytest.fixture
def sample_data():
    """Create a small synthetic dataset for testing."""
    return pd.DataFrame(
        {
            "AppID": [10, 20, 20, 30, 40],
            "Name": [
                "Game A",
                "Game B",
                "Game B duplicate",
                "",
                "Game D",
            ],
            "Price": [1.99, 4.99, 4.99, 2.99, -1.0],
            "Positive": [100, 50, 50, 20, 10],
            "Negative": [5, 2, 2, 1, 0],
        }
    )


def test_transform_removes_invalid_and_duplicate_rows(sample_data):
    result = transform_data(sample_data)

    assert len(result) == 2
    assert result["AppID"].tolist() == [10, 20]
    assert result["AppID"].is_unique
    assert not result.isna().any().any()


def test_validate_accepts_clean_data(sample_data):
    clean = transform_data(sample_data)

    result = validate_data(clean)

    assert len(result) == 2


def test_validate_rejects_duplicate_ids():
    df = pd.DataFrame(
        {
            "AppID": [10, 10],
            "Name": ["Game A", "Game B"],
            "Price": [1.99, 2.99],
            "Positive": [10, 20],
            "Negative": [1, 2],
        }
    )

    with pytest.raises(ValueError, match="duplicate AppIDs"):
        validate_data(df)


def test_validate_rejects_more_than_100_rows():
    df = pd.DataFrame(
        {
            "AppID": range(101),
            "Name": ["Game"] * 101,
            "Price": [1.99] * 101,
            "Positive": [10] * 101,
            "Negative": [1] * 101,
        }
    )

    with pytest.raises(ValueError, match="maximum 100"):
        validate_data(df)


def test_validate_rejects_negative_prices():
    df = pd.DataFrame(
        {
            "AppID": [10],
            "Name": ["Invalid Game"],
            "Price": [-5.0],
            "Positive": [10],
            "Negative": [1],
        }
    )

    with pytest.raises(ValueError, match="negative Price"):
        validate_data(df)
