# HR Analytics Dashboard

A comprehensive HR Analytics Dashboard built with Streamlit for analyzing employee data, attrition, tenure, and workforce trends.

## Live Demo

**URL:** https://hr-dashboard-51talk.streamlit.app

---

## Features

### Key Metrics (KPIs)
- Total Employees
- Active Employees
- Departed Employees
- Attrition Rate
- Average Tenure
- Average Age

### Analysis Tabs

| Tab | Description |
|-----|-------------|
| **Overview** | Gender distribution, Employee status, Department & Position breakdown, Age distribution |
| **Attrition Analysis** | Exit types, Exit reasons, Voluntary vs Involuntary turnover, Attrition by department |
| **Tenure Analysis** | Tenure distribution, Tenure by department, Early leavers analysis |
| **Trends** | Hiring trends, Attrition trends, Monthly patterns, Headcount analysis |
| **Employee Data** | Searchable table, Column selector, CSV export |

### Data Management
- **Default Data:** Uses Master.xlsx from the repository
- **Upload Feature:** Users can upload updated Excel files directly in the app

---

## Project Structure

```
HC Analysis/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── Master.xlsx             # Default HR data file
├── README.md               # This file
├── DOCUMENTATION.md        # Technical documentation
├── DATA_DICTIONARY.md      # Data column specifications
└── app_full_backup.py      # Backup of full Plotly version
```

---

## Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ahmedalsadeqhr/HR-Dashboard.git
   cd HR-Dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. **Open browser:** http://localhost:8501

### Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy

---

## Updating Data

### Option 1: Upload in App (Recommended)
1. Open the dashboard
2. Select "Upload New File" in sidebar
3. Upload your Excel file
4. Dashboard updates instantly

### Option 2: Replace Master.xlsx
1. Update Master.xlsx locally
2. Push to GitHub:
   ```bash
   git add Master.xlsx
   git commit -m "Update HR data"
   git push
   ```
3. Streamlit Cloud auto-redeploys

---

## Requirements

- Python 3.8+
- streamlit
- pandas
- openpyxl
- numpy

---

## Support

For issues or feature requests, contact the HR Analytics team.

---

## License

Internal use only.
