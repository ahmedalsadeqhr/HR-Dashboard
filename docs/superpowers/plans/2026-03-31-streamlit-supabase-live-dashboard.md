# Streamlit + Supabase Live Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the session-based Excel upload with a persistent Supabase PostgreSQL backend so the HR dashboard is always live, requires no re-upload between sessions, and supports schema changes via a column-mapping UI.

**Architecture:** Three uploaders authenticate via a password-protected Streamlit upload page, upload Excel files that are parsed and written to Supabase, while all other internal users access the dashboard at the root URL with no login. The dashboard reads from Supabase on load (cached 5 min) and all existing Python calculations remain untouched.

**Tech Stack:** Streamlit, Supabase (PostgreSQL + Python client), pandas, streamlit-authenticator, openpyxl

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `requirements.txt` | Modify | Add `supabase`, `streamlit-authenticator`, `bcrypt` |
| `.streamlit/secrets.toml` | Create | Supabase URL/key + uploader credentials (local only, not committed) |
| `.streamlit/secrets.toml.example` | Create | Template showing required secret keys (committed) |
| `src/supabase_client.py` | Create | Supabase connection singleton |
| `src/db.py` | Create | All DB read/write operations (employees table, upload_log table) |
| `src/data_processing.py` | Modify | Replace `load_excel()` with `load_from_db()` that reads from Supabase |
| `src/upload.py` | Create | Column detection, mapping logic, upload pipeline |
| `pages/upload.py` | Create | Streamlit upload page with auth + upload UX |
| `app.py` | Modify | Remove file uploader from sidebar; add "Last updated" badge |
| `sql/schema.sql` | Create | SQL to create employees + upload_log tables in Supabase |
| `tests/test_db.py` | Create | Unit tests for db.py functions |
| `tests/test_upload.py` | Create | Unit tests for upload pipeline (column mapping, validation) |

---

## Task 1: Supabase Project Setup (manual steps)

This task is performed by you in the Supabase web UI — no code changes.

- [ ] **Step 1: Create Supabase project**

  Go to https://supabase.com → New project → name it `hr-dashboard` → choose free tier → set a strong DB password → save the password somewhere safe.

- [ ] **Step 2: Get your credentials**

  In the Supabase dashboard → Project Settings → API:
  - Copy **Project URL** (looks like `https://xxxx.supabase.co`)
  - Copy **anon/public key** (long JWT string under "Project API keys")

- [ ] **Step 3: Run schema SQL**

  In Supabase dashboard → SQL Editor → New query → paste and run:

  ```sql
  -- Drop and recreate employees table (run once on setup)
  create table if not exists employees (
    id bigserial primary key,
    _uploaded_at timestamptz default now()
  );

  -- Upload log table
  create table if not exists upload_log (
    id bigserial primary key,
    uploaded_by text not null,
    uploaded_at timestamptz default now(),
    row_count integer not null,
    column_snapshot jsonb not null
  );

  -- Enable Row Level Security (open read for internal use)
  alter table employees enable row level security;
  alter table upload_log enable row level security;

  -- Allow all reads (internal dashboard, no auth)
  create policy "allow_read_employees" on employees for select using (true);
  create policy "allow_read_upload_log" on upload_log for select using (true);

  -- Allow all inserts/deletes (upload page uses service role key)
  create policy "allow_all_employees" on employees for all using (true);
  create policy "allow_all_upload_log" on upload_log for all using (true);
  ```

  Expected: No errors, tables appear in Table Editor.

---

## Task 2: Add Dependencies

- [ ] **Step 1: Update requirements.txt**

  Current content:
  ```
  streamlit==1.41.0
  pandas==2.2.3
  openpyxl==3.1.5
  numpy==2.2.2
  plotly==5.24.1
  ```

  Replace with:
  ```
  streamlit==1.41.0
  pandas==2.2.3
  openpyxl==3.1.5
  numpy==2.2.2
  plotly==5.24.1
  supabase==2.10.0
  streamlit-authenticator==0.3.3
  bcrypt==4.2.1
  ```

- [ ] **Step 2: Install locally**

  ```bash
  pip install supabase==2.10.0 streamlit-authenticator==0.3.3 bcrypt==4.2.1
  ```

  Expected: No errors.

