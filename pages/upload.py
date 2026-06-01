import streamlit as st
import pandas as pd
import json
import streamlit_authenticator as stauth

from src.data_processing import merge_two_sources, load_from_db
from src.upload import prepare_upload
from src.db import replace_employees, log_upload, fetch_last_upload

st.set_page_config(page_title="Upload HR Data", page_icon="📤")

# ── Auth ─────────────────────────────────────────────────────────────────────
credentials = json.loads(json.dumps({"usernames": st.secrets["credentials"]["usernames"].to_dict()}))
cookie_cfg = st.secrets["cookie"].to_dict()

authenticator = stauth.Authenticate(
    credentials,
    cookie_cfg["name"],
    cookie_cfg["key"],
    cookie_cfg["expiry_days"],
)

authenticator.login(location="main")

auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

if auth_status is False:
    st.error("Incorrect username or password.")
    st.stop()
if auth_status is None:
    st.info("Please log in to upload data.")
    st.stop()

# ── Authenticated ─────────────────────────────────────────────────────────────
st.title("📤 Upload HR Data")
authenticator.logout(location="sidebar")

last = fetch_last_upload()
if last:
    st.info(
        f"Current data: uploaded **{last['uploaded_at'][:10]}** "
        f"by **{last['uploaded_by']}** — **{last['row_count']:,}** rows"
    )
else:
    st.warning("No data in the system yet.")

st.divider()

# ── Step 1: Active Employees ──────────────────────────────────────────────────
st.subheader("Step 1 — Active Employees file")
st.caption("Export: All Active Employees_*.xlsx")
active_file = st.file_uploader("", type=["xlsx"], key="active_upload", label_visibility="collapsed")

# ── Step 2: Leavers ───────────────────────────────────────────────────────────
st.subheader("Step 2 — Offboarding / Leavers file")
st.caption("Export: Offboarding Management_*.xlsx")
leavers_file = st.file_uploader("", type=["xlsx"], key="leavers_upload", label_visibility="collapsed")

# ── Status indicators ─────────────────────────────────────────────────────────
active_ok  = active_file is not None
leavers_ok = leavers_file is not None

c1, c2 = st.columns(2)
c1.markdown(f"Active file: {'✅ loaded' if active_ok else '⏳ waiting'}")
c2.markdown(f"Leavers file: {'✅ loaded' if leavers_ok else '⏳ waiting'}")

if not (active_ok and leavers_ok):
    st.stop()

st.divider()

# ── Parse & Merge ─────────────────────────────────────────────────────────────
try:
    active_raw = pd.read_excel(active_file)
except Exception as e:
    st.error(f"Could not read Active Employees file: {e}")
    st.stop()

try:
    leavers_raw = pd.read_excel(leavers_file)
except Exception as e:
    st.error(f"Could not read Offboarding file: {e}")
    st.stop()

try:
    merged_df = merge_two_sources(active_raw, leavers_raw)
except Exception as e:
    st.error(f"Merge failed: {e}")
    st.stop()

active_count  = (merged_df['Employee Status'] == 'Active').sum()
leaver_count  = (merged_df['Employee Status'] == 'Departed').sum()

st.success(
    f"Ready to upload — **{len(merged_df):,} total rows**: "
    f"{active_count:,} active, {leaver_count:,} departed."
)

with st.expander("Preview merged data (first 10 rows)"):
    st.dataframe(merged_df.head(10), use_container_width=True)

with st.expander("Column summary"):
    col_info = pd.DataFrame({
        'Column': merged_df.columns,
        'Non-null': merged_df.notna().sum().values,
        'Sample': [
            str(merged_df[c].dropna().iloc[0]) if merged_df[c].notna().any() else '—'
            for c in merged_df.columns
        ],
    })
    st.dataframe(col_info, use_container_width=True, hide_index=True)

# ── Upload ────────────────────────────────────────────────────────────────────
st.divider()
if st.button("Apply Upload", type="primary"):
    with st.spinner("Uploading to Supabase..."):
        try:
            final_df = prepare_upload(merged_df.copy(), {})
            replace_employees(final_df)
            log_upload(username, len(final_df), list(final_df.columns))
            load_from_db.clear()
            st.success(f"{len(final_df):,} rows uploaded. Dashboard is now live.")
            st.balloons()
        except Exception as e:
            st.error(f"Upload failed: {e}")
