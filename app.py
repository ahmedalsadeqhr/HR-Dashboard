import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from pathlib import Path

from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, detect_name_column
from src.data_processing import load_from_db, calculate_kpis
from src.db import fetch_last_upload
from src.utils import delta
from src.pages import analysis, employee_data

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="51Talk HR Analytics", page_icon="assets/logo.png", layout="wide")



# ===================== CUSTOM CSS =====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ======================================================
       DESIGN TOKENS
    ====================================================== */
    :root {
        --brand:        #0057B8;
        --brand-dark:   #003D80;
        --brand-light:  #E8F0FC;
        --accent:       #FFD100;
        --success:      #10B981;
        --danger:       #EF4444;
        --warning:      #F59E0B;
        --purple:       #8B5CF6;
        --sidebar-bg:   #0F172A;
        --sidebar-text: #CBD5E1;
        --sidebar-head: #F8FAFC;
        --bg:           #F1F5F9;
        --card:         #FFFFFF;
        --border:       #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary:#64748B;
        --text-muted:   #94A3B8;
    }

    /* ======================================================
       GLOBAL RESET
    ====================================================== */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        color: var(--text-primary);
    }

    /* Remove Streamlit default padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }

    /* Page background */
    [data-testid="stAppViewContainer"] > .main {
        background: var(--bg);
    }

    /* ======================================================
       DARK SIDEBAR
    ====================================================== */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--sidebar-text) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--sidebar-head) !important;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stFileUploader label {
        color: var(--sidebar-text) !important;
        font-weight: 500;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    /* Sidebar inputs */
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 1rem 0;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: var(--accent) !important;
        color: var(--sidebar-bg) !important;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        width: 100%;
        padding: 0.55rem 1rem;
        transition: opacity 0.15s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        opacity: 0.88;
    }
    [data-testid="stSidebar"] [data-testid="stCaption"],
    [data-testid="stSidebar"] small {
        color: var(--text-muted) !important;
    }

    /* ======================================================
       HEADER
    ====================================================== */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 0.5rem 0 1.25rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    .header-logo {
        height: 48px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,87,184,0.18);
    }
    .header-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .header-subtitle {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin: 2px 0 0 0;
        font-weight: 400;
    }
    .header-badge {
        margin-left: auto;
        background: var(--brand-light);
        color: var(--brand);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    /* ======================================================
       KPI CARDS
    ====================================================== */
    [data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--brand), #3B82F6);
        border-radius: 14px 14px 0 0;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,87,184,0.12);
    }
    [data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 800;
        font-size: 1.6rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Colour-coded top bar per card position */
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"]::before {
        background: linear-gradient(90deg, var(--success), #34D399);
    }
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"]::before {
        background: linear-gradient(90deg, var(--danger), #F87171);
    }
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"]::before {
        background: linear-gradient(90deg, var(--warning), #FCD34D);
    }

    /* ======================================================
       SECTION HEADING STYLE
    ====================================================== */
    h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: -0.01em;
        border-bottom: none !important;
        padding-bottom: 0 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    h2::before, h3::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 14px;
        background: var(--brand);
        border-radius: 2px;
        margin-right: 8px;
        vertical-align: middle;
    }

    /* ======================================================
       CHART CONTAINERS
    ====================================================== */
    [data-testid="stPlotlyChart"] {
        background: var(--card);
        border-radius: 14px;
        padding: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        transition: box-shadow 0.18s ease;
    }
    [data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 8px 24px rgba(0,87,184,0.09);
    }

    /* ======================================================
       TABS — pill style
    ====================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: none;
        background: var(--card);
        border-radius: 12px;
        padding: 6px;
        border: 1px solid var(--border);
        display: inline-flex;
        margin-bottom: 1.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 24px;
        color: var(--text-secondary);
        border-radius: 8px;
        border: none !important;
        transition: all 0.15s;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--brand);
        background: var(--brand-light);
    }
    .stTabs [aria-selected="true"] {
        color: var(--card) !important;
        background: var(--brand) !important;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,87,184,0.3);
    }

    /* ======================================================
       DIVIDERS
    ====================================================== */
    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: 1.75rem 0;
    }

    /* ======================================================
       DATAFRAMES
    ====================================================== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: 12px;
    }

    /* ======================================================
       BUTTONS
    ====================================================== */
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        background: var(--brand);
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 20px;
        transition: all 0.15s;
        letter-spacing: 0.01em;
    }
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: var(--brand-dark);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,87,184,0.3);
    }

    /* ======================================================
       FORMS & INPUTS
    ====================================================== */
    [data-testid="stForm"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 8px;
        border-color: var(--border);
        transition: border-color 0.15s, box-shadow 0.15s;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--brand);
        box-shadow: 0 0 0 3px rgba(0,87,184,0.12);
    }

    /* ======================================================
       ALERTS
    ====================================================== */
    .stAlert {
        border-radius: 10px;
    }

    /* ======================================================
       FILTER BADGE
    ====================================================== */
    .filter-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--brand-light);
        border: 1px solid rgba(0,87,184,0.2);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--brand);
        margin-bottom: 1rem;
    }
    .filter-badge::before {
        content: '⚙';
        font-size: 0.7rem;
    }

    /* ======================================================
       SIDEBAR LOGO
    ====================================================== */
    .sidebar-logo-container {
        text-align: center;
        padding: 1.25rem 0 1rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.5rem;
    }
    .sidebar-logo {
        height: 44px;
        border-radius: 8px;
    }

    /* ======================================================
       HEADER (fallback no-logo version)
    ====================================================== */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
    }
    .welcome-container h2 {
        color: var(--text-primary) !important;
        border: none !important;
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
    }
    .welcome-container p {
        color: var(--text-secondary);
        font-size: 1rem;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ======================================================
       FOOTER
    ====================================================== */
    .footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.78rem;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 1px solid var(--border);
        margin-top: 2.5rem;
    }
    .footer strong { color: var(--brand); }
    .footer a { color: var(--brand); text-decoration: none; }

    /* ======================================================
       KPI SECTION LABEL
    ====================================================== */
    .kpi-section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .kpi-section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* ======================================================
       RADIO TOGGLE
    ====================================================== */
    .stRadio > div { gap: 0 !important; }
    .stRadio [role="radiogroup"] label {
        background: var(--card);
        border: 1px solid var(--border);
        padding: 7px 18px;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.15s;
        cursor: pointer;
    }
    .stRadio [role="radiogroup"] label:first-of-type { border-radius: 8px 0 0 8px; }
    .stRadio [role="radiogroup"] label:last-of-type  { border-radius: 0 8px 8px 0; }
    .stRadio [role="radiogroup"] label[data-checked="true"] {
        background: var(--brand);
        color: #FFFFFF !important;
        border-color: var(--brand);
    }
    </style>
    """, unsafe_allow_html=True)


load_css()

# ===================== LOGO HEADER =====================
logo_path = Path(__file__).parent / "assets" / "logo.png"


@st.cache_data
def _encode_logo(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


if logo_path.exists():
    logo_b64 = _encode_logo(logo_path)
    st.markdown(f"""
    <div class="header-container">
        <img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="51Talk">
        <div>
            <p class="header-title">HR Analytics</p>
            <p class="header-subtitle">Workforce Intelligence &amp; People Analytics</p>
        </div>
        <span class="header-badge">Live Data</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-container">
        <div>
            <p class="header-title">HR Analytics</p>
            <p class="header-subtitle">Workforce Intelligence &amp; People Analytics</p>
        </div>
        <span class="header-badge">Live Data</span>
    </div>
    """, unsafe_allow_html=True)

# ===================== SIDEBAR LOGO =====================
if logo_path.exists():
    st.sidebar.markdown(f"""
    <div class="sidebar-logo-container">
        <img src="data:image/png;base64,{logo_b64}" class="sidebar-logo" alt="51Talk">
    </div>
    """, unsafe_allow_html=True)

# ===================== DATA LOADING =====================
st.sidebar.header("Data Source")

df = load_from_db()

# Show last updated badge in sidebar
last = fetch_last_upload()
if last:
    st.sidebar.caption(
        f"Last updated: {last['uploaded_at'][:10]} by {last['uploaded_by']} ({last['row_count']:,} rows)"
    )
else:
    st.sidebar.caption("No data uploaded yet. Go to the Upload page.")

if df.empty:
    st.warning("No employee data found. Please upload a Master Sheet via the Upload page.")
    st.stop()

NAME_COL = detect_name_column(df)

# ===================== SIDEBAR FILTERS =====================
st.sidebar.markdown("---")
st.sidebar.header("Filters")

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

if date_range is not None and isinstance(date_range, tuple):
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Join Date'].dt.date >= date_range[0]) &
            (filtered_df['Join Date'].dt.date <= date_range[1])
        ]
    else:
        st.warning("Please select both a start and end date for the Join Date Range filter.")

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

st.markdown('<div class="kpi-section-label">Key Performance Indicators</div>', unsafe_allow_html=True)

if len(filtered_df) < len(df):
    st.markdown(
        f'<div class="filter-badge">Showing {len(filtered_df):,} of {len(df):,} records &mdash; deltas vs. full dataset</div>',
        unsafe_allow_html=True
    )

row1 = st.columns(4)
row1[0].metric("Total Employees", f"{kpis['total']:,}")
row1[1].metric("Active Employees", f"{kpis['active']:,}")
row1[2].metric("Departed", f"{kpis['departed']:,}")
row1[3].metric("Departure Rate", f"{kpis['attrition_rate']:.1f}%",
               delta=delta(kpis['attrition_rate'], kpis_all['attrition_rate'], '%', len(filtered_df), len(df)),
               delta_color="inverse")

st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

row2 = st.columns(4)
row2[0].metric("Retention Rate", f"{kpis['retention_rate']:.1f}%",
               delta=delta(kpis['retention_rate'], kpis_all['retention_rate'], '%', len(filtered_df), len(df)))
row2[1].metric("Avg Tenure (Mo)", f"{kpis['avg_tenure']:.1f}",
               delta=delta(kpis['avg_tenure'], kpis_all['avg_tenure'], '', len(filtered_df), len(df)))
row2[2].metric("Average Age", f"{kpis['avg_age']:.0f}" if not pd.isna(kpis['avg_age']) else "N/A")
row2[3].metric("Gender Ratio (M:F)", kpis['gender_ratio'])

st.markdown("---")

# ===================== TABS =====================
tabs = st.tabs(["Analysis", "Employee Data"])

with tabs[0]:
    analysis.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

with tabs[1]:
    employee_data.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)

# ===================== FOOTER =====================
st.markdown("""
<div class="footer">
    <strong>51Talk</strong> HR Analytics &nbsp;&middot;&nbsp; Workforce Intelligence Platform &nbsp;&middot;&nbsp; Built with Streamlit &amp; Plotly
</div>
""", unsafe_allow_html=True)
