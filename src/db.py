import pandas as pd
from src.supabase_client import get_supabase_client

_INTERNAL_COLS = {"id", "_uploaded_at"}
_BATCH_SIZE = 500  # Supabase insert limit per request


def fetch_employees() -> pd.DataFrame:
    """Fetch all rows from employees table, unpacking the JSONB data column."""
    client = get_supabase_client()
    result = client.table("employees").select("data").execute()
    rows = result.data
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([r["data"] for r in rows])


def fetch_last_upload() -> dict | None:
    """Return the most recent upload_log row, or None if no uploads yet."""
    client = get_supabase_client()
    result = (
        client.table("upload_log")
        .select("*")
        .order("uploaded_at", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    return None


def replace_employees(df: pd.DataFrame) -> None:
    """Truncate employees table and insert all rows as JSONB in batches."""
    client = get_supabase_client()
    client.table("employees").delete().gte("id", 0).execute()
    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    for i in range(0, len(records), _BATCH_SIZE):
        batch = [{"data": row} for row in records[i: i + _BATCH_SIZE]]
        client.table("employees").insert(batch).execute()


def log_upload(uploaded_by: str, row_count: int, columns: list[str]) -> None:
    """Insert one row into upload_log."""
    client = get_supabase_client()
    client.table("upload_log").insert({
        "uploaded_by": uploaded_by,
        "row_count": row_count,
        "column_snapshot": columns,
    }).execute()
