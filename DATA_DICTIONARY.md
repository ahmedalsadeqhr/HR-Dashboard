# Data Dictionary

This document describes the required columns and data formats for the HR Analytics Dashboard.

---

## Required Columns

### Employee Information

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `Full Name` | Text | Yes | Employee's full name | "Ahmed Mohamed" |
| `Gender` | Text | Yes | M or F | "M" |
| `Birthday Date` | Date | Yes | Date of birth | 1990-05-15 |
| `Nationality` | Text | No | Employee nationality | "Egypt" |
| `Identity number` | Number | No | National ID number | 29001234567890 |

### Position & Department

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `Department` | Text | Yes | Department code/name | "EA", "CM", "HR" |
| `Position` | Text | Yes | Job title | "EA-L2", "CM-L1" |
| `Position (After Joining)` | Text | No | Position after probation | "EA-L2" |

### Employment Status

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `Employee Status` | Text | Yes | Current status | "Active" or "Departed" |
| `Type` | Text | No | Employment type | "Full time", "Freelancer" |
| `Vendor` | Text | No | Vendor/contractor name | "CompanyX" |

### Dates

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `Join Date (yyyy/mm/dd)` | Date | Yes | Employment start date | 2023-01-15 |
| `Exit Date yyyy/mm/dd` | Date | No* | Employment end date | 2024-06-30 |
| `Probation Period End Date` | Date | No | Probation end date | 2023-04-15 |

*Required if Employee Status = "Departed"

### Exit Information

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `Exit Type` | Text | No* | Type of departure | "Resigned", "Terminated", "Dropped" |
| `Exit Reason Category` | Text | No* | Category of exit reason | "Personal Reasons", "Performance Issues" |
| `Exit Reason` | Text | No | Detailed exit reason | "Found better opportunity" |

*Required if Employee Status = "Departed"

### Other Fields

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `PS ID` | Number | No | Payroll System ID | 12345 |
| `CRM` | Text | No | CRM identifier | "CRM001" |
| `Work Email address` | Text | No | Work email | "ahmed@company.com" |
| `Direct Manager CRM while Resignation` | Text | No | Manager's CRM ID | "MGR001" |
| `Remark` | Text | No | Additional notes | "Transferred from..." |

---

## Data Values

### Employee Status

| Value | Description |
|-------|-------------|
| `Active` | Currently employed |
| `Departed` | No longer employed |

### Gender

| Value | Description |
|-------|-------------|
| `M` | Male |
| `F` | Female |

### Exit Type

| Value | Description |
|-------|-------------|
| `Resigned` | Voluntary departure |
| `Terminated` | Involuntary departure (fired) |
| `Dropped` | Left during probation/training |

### Exit Reason Category

| Value | Description |
|-------|-------------|
| `Personal Reasons` | Family, health, relocation, etc. |
| `Career & Growth` | Better opportunity, career change |
| `Performance Issues` | Performance-related termination |
| `Training Fail` | Failed to pass training |
| `Failed Probation` | Did not pass probation period |
| `No Show` | Did not show up for work |
| `Misconduct & Compliance` | Policy violations |
| `Work Environment & Culture` | Workplace issues |
| `Management Issues` | Problems with management |
| `Business Restructuring` | Layoffs, restructuring |
| `Job Content Mismatch` | Role not as expected |
| `Other` | Other reasons |

### Department Codes

| Code | Description |
|------|-------------|
| `EA` | Executive Assistant |
| `CM` | Community Manager |
| `CC` | Customer Care |
| `TMK` | Telemarketing |
| `TA` | Talent Acquisition |
| `HR` | Human Resources |
| `AI` | Artificial Intelligence |
| `IT` | Information Technology |
| `Admin` | Administration |
| `Training` | Training Department |
| `Operations` | Operations |
| `Marketing` | Marketing |
| `Legal` | Legal Department |

---

## Date Formats

The application accepts multiple date formats:

