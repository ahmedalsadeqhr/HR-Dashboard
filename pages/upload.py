import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from src.config import REQUIRED_COLUMNS
from src.upload import detect_schema_changes, prepare_upload, validate_required_columns
from src.db import replace_employees, log_upload, fetch_last_upload
from src.data_processing import load_from_db

st.set_page_config(page_title="Upload Master Sheet", page_icon="📤")

# ── Auth ────────────────────────────────────────────────────────────────────
# Deep-copy secrets into plain dicts — streamlit-authenticator modifies credentials
# in-place (to hash passwords) which fails on Streamlit's read-only secrets object
import json
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

# ── Authenticated ────────────────────────────────────────────────────────────
st.title("📤 Upload Master Sheet")
authenticator.logout(location="sidebar")

# Show current data stats
last = fetch_last_upload()
if last:
    st.info(
        f"Current data: uploaded **{last['uploaded_at'][:10]}** "
        f"by **{last['uploaded_by']}** — **{last['row_count']:,}** rows"
    )
else:
    st.warning("No data in the system yet. Upload a Master Sheet to get started.")

st.divider()

# ── File Upload ──────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Select Master Sheet (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.stop()

# Parse file
try:
    raw_df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Could not read Excel file: {e}")
    st.stop()

st.success(f"File parsed: {len(raw_df):,} rows, {len(raw_df.columns)} columns detected.")

# ── Column Mapping ───────────────────────────────────────────────────────────
schema_changes = detect_schema_changes(raw_df, REQUIRED_COLUMNS)

if schema_changes:
    st.subheader("Column Mapping Required")
    st.caption("Some expected columns were not found. Map them below or mark as Skip.")

    mapping = {}
    all_file_cols = list(raw_df.columns)
    skip_option = "— Skip (drop this column) —"

    for required_col, guess in schema_changes.items():
        default = guess if guess in all_file_cols else skip_option
        selected = st.selectbox(
            f'Map file column for **"{required_col}"**',
            options=all_file_cols + [skip_option],
            index=(all_file_cols + [skip_option]).index(default) if default in (all_file_cols + [skip_option]) else len(all_file_cols),
            key=f"map_{required_col}",
        )
        if selected == skip_option:
            mapping[required_col] = None
        else:
            mapping[selected] = required_col

    # Apply mapping to a preview copy
    preview_df = raw_df.copy()
    for src, tgt in mapping.items():
        if tgt is None and src in preview_df.columns:
            preview_df = preview_df.drop(columns=[src])
        elif tgt and src in preview_df.columns:
            preview_df = preview_df.rename(columns={src: tgt})
else:
    mapping = {}
    preview_df = raw_df.copy()

# ── Validation ───────────────────────────────────────────────────────────────
missing = validate_required_columns(preview_df, REQUIRED_COLUMNS)
if missing:
    st.error(f"Cannot upload — required columns still missing: **{', '.join(missing)}**")
    st.caption("Please fix the column mapping above or check your Excel file.")
    st.stop()

st.success("All required columns present. Ready to upload.")

# ── Confirm & Upload ─────────────────────────────────────────────────────────
with st.expander("Preview first 5 rows"):
    st.dataframe(preview_df.head())

if st.button("Apply Upload", type="primary"):
    with st.spinner("Uploading to Supabase..."):
        try:
            final_df = prepare_upload(raw_df.copy(), mapping)
            replace_employees(final_df)
            log_upload(username, len(final_df), list(final_df.columns))
            load_from_db.clear()  # Invalidate dashboard cache
            st.success(f"{len(final_df):,} rows loaded. Dashboard is now live.")
            st.balloons()
        except Exception as e:
            st.error(f"Upload failed: {e}")
