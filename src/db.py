import pandas as pd
import streamlit as st
from src.supabase_client import get_supabase_client

_INTERNAL_COLS = {"id", "_uploaded_at"}
_BATCH_SIZE = 500  # Supabase insert limit per request


def fetch_employees() -> pd.DataFrame:
    """Fetch all rows from employees table, unpacking the JSONB data column.

    Supabase returns at most 1000 rows per request by default, so we paginate
    using .range() until we get a partial page (or empty page), which signals
    we've fetched everything.
    """
    client = get_supabase_client()
    all_rows: list[dict] = []
    page_size = 1000
    offset = 0

    while True:
        result = (
            client.table("employees")
            .select("data")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = result.data
        if not batch:
            break
        all_rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    if not all_rows:
        return pd.DataFrame()
    return pd.DataFrame([r["data"] for r in all_rows])


@st.cache_data(ttl=300, show_spinner=False)
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


def _max_id(client) -> int | None:
    rows = client.table("employees").select("id").order("id", desc=True).limit(1).execute().data
    return rows[0]["id"] if rows else None


def replace_employees(df: pd.DataFrame) -> None:
    """Replace all employee rows without ever leaving the table empty on failure.

    New rows are inserted first; only after every batch succeeds are the old rows
    (id <= the max id seen before the insert) deleted. If an insert fails, the
    partially inserted new rows are removed and the old data stays intact.
    """
    import math
    client = get_supabase_client()

    # Replace all NaN/inf/NaT with None for valid JSON
    clean = df.where(pd.notnull(df), None)
    raw_records = clean.to_dict(orient="records")

    def sanitize(v):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return v
    records = [{k: sanitize(v) for k, v in row.items()} for row in raw_records]

    old_max = _max_id(client)
    try:
        for i in range(0, len(records), _BATCH_SIZE):
            batch = [{"data": row} for row in records[i: i + _BATCH_SIZE]]
            client.table("employees").insert(batch).execute()
    except Exception:
        # Roll back: drop whatever new rows made it in, keep the old data.
        floor = old_max if old_max is not None else -1
        client.table("employees").delete().gt("id", floor).execute()
        raise

    if old_max is not None:
        client.table("employees").delete().lte("id", old_max).execute()


def log_upload(uploaded_by: str, row_count: int, columns: list[str]) -> None:
    """Insert one row into upload_log."""
    client = get_supabase_client()
    client.table("upload_log").insert({
        "uploaded_by": uploaded_by,
        "row_count": row_count,
        "column_snapshot": columns,
    }).execute()