- [ ] **Step 3: Commit**

  ```bash
  git add requirements.txt
  git commit -m "chore: add supabase and streamlit-authenticator dependencies"
  ```

---

## Task 3: Secrets Configuration

- [ ] **Step 1: Create secrets template (committed)**

  Create `.streamlit/secrets.toml.example`:

  ```toml
  # Copy this file to .streamlit/secrets.toml and fill in real values
  # DO NOT commit secrets.toml

  SUPABASE_URL = "https://your-project-ref.supabase.co"
  SUPABASE_KEY = "your-anon-public-key"

  [credentials.usernames.ahmed]
  name = "Ahmed"
  password = "$2b$12$hashed_password_here"

  [credentials.usernames.member2]
  name = "Member 2"
  password = "$2b$12$hashed_password_here"

  [credentials.usernames.member3]
  name = "Member 3"
  password = "$2b$12$hashed_password_here"

  [cookie]
  name = "hr_upload_auth"
  key = "some_random_32_char_string_here"
  expiry_days = 1
  ```

- [ ] **Step 2: Create actual secrets.toml (NOT committed)**

  Create `.streamlit/secrets.toml` with your real values.

  To generate hashed passwords, run in Python:
  ```python
  import bcrypt
  password = "your_plain_password"
  hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
  print(hashed)
  ```
  Run once per uploader to get their hashed password, paste into secrets.toml.

- [ ] **Step 3: Verify .gitignore excludes secrets.toml**

  ```bash
  grep "secrets.toml" .gitignore
  ```

  If no output, run:
  ```bash
  echo ".streamlit/secrets.toml" >> .gitignore
  ```

- [ ] **Step 4: Commit template and gitignore update**

  ```bash
  git add .streamlit/secrets.toml.example .gitignore
  git commit -m "chore: add secrets template and gitignore for secrets.toml"
  ```

---

## Task 4: Supabase Client Module

- [ ] **Step 1: Write the failing test**

  Create `tests/test_db.py`:

  ```python
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
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  pytest tests/test_db.py::test_get_supabase_client_returns_client -v
  ```

  Expected: `ModuleNotFoundError` or `ImportError` — `src.supabase_client` does not exist yet.

- [ ] **Step 3: Create src/supabase_client.py**

  ```python
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
  ```

- [ ] **Step 4: Run test to verify it passes**

  ```bash
  pytest tests/test_db.py::test_get_supabase_client_returns_client -v
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/supabase_client.py tests/test_db.py
  git commit -m "feat: add supabase client singleton"
  ```

---

## Task 5: Database Operations Module

- [ ] **Step 1: Write failing tests**

  Add to `tests/test_db.py`:

  ```python
  import pandas as pd
  from unittest.mock import patch, MagicMock
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
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_db.py -v
  ```

  Expected: `ImportError: cannot import name 'fetch_employees' from 'src.db'`

