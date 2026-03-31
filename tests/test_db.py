import pytest
from unittest.mock import patch, MagicMock
import src.supabase_client as sc


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch):
    """Reset the singleton _client before and after each test."""
    monkeypatch.setattr(sc, "_client", None)
    yield
    monkeypatch.setattr(sc, "_client", None)


def test_get_supabase_client_returns_mock_client():
    """get_supabase_client() returns exactly the client from create_client()."""
    mock_client = MagicMock()
    with patch("src.supabase_client.create_client", return_value=mock_client) as mock_create:
        with patch("src.supabase_client.st") as mock_st:
            mock_st.secrets = {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_KEY": "test-key",
            }
            client = sc.get_supabase_client()
            assert client is mock_client
            mock_create.assert_called_once_with("https://test.supabase.co", "test-key")


def test_get_supabase_client_is_singleton():
    """get_supabase_client() returns cached client on second call without re-connecting."""
    mock_client = MagicMock()
    with patch("src.supabase_client.create_client", return_value=mock_client) as mock_create:
        with patch("src.supabase_client.st") as mock_st:
            mock_st.secrets = {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_KEY": "test-key",
            }
            first = sc.get_supabase_client()
            second = sc.get_supabase_client()
            assert first is second
            mock_create.assert_called_once()


import pandas as pd
from src.db import fetch_employees, log_upload, replace_employees


def test_fetch_employees_returns_dataframe():
    """fetch_employees() returns a DataFrame."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = [
        {"id": 1, "Gender": "M", "Department": "Tech", "_uploaded_at": "2026-01-01"}
    ]
    with patch("src.db.get_supabase_client", return_value=mock_client):
        df = fetch_employees()
        assert isinstance(df, pd.DataFrame)
        assert "Gender" in df.columns
        assert "_uploaded_at" not in df.columns  # internal column stripped


def test_fetch_employees_returns_empty_dataframe_when_no_data():
    """fetch_employees() returns empty DataFrame when table is empty."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = []
    with patch("src.db.get_supabase_client", return_value=mock_client):
        df = fetch_employees()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


def test_log_upload_inserts_row():
    """log_upload() inserts one row into upload_log."""
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock()
    with patch("src.db.get_supabase_client", return_value=mock_client):
        log_upload("ahmed", 500, ["Gender", "Department"])
        mock_client.table.assert_called_with("upload_log")
        call_args = mock_client.table.return_value.insert.call_args[0][0]
        assert call_args["uploaded_by"] == "ahmed"
        assert call_args["row_count"] == 500
        assert "Gender" in call_args["column_snapshot"]


def test_replace_employees_truncates_then_inserts():
    """replace_employees() deletes all rows then inserts new ones."""
    mock_client = MagicMock()
    mock_client.table.return_value.delete.return_value.neq.return_value.execute.return_value = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock()

    df = pd.DataFrame({"Gender": ["M", "F"], "Department": ["Tech", "HR"]})
    with patch("src.db.get_supabase_client", return_value=mock_client):
        replace_employees(df)
        # Delete was called
        mock_client.table.return_value.delete.assert_called()
        # Insert was called
        mock_client.table.return_value.insert.assert_called()
