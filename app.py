import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from pathlib import Path

from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, detect_name_column
from src.data_processing import load_excel, calculate_kpis
from src.utils import delta
from src.pages import analysis, employee_data

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="51Talk HR Analytics", page_icon="assets/logo.png", layout="wide")


# ===================== CUSTOM CSS =====================
def load_css():
    st.markdown("""
    <style>
    /* ---- Global ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ---- Header with logo ---- */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 0.5rem 0 1rem 0;
    }
    .header-logo {
        height: 52px;
        border-radius: 8px;
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0057B8;
        margin: 0;
        line-height: 1.2;
    }
    .header-subtitle {
        font-size: 0.85rem;
        color: #6C757D;
        margin: 0;
    }

    /* ---- Sidebar branding ---- */
    [data-testid="stSidebar"] {
        background: #F4F6F8;
        border-right: 1px solid #E2E6EA;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0057B8 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stFileUploader label {
        color: #495057 !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] hr {
        border-color: #DEE2E6;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #0057B8;
        color: #FFFFFF !important;
        font-weight: 600;
        border: none;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #003D80;
    }

    /* ---- KPI Cards ---- */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-left: 4px solid #0057B8;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: transform 0.15s, box-shadow 0.15s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,87,184,0.12);
    }
    [data-testid="stMetric"] label {
        color: #6C757D !important;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0057B8 !important;
        font-weight: 700;
        font-size: 1.5rem;
    }

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #E9ECEF;
        background: #FFFFFF;
        border-radius: 8px 8px 0 0;
        padding: 0 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
        padding: 12px 32px;
        color: #6C757D;
        border-bottom: 3px solid transparent;
        transition: color 0.15s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0057B8;
    }
    .stTabs [aria-selected="true"] {
        color: #0057B8 !important;
        border-bottom: 3px solid #FFD100 !important;
        background: transparent;
    }

    /* ---- Section headers ---- */
    h2, h3 {
        color: #0057B8 !important;
        border-bottom: 2px solid #FFD100;
        padding-bottom: 6px;
        margin-top: 1.5rem;
    }

    /* ---- Dividers ---- */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #CFD8DC, #FFD100, #CFD8DC, transparent);
        margin: 2rem 0;
    }

    /* ---- DataFrames ---- */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E9ECEF;
    }

    /* ---- Main content buttons ---- */
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        background-color: #0057B8;
        color: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 20px;
        transition: background-color 0.15s, transform 0.1s;
    }
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #003D80;
        transform: translateY(-1px);
    }
    .stDownloadButton > button:active,
    .stFormSubmitButton > button:active {
        transform: translateY(0);
    }

    /* ---- Radio buttons (mode selector) ---- */
    .stRadio > div {
        gap: 0 !important;
    }
    .stRadio [role="radiogroup"] {
        gap: 0;
    }
    .stRadio [role="radiogroup"] label {
        background: #FFFFFF;
        border: 1px solid #DEE2E6;
        padding: 8px 18px;
        font-weight: 500;
        font-size: 0.88rem;
        transition: all 0.15s;
        cursor: pointer;
    }
    .stRadio [role="radiogroup"] label:first-of-type {
        border-radius: 6px 0 0 6px;
    }
    .stRadio [role="radiogroup"] label:last-of-type {
        border-radius: 0 6px 6px 0;
    }
    .stRadio [role="radiogroup"] label[data-checked="true"] {
        background: #0057B8;
        color: #FFFFFF !important;
        border-color: #0057B8;
    }

    /* ---- Alerts ---- */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    [data-testid="stAlert"][data-baseweb*="notification"] {
        border-radius: 8px;
    }

    /* ---- Forms ---- */
    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }

    /* ---- Text inputs ---- */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #DEE2E6;
        transition: border-color 0.15s, box-shadow 0.15s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0057B8;
        box-shadow: 0 0 0 2px rgba(0,87,184,0.15);
    }

    /* ---- Plotly chart containers ---- */
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        border: 1px solid #F0F0F0;
        margin-bottom: 0.5rem;
        transition: box-shadow 0.15s;
    }
    [data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 3px 10px rgba(0,87,184,0.08);
    }

    /* ---- Footer ---- */
    .footer {
        text-align: center;
        color: #6C757D;
        font-size: 0.8rem;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 2px solid #FFD100;
        margin-top: 2rem;
    }
    .footer a { color: #0057B8; text-decoration: none; }

    /* ---- Welcome screen ---- */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
    }
    .welcome-container img {
        height: 80px;
        margin-bottom: 1.5rem;
        border-radius: 12px;
    }
    .welcome-container h2 {
        color: #0057B8 !important;
        border: none !important;
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
    }
    .welcome-container p {
        color: #6C757D;
        font-size: 1rem;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ---- Sidebar logo ---- */
    .sidebar-logo-container {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .sidebar-logo {
        height: 48px;
        border-radius: 8px;
    }

    /* ---- Filter record count badge ---- */
    .filter-badge {
        background: rgba(255,209,0,0.2);
        border: 1px solid rgba(255,209,0,0.5);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #0057B8;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


load_css()

# ===================== LOGO HEADER =====================
logo_path = Path(__file__).parent / "assets" / "logo.png"
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.markdown(f"""
    <div class="header-container">
        <img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="51Talk">
        <div>
            <p class="header-title">HR Analytics Dashboard</p>
            <p class="header-subtitle">Workforce Intelligence & People Analytics</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("HR Analytics Dashboard")

# ===================== SIDEBAR LOGO =====================
if logo_path.exists():
    st.sidebar.markdown(f"""
    <div class="sidebar-logo-container">
        <img src="data:image/png;base64,{logo_b64}" class="sidebar-logo" alt="51Talk">
    </div>
    """, unsafe_allow_html=True)

# ===================== DATA LOADING =====================
st.sidebar.header("Data Source")

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
    if logo_path.exists():
        st.markdown(f"""
        <div class="welcome-container">
            <img src="data:image/png;base64,{logo_b64}" alt="51Talk">
            <h2>Welcome to HR Analytics</h2>
            <p>Upload your Master Sheet (.xlsx) using the sidebar to get started with workforce intelligence and people analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No data loaded. Please upload the Master Sheet to get started.")
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

if len(filtered_df) < len(df):
    st.markdown(
        f'<div class="filter-badge">Showing {len(filtered_df):,} of {len(df):,} records &mdash; deltas vs. full dataset</div>',
        unsafe_allow_html=True
    )

row1 = st.columns(4)
row1[0].metric("Total Employees", f"{kpis['total']:,}")
row1[1].metric("Active", f"{kpis['active']:,}")
row1[2].metric("Departed", f"{kpis['departed']:,}")
row1[3].metric("Attrition Rate", f"{kpis['attrition_rate']:.1f}%",
               delta=delta(kpis['attrition_rate'], kpis_all['attrition_rate'], '%', len(filtered_df), len(df)),
               delta_color="inverse")

row2 = st.columns(4)
row2[0].metric("Retention Rate", f"{kpis['retention_rate']:.1f}%",
               delta=delta(kpis['retention_rate'], kpis_all['retention_rate'], '%', len(filtered_df), len(df)))
row2[1].metric("Avg Tenure (Mo)", f"{kpis['avg_tenure']:.1f}",
               delta=delta(kpis['avg_tenure'], kpis_all['avg_tenure'], '', len(filtered_df), len(df)))
row2[2].metric("Avg Age", f"{kpis['avg_age']:.0f}" if not pd.isna(kpis['avg_age']) else "N/A")
row2[3].metric("Gender (M:F)", kpis['gender_ratio'])

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
    <strong>51Talk</strong> HR Analytics Dashboard &middot; Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
