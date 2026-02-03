# HR Analytics Dashboard - Complete Offline Guide

**Version:** 1.2
**Last Updated:** February 2026
**Author:** HR Analytics Team

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [Getting Started](#2-getting-started)
3. [Dashboard Features](#3-dashboard-features)
4. [How to Use the Dashboard](#4-how-to-use-the-dashboard)
5. [Updating Data](#5-updating-data)
6. [Data Requirements](#6-data-requirements)
7. [Technical Documentation](#7-technical-documentation)
8. [Customization Guide](#8-customization-guide)
9. [Troubleshooting](#9-troubleshooting)
10. [Appendix](#10-appendix)

---

# 1. Project Overview

## 1.1 What is this Dashboard?

The HR Analytics Dashboard is a web-based application that provides comprehensive insights into workforce data. It analyzes employee information, tracks attrition, measures tenure, and identifies trends.

## 1.2 Live URL

```
https://hr-dashboard-51talk.streamlit.app
```

## 1.3 Key Features

| Feature | Description |
|---------|-------------|
| Real-time Analytics | Instant calculations and visualizations |
| Interactive Filters | Filter by department, status, gender, exit type |
| File Upload | Update data without coding |
| Export | Download filtered data as CSV |
| 5 Analysis Tabs | Overview, Attrition, Tenure, Trends, Employee Data |

## 1.4 Project Files

```
HR Dashboard/
│
├── app.py                    # Main application code
├── requirements.txt          # Python dependencies
├── Master.xlsx               # Default HR data file
│
├── README.md                 # Quick start guide
├── DOCUMENTATION.md          # Technical documentation
├── DATA_DICTIONARY.md        # Data column specifications
└── HR_Dashboard_Complete_Guide.md  # This file (offline guide)
```

---

# 2. Getting Started

## 2.1 Access Online (Recommended)

Simply open your web browser and go to:
```
https://hr-dashboard-51talk.streamlit.app
```

No installation required!

## 2.2 Run Locally

### Step 1: Install Python
Download Python 3.8 or higher from https://python.org

### Step 2: Download Project Files
Download the project folder or clone from GitHub:
```
git clone https://github.com/ahmedalsadeqhr/HR-Dashboard.git
```

### Step 3: Install Dependencies
Open Command Prompt/Terminal in the project folder:
```
pip install -r requirements.txt
```

### Step 4: Run the Dashboard
```
streamlit run app.py
```

### Step 5: Open Browser
Go to: http://localhost:8501

---

# 3. Dashboard Features

## 3.1 Key Performance Indicators (KPIs)

The top of the dashboard shows 6 key metrics:

| Metric | Description | Calculation |
|--------|-------------|-------------|
| Total Employees | All employees in filtered data | Count of rows |
| Active | Currently employed | Status = "Active" |
| Departed | No longer employed | Status = "Departed" |
| Attrition Rate | Percentage who left | (Departed / Total) × 100 |
| Avg Tenure | Average employment duration | Mean of tenure in months |
| Avg Age | Average employee age | Mean of calculated ages |

## 3.2 Tab 1: Overview

### Gender Distribution
- Bar chart showing Male vs Female count
- Table with count and percentage

### Employee Status
- Bar chart showing Active vs Departed
- Table with count and percentage

### Top 10 Departments
- Bar chart of largest departments
- Table with employee counts

### Top 10 Positions
- Bar chart of most common positions
- Table with employee counts

### Age Distribution
- Bar chart with age brackets:
  - 18-25, 26-30, 31-35, 36-40, 41-45, 46-50, 50+

## 3.3 Tab 2: Attrition Analysis

### Exit Types
- Breakdown of how employees left:
  - Resigned (voluntary)
  - Terminated (involuntary)
  - Dropped (during probation)

### Exit Reason Categories
- Why employees left:
  - Personal Reasons
  - Career & Growth
  - Performance Issues
  - Training Fail
  - Failed Probation
  - No Show
  - Misconduct & Compliance
  - Work Environment & Culture
  - Management Issues
  - Business Restructuring
  - Other

### Attrition by Department
- Table showing:
  - Department name
  - Active count
  - Departed count
  - Total count
  - Attrition rate %

### Voluntary vs Involuntary
- Voluntary: Resigned
- Involuntary: Terminated + Dropped

### Detailed Exit Reasons
- Top 15 specific exit reasons

## 3.4 Tab 3: Tenure Analysis

### Tenure Statistics
- Minimum tenure
- Maximum tenure
- Average tenure
- Median tenure

### Tenure Distribution
- Bar chart with brackets:
  - 0-3 months
  - 3-6 months
  - 6-12 months
  - 1-2 years
  - 2-3 years
  - 3+ years

### Average Tenure by Department
- Ranked list of departments by avg tenure

### Tenure by Employee Status
- Comparison of Active vs Departed tenure stats

### Early Leavers Analysis
- Employees who left within 6 months
- Count and percentage of all departures
- Top reasons for early departure

## 3.5 Tab 4: Trends

### Hiring Trend by Year
- Line chart showing hires per year
- Table with yearly counts

### Attrition Trend by Year
- Line chart showing exits per year
- Table with yearly counts

### Monthly Hiring Trend
- Recent 24 months of hiring activity

### Headcount Analysis
- Breakdown by year and status

## 3.6 Tab 5: Employee Data

### Search
- Search employees by name

### Column Selector
- Choose which columns to display

### Data Table
- Scrollable table with employee details

### CSV Download
- Export filtered data to Excel/CSV

### Quick Statistics
- Numerical summary (age, tenure)
- Category counts

---

# 4. How to Use the Dashboard

## 4.1 Using Filters

### Location
Filters are in the **left sidebar**

### Available Filters

| Filter | Options | Effect |
|--------|---------|--------|
| Department | All departments | Shows only selected department |
| Employee Status | Active, Departed | Shows only selected status |
| Gender | M, F | Shows only selected gender |
| Exit Type | Resigned, Terminated, Dropped | Shows only selected exit type |

### How to Apply
1. Click the dropdown
2. Select your option
3. Dashboard updates automatically

### Reset Filters
Select "All" to remove a filter

## 4.2 Reading Charts

### Bar Charts
- Horizontal bars = categories
- Length = count/value
- Hover for exact numbers

### Line Charts
- X-axis = time (years/months)
- Y-axis = count
- Shows trends over time

### Tables
- Click column headers to sort
- Scroll for more rows

## 4.3 Exporting Data

### Download CSV
1. Go to "Employee Data" tab
2. Apply desired filters
3. Click "Download Filtered Data as CSV"
4. Open in Excel

---

# 5. Updating Data

## 5.1 Method 1: Upload in Dashboard (Easiest)

### Steps:
1. Open the dashboard
2. In sidebar, select **"Upload New File"**
3. Click **"Browse files"**
4. Select your Excel file (.xlsx)
5. Dashboard updates instantly

### Requirements:
- File must be .xlsx format
- Must have required columns (see Section 6)
- Same structure as Master.xlsx

## 5.2 Method 2: Replace Master.xlsx

### Steps:
1. Update your Master.xlsx file
2. Open Command Prompt in project folder
3. Run these commands:
```
git add Master.xlsx
git commit -m "Update HR data"
git push
```
4. Streamlit Cloud auto-redeploys (2-3 minutes)

## 5.3 Method 3: Edit on GitHub

### Steps:
1. Go to https://github.com/ahmedalsadeqhr/HR-Dashboard
2. Click on Master.xlsx
3. Click "Delete" and confirm
4. Click "Add file" > "Upload files"
5. Upload new Master.xlsx
6. Click "Commit changes"

---

# 6. Data Requirements

## 6.1 Required Columns

These columns MUST exist in your Excel file:

| Column Name | Type | Example |
|-------------|------|---------|
| Full Name | Text | "Ahmed Mohamed" |
| Gender | Text | "M" or "F" |
| Birthday Date | Date | 1990-05-15 |
| Department | Text | "EA" |
| Position | Text | "EA-L2" |
| Employee Status | Text | "Active" or "Departed" |
| Join Date (yyyy/mm/dd) | Date | 2023-01-15 |

## 6.2 Required for Departed Employees

| Column Name | Type | Example |
|-------------|------|---------|
| Exit Date yyyy/mm/dd | Date | 2024-06-30 |
| Exit Type | Text | "Resigned" |
| Exit Reason Category | Text | "Personal Reasons" |

## 6.3 Optional Columns

| Column Name | Type | Example |
|-------------|------|---------|
| PS ID | Number | 12345 |
| CRM | Text | "CRM001" |
| Identity number | Number | 29001234567890 |
| Nationality | Text | "Egypt" |
| Work Email address | Text | "ahmed@company.com" |
| Exit Reason | Text | "Found better opportunity" |
| Remark | Text | "Transferred from..." |

## 6.4 Valid Values

### Employee Status
- `Active` - Currently employed
- `Departed` - No longer employed

### Gender
- `M` - Male
- `F` - Female

### Exit Type
- `Resigned` - Voluntary departure
- `Terminated` - Fired
- `Dropped` - Left during probation

### Exit Reason Category
- Personal Reasons
- Career & Growth
- Performance Issues
- Training Fail
- Failed Probation
- No Show
- Misconduct & Compliance
- Work Environment & Culture
- Management Issues
- Business Restructuring
- Job Content Mismatch
- Other

## 6.5 Date Formats

Accepted formats:
- 2023-01-15 (YYYY-MM-DD) ✓ Recommended
- 2023/01/15 (YYYY/MM/DD)
- 15/01/2023 (DD/MM/YYYY)
- 01/15/2023 (MM/DD/YYYY)
- Excel date numbers

## 6.6 Sample Data Template

```
Full Name,Gender,Birthday Date,Department,Position,Employee Status,Join Date (yyyy/mm/dd),Exit Date yyyy/mm/dd,Exit Type,Exit Reason Category
Ahmed Mohamed,M,1990-05-15,EA,EA-L2,Active,2023-01-15,,,
Sara Ahmed,F,1995-03-20,CM,CM-L1,Departed,2022-06-01,2024-01-15,Resigned,Career & Growth
```

---

# 7. Technical Documentation

## 7.1 Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| Framework | Streamlit |
| Data Processing | Pandas, NumPy |
| Charts | Streamlit native |
| Data Format | Excel (.xlsx) |
| Hosting | Streamlit Community Cloud |

## 7.2 File Structure

### app.py (Main Application)

```
Lines 1-8:      Imports and page configuration
Lines 10-16:    Data source selection (sidebar)
Lines 18-57:    Data processing functions
Lines 59-106:   Data loading logic
Lines 108-141:  Sidebar filters
Lines 143-161:  KPI metrics display
Lines 163-170:  Tab definitions
Lines 172-222:  Tab 1: Overview
Lines 224-290:  Tab 2: Attrition Analysis
Lines 292-346:  Tab 3: Tenure Analysis
Lines 348-383:  Tab 4: Trends
Lines 385-432:  Tab 5: Employee Data
Lines 434-439:  Footer
```

### requirements.txt

```
streamlit
pandas
openpyxl
numpy
```

## 7.3 Key Functions

### process_data(df)
**Purpose:** Clean and transform raw Excel data

**What it does:**
1. Cleans column names (removes line breaks)
2. Converts date columns to datetime
3. Calculates Age from Birthday Date
4. Calculates Tenure in months
5. Extracts Year and Month from dates

### load_default_data()
**Purpose:** Load Master.xlsx with caching

**Caching:** Results are cached to improve performance

## 7.4 Calculated Fields

| Field | Formula |
|-------|---------|
| Age | (Today - Birthday Date) ÷ 365.25 days |
| Tenure (Months) | (Exit Date or Today - Join Date) ÷ 30.44 days |
| Join Year | Year extracted from Join Date |
| Join Month | Year-Month from Join Date |
| Exit Year | Year extracted from Exit Date |
| Exit Month | Year-Month from Exit Date |
| Attrition Rate | (Departed ÷ Total) × 100 |

---

# 8. Customization Guide

## 8.1 Adding a New KPI

### Step 1: Calculate the metric
```python
new_metric = filtered_df['column'].mean()
```

### Step 2: Add column to display
```python
# Change from 6 columns to 7
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

# Add the new metric
col7.metric("New Metric", f"{new_metric:.1f}")
```

## 8.2 Adding a New Filter

### Step 1: Add to sidebar
```python
new_filter = st.sidebar.selectbox(
    "New Filter Label",
    ["All"] + sorted(df['column_name'].dropna().unique().tolist())
)
```

### Step 2: Apply the filter
```python
if new_filter != "All":
    filtered_df = filtered_df[filtered_df['column_name'] == new_filter]
```

## 8.3 Adding a New Chart

### Bar Chart
```python
st.subheader("Chart Title")
data = filtered_df['column'].value_counts()
st.bar_chart(data)
```

### Line Chart
```python
st.subheader("Trend Title")
trend_data = filtered_df.groupby('date_column').size()
st.line_chart(trend_data)
```

### Table
```python
st.subheader("Table Title")
st.dataframe(data, use_container_width=True)
```

## 8.4 Adding a New Tab

### Step 1: Add tab name
```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview",
    "🚪 Attrition Analysis",
    "⏱️ Tenure Analysis",
    "📅 Trends",
    "📋 Employee Data",
    "🆕 New Tab"  # Add this
])
```

### Step 2: Add tab content
```python
with tab6:
    st.subheader("New Analysis")
    # Add your charts and tables here
```

## 8.5 Changing the Title

```python
st.title("Your New Dashboard Title")
```

## 8.6 Adding a Logo

```python
st.sidebar.image("logo.png", width=200)
```

---

# 9. Troubleshooting

## 9.1 Common Issues

### Issue: Dashboard won't load
**Causes:**
- Internet connection issue
- Streamlit Cloud is down

**Solutions:**
- Check internet connection
- Try again in a few minutes
- Run locally if urgent

### Issue: "Column not found" error
**Cause:** Excel file missing required columns

**Solution:**
- Check column names match exactly
- See Section 6 for required columns

### Issue: Charts are empty
**Cause:** All data filtered out

**Solution:**
- Reset filters to "All"
- Check if data exists for selected filters

### Issue: Wrong age/tenure calculations
**Cause:** Invalid date formats

**Solution:**
- Use YYYY-MM-DD date format
- Check for invalid dates in Excel

### Issue: Upload fails
**Causes:**
- Wrong file format
- File too large
- Missing columns

**Solutions:**
- Use .xlsx format (not .xls)
- Reduce file size if over 200MB
- Check required columns exist

### Issue: Data not updating
**Cause:** Browser cache

**Solution:**
- Hard refresh: Ctrl + Shift + R
- Clear browser cache
- Try incognito/private window

## 9.2 Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "No data loaded" | File not found | Upload file or check Master.xlsx |
| "KeyError: 'column'" | Missing column | Add the column to Excel |
| "ValueError: date" | Invalid date | Fix date format in Excel |
| "MemoryError" | File too large | Reduce data size |

## 9.3 Getting Help

1. Check this documentation
2. Review error message carefully
3. Try the troubleshooting steps
4. Contact HR Analytics team

---

# 10. Appendix

## 10.1 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + R | Refresh page |
| Ctrl + Shift + R | Hard refresh (clear cache) |
| Ctrl + F | Find on page |
| Ctrl + P | Print page |

## 10.2 Browser Compatibility

| Browser | Supported |
|---------|-----------|
| Chrome | ✓ Recommended |
| Firefox | ✓ |
| Edge | ✓ |
| Safari | ✓ |
| Internet Explorer | ✗ Not supported |

## 10.3 Department Codes Reference

| Code | Full Name |
|------|-----------|
| EA | Executive Assistant |
| CM | Community Manager |
| CC | Customer Care |
| TMK | Telemarketing |
| TA | Talent Acquisition |
| HR | Human Resources |
| AI | Artificial Intelligence |
| IT | Information Technology |
| Admin | Administration |
| Training | Training Department |
| Operations | Operations |
| Marketing | Marketing |
| Legal | Legal Department |

## 10.4 Glossary

| Term | Definition |
|------|------------|
| Attrition | Employees leaving the organization |
| Attrition Rate | Percentage of employees who left |
| Tenure | Length of employment |
| Voluntary Turnover | Employees who resigned |
| Involuntary Turnover | Employees who were terminated |
| Early Leaver | Employee who left within 6 months |
| KPI | Key Performance Indicator |

## 10.5 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial release |
| 1.1 | Feb 2026 | Added file upload feature |
| 1.2 | Feb 2026 | Added comprehensive analysis tabs |

## 10.6 Contact Information

**HR Analytics Team**
- Email: [Your email]
- Phone: [Your phone]

**Technical Support**
- GitHub: https://github.com/ahmedalsadeqhr/HR-Dashboard

---

# Quick Reference Card

## Dashboard URL
```
https://hr-dashboard-51talk.streamlit.app
```

## Update Data
1. Sidebar → "Upload New File"
2. Browse → Select Excel file
3. Done!

## Required Columns
- Full Name
- Gender (M/F)
- Birthday Date
- Department
- Position
- Employee Status (Active/Departed)
- Join Date

## For Departed Employees Add
- Exit Date
- Exit Type
- Exit Reason Category

## Run Locally
```
pip install -r requirements.txt
streamlit run app.py
```

---

*End of Document*
