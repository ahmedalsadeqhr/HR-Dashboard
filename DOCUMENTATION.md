# Technical Documentation

## Application Architecture

### Overview

The HR Analytics Dashboard is a single-page Streamlit application that reads employee data from Excel files and displays interactive visualizations and analytics.

### Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Charts | Streamlit native charts |
| Data Source | Excel (.xlsx) |
| Hosting | Streamlit Community Cloud |

---

## Code Structure

### app.py - Main Application

```
app.py
├── Imports & Config (lines 1-8)
├── Data Source Selection (lines 10-16)
├── Data Processing Functions (lines 18-57)
│   ├── load_default_data()
│   └── process_data()
├── Data Loading Logic (lines 59-106)
├── Sidebar Filters (lines 108-141)
├── KPI Metrics (lines 143-161)
├── Tab 1: Overview (lines 172-222)
├── Tab 2: Attrition Analysis (lines 224-290)
├── Tab 3: Tenure Analysis (lines 292-346)
├── Tab 4: Trends (lines 348-383)
├── Tab 5: Employee Data (lines 385-432)
└── Footer (lines 434-439)
```

---

## Key Functions

### 1. process_data(df)

**Purpose:** Cleans and transforms raw Excel data

**Input:** Raw pandas DataFrame from Excel

**Output:** Processed DataFrame with calculated fields

**Transformations:**
```python
# Column name cleaning
df.columns = df.columns.str.replace('\n', ' ').str.strip()

# Date conversions
df['Join Date'] = pd.to_datetime(df['Join Date'], errors='coerce')
df['Exit Date'] = pd.to_datetime(df['Exit Date'], errors='coerce')
df['Birthday Date'] = pd.to_datetime(df['Birthday Date'], errors='coerce')

# Calculated fields
df['Age'] = ((today - df['Birthday Date']).dt.days / 365.25)
df['Tenure (Months)'] = ((exit_or_today - df['Join Date']).dt.days / 30.44)
df['Join Year'] = df['Join Date'].dt.year
df['Join Month'] = df['Join Date'].dt.to_period('M')
df['Exit Year'] = df['Exit Date'].dt.year
df['Exit Month'] = df['Exit Date'].dt.to_period('M')
```

### 2. load_default_data()

**Purpose:** Loads Master.xlsx with caching

**Caching:** Uses `@st.cache_data` for performance

```python
@st.cache_data
def load_default_data():
    df = pd.read_excel("Master.xlsx")
    return process_data(df)
```

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Excel File     │────>│  process_data()  │────>│  Streamlit UI   │
│  (Master.xlsx   │     │  - Clean columns │     │  - KPIs         │
│   or uploaded)  │     │  - Convert dates │     │  - Charts       │
│                 │     │  - Calculate age │     │  - Tables       │
│                 │     │  - Calculate     │     │  - Filters      │
│                 │     │    tenure        │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Filters Implementation

### Sidebar Filters

```python
# Filter options are dynamically generated from data
dept_filter = st.sidebar.selectbox(
    "Department",
    ["All"] + sorted(df['Department'].dropna().unique().tolist())
)

# Filter application
filtered_df = df.copy()
if dept_filter != "All":
    filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
```

### Available Filters
- Department
- Employee Status (Active/Departed)
- Gender (M/F)
- Exit Type (Resigned/Terminated/Dropped)

---

## Metrics Calculations

### Attrition Rate
```python
attrition_rate = (departed / total * 100)
```

### Average Tenure
```python
# For Active employees: today - join_date
# For Departed employees: exit_date - join_date
df['Tenure (Months)'] = np.where(
    df['Employee Status'] == 'Active',
    ((today - df['Join Date']).dt.days / 30.44),
    ((df['Exit Date'] - df['Join Date']).dt.days / 30.44)
)
```

### Age Calculation
```python
df['Age'] = ((today - df['Birthday Date']).dt.days / 365.25).astype(int)
```

---

## Adding New Features

### Adding a New KPI

1. Calculate the metric:
```python
new_metric = filtered_df['column'].mean()  # or other calculation
```

2. Add to the KPI row:
```python
col7.metric("New Metric", f"{new_metric:.1f}")
```

### Adding a New Chart

1. Prepare the data:
```python
chart_data = filtered_df['column'].value_counts()
```

2. Display the chart:
```python
st.bar_chart(chart_data)
# or
st.line_chart(chart_data)
```

### Adding a New Filter

1. Add to sidebar:
```python
new_filter = st.sidebar.selectbox(
    "New Filter",
    ["All"] + df['new_column'].dropna().unique().tolist()
)
```

2. Apply filter:
```python
if new_filter != "All":
    filtered_df = filtered_df[filtered_df['new_column'] == new_filter]
```

### Adding a New Tab

1. Add tab name:
```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview",
    # ... existing tabs ...
    "🆕 New Tab"
])
```

2. Add tab content:
```python
with tab6:
    st.subheader("New Analysis")
    # Add your visualizations here
```

---

## Customization Guide

### Changing Colors

Streamlit uses default colors. For custom colors, use Plotly:

1. Update requirements.txt:
```
plotly
```

2. Use Plotly charts:
```python
import plotly.express as px
fig = px.bar(data, color_discrete_sequence=['#3498db'])
st.plotly_chart(fig)
```

### Changing Layout

```python
# Wide layout (current)
st.set_page_config(layout="wide")

# Centered layout
st.set_page_config(layout="centered")
```

### Adding Logo

```python
st.sidebar.image("logo.png", width=200)
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Column not found" error | Check if Excel columns match expected names |
| Slow loading | Reduce data size or add more caching |
| Charts not showing | Check if data is empty after filtering |
| Upload fails | Verify Excel file format (.xlsx) |

### Debugging

Add debug info:
```python
st.write("Debug - DataFrame shape:", df.shape)
st.write("Debug - Columns:", df.columns.tolist())
```

---

## Performance Optimization

### Current Optimizations

1. **Caching:** `@st.cache_data` for data loading
2. **Lazy Loading:** Tabs only render when clicked
3. **Filtered Data:** Charts use filtered data, not full dataset

### Additional Optimizations

```python
# Cache expensive calculations
@st.cache_data
def calculate_metrics(df):
    return {
        'total': len(df),
        'active': len(df[df['Employee Status'] == 'Active']),
        # ... more metrics
    }
```

---

## Deployment

### Streamlit Cloud

1. Requirements file must be named `requirements.txt`
2. Main file should be `app.py` (or specify in Streamlit Cloud)
3. Data files must be in the repository

### Environment Variables

For sensitive data, use Streamlit secrets:
```python
# .streamlit/secrets.toml
api_key = "your_key"

# In app.py
st.secrets["api_key"]
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial release |
| 1.1 | 2026-02-01 | Added file upload feature |
| 1.2 | 2026-02-01 | Added comprehensive analysis tabs |
