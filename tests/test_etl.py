"""Automated tests for the Steam Games ETL package."""

import pandas as pd
import pytest

from etl import load as etl_load
from etl.extract import extract_data
from etl.load import load_data
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


def test_extract_reads_valid_parquet(tmp_path):
    """Test extraction of a valid Parquet dataset."""

    data = pd.DataFrame(
        {
            "AppID": [10, 20],
            "Name": ["Game A", "Game B"],
            "Price": [1.99, 2.99],
            "Positive": [100, 200],
            "Negative": [10, 20],
        }
    )

    dataset = tmp_path / "games.parquet"
    data.to_parquet(dataset, index=False)

    result = extract_data(dataset)

    assert len(result) == 2
    assert list(result.columns) == ["AppID", "Name", "Price", "Positive", "Negative"]


def test_extract_rejects_missing_dataset(tmp_path):
    """Test extraction when the dataset does not exist."""

    dataset = tmp_path / "missing.parquet"

    with pytest.raises(FileNotFoundError, match="Dataset not found"):
        extract_data(dataset)


def test_extract_rejects_missing_columns(tmp_path):
    """Test extraction when required columns are missing."""

    data = pd.DataFrame(
        {
            "AppID": [10],
            "Name": ["Game A"],
        }
    )

    dataset = tmp_path / "incomplete.parquet"
    data.to_parquet(dataset, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        extract_data(dataset)


def test_load_data_uploads_and_verifies_records(monkeypatch):
    """Test database loading using a mocked PostgreSQL connection."""

    class FakeComposable:
        def __init__(self, value):
            self.value = value

        def format(self, *args):
            return self

        def as_string(self, conn):
            return self.value

    class FakeCursor:
        def __init__(self):
            self.executed = []

        def execute(self, query):
            self.executed.append(query)

        def fetchone(self):
            return (1,)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class FakeConnection:
        def __init__(self):
            self.fake_cursor = FakeCursor()
            self.closed = False

        def cursor(self):
            return self.fake_cursor

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def close(self):
            self.closed = True

    connection = FakeConnection()
    uploaded_records = []

    monkeypatch.setattr(
        etl_load,
        "get_credentials",
        lambda path: {
            "url": "localhost",
            "port": 5432,
            "user": "test",
            "pass": "test",
            "db_name": "homeworks",
        },
    )

    monkeypatch.setattr(
        etl_load.psycopg2,
        "connect",
        lambda **kwargs: connection,
    )

    monkeypatch.setattr(
        etl_load.sql,
        "SQL",
        FakeComposable,
    )

    monkeypatch.setattr(
        etl_load.sql,
        "Identifier",
        FakeComposable,
    )

    monkeypatch.setattr(
        etl_load,
        "execute_values",
        lambda cursor, query, records: uploaded_records.extend(records),
    )

    data = pd.DataFrame(
        {
            "AppID": [10],
            "Name": ["Game A"],
            "Price": [1.99],
            "Positive": [100],
            "Negative": [10],
        }
    )

    result = load_data(
        data,
        creds_path="creds.db",
        table_name="deebm",
    )

    assert result == 1
    assert len(uploaded_records) == 1
    assert uploaded_records[0][0] == 10
    assert connection.closed is True
