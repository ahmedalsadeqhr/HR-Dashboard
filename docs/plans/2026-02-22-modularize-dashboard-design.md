# Design: Modularize HR Analytics Dashboard

**Date**: 2026-02-22
**Approach**: A — Modularize v1 into src/pages/ structure
**Goal**: Split monolithic 1,325-line app.py into maintainable modules while preserving all functionality

## Context

The current dashboard is a single-file Streamlit app with 8 analytical tabs, 40+ Plotly charts, and full CRUD operations. A proposed v2 rewrite introduced better architecture (modular structure, auth, database, Docker, CI/CD) but removed 95% of the HR analytics. This design takes the best of both: v1's complete analytics with v2's structural patterns.

## Constraints

- Deploy on Streamlit Cloud (no Docker, no persistent database)
- No authentication needed
- Excel-based data flow (upload, process in-memory, optional save-back)
- Zero logic changes — purely structural refactor
- All 8 tabs and 40+ charts preserved as-is

## File Structure

```
HC Analysis/
├── app.py                      (~80 lines — router, data loading, sidebar, tab dispatch)
├── src/
│   ├── __init__.py
│   ├── config.py               (COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, DATA_FILE, NAME_COL)
│   ├── data_processing.py      (load_excel, process_data, calculate_kpis, get_cohort_retention, get_manager_attrition, save_to_excel)
│   ├── utils.py                (_delta helper, export functions)
│   └── pages/
│       ├── __init__.py
│       ├── overview.py          (gender, status, dept breakdown, positions, age, nationality)
│       ├── attrition.py         (exit types, reasons, voluntary/involuntary, dept rates, manager-linked)
│       ├── tenure_retention.py  (tenure stats, distribution, cohort retention, probation)
│       ├── workforce.py         (employment type, vendor analysis, position changes)
│       ├── trends.py            (hiring/attrition trends, net HC, monthly, hire-to-exit ratio)
│       ├── employee_data.py     (search, table display, CSV/Excel/summary exports)
│       ├── advanced_analytics.py(90-day retention, rolling turnover, risk analysis, survival curve, cost, regrettable turnover)
│       └── edit_data.py         (add/edit/delete employee records, save to Excel)
├── tests/
│   ├── __init__.py
│   ├── test_data_processing.py  (40-test suite: KPIs, cohorts, manager attrition, edge cases, column variants)
│   ├── test_config.py           (constants validation)
│   └── test_pages.py            (import smoke tests)
├── .github/
│   └── workflows/
│       └── ci.yml               (flake8 + pytest on push/PR to main)
├── requirements.txt             (pinned versions)
├── .gitignore
└── README.md
```

## Data Flow

```
Upload Excel → load_excel() → process_data() → DataFrame in session_state
                                                       ↓
                                              sidebar filters applied
                                                       ↓
                                              filtered_df + kpis passed to active tab's render()
                                                       ↓
                                              each page module renders its Plotly charts
```

## Page Module Interface

Each page in `src/pages/` exports a single function:

```python
def render(df, filtered_df, kpis, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    """Render this tab's content using Streamlit and Plotly."""
    ...
```

The main `app.py` creates tabs and dispatches:

```python
tabs = st.tabs(["Overview", "Attrition", "Tenure & Retention", ...])
with tabs[0]:
    overview.render(df, filtered_df, kpis, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
```

## What Moves Where

| Source (app.py lines) | Destination |
|---|---|
| 15-43 (COLORS, CHART_CONFIG, constants) | src/config.py |
| data_processing.py | src/data_processing.py (unchanged) |
| _delta() helper, export logic | src/utils.py |
| 238-307 (Tab 1: Overview) | src/pages/overview.py |
| 308-412 (Tab 2: Attrition) | src/pages/attrition.py |
| 413-524 (Tab 3: Tenure & Retention) | src/pages/tenure_retention.py |
| 525-611 (Tab 4: Workforce) | src/pages/workforce.py |
| 612-711 (Tab 5: Trends) | src/pages/trends.py |
| 712-817 (Tab 6: Employee Data) | src/pages/employee_data.py |
| 818-1159 (Tab 7: Advanced Analytics) | src/pages/advanced_analytics.py |
| 1160-1317 (Tab 8: Edit Data) | src/pages/edit_data.py |
| 1-14, 46-237, 1318-1325 (router) | app.py (stays, slimmed down) |

## Testing

- **test_data_processing.py**: 40 tests covering KPI math, cohort retention, manager attrition, edge cases, NAME_COL variants, save/load round-trip
- **test_config.py**: Constants exist and are correct types
- **test_pages.py**: Each page module imports cleanly and has a `render` callable

## CI Pipeline

- Trigger: push/PR to main
- Python 3.11
- flake8 (errors only)
- pytest --cov=src

## Dependencies (pinned)

```
streamlit==1.41.0
pandas==2.2.3
openpyxl==3.1.5
numpy==2.2.2
plotly==5.24.1
pytest==8.3.4
pytest-cov==6.0.0
flake8==7.1.1
```

## What Does NOT Change

- All Plotly chart logic (moved, not modified)
- data_processing.py functions and API
- Sidebar filter behavior
- KPI calculations and delta comparisons
- Edit Data CRUD operations
- Session state caching pattern
- Export functionality (CSV, Excel, summary)
- NAME_COL dynamic detection