- [ ] **Step 3: Create src/db.py**

  ```python
  import pandas as pd
  from src.supabase_client import get_supabase_client

  _INTERNAL_COLS = {"id", "_uploaded_at"}
  _BATCH_SIZE = 500  # Supabase insert limit per request


  def fetch_employees() -> pd.DataFrame:
      """Fetch all rows from employees table, dropping internal columns."""
      client = get_supabase_client()
      result = client.table("employees").select("*").execute()
      rows = result.data
      if not rows:
          return pd.DataFrame()
      df = pd.DataFrame(rows)
      cols_to_drop = [c for c in _INTERNAL_COLS if c in df.columns]
      return df.drop(columns=cols_to_drop)


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
      """Truncate employees table and insert all rows from df in batches."""
      client = get_supabase_client()
      # Truncate: delete where id != 0 (deletes all rows)
      client.table("employees").delete().neq("id", 0).execute()
      # Insert in batches
      records = df.where(pd.notnull(df), None).to_dict(orient="records")
      for i in range(0, len(records), _BATCH_SIZE):
          batch = records[i : i + _BATCH_SIZE]
          client.table("employees").insert(batch).execute()


  def log_upload(uploaded_by: str, row_count: int, columns: list[str]) -> None:
      """Insert one row into upload_log."""
      client = get_supabase_client()
      client.table("upload_log").insert({
          "uploaded_by": uploaded_by,
          "row_count": row_count,
          "column_snapshot": columns,
      }).execute()
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_db.py -v
  ```

  Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/db.py tests/test_db.py
  git commit -m "feat: add db module for supabase read/write operations"
  ```

---

## Task 6: Upload Pipeline (Column Mapping + Validation)

- [ ] **Step 1: Write failing tests**

  Create `tests/test_upload.py`:

  ```python
  import pytest
  import pandas as pd
  from src.upload import detect_schema_changes, apply_column_mapping, validate_required_columns

  REQUIRED = ["Gender", "Department", "Position", "Employee Status", "Exit Type"]


  def test_detect_schema_changes_returns_empty_when_columns_match():
      """No changes detected when file columns match required columns exactly."""
      df = pd.DataFrame(columns=["Gender", "Department", "Position", "Employee Status", "Exit Type", "Join Date"])
      changes = detect_schema_changes(df, REQUIRED)
      assert changes == {}


  def test_detect_schema_changes_flags_renamed_columns():
      """Flags columns that are missing from required but similar names exist in file."""
      df = pd.DataFrame(columns=["gender", "Department", "Position", "Employee Status", "Exit Type"])
      changes = detect_schema_changes(df, REQUIRED)
      # "gender" vs "Gender" — case mismatch should be detected
      assert "Gender" in changes


  def test_apply_column_mapping_renames_columns():
      """apply_column_mapping() renames df columns according to the mapping dict."""
      df = pd.DataFrame({"Emp Status": ["Active"], "Dept": ["Tech"]})
      mapping = {"Emp Status": "Employee Status", "Dept": "Department"}
      result = apply_column_mapping(df, mapping)
      assert "Employee Status" in result.columns
      assert "Department" in result.columns
      assert "Emp Status" not in result.columns


  def test_apply_column_mapping_skips_none_values():
      """Columns mapped to None are dropped from the dataframe."""
      df = pd.DataFrame({"Gender": ["M"], "UNKNOWN_COL": ["X"]})
      mapping = {"UNKNOWN_COL": None}
      result = apply_column_mapping(df, mapping)
      assert "UNKNOWN_COL" not in result.columns
      assert "Gender" in result.columns


  def test_validate_required_columns_passes_when_all_present():
      """No error raised when all required columns are present."""
      df = pd.DataFrame(columns=["Gender", "Department", "Position", "Employee Status", "Exit Type"])
      missing = validate_required_columns(df, REQUIRED)
      assert missing == []


  def test_validate_required_columns_returns_missing_list():
      """Returns list of missing required columns."""
      df = pd.DataFrame(columns=["Gender", "Department"])
      missing = validate_required_columns(df, REQUIRED)
      assert "Position" in missing
      assert "Employee Status" in missing
      assert "Exit Type" in missing
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_upload.py -v
  ```

  Expected: `ImportError: cannot import name 'detect_schema_changes' from 'src.upload'`

- [ ] **Step 3: Create src/upload.py**

  ```python
  import pandas as pd
  from src.config import REQUIRED_COLUMNS


  def detect_schema_changes(df: pd.DataFrame, required: list[str]) -> dict[str, str | None]:
      """
      Compare df columns against required columns.
      Returns a mapping of {required_col: best_guess_from_file} for any that are missing.
      best_guess is the closest match found in df.columns (case-insensitive), or None.
      """
      file_cols = list(df.columns)
      file_cols_lower = {c.lower(): c for c in file_cols}
      changes = {}
      for req in required:
          if req not in file_cols:
              # Try case-insensitive match
              guess = file_cols_lower.get(req.lower())
              changes[req] = guess  # None if no guess found
      return changes


  def apply_column_mapping(df: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
      """
      Rename or drop columns based on mapping.
      mapping: {current_col_name: target_col_name} — None means drop.
      """
      rename = {k: v for k, v in mapping.items() if v is not None and k in df.columns}
      drop = [k for k, v in mapping.items() if v is None and k in df.columns]
      df = df.rename(columns=rename)
      df = df.drop(columns=drop, errors="ignore")
      return df


  def validate_required_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
      """Return list of required columns missing from df. Empty list means valid."""
      return [col for col in required if col not in df.columns]


  def prepare_upload(df: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
      """Apply column mapping then return the processed dataframe ready for DB insert."""
      df = apply_column_mapping(df, mapping)
      # Convert all date columns to ISO string for JSON serialisation
      for col in df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
          df[col] = df[col].dt.strftime("%Y-%m-%d").where(df[col].notna(), None)
      return df
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_upload.py -v
  ```

  Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/upload.py tests/test_upload.py
  git commit -m "feat: add upload pipeline with column mapping and validation"
  ```

---

## Task 7: Update data_processing.py to Read from Supabase

- [ ] **Step 1: Write failing test**

  Add to `tests/test_db.py`:

  ```python
  from src.data_processing import load_from_db


  def test_load_from_db_returns_processed_dataframe():
      """load_from_db() returns a processed DataFrame with derived columns."""
      import pandas as pd
      from unittest.mock import patch

      raw_data = pd.DataFrame({
          "Gender": ["M", "F"],
          "Department": ["Tech", "HR"],
          "Employee Status": ["Active", "Departed"],
          "Join Date": ["2022-01-15", "2021-06-01"],
          "Exit Date": [None, "2023-03-01"],
          "Position": ["Engineer", "Manager"],
          "Exit Type": [None, "Resignation"],
      })

      with patch("src.data_processing.fetch_employees", return_value=raw_data):
          df = load_from_db()
          assert isinstance(df, pd.DataFrame)
          assert "Tenure (Months)" in df.columns
          assert "Join Year" in df.columns
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  pytest tests/test_db.py::test_load_from_db_returns_processed_dataframe -v
  ```

  Expected: `ImportError: cannot import name 'load_from_db' from 'src.data_processing'`

- [ ] **Step 3: Modify src/data_processing.py**

  Add this import at the top of the file (after the existing imports):
  ```python
  from src.db import fetch_employees
  ```

  Add this new function after the existing `load_excel()` function:
  ```python
  @st.cache_data(ttl=300)
  def load_from_db() -> pd.DataFrame:
      """Load employee data from Supabase and process it. Cached for 5 minutes."""
      df = fetch_employees()
      if df.empty:
          return df
      return process_data(df)
  ```

  Do NOT remove `load_excel()` — it stays for local development fallback.

- [ ] **Step 4: Run test to verify it passes**

  ```bash
  pytest tests/test_db.py::test_load_from_db_returns_processed_dataframe -v
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/data_processing.py tests/test_db.py
  git commit -m "feat: add load_from_db() to data_processing for supabase-backed data load"
  ```

---

## Task 8: Update app.py to Use Supabase Data

- [ ] **Step 1: Open app.py and find the data loading section**

  In `app.py`, find the sidebar section that contains `st.file_uploader`. It looks like:

  ```python
  uploaded_file = st.sidebar.file_uploader("Upload Master Sheet", type=["xlsx"])
  if uploaded_file:
      df = load_excel(uploaded_file)
  else:
      df = load_excel(DATA_FILE)
  ```

- [ ] **Step 2: Replace file uploader with DB loader**

  Replace the block identified above with:

  ```python
  from src.data_processing import load_from_db
  from src.db import fetch_last_upload

  df = load_from_db()

  # Show last updated badge in sidebar
  last = fetch_last_upload()
  if last:
      st.sidebar.caption(
          f"Last updated: {last['uploaded_at'][:10]} by {last['uploaded_by']} ({last['row_count']:,} rows)"
      )
  else:
      st.sidebar.caption("No data uploaded yet. Go to the Upload page.")
  ```

- [ ] **Step 3: Handle empty state**

  Directly after `df = load_from_db()`, add:

  ```python
  if df.empty:
      st.warning("No employee data found. Please upload a Master Sheet via the Upload page.")
      st.stop()
  ```

- [ ] **Step 4: Run the app locally to verify dashboard loads**

  ```bash
  streamlit run app.py
  ```

  Expected: Dashboard loads. If Supabase is connected and has data, charts render. If empty, warning message shows.

- [ ] **Step 5: Commit**

  ```bash
  git add app.py
  git commit -m "feat: connect dashboard to supabase — replace file uploader with load_from_db"
  ```

---

## Task 9: Upload Page (Authentication + Upload UX)

- [ ] **Step 1: Create pages/ directory if it doesn't exist**

  ```bash
  mkdir -p pages
  ```

- [ ] **Step 2: Create pages/upload.py**

  ```python
  import streamlit as st
  import pandas as pd
  import streamlit_authenticator as stauth
  from src.config import REQUIRED_COLUMNS
  from src.upload import detect_schema_changes, prepare_upload, validate_required_columns
  from src.db import replace_employees, log_upload, fetch_last_upload
  from src.data_processing import load_from_db

  st.set_page_config(page_title="Upload Master Sheet", page_icon="📤")

  # ── Auth ────────────────────────────────────────────────────────────────────
  credentials = {"usernames": dict(st.secrets["credentials"]["usernames"])}
  cookie_cfg = st.secrets["cookie"]

  authenticator = stauth.Authenticate(
      credentials,
      cookie_cfg["name"],
      cookie_cfg["key"],
      cookie_cfg["expiry_days"],
  )

  name, auth_status, username = authenticator.login("Upload Login", "main")

  if auth_status is False:
      st.error("Incorrect username or password.")
      st.stop()
  if auth_status is None:
      st.info("Please log in to upload data.")
      st.stop()

  # ── Authenticated ────────────────────────────────────────────────────────────
  st.title("📤 Upload Master Sheet")
  authenticator.logout("Logout", "sidebar")

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
      options = [skip_option] + REQUIRED_COLUMNS + all_file_cols

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
              # User picked a file column → rename it to the required name
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

  st.success(f"All required columns present. Ready to upload.")

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
  ```

- [ ] **Step 3: Run the upload page locally**

  ```bash
  streamlit run app.py
  ```

  Navigate to the Upload page in the sidebar. Log in with your credentials. Upload a test Excel file.

  Expected:
  - Login form appears
  - After login: file uploader appears
  - After selecting file: column mapping shown if needed, validation runs
  - After clicking Apply Upload: success message, dashboard updates

- [ ] **Step 4: Commit**

  ```bash
  git add pages/upload.py
  git commit -m "feat: add password-protected upload page with column mapping UI"
  ```

---

## Task 10: End-to-End Verification

- [ ] **Step 1: Full local test**

  ```bash
  streamlit run app.py
  ```

  Verify:
  - [ ] Dashboard loads at root URL with no login
  - [ ] "Last updated" badge shows in sidebar (or "No data" message if DB empty)
  - [ ] Upload page accessible via sidebar navigation
  - [ ] Login with wrong password shows error
  - [ ] Login with correct password succeeds
  - [ ] Uploading Master.xlsx loads data and dashboard refreshes
  - [ ] All 5 dashboard tabs work (Overview, Attrition, Tenure, Trends, Employee Data)
  - [ ] Filters still work

- [ ] **Step 2: Run full test suite**

  ```bash
  pytest tests/ -v
  ```

  Expected: All tests pass.

- [ ] **Step 3: Deploy to Streamlit Community Cloud**

  In Streamlit Community Cloud (share.streamlit.io):
  - Go to your app settings → Secrets
  - Paste the full contents of your `.streamlit/secrets.toml`
  - Redeploy the app

  Expected: App deploys and connects to Supabase.

- [ ] **Step 4: Final commit**

  ```bash
  git add .
  git commit -m "feat: streamlit + supabase live dashboard — complete integration"
  git push origin master
  ```

---

## Summary of New Files

```
src/
  supabase_client.py     ← Supabase connection
  db.py                  ← DB read/write
  upload.py              ← Column mapping + validation
pages/
  upload.py              ← Upload page UI (auth + UX)
tests/
  test_db.py             ← DB + data_processing tests
  test_upload.py         ← Upload pipeline tests
.streamlit/
  secrets.toml           ← Real secrets (NOT committed)
  secrets.toml.example   ← Template (committed)
sql/
  schema.sql             ← Supabase table definitions
```

**Modified files:** `requirements.txt`, `src/data_processing.py`, `app.py`, `.gitignore`
