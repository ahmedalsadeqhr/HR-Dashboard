# Streamlit + Supabase Live Dashboard Design

**Date:** 2026-03-31
**Status:** Approved

---

## Goal

Make the HR Dashboard always live without requiring manual Excel uploads each session. Data persists in Supabase PostgreSQL and is accessible to all internal viewers at any time.

---

## Architecture Overview

```
Excel Upload (by 3 HR members)
        ↓
Streamlit Upload Page (password protected)
        ↓
  Column Mapping UI  ←── detects schema automatically
        ↓
Supabase PostgreSQL  ←── single "employees" table
        ↓
Streamlit Dashboard  ←── reads from DB, always live
        ↑
   Viewers (internal, no login required)
```

**Key decisions:**
- One `employees` table — each upload does a full replace (truncate + insert), matching master sheet semantics
- `upload_log` table records every upload for audit trail
- Viewers access the dashboard URL directly with no login
- Uploaders authenticate via a separate `/upload` page
- All existing Python calculations in `data_processing.py` stay untouched — only the data source changes

---

## Data Design

### employees table
| Column | Type |
|--------|------|
| id | bigint, auto, primary key |
| [all Master.xlsx columns] | text / date / numeric |
| _uploaded_at | timestamp |

### upload_log table
| Column | Type |
|--------|------|
| id | bigint, auto, primary key |
| uploaded_by | text |
| uploaded_at | timestamp |
| row_count | integer |
| column_snapshot | jsonb (stores schema of that upload) |

### Schema Flexibility
When a new Excel is uploaded:
1. Detect all columns in the file
2. Compare against required columns (Department, Employee Status, Gender, Join Date, Exit Date, etc.)
3. Show column mapping UI if any names differ
4. Block upload if a required column is completely missing, with a clear error listing what's missing
5. On confirm, truncate `employees` and insert fresh rows

No version history of employee data — only the latest state is kept. Upload log preserves audit trail.

---

## Authentication & Access

| Who | Access | Method |
|-----|--------|--------|
| 3 HR uploaders | Upload page + dashboard | `streamlit-authenticator` password login |
| All other internal viewers | Dashboard only | Direct URL, no login |

- Credentials stored in Streamlit secrets (not hardcoded)
- Each uploader has their own username/password
- Credential changes (new/departing staff) handled by updating Streamlit secrets directly
- No lockout policy needed for internal use

---

## Upload Flow (UX)

1. Go to `/upload` → enter username + password
2. See current data stats: last upload (who, when, row count)
3. Click "Upload new Master Sheet" → select Excel file
4. If column names differ → show mapping screen:
   ```
   File column          →  Maps to
   ─────────────────────────────────
   "Emp Status"         →  [Employee Status ▼]
   "Date of Joining"    →  [Join Date ▼]
   "NEW_COLUMN"         →  [Skip / New field ▼]
   ```
5. Confirm mapping → click "Apply Upload"
6. Data replaces existing records in Supabase
7. Success: "1,234 rows loaded. Dashboard is now live."

---

## Dashboard Changes

Minimal — dashboard stays structurally identical.

**Changes:**
- `src/data_processing.py` — replace file loader with Supabase query:
  ```python
  # Before
  df = pd.read_excel(uploaded_file)

  # After
  df = supabase.table("employees").select("*").execute().data
  df = pd.DataFrame(df)
  ```
- Wrap with `@st.cache_data(ttl=300)` — DB queried at most once every 5 minutes per session
- Add "Last updated" badge on dashboard showing timestamp from `upload_log`

**Unchanged:** All calculations, charts, filters, tabs, and pages in the existing codebase.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `supabase` | Supabase Python client |
| `streamlit-authenticator` | Upload page login |

---

## Out of Scope

- Email notifications on upload
- Data version history / rollback
- Role management UI
- SSO / enterprise auth
- Public access outside the organization
