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