| Format | Example |
|--------|---------|
| YYYY-MM-DD | 2023-01-15 |
| YYYY/MM/DD | 2023/01/15 |
| DD/MM/YYYY | 15/01/2023 |
| MM/DD/YYYY | 01/15/2023 |
| Excel Date | 44941 (serial number) |

**Recommendation:** Use YYYY-MM-DD format for consistency.

---

## Calculated Fields

These fields are automatically calculated by the application:

| Field | Calculation | Description |
|-------|-------------|-------------|
| `Age` | (Today - Birthday Date) / 365.25 | Employee age in years |
| `Tenure (Months)` | (Exit Date or Today - Join Date) / 30.44 | Employment duration in months |
| `Join Year` | Year from Join Date | Year of joining |
| `Join Month` | Year-Month from Join Date | Month of joining (YYYY-MM) |
| `Exit Year` | Year from Exit Date | Year of departure |
| `Exit Month` | Year-Month from Exit Date | Month of departure (YYYY-MM) |

---

## Sample Data

### Minimum Required Columns

```csv
Full Name,Gender,Birthday Date,Department,Position,Employee Status,Join Date (yyyy/mm/dd)
Ahmed Mohamed,M,1990-05-15,EA,EA-L2,Active,2023-01-15
Sara Ahmed,F,1995-03-20,CM,CM-L1,Departed,2022-06-01
```

### Full Data Example

```csv
Full Name,Gender,Birthday Date,Department,Position,Employee Status,Join Date (yyyy/mm/dd),Exit Date yyyy/mm/dd,Exit Type,Exit Reason Category,Exit Reason
Ahmed Mohamed,M,1990-05-15,EA,EA-L2,Active,2023-01-15,,,
Sara Ahmed,F,1995-03-20,CM,CM-L1,Departed,2022-06-01,2024-01-15,Resigned,Career & Growth,Found better opportunity
Mohamed Ali,M,1988-11-10,CC,CC,Departed,2023-03-01,2023-05-15,Terminated,Performance Issues,Failed to meet targets
```

---

## Data Validation Rules

### Required Fields Validation

| Rule | Description |
|------|-------------|
| Full Name cannot be empty | Every row must have a name |
| Gender must be M or F | Only these values accepted |
| Employee Status must be Active or Departed | Only these values accepted |
| Join Date cannot be empty | Every employee must have a join date |
| Exit Date required for Departed | If status is Departed, exit date is needed |

### Data Quality Checks

| Check | Description |
|-------|-------------|
| Join Date < Exit Date | Exit date must be after join date |
| Birthday Date < Join Date | Employee must be born before joining |
| Age >= 18 | Employees must be 18+ |
| No future Join Dates | Join date should not be in the future |

---

## Column Name Variations

The application handles these column name variations:

| Standard Name | Also Accepts |
|---------------|--------------|
| `Join Date (yyyy/mm/dd)` | `Join Date`, `JoinDate`, `Joining Date` |
| `Exit Date yyyy/mm/dd` | `Exit Date`, `ExitDate`, `Leaving Date` |
| `Employee Status` | `Status`, `Employment Status` |
| `Full Name` | `Name`, `Employee Name` |

**Note:** Column names are case-sensitive. Use exact names for best results.

---

## Troubleshooting Data Issues

### Common Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| Missing employees | Empty rows in Excel | Remove blank rows |
| Wrong age calculations | Invalid birth dates | Check date format |
| 0 tenure | Missing join date | Add join dates |
| Charts empty | All data filtered out | Reset filters |
| Upload fails | Wrong file format | Use .xlsx format |

### Data Cleaning Checklist

- [ ] Remove blank rows
- [ ] Standardize Gender values (M/F)
- [ ] Standardize Employee Status (Active/Departed)
- [ ] Check date formats
- [ ] Fill Exit Date for Departed employees
- [ ] Fill Exit Type for Departed employees
- [ ] Remove special characters from names
