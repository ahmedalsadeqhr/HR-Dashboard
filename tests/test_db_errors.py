import httpx
from postgrest.exceptions import APIError

from src.db_errors import describe_db_error


def test_api_error_shows_code_and_hint():
    exc = APIError({"code": "PGRST002", "message": "schema cache", "details": None, "hint": None})
    out = describe_db_error(exc)
    assert "PGRST002" in out and "schema cache" in out and "Wait a few minutes" in out


def test_connect_error():
    assert "Cannot reach the database" in describe_db_error(httpx.ConnectError("x"))


def test_unknown_error():
    assert "ValueError" in describe_db_error(ValueError("boom"))
