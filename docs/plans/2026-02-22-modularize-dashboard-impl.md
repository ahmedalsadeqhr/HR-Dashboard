# Modularize HR Analytics Dashboard — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split the monolithic 1,325-line app.py into a modular `src/pages/` structure while preserving every feature, chart, and interaction.

**Architecture:** Extract constants to `src/config.py`, move `data_processing.py` to `src/`, create one page module per tab with a `render()` function, slim `app.py` down to a router. Add tests and CI.

**Tech Stack:** Streamlit, Pandas, Plotly, NumPy, pytest, flake8

---

### Task 1: Create src/ package structure and config.py

**Files:**
- Create: `src/__init__.py`
- Create: `src/pages/__init__.py`
- Create: `src/config.py`

**Step 1: Create directory structure**

```bash
mkdir -p src/pages tests
```

**Step 2: Create `src/__init__.py`**

```python
```

(Empty file)

**Step 3: Create `src/pages/__init__.py`**

```python
```

(Empty file)

**Step 4: Create `src/config.py`**

```python
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17becf',
    'purple': '#9467bd',
    'pink': '#e377c2',
    'brown': '#8c564b',
    'gray': '#7f7f7f',
}

COLOR_SEQUENCE = [
    COLORS['primary'], COLORS['success'], COLORS['danger'],
    COLORS['warning'], COLORS['info'], COLORS['purple'],
    COLORS['pink'], COLORS['brown'],
]

DATA_FILE = "Master.xlsx"

REQUIRED_COLUMNS = ['Gender', 'Department', 'Position', 'Employee Status', 'Exit Type']

CHART_CONFIG = {
    'displayModeBar': True,
    'toImageButtonOptions': {
        'format': 'png',
        'scale': 3,
        'filename': 'hr_chart',
    },
    'modeBarButtonsToAdd': ['downloadCsv'],
    'displaylogo': False,
}


def detect_name_column(df):
    """Detect the name column from various naming conventions."""
    for c in df.columns:
        if 'full' in str(c).lower() and 'name' in str(c).lower():
            return c
    for c in df.columns:
        if 'name' in str(c).lower() and c != 'Bank Name':
            return c
    return None
```

**Step 5: Verify config imports work**

```bash
python -c "from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, DATA_FILE, detect_name_column; print('OK')"
```

Expected: `OK`

**Step 6: Commit**

```bash
git add src/__init__.py src/pages/__init__.py src/config.py
git commit -m "feat: add src/ package with config constants"
```

---

### Task 2: Move data_processing.py to src/

**Files:**
- Move: `data_processing.py` → `src/data_processing.py`

