# HR Analytics Dashboard — User Guide

Welcome to the HR Analytics Dashboard! This guide walks you through every feature so you can get insights from your workforce data quickly and confidently.

---

## Getting Started

### Uploading Your Data

The dashboard works with your HR Master Sheet (.xlsx or .xls file).

1. Open the app in your browser.
2. In the **left sidebar**, under **Data Source**, click **Browse files**.
3. Select your Master Sheet Excel file.
4. Once uploaded, you'll see a green confirmation message showing how many records were loaded.

> Your data stays in your browser session only — it is never stored on any server. If you refresh the page, you will need to re-upload your file.

---

## The Sidebar — Filters

All filters live in the left sidebar and apply instantly across every chart and metric on the page. You can combine multiple filters together to drill into any segment of your workforce.

| Filter | What it does |
|--------|-------------|
| **Join Date Range** | Show only employees who joined between two dates. Select both a start and end date. |
| **Department** | Select one or more departments. All departments are selected by default. |
| **Employee Status** | Filter by Active, Departed, or All employees. |
| **Gender** | Filter by a specific gender or view All. |
| **Employment Type** | Filter by employment type (e.g. full-time, part-time) if available in your data. |
| **Nationality** | Filter by nationality if available in your data. |
| **Exit Type** | Filter departed employees by how they left (Resigned, Terminated, Dropped). |

**Reset All Filters** — Click this button at the top of the filters section to clear every filter and return to the full dataset.

When filters are active, a badge appears at the top of the dashboard showing how many records are currently displayed vs. the full dataset. The KPI delta indicators also show how the filtered group compares to the full workforce.

---

## Key Performance Indicators (KPIs)

Eight headline metrics sit at the top of the page so you always have a quick pulse on your workforce.

| Metric | Description |
|--------|-------------|
| **Total Employees** | Total number of records in the filtered view. |
| **Active** | Employees currently active. |
| **Departed** | Employees who have left. |
| **Departure Rate** | Departed ÷ Total employees, shown as a percentage. |
| **Retention Rate** | Active ÷ Total employees, shown as a percentage. |
| **Avg Tenure (Mo)** | Average months of employment across the filtered group. |
| **Avg Age** | Average employee age. |
| **Gender (M:F)** | Ratio of male to female employees. |

When a filter is active, each metric shows a small **delta arrow** comparing the filtered group to the full dataset — a quick way to spot how a department or cohort differs from the company overall.

---

## Analysis Tab

The Analysis tab is a scrollable dashboard containing six sections of charts and tables.

### 1. Overview

A snapshot of your workforce composition.

- **Gender Distribution** — Pie chart of gender breakdown.
- **Employee Status** — Pie chart of Active vs. Departed split.
- **Department Breakdown** — Bar chart showing headcount per department.
- **Age Distribution** — Histogram showing the spread of employee ages.

### 2. Attrition & Departure Analysis

Understand why and how employees leave.

- **Exit Types** — Breakdown of Resigned / Terminated / Dropped.
- **Exit Reason Categories** — The specific reasons employees gave for leaving.
- **Voluntary vs. Involuntary Turnover** — Compare resignations (voluntary) against terminations and drops (involuntary).
- **Departure Rate by Department** — Which departments have the highest departure rates.
- **Exit Reasons (Categorized)** — A detailed look at categorized exit reasons.
- **Manager-Linked Attrition** — Departure rates grouped by reporting manager, useful for identifying management risk.

### 3. Tenure & Retention

How long do employees stay?

- **Tenure Distribution** — Histogram of how many months employees stayed before leaving or their current tenure.
- **Average Tenure by Department** — Which departments retain people longest.
- **Early Leavers (Left within 3 months)** — Employees who departed within their first 90 days — a key indicator of onboarding and fit issues.

### 4. Workforce Composition

Understand how your workforce is built.

- **Vendor / Source Analysis** — Where employees were sourced from (recruitment agency, referral, direct, etc.).
- **Position Changes After Joining** — Employees who changed roles after their initial hire, indicating internal mobility.

### 5. Hiring & Departure Trends

Track changes in your workforce over time.

- **Hiring Trend by Month** — Monthly new hire volume — spot seasonal hiring patterns.
- **Departure Trend by Month** — Monthly departure volume — identify problem periods.
- **Headcount Summary by Year** — Annual hired vs. departed vs. net headcount change.
- **Hire-to-Exit Ratio by Year** — For every person hired, how many left? A ratio below 1 means more people left than joined.

### 6. Advanced Analytics

Deeper metrics for HR professionals.

- **New Hire 90-Day Retention** — By department, the percentage of new hires who stayed beyond 90 days. A critical early-warning metric.
- **Rolling Turnover Rate** — Turnover rate tracked over time. Toggle between **Monthly** and **Quarterly** views using the selector above the chart.

---

## Employee Data Tab

The Employee Data tab lets you view, search, add, edit, and delete individual employee records.

### View Data

The default mode shows the full filtered employee table. Three export options are available:

| Button | What you get |
|--------|-------------|
| **Download as CSV** | A .csv file of the currently filtered data. |
| **Download as Excel** | A .xlsx file of the currently filtered data. |
| **Download Summary Report** | A plain-text summary report with key KPIs and breakdowns. |

### Add Employee

Switch to **Add Employee** mode using the radio buttons at the top of the tab. Fill in the form fields and click **Add Employee**. After adding, you will see a **Download updated data as Excel** button — download this file to save your changes permanently.

> Important: Changes are held in your browser session. Download the updated Excel file after every edit session to preserve your work.

### Edit Employee

Switch to **Edit Employee** mode. Search for an employee by name, PS ID, CRM number, or National ID. Select the employee from the dropdown, update the fields in the form, and click **Save Changes**. Download the updated Excel file that appears to keep the changes.

### Delete Employee

Switch to **Delete Employee** mode. Search for and select the employee you want to remove. Review their details, tick the confirmation checkbox, then click **Delete Record**. Download the updated Excel file to save the change.

---

## Tips & Best Practices

- **Always download after editing.** The dashboard holds your changes in memory during your session, but they are not saved automatically. Use the download buttons after adding, editing, or deleting records, then re-upload the downloaded file next time.
- **Use filters before exporting.** The CSV and Excel exports include only the currently filtered data — great for sending department-specific reports.
- **Combine filters for deeper insight.** For example, filter to a specific department + "Departed" status + a date range to analyze a department's attrition over a specific period.
- **Check the delta indicators.** The small arrows on each KPI card quickly show whether a filtered group is above or below the company average.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing required columns" error on upload | Your file may use different column names. Check the Data Dictionary for the expected column names. |
| Charts are empty after filtering | Your filter combination may have returned zero records. Try loosening one of the filters. |
| Date range filter shows a warning | You need to select both a start date and an end date for the range to apply. |
| Changes disappeared after refresh | The session was reset. Re-upload your last downloaded Excel file to restore your data. |
| A chart is missing (e.g. Vendor Analysis) | That chart only appears if the relevant column (e.g. Vendor/Source) exists in your data. |
