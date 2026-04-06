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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ======================================================
       DESIGN TOKENS  — Dark Neon Theme
    ====================================================== */
    :root {
        /* Brand / accent */
        --purple:       #7C3AED;
        --purple-light: #A78BFA;
        --cyan:         #06B6D4;
        --cyan-light:   #67E8F9;
        --magenta:      #D946EF;
        --green:        #10B981;
        --amber:        #F59E0B;
        --danger:       #EF4444;

        /* Gradients */
        --grad-purple:  linear-gradient(135deg, #7C3AED 0%, #D946EF 100%);
        --grad-cyan:    linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
        --grad-green:   linear-gradient(135deg, #10B981 0%, #06B6D4 100%);
        --grad-amber:   linear-gradient(135deg, #F59E0B 0%, #EF4444 100%);

        /* Backgrounds */
        --bg:           #0D0E1A;
        --bg-card:      #161728;
        --bg-card2:     #1E1F35;
        --bg-hover:     #222340;

        /* Sidebar */
        --sidebar-bg:   #0A0B15;
        --sidebar-active: rgba(124,58,237,0.25);
        --sidebar-border: rgba(124,58,237,0.35);

        /* Text */
        --text-primary:   #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted:     #475569;

        /* Borders / dividers */
        --border:       rgba(255,255,255,0.07);
        --border-glow:  rgba(124,58,237,0.4);
    }

    /* ======================================================
       GLOBAL
    ====================================================== */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif !important;
        color: var(--text-primary);
    }
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max-width: 1440px !important;
    }
    /* Full-page dark background */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    .stApp {
        background: var(--bg) !important;
    }

    /* ======================================================
       SIDEBAR — deep dark with purple glow
    ====================================================== */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-secondary) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        border-bottom: none !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stSidebar"] h2::before,
    [data-testid="stSidebar"] h3::before {
        display: none !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-baseweb="base-input"] {
        background: var(--bg-card2) !important;
        border-color: var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
        margin: 1.1rem 0 !important;
    }
    /* Reset button — amber/yellow pill */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #7C3AED, #D946EF) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100% !important;
        padding: 0.5rem 1rem !important;
        letter-spacing: 0.03em !important;
        transition: opacity 0.15s !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover { opacity: 0.85 !important; }
    [data-testid="stSidebar"] [data-testid="stCaption"],
    [data-testid="stSidebar"] small {
        color: var(--text-muted) !important;
        font-size: 0.7rem !important;
    }

    /* ======================================================
       HEADER
    ====================================================== */
    .header-container {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 0.4rem 0 1.2rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    .header-logo {
        height: 46px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(124,58,237,0.4);
    }
    .header-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #A78BFA, #67E8F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header-subtitle {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin: 3px 0 0 0;
        font-weight: 400;
    }
    .header-badge {
        margin-left: auto;
        background: rgba(16,185,129,0.15);
        border: 1px solid rgba(16,185,129,0.35);
        color: #10B981;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .header-badge::before {
        content: '●';
        font-size: 0.5rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.3; }
    }

    /* ======================================================
       KPI SECTION LABEL
    ====================================================== */
    .kpi-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .kpi-section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* ======================================================
       KPI CARDS — dark glass with gradient accent
    ====================================================== */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px 22px 18px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s;
    }
    /* Gradient left stripe */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 3px;
        background: var(--grad-purple);
        border-radius: 16px 0 0 16px;
    }
    /* Faint glow blob in corner */
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: -30px; right: -30px;
        width: 100px; height: 100px;
        background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: var(--border-glow);
        box-shadow: 0 8px 32px rgba(124,58,237,0.2);
    }
    [data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 800;
        font-size: 1.7rem;
        letter-spacing: -0.03em;
        line-height: 1.15;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-size: 0.75rem;
        font-weight: 600;
    }
    /* Colour-code per column: purple / cyan / magenta / amber */
    [data-testid="column"]:nth-child(1) [data-testid="stMetric"]::before { background: var(--grad-purple); }
    [data-testid="column"]:nth-child(1) [data-testid="stMetric"]::after  { background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%); }
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"]::before { background: var(--grad-cyan); }
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"]::after  { background: radial-gradient(circle, rgba(6,182,212,0.15) 0%, transparent 70%); }
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"]::before { background: var(--grad-amber); }
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"]::after  { background: radial-gradient(circle, rgba(239,68,68,0.12) 0%, transparent 70%); }
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"]::before { background: var(--grad-green); }
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"]::after  { background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%); }

    /* ======================================================
       SECTION HEADINGS
    ====================================================== */
    h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.01em !important;
        border-bottom: none !important;
        padding-bottom: 0 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.6rem !important;
    }
    h2::before, h3::before {
        content: '';
        display: inline-block;
        width: 3px;
        height: 12px;
        background: var(--grad-purple);
        border-radius: 2px;
        margin-right: 8px;
        vertical-align: middle;
    }

    /* ======================================================
       CHART CONTAINERS — dark glass cards
    ====================================================== */
    [data-testid="stPlotlyChart"] {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    [data-testid="stPlotlyChart"]:hover {
        border-color: rgba(124,58,237,0.3);
        box-shadow: 0 4px 24px rgba(124,58,237,0.12);
    }

    /* ======================================================
       TABS — pill, dark
    ====================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: none;
        background: var(--bg-card);
        border-radius: 12px;
        padding: 5px;
        border: 1px solid var(--border);
        display: inline-flex;
        margin-bottom: 1.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.82rem;
        padding: 8px 22px;
        color: var(--text-secondary);
        border-radius: 8px;
        border: none !important;
        background: transparent;
        transition: all 0.15s;
        letter-spacing: 0.02em;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--purple-light);
        background: rgba(124,58,237,0.12);
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        background: var(--grad-purple) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 12px rgba(124,58,237,0.4) !important;
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
       DATAFRAMES — dark style
    ====================================================== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border) !important;
    }

    /* ======================================================
       BUTTONS
    ====================================================== */
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        background: var(--grad-purple);
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.83rem;
        padding: 8px 20px;
        transition: all 0.15s;
        letter-spacing: 0.02em;
    }
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        opacity: 0.88;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(124,58,237,0.35);
    }

    /* ======================================================
       FORMS & INPUTS
    ====================================================== */
    [data-testid="stForm"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
    }
    .stTextInput > div > div > input {
        background: var(--bg-card2) !important;
        border-color: var(--border) !important;
        border-radius: 8px;
        color: var(--text-primary) !important;
        transition: border-color 0.15s, box-shadow 0.15s;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--purple) !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
    }

    /* ======================================================
       ALERTS
    ====================================================== */
    .stAlert {
        border-radius: 10px;
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
    }

    /* ======================================================
       FILTER BADGE
    ====================================================== */
    .filter-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(124,58,237,0.12);
        border: 1px solid rgba(124,58,237,0.3);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--purple-light);
        margin-bottom: 1rem;
    }
    .filter-badge::before { content: '⚙'; font-size: 0.68rem; }

    /* ======================================================
       SIDEBAR LOGO
    ====================================================== */
    .sidebar-logo-container {
        text-align: center;
        padding: 1.25rem 0 1rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.5rem;
    }
    .sidebar-logo {
        height: 42px;
        border-radius: 8px;
        box-shadow: 0 0 16px rgba(124,58,237,0.3);
    }

    /* ======================================================
       FOOTER
    ====================================================== */
    .footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.75rem;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 1px solid var(--border);
        margin-top: 2.5rem;
    }
    .footer strong {
        background: var(--grad-purple);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ======================================================
       WELCOME SCREEN
    ====================================================== */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
    }
    .welcome-container h2 {
        color: var(--text-primary) !important;
        border: none !important;
    }
    .welcome-container p {
        color: var(--text-secondary);
    }

    /* ======================================================
       MULTISELECT TAGS — subtle dark purple, easy on the eyes
    ====================================================== */
    /* Tag pill */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: rgba(124,58,237,0.2) !important;
        border: 1px solid rgba(124,58,237,0.4) !important;
        border-radius: 6px !important;
    }
    /* Tag label text */
    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #C4B5FD !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }
    /* Tag × close button */
    [data-testid="stSidebar"] [data-baseweb="tag"] [role="button"] {
        color: #A78BFA !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] [role="button"]:hover {
        color: #EDE9FE !important;
    }
    /* Multiselect dropdown container */
    [data-testid="stSidebar"] [data-baseweb="popover"] {
        background: #1E1F35 !important;
        border: 1px solid rgba(124,58,237,0.3) !important;
    }

    /* Sidebar date label override (for the bold markdown labels) */
    [data-testid="stSidebar"] strong {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.07em !important;
    }

    /* ======================================================
       RADIO TOGGLE
    ====================================================== */
    .stRadio > div { gap: 0 !important; }
    .stRadio [role="radiogroup"] label {
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 7px 18px;
        font-weight: 500;
        font-size: 0.83rem;
        color: var(--text-secondary);
        transition: all 0.15s;
        cursor: pointer;
    }
    .stRadio [role="radiogroup"] label:first-of-type { border-radius: 8px 0 0 8px; }
    .stRadio [role="radiogroup"] label:last-of-type  { border-radius: 0 8px 8px 0; }
    .stRadio [role="radiogroup"] label[data-checked="true"] {
        background: var(--grad-purple);
        color: #FFFFFF !important;
        border-color: transparent;
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
    for key in ['dept_filter', 'status_filter', 'gender_filter', 'vendor_filter',
                'nationality_filter', 'exit_type_filter',
                'join_start', 'join_end', 'exit_start', 'exit_end']:
        st.session_state.pop(key, None)
    st.rerun()

# ---- Join Date: two separate pickers ----
join_start = join_end = None
if 'Join Date' in df.columns:
    jmin = df['Join Date'].dropna().min().date()
    jmax = df['Join Date'].dropna().max().date()
    st.sidebar.markdown("**Join Date — From**")
    join_start = st.sidebar.date_input(
        "join_from", value=jmin, min_value=jmin, max_value=jmax,
        label_visibility="collapsed", key="join_start",
    )
    st.sidebar.markdown("**Join Date — To**")
    join_end = st.sidebar.date_input(
        "join_to", value=jmax, min_value=jmin, max_value=jmax,
        label_visibility="collapsed", key="join_end",
    )

# ---- Exit Date: two separate pickers ----
exit_start = exit_end = None
if 'Exit Date' in df.columns:
    exit_dates = df['Exit Date'].dropna()
    if len(exit_dates) > 0:
        emin = exit_dates.min().date()
        emax = exit_dates.max().date()
        st.sidebar.markdown("**Exit Date — From**")
        exit_start = st.sidebar.date_input(
            "exit_from", value=emin, min_value=emin, max_value=emax,
            label_visibility="collapsed", key="exit_start",
        )
        st.sidebar.markdown("**Exit Date — To**")
        exit_end = st.sidebar.date_input(
            "exit_to", value=emax, min_value=emin, max_value=emax,
            label_visibility="collapsed", key="exit_end",
        )

all_depts = sorted(df['Department'].dropna().unique().tolist())
dept_filter = st.sidebar.multiselect("Department", all_depts, default=all_depts)

status_filter = st.sidebar.selectbox("Employee Status", ["All", "Active", "Departed"])
gender_filter = st.sidebar.selectbox("Gender", ["All"] + df['Gender'].dropna().unique().tolist())

if 'Vendor' in df.columns:
    vendors = sorted(df['Vendor'].dropna().unique().tolist())
    vendor_filter = st.sidebar.selectbox("Vendor", ["All"] + vendors)
else:
    vendor_filter = "All"

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

if join_start and join_end and 'Join Date' in filtered_df.columns:
    if join_start <= join_end:
        filtered_df = filtered_df[
            (filtered_df['Join Date'].dt.date >= join_start) &
            (filtered_df['Join Date'].dt.date <= join_end)
        ]
    else:
        st.sidebar.warning("Join 'From' date must be before 'To' date.")

if exit_start and exit_end and 'Exit Date' in filtered_df.columns:
    if exit_start <= exit_end:
        filtered_df = filtered_df[
            filtered_df['Exit Date'].isna() |
            (
                (filtered_df['Exit Date'].dt.date >= exit_start) &
                (filtered_df['Exit Date'].dt.date <= exit_end)
            )
        ]
    else:
        st.sidebar.warning("Exit 'From' date must be before 'To' date.")

if dept_filter:
    filtered_df = filtered_df[filtered_df['Department'].isin(dept_filter)]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df['Employee Status'] == status_filter]
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df['Gender'] == gender_filter]
if vendor_filter != "All":
    filtered_df = filtered_df[filtered_df['Vendor'] == vendor_filter]
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
