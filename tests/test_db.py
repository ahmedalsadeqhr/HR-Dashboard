import pytest
from unittest.mock import patch, MagicMock


def test_get_supabase_client_returns_client():
    """get_supabase_client() returns a Supabase client instance."""
    mock_client = MagicMock()
    with patch("src.supabase_client.create_client", return_value=mock_client):
        with patch("src.supabase_client.st") as mock_st:
            mock_st.secrets = {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_KEY": "test-key",
            }
            # Re-import to pick up mocked secrets
            import importlib
            import src.supabase_client as sc
            importlib.reload(sc)
            client = sc.get_supabase_client()
            assert client is not None
