import httpx
from postgrest.exceptions import APIError

_HINTS = {
    "PGRST002": (
        "The API is still loading its schema cache (common right after a project "
        "restore). Wait a few minutes and reload."
    ),
    "PGRST205": "Table not found. Check that the table exists in the restored project.",
    "42P01": "Table does not exist. Check that the table exists in the restored project.",
    "42501": "Permission denied. Check Row Level Security policies and that SUPABASE_KEY has read access.",
    "PGRST301": "JWT problem. Check that SUPABASE_KEY matches Project Settings > API.",
    "PGRST300": "JWT problem. Check that SUPABASE_KEY matches Project Settings > API.",
}


def describe_db_error(exc: Exception) -> str:
    """Return a user-facing description of a Supabase/PostgREST failure."""
    if isinstance(exc, APIError):
        code = exc.code or "unknown"
        parts = [f"**Database error `{code}`**: {exc.message or 'no message'}"]
        if exc.details:
            parts.append(f"Details: {exc.details}")
        if exc.hint:
            parts.append(f"Hint: {exc.hint}")
        if code in _HINTS:
            parts.append(_HINTS[code])
        return "\n\n".join(parts)
    if isinstance(exc, httpx.ConnectError):
        return (
            "**Cannot reach the database.** The Supabase project may be paused "
            "or SUPABASE_URL may be wrong."
        )
    return f"**Unexpected error loading data** ({type(exc).__name__}): {exc}"
