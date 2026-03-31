from supabase import create_client, Client
import streamlit as st

_client: Client | None = None


def get_supabase_client() -> Client:
    """Return a cached Supabase client, initialised from Streamlit secrets."""
    global _client
    if _client is None:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client
