# HR Analytics Dashboard - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Login & User Roles](#login--user-roles)
3. [Dashboard Navigation](#dashboard-navigation)
4. [Sidebar Filters](#sidebar-filters)
5. [Key Performance Indicators (KPIs)](#key-performance-indicators)
6. [Tab 1: Overview](#tab-1-overview)
7. [Tab 2: Attrition Analysis](#tab-2-attrition-analysis)
8. [Tab 3: Tenure & Retention](#tab-3-tenure--retention)
9. [Tab 4: Workforce Composition](#tab-4-workforce-composition)
10. [Tab 5: Trends](#tab-5-trends)
11. [Tab 6: Employee Data](#tab-6-employee-data)
12. [Tab 7: Edit Data](#tab-7-edit-data-editoradmin-only)
13. [Data Upload](#data-upload)
14. [Managing User Accounts](#managing-user-accounts)
15. [Deployment to Streamlit Cloud](#deployment-to-streamlit-cloud)
16. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages (installed automatically):
  - streamlit
  - pandas
  - openpyxl
  - numpy
  - plotly
  - streamlit-authenticator
  - pyyaml

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch the dashboard:
   ```bash
   python -m streamlit run app.py
   ```

3. Open your browser to `http://localhost:8501`

---

## Login & User Roles

The dashboard requires authentication. There are three access levels:

| Role | Username | Default Password | Permissions |
|------|----------|-----------------|-------------|
| **Admin** | `admin` | `admin123` | View all tabs + Edit/Add/Delete employee data |
| **Editor** | `editor` | `editor123` | View all tabs + Edit/Add/Delete employee data |
| **Viewer** | `viewer` | `viewer123` | View all tabs (read-only, no editing) |

### How to Log In

1. Open the dashboard URL in your browser
2. Enter your **Username** and **Password** in the login form
3. Click **Login**
4. Your name and role will appear in the top-right corner of the dashboard

### How to Log Out

- Click the **Logout** button in the top-right corner of the dashboard
- Your session cookie expires after 30 days of inactivity

### Changing Passwords

To change a user's password, edit the `auth_config.yaml` file. You need to generate a new hashed password:

```python
import streamlit_authenticator as stauth
print(stauth.Hasher.hash('your_new_password'))
```

Replace the password hash in `auth_config.yaml` under the corresponding username.

---

## Dashboard Navigation

The dashboard is organized into **tabs** across the top of the page:

| Tab | Icon | Description |
|-----|------|-------------|
| Overview | 📈 | High-level workforce snapshot |
| Attrition Analysis | 🚪 | Exit patterns and reasons |
| Tenure & Retention | ⏱️ | Employee duration and cohort analysis |
| Workforce Composition | 🏗️ | Employment types, vendors, diversity |
| Trends | 📅 | Hiring, attrition, and headcount over time |
| Employee Data | 📋 | Searchable employee table with export |
| Edit Data | ✏️ | Add/Edit/Delete records (Editor & Admin only) |

Click any tab to switch between views. All tabs respond to the sidebar filters.

---

## Sidebar Filters

The left sidebar contains filters that apply to **all tabs simultaneously**.

### Available Filters

| Filter | Type | Description |
|--------|------|-------------|
| **Data Source** | Radio button | Choose between default Master.xlsx or upload a new file |
| **Join Date Range** | Date picker | Filter employees by their join date range |
| **Department** | Multi-select | Select one or more departments (all selected by default) |
| **Employee Status** | Dropdown | All / Active / Departed |
| **Gender** | Dropdown | All / M / F |
| **Employment Type** | Dropdown | All / Full time / Freelancer |
| **Nationality** | Dropdown | All / (available nationalities) |
| **Exit Type** | Dropdown | All / Resigned / Terminated / Dropped |

### How Filters Work

- Filters are applied **cumulatively** (AND logic) - selecting Department = "HR" and Status = "Active" shows only active HR employees
- The **Department** filter is multi-select - you can select/deselect multiple departments
- All other filters are single-select dropdowns
- KPIs and all charts update automatically when filters change
- If no records match the current filters, a warning message will appear

### Resetting Filters

To reset all filters, refresh the page in your browser (F5 or Ctrl+R).

---

## Key Performance Indicators

At the top of the dashboard, 12 KPIs are displayed in two rows:

### Row 1 - Core Metrics

| KPI | Description |
|-----|-------------|
| **Total Employees** | Total count of employees matching current filters |
| **Active** | Number of currently active employees |
| **Departed** | Number of employees who have left |
| **Attrition Rate** | Departed / Total × 100% |
| **Retention Rate** | Active / Total × 100% |
| **Avg Tenure (Mo)** | Average employment duration in months |

### Row 2 - Advanced Metrics

| KPI | Description |
|-----|-------------|
| **Avg Age** | Average age of employees |
| **Gender (M:F)** | Male to Female ratio |
| **Contractor %** | Percentage of freelancers/contractors |
| **Nationalities** | Number of unique nationalities |
| **Probation Pass** | Percentage who completed probation |
| **YoY Growth** | Year-over-year hiring growth rate |

---

## Tab 1: Overview

Provides a high-level snapshot of the workforce.

### Charts Included

1. **Gender Distribution** - Donut chart showing male/female split with percentages
2. **Employee Status** - Donut chart showing active vs departed ratio
3. **Department Breakdown** - Grouped bar chart comparing active and departed by department
4. **Top 15 Positions** - Horizontal bar chart of most common positions
5. **Age Distribution** - Histogram with box plot showing age spread
6. **Nationality Distribution** - Donut chart of nationality breakdown

### How to Use

- **Hover** over any chart element to see exact values
- **Click** legend items to show/hide categories
- **Zoom** by clicking and dragging on a chart area
- **Download** any chart as PNG by clicking the camera icon in the top-right of each chart

---

## Tab 2: Attrition Analysis

Deep dive into why employees leave.

### Charts Included

1. **Exit Types** - Donut chart (Resigned / Terminated / Dropped)
2. **Exit Reason Categories** - Horizontal bar chart of reason categories
3. **Voluntary vs Involuntary Turnover** - KPI metrics + donut chart
4. **Attrition Rate by Department** - Color-coded bar chart (red = high attrition)
5. **Exit Reasons (Categorized)** - Bar chart using the 17-category Exit ReasonList
6. **Manager-Linked Attrition** - Shows which managers had the most departures under them

### Key Insights to Look For

- **High voluntary turnover** may indicate compensation or culture issues
- **High involuntary turnover** may indicate hiring quality problems
- **Manager-linked patterns** - if one manager consistently loses employees, it may warrant investigation
- **Department hotspots** - departments with attrition rates above the company average need attention

---

## Tab 3: Tenure & Retention

Analyzes how long employees stay and cohort-based retention.

### Charts Included

1. **Tenure Distribution** - Histogram split by Active/Departed with box plot
2. **Average Tenure by Department** - Bar chart with values
3. **Cohort Retention Analysis** - Combined stacked bar (Active/Departed) + line (Retention %) by join year
4. **Probation Analysis** - Donut chart of probation outcomes + pass rate by department
5. **Early Leavers** - Analysis of employees who left within 6 months

### KPI Metrics

- Min / Max / Avg / Median tenure displayed at the top

### Understanding Cohort Retention

The cohort chart shows retention by **join year**:
- Each bar represents a hiring cohort (year)
- Green = still active, Red = departed
- The blue line shows the retention rate percentage
- Newer cohorts typically show higher retention (less time to leave)

---

## Tab 4: Workforce Composition

Analyzes the structure and diversity of the workforce.

### Charts Included

1. **Employment Type Breakdown** - Donut chart (Full time vs Freelancer) + stacked bar by department
2. **Vendor / Source Analysis** - Donut chart of vendors + grouped bar by status + attrition rate table
3. **Position Changes After Joining** - Tracks employees whose role changed after onboarding
4. **Workforce Composition Over Time** - Area chart showing employment type mix by year

### Key Insights to Look For

- **Contractor dependency** - high freelancer ratio may indicate scaling challenges
- **Vendor performance** - compare attrition rates across vendors to identify quality sources
- **Position changes** - departments with many role changes may have unclear job descriptions

---

## Tab 5: Trends

Time-series analysis of hiring, attrition, and headcount.

### Charts Included

1. **Hiring Trend by Year** - Line chart of annual hires
2. **Attrition Trend by Year** - Line chart of annual exits
3. **Net Headcount Change** - Combined bar (hires up, exits down) + line (net change)
4. **Monthly Hiring Trend** - Bar chart of recent 24 months
5. **Headcount Summary by Year** - Stacked bar of Active/Departed by join year
6. **Hire-to-Exit Ratio** - Line chart with breakeven line at 1.0

### Understanding the Hire-to-Exit Ratio

- **Ratio > 1**: More hires than exits (growing workforce)
- **Ratio = 1**: Hires equal exits (stable workforce)
- **Ratio < 1**: More exits than hires (shrinking workforce)

---

## Tab 6: Employee Data

Searchable, exportable employee table.

### Features

| Feature | Description |
|---------|-------------|
| **Search** | Type a name to filter the table in real-time |
| **Column Selection** | Choose which columns to display using the multi-select dropdown |
| **Sorting** | Click any column header to sort ascending/descending |
| **CSV Export** | Click "Download Filtered Data as CSV" to export current view |
| **Statistics** | Numerical summary and category counts at the bottom |

### Available Columns

Full Name, Gender, Age, Nationality, Department, Position, Employment Type, Vendor, Employee Status, Join Date, Exit Date, Exit Type, Exit Reason Category, Exit Reason, Tenure (Months), Probation Completed, Position After Joining

### Exporting Data

1. Apply desired filters in the sidebar
2. Go to the Employee Data tab
3. Click **"Download Filtered Data as CSV"**
4. The file `hr_data_export.csv` will download with only the filtered records

---

## Tab 7: Edit Data (Editor/Admin Only)

This tab is **only visible** to users with `editor` or `admin` roles.

### Add New Employee

1. Select **"Add New Employee"** from the action radio buttons
2. Fill in the form fields:
   - Fields marked with **\*** are required
   - Full Name, Gender, Birthday Date, Department, Position, Employee Status, Join Date
   - If status is "Departed", Exit Date is required
3. Click **"Add Employee"**
4. **Refresh the page** to see the new record in all charts

### Edit Existing Employee

1. Select **"Edit Existing"** from the action radio buttons
2. **Search** for the employee by typing their name
3. Select the employee from the dropdown
4. Modify the fields as needed
5. Click **"Save Changes"**
6. **Refresh the page** to see updates

### Delete Employee Record

1. Select **"Delete Record"** from the action radio buttons
2. **Search** for the employee by typing their name
3. Select the employee from the dropdown
4. Review the employee details shown
5. **Check the confirmation box** ("I confirm I want to delete this record")
6. Click **"Delete Record"**
7. **Refresh the page** to see the removal

### Important Notes

- All changes are saved directly to `Master.xlsx`
- After any edit, **refresh the page** (F5) to update all charts and KPIs
- There is no undo - deleted records cannot be recovered
- Keep a backup of `Master.xlsx` before making bulk changes

---

## Data Upload

### Uploading a New Data File

1. In the sidebar, select **"Upload New File"** under Data Source
2. Click **"Browse files"** and select your `.xlsx` file
3. The dashboard will process and display the new data immediately
4. Uploaded data is temporary - it does not replace Master.xlsx

### Required Data Format

Your Excel file must contain these columns (at minimum):

| Column | Format | Example |
|--------|--------|---------|
| Full Name | Text | "Ahmed Mohamed" |
| Gender | M or F | "M" |
| Birthday Date | Date | 1990-05-15 |
| Department | Text | "HR" |
| Position | Text | "EA-L2" |
| Employee Status | Active or Departed | "Active" |
| Join Date (yyyy/mm/dd) | Date | 2023-01-15 |

### Optional Columns (for full functionality)

| Column | Enables |
|--------|---------|
| Exit Date yyyy/mm/dd | Attrition analysis |
| Exit Type | Voluntary/involuntary breakdown |
| Exit Reason Category | Reason analysis |
| Exit Reason | Detailed reason view |
| Type | Employment type analysis |
| Vendor | Vendor analysis |
| Nationality | Diversity metrics |
| Probation Period End Date | Probation analysis |
| Position (After Joining) | Position change tracking |
| Direct Manager CRM while Resignation | Manager attrition analysis |
| Exit ReasonList | Categorized exit reasons |

---

## Managing User Accounts

### Adding a New User

1. Generate a hashed password:
   ```python
   import streamlit_authenticator as stauth
   print(stauth.Hasher.hash('new_password_here'))
   ```

2. Edit `auth_config.yaml` and add under `credentials > usernames`:
   ```yaml
   new_username:
     name: Display Name
     password: $2b$12$...hashed_password_here...
     role: viewer   # or editor, admin
   ```

3. Restart the Streamlit app

### Removing a User

Delete the username block from `auth_config.yaml` and restart the app.

### Available Roles

| Role | View Dashboards | Export CSV | Edit/Add/Delete Records |
|------|:-:|:-:|:-:|
| **viewer** | Yes | Yes | No |
| **editor** | Yes | Yes | Yes |
| **admin** | Yes | Yes | Yes |

---

## Deployment to Streamlit Cloud

### Step-by-Step

1. Push your code to a GitHub repository:
   ```bash
   git add app.py data_processing.py auth_config.yaml requirements.txt Master.xlsx
   git commit -m "HR Dashboard v2"
   git push
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click **"New app"**

4. Select your GitHub repository, branch, and set `app.py` as the main file

5. Click **"Deploy"**

### Important Considerations

- **Secrets**: For production, move sensitive config (passwords, cookie key) to Streamlit secrets instead of `auth_config.yaml`
- **Data persistence**: On Streamlit Cloud, file edits (Master.xlsx) are temporary and reset on reboot. For persistent editing, migrate to a database (Supabase, Google Sheets)
- **The free tier** supports 1 app with unlimited viewers

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "No data loaded" | Master.xlsx missing or corrupted | Ensure Master.xlsx is in the same directory as app.py |
| Login not working | Wrong credentials | Check username/password, passwords are case-sensitive |
| Charts are empty | Filters too restrictive | Reset filters by refreshing the page |
| "Port is not available" | Another Streamlit instance running | Stop other instances or use `--server.port 8502` |
| Edit tab not visible | Logged in as viewer | Log out and log in as editor or admin |
| Changes not showing after edit | Page cache | Click F5 to refresh the page |
| Upload fails | Wrong file format | Ensure file is .xlsx format with required columns |

### Getting Help

- Check the sidebar **"Required Columns"** expander for data format requirements
- Refer to `DATA_DICTIONARY.md` for detailed column specifications
- For technical issues, check the terminal/console where Streamlit is running for error messages

---

## Keyboard Shortcuts (Plotly Charts)

| Shortcut | Action |
|----------|--------|
| Click + Drag | Zoom into area |
| Double-click | Reset zoom |
| Hover | See exact values |
| Click legend item | Toggle visibility |
| Camera icon | Download chart as PNG |
| Home icon | Reset axes |

---

*HR Analytics Dashboard v2.0 | Built with Streamlit & Plotly*