**Step 1: Copy data_processing.py to src/**

```bash
cp data_processing.py src/data_processing.py
```

The file content stays **exactly the same** — no modifications.

**Step 2: Verify import works**

```bash
python -c "from src.data_processing import load_excel, process_data, calculate_kpis, get_cohort_retention, get_manager_attrition, save_to_excel; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/data_processing.py
git commit -m "feat: copy data_processing.py to src/ package"
```

Note: Do NOT delete the root `data_processing.py` yet — `app.py` still imports from it. We'll clean up in the final task.

---

### Task 3: Create src/utils.py

**Files:**
- Create: `src/utils.py`

**Step 1: Create `src/utils.py`**

This extracts the `_delta()` helper and the summary report generator from app.py.

```python
import io
import pandas as pd
from datetime import datetime


def delta(filtered_val, all_val, suffix="", filtered_len=0, full_len=0):
    """Return delta string if filters are active, else None."""
    if filtered_len == full_len:
        return None
    diff = filtered_val - all_val
    if abs(diff) < 0.05:
        return None
    return f"{diff:+.1f}{suffix}"


def generate_summary_report(filtered_df, df, kpis):
    """Generate a text summary report of HR metrics."""
    summary_lines = [
        "HR ANALYTICS SUMMARY REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Data: {len(filtered_df)} records (filtered from {len(df)} total)",
        "",
        "=== KEY METRICS ===",
        f"Total Employees: {kpis['total']:,}",
        f"Active: {kpis['active']:,}",
        f"Departed: {kpis['departed']:,}",
        f"Attrition Rate: {kpis['attrition_rate']:.1f}%",
        f"Retention Rate: {kpis['retention_rate']:.1f}%",
        f"Avg Tenure: {kpis['avg_tenure']:.1f} months",
        f"Avg Age: {kpis['avg_age']:.0f}" if not pd.isna(kpis['avg_age']) else "Avg Age: N/A",
        f"Gender (M:F): {kpis['gender_ratio']}",
        f"Contractor Ratio: {kpis['contractor_ratio']:.1f}%",
        f"Nationalities: {kpis['nationality_count']}",
        f"Probation Pass Rate: {kpis['probation_pass_rate']:.1f}%",
        f"YoY Growth: {kpis['growth_rate']:+.1f}%",
        "",
        "=== DEPARTMENT BREAKDOWN ===",
    ]
    dept_summary = filtered_df.groupby('Department').agg(
        Total=('Employee Status', 'count'),
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
    ).reset_index()
    dept_summary['Attrition %'] = (dept_summary['Departed'] / dept_summary['Total'] * 100).round(1)
    for _, row in dept_summary.iterrows():
        summary_lines.append(
            f"  {row['Department']}: {row['Total']} total, {row['Active']} active, "
            f"{row['Departed']} departed ({row['Attrition %']}% attrition)"
        )

    summary_lines += ["", "=== TOP EXIT REASONS ==="]
    departed_summary = filtered_df[filtered_df['Employee Status'] == 'Departed']
    if len(departed_summary) > 0 and 'Exit Reason Category' in departed_summary.columns:
        for reason, count in departed_summary['Exit Reason Category'].value_counts().head(10).items():
            summary_lines.append(f"  {reason}: {count}")

    return "\n".join(summary_lines)


def export_excel(filtered_df):
    """Export filtered dataframe to Excel bytes buffer."""
    excel_buffer = io.BytesIO()
    filtered_df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    return excel_buffer
```

**Step 2: Verify import works**

```bash
python -c "from src.utils import delta, generate_summary_report, export_excel; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/utils.py
git commit -m "feat: add utils with delta helper and export functions"
```

---

### Task 4: Create src/pages/overview.py

**Files:**
- Create: `src/pages/overview.py`

**Step 1: Create the file**

This is app.py lines 238-307 wrapped in a `render()` function. All Streamlit/Plotly calls stay identical.

```python
import streamlit as st
import plotly.express as px


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(gender_counts, values='Count', names='Gender',
                     color_discrete_sequence=[COLORS['primary'], COLORS['pink']],
                     hole=0.4)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Employee Status")
        status_counts = filtered_df['Employee Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status',
                     color_discrete_sequence=[COLORS['success'], COLORS['danger']],
                     hole=0.4)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Department Breakdown")
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                 barmode='group')
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 15 Positions")
        pos_counts = filtered_df['Position'].value_counts().head(15).reset_index()
        pos_counts.columns = ['Position', 'Count']
        fig = px.bar(pos_counts, x='Count', y='Position', orientation='h',
                     color='Count', color_continuous_scale='Blues')
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Age Distribution")
        age_df = filtered_df[filtered_df['Age'] > 0]
        if len(age_df) > 0:
            fig = px.histogram(age_df, x='Age', nbins=20,
                               color_discrete_sequence=[COLORS['primary']],
                               marginal='box')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    if 'Nationality' in filtered_df.columns:
        st.markdown("---")
        st.subheader("Nationality Distribution")
        nat_counts = filtered_df['Nationality'].value_counts().reset_index()
        nat_counts.columns = ['Nationality', 'Count']
        fig = px.pie(nat_counts, values='Count', names='Nationality',
                     color_discrete_sequence=COLOR_SEQUENCE)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/overview.py').read()); print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/pages/overview.py
git commit -m "feat: extract Overview tab to src/pages/overview.py"
```

---

### Task 5: Create src/pages/attrition.py

**Files:**
- Create: `src/pages/attrition.py`

**Step 1: Create the file**

This is app.py lines 308-411 wrapped in `render()`. Uses `get_manager_attrition` from data_processing.

```python
import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_processing import get_manager_attrition


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    if len(departed_df) == 0:
        st.info("No departed employees in current filter selection.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Exit Types")
        exit_counts = departed_df['Exit Type'].value_counts().reset_index()
        exit_counts.columns = ['Exit Type', 'Count']
        fig = px.pie(exit_counts, values='Count', names='Exit Type',
                     color_discrete_sequence=[COLORS['warning'], COLORS['danger'], COLORS['brown']])
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Exit Reason Categories")
        reason_counts = departed_df['Exit Reason Category'].value_counts().reset_index()
        reason_counts.columns = ['Category', 'Count']
        fig = px.bar(reason_counts, x='Count', y='Category', orientation='h',
                     color='Count', color_continuous_scale='Reds')
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Voluntary vs Involuntary
    st.subheader("Voluntary vs Involuntary Turnover")
    voluntary = len(departed_df[departed_df['Exit Type'] == 'Resigned'])
    involuntary = len(departed_df[departed_df['Exit Type'].isin(['Terminated', 'Dropped'])])
    total_departed = len(departed_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Voluntary (Resigned)", f"{voluntary} ({voluntary / total_departed * 100:.1f}%)")
    col2.metric("Involuntary (Term/Drop)", f"{involuntary} ({involuntary / total_departed * 100:.1f}%)")
    col3.metric("Total Departures", f"{total_departed}")

    vol_data = pd.DataFrame({
        'Type': ['Voluntary (Resigned)', 'Involuntary (Terminated/Dropped)'],
        'Count': [voluntary, involuntary]
    })
    fig = px.pie(vol_data, values='Count', names='Type',
                 color_discrete_sequence=[COLORS['warning'], COLORS['danger']], hole=0.4)
    fig.update_traces(textinfo='percent+value')
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Attrition by department
    st.subheader("Attrition Rate by Department")
    dept_attrition = filtered_df.groupby('Department').agg(
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
        Total=('Employee Status', 'count')
    ).reset_index()
    dept_attrition['Attrition Rate %'] = (dept_attrition['Departed'] / dept_attrition['Total'] * 100).round(1)
    dept_attrition = dept_attrition.sort_values('Attrition Rate %', ascending=False)

    fig = px.bar(dept_attrition, x='Department', y='Attrition Rate %',
                 color='Attrition Rate %', color_continuous_scale='RdYlGn_r',
                 text='Attrition Rate %')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.dataframe(dept_attrition, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Exit Reason List
    if 'Exit ReasonList' in departed_df.columns:
        st.subheader("Exit Reasons (Categorized)")
        reason_list = departed_df[departed_df['Exit ReasonList'].str.len() > 0]['Exit ReasonList'].value_counts().reset_index()
        reason_list.columns = ['Reason', 'Count']
        if len(reason_list) > 0:
            fig = px.bar(reason_list, x='Count', y='Reason', orientation='h',
                         color='Count', color_continuous_scale='Oranges')
            fig.update_layout(height=max(300, len(reason_list) * 30),
                              yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Manager-linked attrition
    st.subheader("Manager-Linked Attrition")
    manager_data = get_manager_attrition(filtered_df)
    if len(manager_data) > 0:
        st.markdown("*Which managers had the most departures under them?*")
        mgr_chart_kwargs = dict(x='Departures', y='Manager CRM', orientation='h')
        if 'Avg Tenure (Months)' in manager_data.columns:
            mgr_chart_kwargs['color'] = 'Avg Tenure (Months)'
            mgr_chart_kwargs['color_continuous_scale'] = 'RdYlBu'
        if 'Top Exit Reason' in manager_data.columns:
            mgr_chart_kwargs['hover_data'] = ['Top Exit Reason']
        fig = px.bar(manager_data.head(15), **mgr_chart_kwargs)
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.dataframe(manager_data, use_container_width=True, hide_index=True)
    else:
        st.info("No manager attrition data available.")
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/attrition.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/attrition.py
git commit -m "feat: extract Attrition Analysis tab to src/pages/attrition.py"
```

---

### Task 6: Create src/pages/tenure_retention.py

**Files:**
- Create: `src/pages/tenure_retention.py`

**Step 1: Create the file**

App.py lines 413-523 wrapped in `render()`.

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing import get_cohort_retention


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    st.subheader("Tenure Distribution")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Tenure", f"{filtered_df['Tenure (Months)'].min():.1f} mo")
    col2.metric("Max Tenure", f"{filtered_df['Tenure (Months)'].max():.1f} mo")
    col3.metric("Avg Tenure", f"{filtered_df['Tenure (Months)'].mean():.1f} mo")
    col4.metric("Median Tenure", f"{filtered_df['Tenure (Months)'].median():.1f} mo")

    fig = px.histogram(filtered_df, x='Tenure (Months)', nbins=30,
                       color='Employee Status',
                       color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                       marginal='box')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Average Tenure by Department")
    tenure_dept = filtered_df.groupby('Department')['Tenure (Months)'].agg(['mean', 'median', 'count']).round(1)
    tenure_dept.columns = ['Avg Tenure', 'Median Tenure', 'Count']
    tenure_dept = tenure_dept.sort_values('Avg Tenure', ascending=False).reset_index()

    fig = px.bar(tenure_dept, x='Department', y='Avg Tenure',
                 color='Avg Tenure', color_continuous_scale='Blues',
                 text='Avg Tenure', hover_data=['Median Tenure', 'Count'])
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Cohort retention
    st.subheader("Cohort Retention Analysis")
    cohort = get_cohort_retention(filtered_df)
    if len(cohort) > 0:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cohort['Join Year'], y=cohort['Active'], name='Active',
                             marker_color=COLORS['success']))
        fig.add_trace(go.Bar(x=cohort['Join Year'], y=cohort['Departed'], name='Departed',
                             marker_color=COLORS['danger']))
        fig.add_trace(go.Scatter(x=cohort['Join Year'], y=cohort['Retention Rate %'],
                                 name='Retention %', yaxis='y2',
                                 line=dict(color=COLORS['primary'], width=3),
                                 mode='lines+markers'))
        fig.update_layout(
            barmode='stack',
            yaxis=dict(title='Employee Count'),
            yaxis2=dict(title='Retention Rate %', overlaying='y', side='right', range=[0, 105]),
            height=450, legend=dict(orientation='h', y=-0.15)
        )
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.dataframe(cohort, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Probation analysis
    st.subheader("Probation Analysis")
    if 'Probation Completed' in filtered_df.columns:
        prob_data = filtered_df[filtered_df['Probation Completed'] != 'No Data']
        if len(prob_data) > 0:
            prob_counts = prob_data['Probation Completed'].value_counts().reset_index()
            prob_counts.columns = ['Status', 'Count']
            fig = px.pie(prob_counts, values='Count', names='Status',
                         color_discrete_sequence=COLOR_SEQUENCE, hole=0.4)
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

            prob_dept = prob_data.groupby('Department')['Probation Completed'].apply(
                lambda x: (x.isin(['Completed', 'Completed Before Exit']).sum() / len(x) * 100)
            ).round(1).reset_index()
            prob_dept.columns = ['Department', 'Pass Rate %']
            prob_dept = prob_dept.sort_values('Pass Rate %', ascending=False)

            fig = px.bar(prob_dept, x='Department', y='Pass Rate %',
                         color='Pass Rate %', color_continuous_scale='RdYlGn',
                         text='Pass Rate %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No probation data available.")
    else:
        st.info("Probation data column not found.")

    st.markdown("---")

    # Early leavers
    st.subheader("Early Leavers (Left within 6 months)")
    dep_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
    early_leavers = dep_df[dep_df['Tenure (Months)'] <= 6]

    if len(early_leavers) > 0 and len(dep_df) > 0:
        col1, col2, col3 = st.columns(3)
        col1.metric("Early Leavers", len(early_leavers))
        col2.metric("% of Departures", f"{len(early_leavers) / len(dep_df) * 100:.1f}%")
        col3.metric("Avg Tenure", f"{early_leavers['Tenure (Months)'].mean():.1f} mo")

        early_reasons = early_leavers['Exit Reason Category'].value_counts().reset_index()
        early_reasons.columns = ['Reason', 'Count']
        fig = px.bar(early_reasons, x='Count', y='Reason', orientation='h',
                     color='Count', color_continuous_scale='Reds')
        fig.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("No early leavers in current selection.")
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/tenure_retention.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/tenure_retention.py
git commit -m "feat: extract Tenure & Retention tab to src/pages/tenure_retention.py"
```

---

### Task 7: Create src/pages/workforce.py

**Files:**
- Create: `src/pages/workforce.py`

**Step 1: Create the file**

App.py lines 525-610 wrapped in `render()`.

```python
import streamlit as st
import plotly.express as px


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    st.subheader("Employment Type Breakdown")

    if 'Employment Type' in filtered_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            type_counts = filtered_df['Employment Type'].value_counts().reset_index()
            type_counts.columns = ['Type', 'Count']
            fig = px.pie(type_counts, values='Count', names='Type',
                         color_discrete_sequence=COLOR_SEQUENCE, hole=0.4)
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        with col2:
            type_dept = filtered_df.groupby(['Department', 'Employment Type']).size().reset_index(name='Count')
            fig = px.bar(type_dept, x='Department', y='Count', color='Employment Type',
                         color_discrete_sequence=COLOR_SEQUENCE, barmode='stack')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Vendor analysis
    if 'Vendor' in filtered_df.columns:
        st.subheader("Vendor / Source Analysis")
        vendor_counts = filtered_df['Vendor'].value_counts().reset_index()
        vendor_counts.columns = ['Vendor', 'Count']

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(vendor_counts, values='Count', names='Vendor',
                         color_discrete_sequence=COLOR_SEQUENCE, hole=0.4)
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        with col2:
            vendor_status = filtered_df.groupby(['Vendor', 'Employee Status']).size().reset_index(name='Count')
            fig = px.bar(vendor_status, x='Vendor', y='Count', color='Employee Status',
                         color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                         barmode='group')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        # Vendor attrition rates
        vendor_attrition = filtered_df.groupby('Vendor').agg(
            Total=('Employee Status', 'count'),
            Departed=('Employee Status', lambda x: (x == 'Departed').sum())
        ).reset_index()
        vendor_attrition['Attrition Rate %'] = (vendor_attrition['Departed'] / vendor_attrition['Total'] * 100).round(1)
        st.dataframe(vendor_attrition, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Position changes
    if 'Position After Joining' in filtered_df.columns:
        st.subheader("Position Changes After Joining")
        pos_change = filtered_df[filtered_df['Position After Joining'].notna()]
        changed = pos_change[pos_change['Position'] != pos_change['Position After Joining']]

        col1, col2 = st.columns(2)
        col1.metric("Employees with Position Data", len(pos_change))
        col2.metric("Position Changes", len(changed))

        if len(changed) > 0:
            change_dept = changed['Department'].value_counts().reset_index()
            change_dept.columns = ['Department', 'Changes']
            fig = px.bar(change_dept, x='Department', y='Changes',
                         color='Changes', color_continuous_scale='Blues')
            fig.update_layout(xaxis_tickangle=-45, height=350)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Workforce composition over time
    st.subheader("Workforce Composition Over Time")
    if 'Join Year' in filtered_df.columns and 'Employment Type' in filtered_df.columns:
        comp_time = filtered_df.groupby(['Join Year', 'Employment Type']).size().reset_index(name='Count')
        comp_time = comp_time[comp_time['Join Year'] > 2000]
        if len(comp_time) > 0:
            fig = px.area(comp_time, x='Join Year', y='Count', color='Employment Type',
                          color_discrete_sequence=COLOR_SEQUENCE)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/workforce.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/workforce.py
git commit -m "feat: extract Workforce Composition tab to src/pages/workforce.py"
```

---

### Task 8: Create src/pages/trends.py

**Files:**
- Create: `src/pages/trends.py`

**Step 1: Create the file**

App.py lines 612-710 wrapped in `render()`.

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    trends_dep_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hiring Trend by Year")
        hiring = filtered_df.groupby('Join Year').size().reset_index(name='Hires')
        hiring = hiring[hiring['Join Year'] > 2000]
        fig = px.line(hiring, x='Join Year', y='Hires', markers=True,
                      color_discrete_sequence=[COLORS['success']])
        fig.update_traces(line_width=3)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Attrition Trend by Year")
        if len(trends_dep_df) > 0:
            attrition = trends_dep_df.groupby('Exit Year').size().reset_index(name='Exits')
            attrition = attrition[attrition['Exit Year'] > 2000]
            fig = px.line(attrition, x='Exit Year', y='Exits', markers=True,
                          color_discrete_sequence=[COLORS['danger']])
            fig.update_traces(line_width=3)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No departed employees in current selection.")

    st.markdown("---")

    # Net headcount change
    st.subheader("Net Headcount Change by Year")
    net_df = pd.DataFrame()
    if 'Join Year' in filtered_df.columns:
        hires_yr = filtered_df.groupby('Join Year').size().rename('Hires')
        exits_yr = trends_dep_df.groupby('Exit Year').size().rename('Exits') if len(trends_dep_df) > 0 else pd.Series(dtype=int)

        years = sorted(set(hires_yr.index.tolist() + exits_yr.index.tolist()))
        years = [y for y in years if y > 2000]
        net_df = pd.DataFrame({'Year': years})
        net_df['Hires'] = net_df['Year'].map(hires_yr).fillna(0).astype(int)
        net_df['Exits'] = net_df['Year'].map(exits_yr).fillna(0).astype(int)
        net_df['Net Change'] = net_df['Hires'] - net_df['Exits']

        fig = go.Figure()
        fig.add_trace(go.Bar(x=net_df['Year'], y=net_df['Hires'], name='Hires',
                             marker_color=COLORS['success']))
        fig.add_trace(go.Bar(x=net_df['Year'], y=-net_df['Exits'], name='Exits',
                             marker_color=COLORS['danger']))
        fig.add_trace(go.Scatter(x=net_df['Year'], y=net_df['Net Change'], name='Net Change',
                                 line=dict(color=COLORS['primary'], width=3), mode='lines+markers'))
        fig.update_layout(barmode='relative', height=450)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        st.dataframe(net_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Monthly trends
    st.subheader("Monthly Hiring Trend (Recent)")
    monthly = filtered_df.groupby('Join Month').size().reset_index(name='Hires')
    monthly = monthly.tail(24)
    if len(monthly) > 0:
        fig = px.bar(monthly, x='Join Month', y='Hires',
                     color_discrete_sequence=[COLORS['primary']])
        fig.update_layout(xaxis_tickangle=-45, height=350)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Headcount by join year and status
    st.subheader("Headcount Summary by Year")
    headcount = filtered_df.groupby(['Join Year', 'Employee Status']).size().unstack(fill_value=0)
    headcount = headcount[headcount.index > 2000]
    if len(headcount) > 0:
        fig = px.bar(headcount.reset_index().melt(id_vars='Join Year', var_name='Status', value_name='Count'),
                     x='Join Year', y='Count', color='Status',
                     color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                     barmode='stack')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.dataframe(headcount, use_container_width=True)

    st.markdown("---")

    # Hire-to-Exit ratio
    st.subheader("Hire-to-Exit Ratio by Year")
    if len(net_df) > 0:
        ratio_df = net_df[net_df['Exits'] > 0].copy()
        if len(ratio_df) > 0:
            ratio_df['Ratio'] = (ratio_df['Hires'] / ratio_df['Exits']).round(2)
            fig = px.line(ratio_df, x='Year', y='Ratio', markers=True,
                          color_discrete_sequence=[COLORS['purple']])
            fig.add_hline(y=1, line_dash="dash", line_color="gray",
                          annotation_text="Breakeven (1:1)")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/trends.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/trends.py
git commit -m "feat: extract Trends tab to src/pages/trends.py"
```

---

### Task 9: Create src/pages/employee_data.py

**Files:**
- Create: `src/pages/employee_data.py`

**Step 1: Create the file**

App.py lines 712-816. Uses utils for exports.

```python
import streamlit as st
import pandas as pd

from src.utils import generate_summary_report, export_excel


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    st.subheader("Employee Data Table")

    search = st.text_input("Search by name", key="emp_search")
    display_df = filtered_df.copy()
    if search and NAME_COL:
        display_df = display_df[display_df[NAME_COL].str.contains(search, case=False, na=False)]

    all_cols = [NAME_COL, 'Gender', 'Age', 'Nationality', 'Department', 'Position',
                'Employment Type', 'Vendor', 'Employee Status', 'Join Date', 'Exit Date',
                'Exit Type', 'Exit Reason Category', 'Exit Reason', 'Tenure (Months)',
                'Probation Completed', 'Position After Joining']
    available_cols = [c for c in all_cols if c in display_df.columns]

    selected_cols = st.multiselect(
        "Select columns to display",
        available_cols,
        default=available_cols[:10],
        key="emp_cols"
    )

    if selected_cols:
        st.dataframe(display_df[selected_cols], use_container_width=True, height=500)
    st.caption(f"Showing {len(display_df)} of {len(filtered_df)} filtered records")

    st.markdown("---")

    st.subheader("Export Data")
    export_col1, export_col2, export_col3 = st.columns(3)

    # CSV download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    export_col1.download_button("Download as CSV", csv, "hr_data_export.csv", "text/csv")

    # Excel download
    excel_buffer = export_excel(filtered_df)
    export_col2.download_button("Download as Excel", excel_buffer, "hr_data_export.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Summary report
    summary_text = generate_summary_report(filtered_df, df, kpis)
    export_col3.download_button("Download Summary Report", summary_text.encode('utf-8'),
                                "hr_summary_report.txt", "text/plain")

    st.markdown("---")
    st.subheader("Quick Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Numerical Summary:**")
        num_cols = [c for c in ['Age', 'Tenure (Months)'] if c in filtered_df.columns]
        if num_cols:
            st.dataframe(filtered_df[num_cols].describe().round(1), use_container_width=True)
    with col2:
        st.write("**Category Counts:**")
        st.write(f"- Departments: {filtered_df['Department'].nunique()}")
        st.write(f"- Positions: {filtered_df['Position'].nunique()}")
        st.write(f"- Male: {len(filtered_df[filtered_df['Gender'] == 'M'])}")
        st.write(f"- Female: {len(filtered_df[filtered_df['Gender'] == 'F'])}")
        if 'Employment Type' in filtered_df.columns:
            st.write(f"- Employment Types: {filtered_df['Employment Type'].nunique()}")
        if 'Nationality' in filtered_df.columns:
            st.write(f"- Nationalities: {filtered_df['Nationality'].nunique()}")
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/employee_data.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/employee_data.py
git commit -m "feat: extract Employee Data tab to src/pages/employee_data.py"
```

---

### Task 10: Create src/pages/advanced_analytics.py

**Files:**
- Create: `src/pages/advanced_analytics.py`

**Step 1: Create the file**

App.py lines 818-1158 — the largest page module.

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    adv_departed = filtered_df[filtered_df['Employee Status'] == 'Departed']

    # --- 1. New Hire 90-Day Retention ---
    st.subheader("New Hire 90-Day Retention")
    if 'Join Date' in filtered_df.columns and 'Exit Date' in filtered_df.columns:
        cutoff_90 = pd.Timestamp(datetime.now()) - pd.Timedelta(days=90)
        measurable = filtered_df[filtered_df['Join Date'] <= cutoff_90]

        if len(measurable) > 0:
            left_within_90 = measurable[
                (measurable['Employee Status'] == 'Departed') &
                (measurable['Exit Date'].notna()) &
                ((measurable['Exit Date'] - measurable['Join Date']).dt.days <= 90)
            ]
            retention_90 = (1 - len(left_within_90) / len(measurable)) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric("90-Day Retention Rate", f"{retention_90:.1f}%")
            col2.metric("Left Within 90 Days", f"{len(left_within_90)}")
            col3.metric("Measurable Employees", f"{len(measurable)}")

            dept_90 = measurable.groupby('Department').apply(
                lambda g: pd.Series({
                    'Total': len(g),
                    'Left <90d': len(g[(g['Employee Status'] == 'Departed') & g['Exit Date'].notna() & ((g['Exit Date'] - g['Join Date']).dt.days <= 90)]),
                })
            ).reset_index()
            dept_90['Retention %'] = ((1 - dept_90['Left <90d'] / dept_90['Total']) * 100).round(1)
            dept_90 = dept_90.sort_values('Retention %')

            fig = px.bar(dept_90, x='Department', y='Retention %',
                         color='Retention %', color_continuous_scale='RdYlGn',
                         text='Retention %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Not enough data to measure 90-day retention.")
    else:
        st.info("Join Date and Exit Date columns required.")

    st.markdown("---")

    # --- 2. Rolling Turnover Rate ---
    st.subheader("Rolling Turnover Rate")
    if len(adv_departed) > 0 and 'Exit Date' in adv_departed.columns:
        monthly_exits = adv_departed.groupby(
            adv_departed['Exit Date'].dt.to_period('M')
        ).size().reset_index(name='Exits')
        monthly_exits.columns = ['Period', 'Exits']
        monthly_exits['Period'] = monthly_exits['Period'].astype(str)

        monthly_hires = filtered_df.groupby(
            filtered_df['Join Date'].dt.to_period('M')
        ).size().reset_index(name='Hires')
        monthly_hires.columns = ['Period', 'Hires']
        monthly_hires['Period'] = monthly_hires['Period'].astype(str)

        turnover_df = pd.merge(monthly_hires, monthly_exits, on='Period', how='outer').fillna(0)
        turnover_df = turnover_df.sort_values('Period').tail(24)
        turnover_df['Cumulative Hires'] = turnover_df['Hires'].cumsum()
        turnover_df['Turnover Rate %'] = (turnover_df['Exits'] / turnover_df['Cumulative Hires'].replace(0, 1) * 100).round(1)

        period_view = st.radio("View", ["Monthly", "Quarterly"], horizontal=True, key="turnover_period")

        if period_view == "Quarterly":
            turnover_df['Quarter'] = pd.to_datetime(turnover_df['Period']).dt.to_period('Q').astype(str)
            q_df = turnover_df.groupby('Quarter').agg({'Exits': 'sum', 'Hires': 'sum'}).reset_index()
            q_df['Turnover Rate %'] = (q_df['Exits'] / q_df['Hires'].replace(0, 1) * 100).round(1)
            fig = px.bar(q_df, x='Quarter', y='Turnover Rate %',
                         color='Turnover Rate %', color_continuous_scale='RdYlGn_r',
                         text='Turnover Rate %')
        else:
            fig = px.bar(turnover_df, x='Period', y='Turnover Rate %',
                         color='Turnover Rate %', color_continuous_scale='RdYlGn_r',
                         text='Turnover Rate %')

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("No departure data available for turnover analysis.")

    st.markdown("---")

    # --- 3. Headcount by Department ---
    st.subheader("Headcount by Department")
    dept_hc = filtered_df.groupby('Department').agg(
        Total=('Employee Status', 'count'),
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
    ).reset_index()
    dept_hc['Fill Rate %'] = (dept_hc['Active'] / dept_hc['Total'] * 100).round(1)
    dept_hc = dept_hc.sort_values('Active', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=dept_hc['Department'], y=dept_hc['Active'], name='Active',
                         marker_color=COLORS['success']))
    fig.add_trace(go.Bar(x=dept_hc['Department'], y=dept_hc['Departed'], name='Departed',
                         marker_color=COLORS['danger']))
    fig.update_layout(barmode='stack', xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    st.dataframe(dept_hc, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- 4. Workforce Risk Analysis ---
    st.subheader("Workforce Risk Analysis")
    active_df = filtered_df[filtered_df['Employee Status'] == 'Active'].copy()

    if len(active_df) > 0 and 'Age' in active_df.columns and 'Tenure (Months)' in active_df.columns:
        retirement_risk = active_df[active_df['Age'] >= 55]
        flight_risk = active_df[(active_df['Tenure (Months)'] >= 12) & (active_df['Tenure (Months)'] <= 36)]
        new_hire_risk = active_df[active_df['Tenure (Months)'] < 6]

        col1, col2, col3 = st.columns(3)
        col1.metric("Retirement Risk (55+)", f"{len(retirement_risk)} ({len(retirement_risk)/len(active_df)*100:.1f}%)")
        col2.metric("Flight Risk (1-3yr tenure)", f"{len(flight_risk)} ({len(flight_risk)/len(active_df)*100:.1f}%)")
        col3.metric("New Hire Risk (<6mo)", f"{len(new_hire_risk)} ({len(new_hire_risk)/len(active_df)*100:.1f}%)")

        fig = px.scatter(active_df[active_df['Age'] > 0], x='Tenure (Months)', y='Age',
                         color='Department', hover_data=[NAME_COL] if NAME_COL and NAME_COL in active_df.columns else None,
                         color_discrete_sequence=COLOR_SEQUENCE)
        fig.add_hrect(y0=55, y1=active_df['Age'].max() + 5, fillcolor="red", opacity=0.08,
                      annotation_text="Retirement Risk Zone", annotation_position="top left")
        fig.add_vrect(x0=12, x1=36, fillcolor="orange", opacity=0.05,
                      annotation_text="Flight Risk Window", annotation_position="top right")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        st.markdown("#### Risk Breakdown by Department")
        risk_dept = active_df.groupby('Department').apply(
            lambda g: pd.Series({
                'Headcount': len(g),
                'Retirement Risk': len(g[g['Age'] >= 55]),
                'Flight Risk': len(g[(g['Tenure (Months)'] >= 12) & (g['Tenure (Months)'] <= 36)]),
                'New Hire Risk': len(g[g['Tenure (Months)'] < 6]),
            })
        ).reset_index()
        risk_dept['Total Risk %'] = (
            (risk_dept['Retirement Risk'] + risk_dept['Flight Risk'] + risk_dept['New Hire Risk'])
            / risk_dept['Headcount'] * 100
        ).round(1)
        risk_dept = risk_dept.sort_values('Total Risk %', ascending=False)
        st.dataframe(risk_dept, use_container_width=True, hide_index=True)
    else:
        st.info("Age and Tenure data required for risk analysis.")

    st.markdown("---")

    # --- 5. Turnover Cost Estimate ---
    st.subheader("Turnover Cost Estimate")
    st.caption("Estimated using industry standard: 50% of annual salary for non-management, 100-150% for management roles.")

    if len(adv_departed) > 0:
        avg_salary_input = st.number_input(
            "Enter average annual salary (for estimation)", min_value=0, value=60000, step=5000,
            key="avg_salary"
        )

        mgmt_keywords = ['manager', 'director', 'head', 'lead', 'chief', 'vp', 'senior manager']
        if 'Position' in adv_departed.columns:
            is_mgmt = adv_departed['Position'].str.lower().str.contains('|'.join(mgmt_keywords), na=False)
            mgmt_departures = is_mgmt.sum()
            non_mgmt_departures = len(adv_departed) - mgmt_departures
        else:
            mgmt_departures = 0
            non_mgmt_departures = len(adv_departed)

        cost_non_mgmt = non_mgmt_departures * avg_salary_input * 0.5
        cost_mgmt = mgmt_departures * avg_salary_input * 1.25
        total_cost = cost_non_mgmt + cost_mgmt

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Departures", f"{len(adv_departed)}")
        col2.metric("Management Departures", f"{mgmt_departures}")
        col3.metric("Non-Management", f"{non_mgmt_departures}")
        col4.metric("Estimated Total Cost", f"${total_cost:,.0f}")

        dept_cost = adv_departed.groupby('Department').apply(
            lambda g: pd.Series({
                'Departures': len(g),
                'Mgmt Departures': g['Position'].str.lower().str.contains('|'.join(mgmt_keywords), na=False).sum() if 'Position' in g.columns else 0,
            })
        ).reset_index()
        dept_cost['Non-Mgmt'] = dept_cost['Departures'] - dept_cost['Mgmt Departures']
        dept_cost['Est. Cost'] = (dept_cost['Non-Mgmt'] * avg_salary_input * 0.5 + dept_cost['Mgmt Departures'] * avg_salary_input * 1.25)
        dept_cost = dept_cost.sort_values('Est. Cost', ascending=False)

        fig = px.bar(dept_cost, x='Department', y='Est. Cost',
                     color='Est. Cost', color_continuous_scale='Reds',
                     text=dept_cost['Est. Cost'].apply(lambda x: f"${x:,.0f}"))
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400, yaxis_title='Estimated Cost ($)')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        st.dataframe(dept_cost, use_container_width=True, hide_index=True)
    else:
        st.info("No departed employees for cost estimation.")

    st.markdown("---")

    # --- 6. Survival Analysis ---
    st.subheader("Employee Survival Curve")
    st.caption("Shows the probability of an employee staying beyond each month of tenure.")

    if 'Tenure (Months)' in filtered_df.columns and len(filtered_df) > 0:
        max_tenure = int(filtered_df['Tenure (Months)'].max())
        months = list(range(0, min(max_tenure + 1, 121)))
        survival_data = []

        total = len(filtered_df)
        for m in months:
            survived = len(filtered_df[filtered_df['Tenure (Months)'] > m])
            survival_data.append({'Month': m, 'Survived': survived, 'Survival Rate %': (survived / total * 100)})

        survival_df = pd.DataFrame(survival_data)

        fig = px.area(survival_df, x='Month', y='Survival Rate %',
                      color_discrete_sequence=[COLORS['primary']])
        fig.update_layout(
            height=400,
            xaxis_title='Tenure (Months)',
            yaxis_title='Survival Rate %',
            yaxis_range=[0, 105]
        )
        for milestone, label in [(3, '3mo'), (6, '6mo'), (12, '1yr'), (24, '2yr'), (36, '3yr')]:
            if milestone <= max(months):
                rate = survival_df[survival_df['Month'] == milestone]['Survival Rate %'].values
                if len(rate) > 0:
                    fig.add_vline(x=milestone, line_dash="dot", line_color="gray", opacity=0.5)
                    fig.add_annotation(x=milestone, y=rate[0], text=f"{label}: {rate[0]:.0f}%",
                                       showarrow=False, yshift=15, font_size=10)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        dept_view = st.checkbox("Show survival curve by department", key="survival_dept")
        if dept_view:
            dept_survival = []
            for dept in filtered_df['Department'].unique():
                dept_df = filtered_df[filtered_df['Department'] == dept]
                dept_total = len(dept_df)
                if dept_total < 5:
                    continue
                for m in range(0, min(int(dept_df['Tenure (Months)'].max()) + 1, 61)):
                    survived = len(dept_df[dept_df['Tenure (Months)'] > m])
                    dept_survival.append({
                        'Month': m, 'Department': dept,
                        'Survival Rate %': (survived / dept_total * 100)
                    })

            if dept_survival:
                dept_surv_df = pd.DataFrame(dept_survival)
                fig = px.line(dept_surv_df, x='Month', y='Survival Rate %', color='Department',
                              color_discrete_sequence=COLOR_SEQUENCE)
                fig.update_layout(height=450, xaxis_title='Tenure (Months)', yaxis_range=[0, 105])
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Tenure data required for survival analysis.")

    st.markdown("---")

    # --- 7. Regrettable Turnover Proxy ---
    st.subheader("Regrettable Turnover (Estimated)")
    st.caption("Voluntary resignations of employees with 12+ months tenure are classified as likely regrettable losses.")

    if len(adv_departed) > 0:
        voluntary = adv_departed[adv_departed['Exit Type'] == 'Resigned']
        if len(voluntary) > 0 and 'Tenure (Months)' in voluntary.columns:
            regrettable = voluntary[voluntary['Tenure (Months)'] >= 12]
            non_regrettable_vol = voluntary[voluntary['Tenure (Months)'] < 12]
            involuntary = adv_departed[adv_departed['Exit Type'] != 'Resigned']

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Departures", f"{len(adv_departed)}")
            col2.metric("Regrettable (Vol 12+mo)", f"{len(regrettable)}",
                        delta=f"{len(regrettable)/len(adv_departed)*100:.1f}% of total",
                        delta_color="inverse")
            col3.metric("Early Vol (<12mo)", f"{len(non_regrettable_vol)}")
            col4.metric("Involuntary", f"{len(involuntary)}")

            turnover_types = pd.DataFrame({
                'Category': ['Regrettable (Vol 12+mo)', 'Early Voluntary (<12mo)', 'Involuntary'],
                'Count': [len(regrettable), len(non_regrettable_vol), len(involuntary)]
            })
            fig = px.pie(turnover_types, values='Count', names='Category',
                         color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['gray']],
                         hole=0.4)
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

            if len(regrettable) > 0:
                st.markdown("#### Regrettable Turnover by Department")
                reg_dept = regrettable.groupby('Department').agg(
                    Count=('Employee Status', 'count'),
                    Avg_Tenure=('Tenure (Months)', 'mean')
                ).reset_index()
                reg_dept['Avg_Tenure'] = reg_dept['Avg_Tenure'].round(1)
                reg_dept.columns = ['Department', 'Regrettable Losses', 'Avg Tenure (Months)']
                reg_dept = reg_dept.sort_values('Regrettable Losses', ascending=False)

                fig = px.bar(reg_dept, x='Department', y='Regrettable Losses',
                             color='Avg Tenure (Months)', color_continuous_scale='RdYlBu',
                             text='Regrettable Losses')
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

                if 'Exit Reason Category' in regrettable.columns:
                    st.markdown("#### Top Exit Reasons (Regrettable)")
                    reg_reasons = regrettable['Exit Reason Category'].value_counts().reset_index()
                    reg_reasons.columns = ['Reason', 'Count']
                    fig = px.bar(reg_reasons, x='Count', y='Reason', orientation='h',
                                 color='Count', color_continuous_scale='Reds')
                    fig.update_layout(height=max(250, len(reg_reasons) * 30),
                                      yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No voluntary departure data available.")
    else:
        st.info("No departed employees in current filter selection.")
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/advanced_analytics.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/advanced_analytics.py
git commit -m "feat: extract Advanced Analytics tab to src/pages/advanced_analytics.py"
```

---

### Task 11: Create src/pages/edit_data.py

**Files:**
- Create: `src/pages/edit_data.py`

**Step 1: Create the file**

App.py lines 1160-1316. This page needs `save_to_excel` and `DATA_FILE`.

```python
import streamlit as st
import pandas as pd
from datetime import datetime

from src.config import DATA_FILE
from src.data_processing import save_to_excel


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    st.subheader("Edit Employee Data")

    edit_action = st.radio("Action", ["Add New Employee", "Edit Existing", "Delete Record"],
                           horizontal=True)

    if edit_action == "Add New Employee":
        st.markdown("### Add New Employee")
        with st.form("add_employee_form"):
            form_col1, form_col2 = st.columns(2)

            with form_col1:
                new_name = st.text_input("Full Name *")
                new_gender = st.selectbox("Gender *", ["M", "F"])
                new_birthday = st.date_input("Birthday Date *",
                                             value=datetime(1995, 1, 1),
                                             min_value=datetime(1950, 1, 1))
                new_nationality = st.text_input("Nationality", value="")
                new_department = st.selectbox("Department *",
                                              sorted(df['Department'].dropna().unique().tolist()))
                new_position = st.selectbox("Position *",
                                            sorted(df['Position'].dropna().unique().tolist()))

            with form_col2:
                new_status = st.selectbox("Employee Status *", ["Active", "Departed"])
                new_join_date = st.date_input("Join Date *")
                new_exit_date = st.date_input("Exit Date (if departed)",
                                              value=None)
                emp_types_list = df['Employment Type'].dropna().unique().tolist() if 'Employment Type' in df.columns else ['Full time']
                new_type = st.selectbox("Employment Type", emp_types_list)
                new_exit_type = st.selectbox("Exit Type", ["", "Resigned", "Terminated", "Dropped"])
                new_exit_reason = st.text_input("Exit Reason Category", value="")

            submitted = st.form_submit_button("Add Employee")

            if submitted:
                if not new_name:
                    st.error("Full Name is required.")
                elif new_status == "Departed" and new_exit_date is None:
                    st.error("Exit Date is required for departed employees.")
                else:
                    new_row = {
                        NAME_COL or 'Full Name': new_name,
                        'Gender': new_gender,
                        'Birthday Date': pd.Timestamp(new_birthday),
                        'Nationality': new_nationality,
                        'Department': new_department,
                        'Position': new_position,
                        'Employee Status': new_status,
                        'Join Date': pd.Timestamp(new_join_date),
                        'Type': new_type,
                    }
                    if new_exit_date:
                        new_row['Exit Date'] = pd.Timestamp(new_exit_date)
                    if new_exit_type:
                        new_row['Exit Type'] = new_exit_type
                    if new_exit_reason:
                        new_row['Exit Reason Category'] = new_exit_reason

                    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    try:
                        save_to_excel(updated_df, DATA_FILE)
                        st.success(f"Added {new_name} successfully! Refresh the page to see changes.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving: {e}")

    elif edit_action == "Edit Existing":
        st.markdown("### Edit Existing Employee")
        if not NAME_COL:
            st.warning("Name column not detected in the data.")
            return

        search_edit = st.text_input("Search employee by name", key="edit_search")

        if search_edit:
            matches = df[df[NAME_COL].str.contains(search_edit, case=False, na=False)]
            if len(matches) == 0:
                st.warning("No employees found.")
            else:
                match_labels = [
                    f"{row[NAME_COL]} -- {row.get('Department', 'N/A')} (#{idx})"
                    for idx, row in matches.iterrows()
                ]
                selected_label = st.selectbox("Select employee", match_labels)
                emp_idx = int(selected_label.split('(#')[-1].rstrip(')'))
                emp_row = df.loc[emp_idx]

                with st.form("edit_employee_form"):
                    ecol1, ecol2 = st.columns(2)

                    with ecol1:
                        dept_list = sorted(df['Department'].dropna().unique().tolist())
                        edit_dept = st.selectbox("Department", dept_list,
                                                 index=dept_list.index(emp_row['Department']) if emp_row['Department'] in dept_list else 0)
                        edit_position = st.text_input("Position", value=str(emp_row.get('Position', '')))
                        edit_status = st.selectbox("Employee Status", ["Active", "Departed"],
                                                   index=0 if emp_row.get('Employee Status') == 'Active' else 1)

                    with ecol2:
                        edit_exit_date = st.date_input("Exit Date",
                                                       value=emp_row['Exit Date'].date() if pd.notna(emp_row.get('Exit Date')) else None)
                        exit_options = ["", "Resigned", "Terminated", "Dropped"]
                        edit_exit_type = st.selectbox("Exit Type", exit_options,
                                                      index=exit_options.index(emp_row['Exit Type']) if pd.notna(emp_row.get('Exit Type')) and emp_row['Exit Type'] in exit_options else 0)
                        edit_exit_reason = st.text_input("Exit Reason Category",
                                                          value=str(emp_row.get('Exit Reason Category', '')) if pd.notna(emp_row.get('Exit Reason Category')) else "")

                    edit_submitted = st.form_submit_button("Save Changes")

                    if edit_submitted:
                        df.at[emp_idx, 'Department'] = edit_dept
                        df.at[emp_idx, 'Position'] = edit_position
                        df.at[emp_idx, 'Employee Status'] = edit_status
                        if edit_exit_date:
                            df.at[emp_idx, 'Exit Date'] = pd.Timestamp(edit_exit_date)
                        if edit_exit_type:
                            df.at[emp_idx, 'Exit Type'] = edit_exit_type
                        if edit_exit_reason:
                            df.at[emp_idx, 'Exit Reason Category'] = edit_exit_reason

                        try:
                            save_to_excel(df, DATA_FILE)
                            st.success(f"Updated {emp_row[NAME_COL]} successfully! Refresh to see changes.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {e}")

    elif edit_action == "Delete Record":
        st.markdown("### Delete Employee Record")
        if not NAME_COL:
            st.warning("Name column not detected in the data.")
            return

        search_del = st.text_input("Search employee by name", key="del_search")

        if search_del:
            matches = df[df[NAME_COL].str.contains(search_del, case=False, na=False)]
            if len(matches) == 0:
                st.warning("No employees found.")
            else:
                match_labels = [
                    f"{row[NAME_COL]} -- {row.get('Department', 'N/A')} (#{idx})"
                    for idx, row in matches.iterrows()
                ]
                selected_del_label = st.selectbox("Select employee to delete", match_labels,
                                                  key="del_select")
                del_idx = int(selected_del_label.split('(#')[-1].rstrip(')'))
                emp_info = df.loc[del_idx]
                st.write(f"**Name:** {emp_info[NAME_COL]}")
                st.write(f"**Department:** {emp_info['Department']}")
                st.write(f"**Status:** {emp_info['Employee Status']}")

                confirm = st.checkbox("I confirm I want to delete this record", key="del_confirm")

                if st.button("Delete Record", type="primary", disabled=not confirm):
                    updated_df = df.drop(index=del_idx)
                    try:
                        save_to_excel(updated_df, DATA_FILE)
                        st.success(f"Deleted {emp_info[NAME_COL] if NAME_COL else 'record'}. Refresh to see changes.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving: {e}")
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('src/pages/edit_data.py').read()); print('OK')"
```

**Step 3: Commit**

```bash
git add src/pages/edit_data.py
git commit -m "feat: extract Edit Data tab to src/pages/edit_data.py"
```

---

### Task 12: Rewrite app.py as slim router

**Files:**
- Modify: `app.py` (replace entire contents)

**Step 1: Back up current app.py**

```bash
cp app.py app_v1_backup.py
```

**Step 2: Rewrite app.py**

Replace the entire file with the slim router:

```python
import streamlit as st
import pandas as pd
from datetime import datetime

from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, detect_name_column
from src.data_processing import load_excel, calculate_kpis
from src.utils import delta
from src.pages import overview, attrition, tenure_retention, workforce, trends, employee_data, advanced_analytics, edit_data

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="HR Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 HR Analytics Dashboard")

# ===================== DATA LOADING =====================
st.sidebar.header("📁 Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload Master Sheet", type=['xlsx', 'xls'],
    help="Upload your HR data Excel file (Master Sheet)"
)

df = None

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)
        df = load_excel(uploaded_file)
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            st.sidebar.error(f"Missing required columns: {', '.join(missing)}")
            df = None
        else:
            st.sidebar.success(f"Loaded {len(df)} records from **{uploaded_file.name}**")
            st.sidebar.caption(f"Uploaded at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            st.session_state['hr_data'] = df
            st.session_state['hr_file_name'] = uploaded_file.name
            st.session_state['hr_upload_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
elif 'hr_data' in st.session_state:
    df = st.session_state['hr_data']
    st.sidebar.success(f"Using **{st.session_state.get('hr_file_name', 'Master Sheet')}** ({len(df)} records)")
    st.sidebar.caption(f"Uploaded at {st.session_state.get('hr_upload_time', 'N/A')}")
else:
    st.sidebar.info("Please upload the Master Sheet (.xlsx) to get started.")

if df is None:
    st.warning("No data loaded. Please upload the Master Sheet to get started.")
    st.stop()

NAME_COL = detect_name_column(df)

# ===================== SIDEBAR FILTERS =====================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

if st.sidebar.button("Reset All Filters"):
    for key in ['dept_filter', 'status_filter', 'gender_filter', 'emp_type_filter',
                'nationality_filter', 'exit_type_filter']:
        st.session_state.pop(key, None)
    st.rerun()

date_range = None
if 'Join Date' in df.columns:
    min_date = df['Join Date'].dropna().min().date()
    max_date = df['Join Date'].dropna().max().date()
    date_range = st.sidebar.date_input(
        "Join Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

all_depts = sorted(df['Department'].dropna().unique().tolist())
dept_filter = st.sidebar.multiselect("Department", all_depts, default=all_depts)

status_filter = st.sidebar.selectbox("Employee Status", ["All", "Active", "Departed"])
gender_filter = st.sidebar.selectbox("Gender", ["All"] + df['Gender'].dropna().unique().tolist())

if 'Employment Type' in df.columns:
    emp_types = df['Employment Type'].dropna().unique().tolist()
    emp_type_filter = st.sidebar.selectbox("Employment Type", ["All"] + emp_types)
else:
    emp_type_filter = "All"

if 'Nationality' in df.columns:
    nationalities = sorted(df['Nationality'].dropna().unique().tolist())
    nationality_filter = st.sidebar.selectbox("Nationality", ["All"] + nationalities)
else:
    nationality_filter = "All"

exit_type_filter = st.sidebar.selectbox(
    "Exit Type", ["All"] + df['Exit Type'].dropna().unique().tolist()
)

# Apply filters
filtered_df = df.copy()

if date_range is not None and isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Join Date'].dt.date >= date_range[0]) &
        (filtered_df['Join Date'].dt.date <= date_range[1])
    ]

if dept_filter:
    filtered_df = filtered_df[filtered_df['Department'].isin(dept_filter)]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df['Employee Status'] == status_filter]
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df['Gender'] == gender_filter]
if emp_type_filter != "All":
    filtered_df = filtered_df[filtered_df['Employment Type'] == emp_type_filter]
if nationality_filter != "All":
    filtered_df = filtered_df[filtered_df['Nationality'] == nationality_filter]
if exit_type_filter != "All":
    filtered_df = filtered_df[filtered_df['Exit Type'] == exit_type_filter]

if len(filtered_df) == 0:
    st.warning("No records match the current filters. Please adjust your selections.")
    st.stop()

# ===================== KPI SECTION =====================
kpis = calculate_kpis(filtered_df)
kpis_all = calculate_kpis(df)

st.subheader("Key Performance Indicators")
row1 = st.columns(6)
row1[0].metric("Total Employees", f"{kpis['total']:,}")
row1[1].metric("Active", f"{kpis['active']:,}")
row1[2].metric("Departed", f"{kpis['departed']:,}")
row1[3].metric("Attrition Rate", f"{kpis['attrition_rate']:.1f}%",
               delta=delta(kpis['attrition_rate'], kpis_all['attrition_rate'], '%', len(filtered_df), len(df)),
               delta_color="inverse")
row1[4].metric("Retention Rate", f"{kpis['retention_rate']:.1f}%",
               delta=delta(kpis['retention_rate'], kpis_all['retention_rate'], '%', len(filtered_df), len(df)))
row1[5].metric("Avg Tenure (Mo)", f"{kpis['avg_tenure']:.1f}",
               delta=delta(kpis['avg_tenure'], kpis_all['avg_tenure'], '', len(filtered_df), len(df)))

row2 = st.columns(6)
row2[0].metric("Avg Age", f"{kpis['avg_age']:.0f}" if not pd.isna(kpis['avg_age']) else "N/A")
row2[1].metric("Gender (M:F)", kpis['gender_ratio'])
row2[2].metric("Contractor %", f"{kpis['contractor_ratio']:.1f}%")
row2[3].metric("Nationalities", f"{kpis['nationality_count']}")
row2[4].metric("Probation Pass", f"{kpis['probation_pass_rate']:.1f}%",
               delta=delta(kpis['probation_pass_rate'], kpis_all['probation_pass_rate'], '%', len(filtered_df), len(df)))
row2[5].metric("YoY Growth", f"{kpis['growth_rate']:+.1f}%")

if len(filtered_df) < len(df):
    st.caption(f"Deltas shown are vs. full dataset ({len(df)} records)")

st.markdown("---")

# ===================== TABS =====================
tab_names = [
    "📈 Overview",
    "🚪 Attrition Analysis",
    "⏱️ Tenure & Retention",
    "🏗️ Workforce Composition",
    "📅 Trends",
    "📋 Employee Data",
    "🔬 Advanced Analytics",
    "✏️ Edit Data",
]

tabs = st.tabs(tab_names)

with tabs[0]:
    overview.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[1]:
    attrition.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[2]:
    tenure_retention.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[3]:
    workforce.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[4]:
    trends.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[5]:
    employee_data.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[6]:
    advanced_analytics.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[7]:
    edit_data.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

# ===================== FOOTER =====================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "HR Analytics Dashboard | Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
```

**Step 3: Verify syntax**

```bash
python -c "import ast; ast.parse(open('app.py').read()); print('OK')"
```

**Step 4: Verify all imports resolve**

```bash
python -c "
from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, detect_name_column
from src.data_processing import load_excel, calculate_kpis
from src.utils import delta
from src.pages import overview, attrition, tenure_retention, workforce, trends, employee_data, advanced_analytics, edit_data
print('All imports OK')
"
```

**Step 5: Commit**

```bash
git add app.py app_v1_backup.py
git commit -m "refactor: rewrite app.py as slim router dispatching to src/pages/"
```

---

### Task 13: Clean up old files

**Files:**
- Delete: root `data_processing.py` (now lives in `src/`)

**Step 1: Remove old data_processing.py**

```bash
git rm data_processing.py
```

**Step 2: Verify app still imports correctly**

```bash
python -c "
from src.data_processing import load_excel, process_data, calculate_kpis
from src.config import COLORS
print('OK')
"
```

**Step 3: Commit**

```bash
git commit -m "chore: remove root data_processing.py (moved to src/)"
```

---

### Task 14: Update requirements.txt with pinned versions

**Files:**
- Modify: `requirements.txt`

**Step 1: Update requirements.txt**

```
streamlit==1.41.0
pandas==2.2.3
openpyxl==3.1.5
numpy==2.2.2
plotly==5.24.1
```

**Step 2: Commit**

```bash
git add requirements.txt
git commit -m "chore: pin dependency versions in requirements.txt"
```

---

### Task 15: Update .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Ensure .gitignore has these entries**

```
__pycache__/
*.pyc
.env
*.xlsx
!requirements*.txt
.pytest_cache/
htmlcov/
.coverage
nul
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: update .gitignore for python and test artifacts"
```

---

### Task 16: Add tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`
- Create: `tests/test_pages.py`
- Create: `tests/test_data_processing.py`

**Step 1: Create `tests/__init__.py`**

Empty file.

**Step 2: Create `tests/test_config.py`**

```python
from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, DATA_FILE, detect_name_column
import pandas as pd


def test_colors_has_required_keys():
    for key in ['primary', 'success', 'danger', 'warning', 'info', 'purple', 'pink', 'brown', 'gray']:
        assert key in COLORS
        assert isinstance(COLORS[key], str)
        assert COLORS[key].startswith('#')


def test_color_sequence_length():
    assert len(COLOR_SEQUENCE) == 8
    for c in COLOR_SEQUENCE:
        assert c in COLORS.values()


def test_chart_config_structure():
    assert CHART_CONFIG['displayModeBar'] is True
    assert CHART_CONFIG['displaylogo'] is False
    assert 'toImageButtonOptions' in CHART_CONFIG


def test_required_columns():
    assert len(REQUIRED_COLUMNS) == 5
    for col in REQUIRED_COLUMNS:
        assert isinstance(col, str)


def test_data_file():
    assert DATA_FILE == "Master.xlsx"


def test_detect_name_column_full_name():
    df = pd.DataFrame({'Full Name': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'Full Name'


def test_detect_name_column_double_space():
    df = pd.DataFrame({'Full  Name': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'Full  Name'


def test_detect_name_column_fullname():
    df = pd.DataFrame({'FullName': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'FullName'


def test_detect_name_column_fallback():
    df = pd.DataFrame({'Employee Name': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'Employee Name'


def test_detect_name_column_none():
    df = pd.DataFrame({'ID': [1], 'Age': [30]})
    assert detect_name_column(df) is None


def test_detect_name_column_skips_bank_name():
    df = pd.DataFrame({'Bank Name': ['HSBC'], 'ID': [1]})
    assert detect_name_column(df) is None
```

**Step 3: Create `tests/test_pages.py`**

```python
"""Smoke tests: every page module imports and has a render callable."""


def test_overview_importable():
    from src.pages import overview
    assert callable(overview.render)


def test_attrition_importable():
    from src.pages import attrition
    assert callable(attrition.render)


def test_tenure_retention_importable():
    from src.pages import tenure_retention
    assert callable(tenure_retention.render)


def test_workforce_importable():
    from src.pages import workforce
    assert callable(workforce.render)


def test_trends_importable():
    from src.pages import trends
    assert callable(trends.render)


def test_employee_data_importable():
    from src.pages import employee_data
    assert callable(employee_data.render)


def test_advanced_analytics_importable():
    from src.pages import advanced_analytics
    assert callable(advanced_analytics.render)


def test_edit_data_importable():
    from src.pages import edit_data
    assert callable(edit_data.render)
```

**Step 4: Create `tests/test_data_processing.py`**

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_processing import process_data, calculate_kpis, get_cohort_retention, get_manager_attrition


def _make_sample_df(n=20):
    """Create a sample HR dataframe for testing."""
    np.random.seed(42)
    today = datetime.now()
    rows = []
    for i in range(n):
        status = 'Active' if i % 3 != 0 else 'Departed'
        join_date = today - timedelta(days=np.random.randint(90, 1800))
        exit_date = join_date + timedelta(days=np.random.randint(30, 500)) if status == 'Departed' else pd.NaT
        rows.append({
            'Full Name': f'Employee {i}',
            'Gender': 'M' if i % 2 == 0 else 'F',
            'Birthday Date': today - timedelta(days=365 * np.random.randint(25, 55)),
            'Nationality': ['Egyptian', 'Saudi', 'Indian'][i % 3],
            'Department': ['IT', 'HR', 'Finance', 'Sales'][i % 4],
            'Position': ['Analyst', 'Manager', 'Director', 'Engineer'][i % 4],
            'Employee Status': status,
            'Join Date (yyyy/mm/dd)': join_date,
            'Exit Date yyyy/mm/dd': exit_date,
            'Exit Type': 'Resigned' if status == 'Departed' and i % 2 == 0 else ('Terminated' if status == 'Departed' else ''),
            'Exit Reason Category': 'Better Opportunity' if status == 'Departed' else '',
            'Type': ['Full time', 'Contract', 'Freelancer'][i % 3],
            'Vendor': ['Direct Hire', 'Agency A'][i % 2],
        })
    return pd.DataFrame(rows)


def test_process_data_creates_age():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Age' in result.columns
    assert (result['Age'] > 0).any()


def test_process_data_creates_tenure():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Tenure (Months)' in result.columns
    assert (result['Tenure (Months)'] > 0).any()


def test_process_data_creates_join_year():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Join Year' in result.columns
    assert 'Join Month' in result.columns
    assert 'Join Quarter' in result.columns


def test_process_data_renames_columns():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Join Date' in result.columns
    assert 'Exit Date' in result.columns


def test_process_data_employment_type():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Employment Type' in result.columns


def test_calculate_kpis_returns_all_keys():
    df = process_data(_make_sample_df())
    kpis = calculate_kpis(df)
    expected_keys = ['total', 'active', 'departed', 'attrition_rate', 'retention_rate',
                     'avg_tenure', 'avg_age', 'contractor_ratio', 'nationality_count',
                     'gender_ratio', 'male_count', 'female_count', 'probation_pass_rate', 'growth_rate']
    for key in expected_keys:
        assert key in kpis, f"Missing KPI key: {key}"


def test_calculate_kpis_math():
    df = process_data(_make_sample_df())
    kpis = calculate_kpis(df)
    assert kpis['total'] == kpis['active'] + kpis['departed']
    assert 0 <= kpis['attrition_rate'] <= 100
    assert 0 <= kpis['retention_rate'] <= 100
    assert abs(kpis['attrition_rate'] + kpis['retention_rate'] - 100) < 0.1


def test_calculate_kpis_empty_df():
    df = process_data(_make_sample_df()).head(0)
    kpis = calculate_kpis(df)
    assert kpis['total'] == 0
    assert kpis['attrition_rate'] == 0


def test_cohort_retention():
    df = process_data(_make_sample_df())
    cohort = get_cohort_retention(df)
    assert len(cohort) > 0
    assert 'Join Year' in cohort.columns
    assert 'Retention Rate %' in cohort.columns


def test_cohort_retention_empty():
    df = pd.DataFrame({'Employee Status': []})
    cohort = get_cohort_retention(df)
    assert len(cohort) == 0


def test_manager_attrition_no_column():
    df = process_data(_make_sample_df())
    result = get_manager_attrition(df)
    assert len(result) == 0  # No manager CRM column


def test_manager_attrition_with_column():
    df = process_data(_make_sample_df())
    df['Direct Manager CRM while Resignation'] = ['MGR_A', 'MGR_B'] * (len(df) // 2)
    result = get_manager_attrition(df)
    if len(df[df['Employee Status'] == 'Departed']) > 0:
        assert len(result) > 0
        assert 'Manager CRM' in result.columns
        assert 'Departures' in result.columns


def test_gender_ratio_format():
    df = process_data(_make_sample_df())
    kpis = calculate_kpis(df)
    assert ':' in kpis['gender_ratio']
    parts = kpis['gender_ratio'].split(':')
    assert len(parts) == 2
    assert int(parts[0]) >= 0
    assert int(parts[1]) >= 0
```

**Step 5: Run tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add tests/
git commit -m "test: add test suite for config, pages, and data processing"
```

---

### Task 17: Add CI pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Create the file**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8

      - name: Lint
        run: flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Test
        run: pytest tests/ -v --cov=src --cov-report=term-missing
```

**Step 2: Commit**

```bash
mkdir -p .github/workflows
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for lint and test"
```

---

### Task 18: Final verification

**Step 1: Run full lint**

```bash
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

Expected: 0 errors

**Step 2: Run full test suite**

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

Expected: All tests pass

**Step 3: Verify app.py syntax is clean**

```bash
python -c "import ast; ast.parse(open('app.py').read()); print('app.py OK')"
```

**Step 4: Verify all page modules parse**

```bash
python -c "
import ast
for f in ['overview', 'attrition', 'tenure_retention', 'workforce', 'trends', 'employee_data', 'advanced_analytics', 'edit_data']:
    ast.parse(open(f'src/pages/{f}.py').read())
    print(f'{f}.py OK')
"
```

Expected: All 8 OK

**Step 5: Commit any fixes if needed, then push**

```bash
git push origin main
```
