import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yaml
import os
import io
from datetime import datetime

import streamlit_authenticator as stauth
from data_processing import load_excel, process_data, calculate_kpis, get_cohort_retention, get_manager_attrition, save_to_excel

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="HR Analytics Dashboard", page_icon="📊", layout="wide")

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
COLOR_SEQUENCE = [COLORS['primary'], COLORS['success'], COLORS['danger'],
                  COLORS['warning'], COLORS['info'], COLORS['purple'],
                  COLORS['pink'], COLORS['brown']]

DATA_FILE = "Master.xlsx"  # Used for saving edits back

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


# ===================== AUTHENTICATION =====================
def load_auth_config():
    config_path = os.path.join(os.path.dirname(__file__), 'auth_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_auth_config(config):
    config_path = os.path.join(os.path.dirname(__file__), 'auth_config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def get_user_role(config, username):
    if username and username in config['credentials']['usernames']:
        return config['credentials']['usernames'][username].get('role', 'viewer')
    return 'viewer'


config = load_auth_config()

cookie_key = os.environ.get('HR_DASHBOARD_COOKIE_KEY', config['cookie']['key'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    cookie_key,
    config['cookie']['expiry_days'],
)

authenticator.login()

if st.session_state.get("authentication_status") is None:
    st.title("📊 HR Analytics Dashboard")
    st.info("Please enter your credentials to access the dashboard.")
    st.stop()

if st.session_state.get("authentication_status") is False:
    st.error("Username or password is incorrect.")
    st.stop()

# User is authenticated
username = st.session_state.get("username", "")
user_role = get_user_role(config, username)
user_name = st.session_state.get("name", username)

# ===================== HEADER =====================
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("📊 HR Analytics Dashboard")
with header_col2:
    st.markdown(f"**{user_name}** ({user_role.upper()})")
    authenticator.logout("Logout", "main")

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
        # Validate required columns
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            st.sidebar.error(f"Missing required columns: {', '.join(missing)}")
            df = None
        else:
            st.sidebar.success(f"Loaded {len(df)} records from **{uploaded_file.name}**")
            st.sidebar.caption(f"Uploaded at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            # Cache in session state so reruns don't lose data
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


# ===================== SIDEBAR FILTERS =====================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

if st.sidebar.button("Reset All Filters"):
    for key in ['dept_filter', 'status_filter', 'gender_filter', 'emp_type_filter',
                'nationality_filter', 'exit_type_filter']:
        st.session_state.pop(key, None)
    st.rerun()

# Date range filter
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

# Multi-select department filter
all_depts = sorted(df['Department'].dropna().unique().tolist())
dept_filter = st.sidebar.multiselect("Department", all_depts, default=all_depts)

status_filter = st.sidebar.selectbox(
    "Employee Status", ["All", "Active", "Departed"]
)

gender_filter = st.sidebar.selectbox(
    "Gender", ["All"] + df['Gender'].dropna().unique().tolist()
)

# Employment type filter
if 'Employment Type' in df.columns:
    emp_types = df['Employment Type'].dropna().unique().tolist()
    emp_type_filter = st.sidebar.selectbox("Employment Type", ["All"] + emp_types)
else:
    emp_type_filter = "All"

# Nationality filter
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

# Calculate deltas vs full (unfiltered) dataset for context
kpis_all = calculate_kpis(df)
def _delta(filtered_val, all_val, suffix="", invert=False):
    """Return delta string if filters are active, else None."""
    if len(filtered_df) == len(df):
        return None
    diff = filtered_val - all_val
    if abs(diff) < 0.05:
        return None
    return f"{diff:+.1f}{suffix}" if not invert else (f"{diff:+.1f}{suffix}", "inverse")

st.subheader("Key Performance Indicators")
row1 = st.columns(6)
row1[0].metric("Total Employees", f"{kpis['total']:,}")
row1[1].metric("Active", f"{kpis['active']:,}")
row1[2].metric("Departed", f"{kpis['departed']:,}")
row1[3].metric("Attrition Rate", f"{kpis['attrition_rate']:.1f}%",
               delta=_delta(kpis['attrition_rate'], kpis_all['attrition_rate'], '%', invert=True))
row1[4].metric("Retention Rate", f"{kpis['retention_rate']:.1f}%",
               delta=_delta(kpis['retention_rate'], kpis_all['retention_rate'], '%'))
row1[5].metric("Avg Tenure (Mo)", f"{kpis['avg_tenure']:.1f}",
               delta=_delta(kpis['avg_tenure'], kpis_all['avg_tenure']))

row2 = st.columns(6)
row2[0].metric("Avg Age", f"{kpis['avg_age']:.0f}" if not pd.isna(kpis['avg_age']) else "N/A")
row2[1].metric("Gender (M:F)", kpis['gender_ratio'])
row2[2].metric("Contractor %", f"{kpis['contractor_ratio']:.1f}%")
row2[3].metric("Nationalities", f"{kpis['nationality_count']}")
row2[4].metric("Probation Pass", f"{kpis['probation_pass_rate']:.1f}%",
               delta=_delta(kpis['probation_pass_rate'], kpis_all['probation_pass_rate'], '%'))
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
]
if user_role in ('editor', 'admin'):
    tab_names.append("✏️ Edit Data")
if user_role == 'admin':
    tab_names.append("👤 User Management")

tabs = st.tabs(tab_names)


# ===================== TAB 1: OVERVIEW =====================
with tabs[0]:
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

    # Department breakdown
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

    # Nationality distribution
    if 'Nationality' in filtered_df.columns:
        st.markdown("---")
        st.subheader("Nationality Distribution")
        nat_counts = filtered_df['Nationality'].value_counts().reset_index()
        nat_counts.columns = ['Nationality', 'Count']
        fig = px.pie(nat_counts, values='Count', names='Nationality',
                     color_discrete_sequence=COLOR_SEQUENCE)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)


# ===================== TAB 2: ATTRITION ANALYSIS =====================
with tabs[1]:
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    if len(departed_df) == 0:
        st.info("No departed employees in current filter selection.")
    else:
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

        # Exit Reason List (cleaner categories)
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
            fig = px.bar(manager_data.head(15), x='Departures', y='Manager CRM',
                         orientation='h', color='Avg Tenure (Months)',
                         color_continuous_scale='RdYlBu',
                         hover_data=['Top Exit Reason'])
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            st.dataframe(manager_data, use_container_width=True, hide_index=True)
        else:
            st.info("No manager attrition data available.")


# ===================== TAB 3: TENURE & RETENTION =====================
with tabs[2]:
    st.subheader("Tenure Distribution")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Tenure", f"{filtered_df['Tenure (Months)'].min():.1f} mo")
    col2.metric("Max Tenure", f"{filtered_df['Tenure (Months)'].max():.1f} mo")
    col3.metric("Avg Tenure", f"{filtered_df['Tenure (Months)'].mean():.1f} mo")
    col4.metric("Median Tenure", f"{filtered_df['Tenure (Months)'].median():.1f} mo")

    # Histogram
    fig = px.histogram(filtered_df, x='Tenure (Months)', nbins=30,
                       color='Employee Status',
                       color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                       marginal='box')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Tenure by department
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

            # Probation by department
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


# ===================== TAB 4: WORKFORCE COMPOSITION =====================
with tabs[3]:
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


# ===================== TAB 5: TRENDS =====================
with tabs[4]:
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


# ===================== TAB 6: EMPLOYEE DATA =====================
with tabs[5]:
    st.subheader("Employee Data Table")

    search = st.text_input("Search by name", key="emp_search")
    display_df = filtered_df.copy()
    if search:
        display_df = display_df[display_df['Full Name'].str.contains(search, case=False, na=False)]

    all_cols = ['Full Name', 'Gender', 'Age', 'Nationality', 'Department', 'Position',
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
    excel_buffer = io.BytesIO()
    filtered_df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    export_col2.download_button("Download as Excel", excel_buffer, "hr_data_export.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Summary report
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
        summary_lines.append(f"  {row['Department']}: {row['Total']} total, {row['Active']} active, {row['Departed']} departed ({row['Attrition %']}% attrition)")

    summary_lines += [
        "",
        "=== TOP EXIT REASONS ===",
    ]
    departed_summary = filtered_df[filtered_df['Employee Status'] == 'Departed']
    if len(departed_summary) > 0 and 'Exit Reason Category' in departed_summary.columns:
        for reason, count in departed_summary['Exit Reason Category'].value_counts().head(10).items():
            summary_lines.append(f"  {reason}: {count}")

    summary_text = "\n".join(summary_lines)
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


# ===================== TAB 7: EDIT DATA (editor/admin only) =====================
if user_role in ('editor', 'admin'):
    with tabs[6]:
        st.subheader("Edit Employee Data")
        st.caption(f"Logged in as: **{user_name}** (Role: {user_role})")

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
                            'Full Name': new_name,
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
            search_edit = st.text_input("Search employee by name", key="edit_search")

            if search_edit:
                matches = df[df['Full Name'].str.contains(search_edit, case=False, na=False)]
                if len(matches) == 0:
                    st.warning("No employees found.")
                else:
                    # Show name + department + index to disambiguate duplicates
                    match_labels = [
                        f"{row['Full Name']} — {row.get('Department', 'N/A')} (#{idx})"
                        for idx, row in matches.iterrows()
                    ]
                    selected_label = st.selectbox("Select employee", match_labels)
                    emp_idx = int(selected_label.split('(#')[-1].rstrip(')'))
                    emp_row = df.loc[emp_idx]

                    with st.form("edit_employee_form"):
                        ecol1, ecol2 = st.columns(2)

                        with ecol1:
                            edit_dept = st.selectbox("Department",
                                                     sorted(df['Department'].dropna().unique().tolist()),
                                                     index=sorted(df['Department'].dropna().unique().tolist()).index(emp_row['Department']) if emp_row['Department'] in df['Department'].dropna().unique().tolist() else 0)
                            edit_position = st.text_input("Position", value=str(emp_row.get('Position', '')))
                            edit_status = st.selectbox("Employee Status", ["Active", "Departed"],
                                                       index=0 if emp_row.get('Employee Status') == 'Active' else 1)

                        with ecol2:
                            edit_exit_date = st.date_input("Exit Date",
                                                           value=emp_row['Exit Date'].date() if pd.notna(emp_row.get('Exit Date')) else None)
                            edit_exit_type = st.selectbox("Exit Type",
                                                          ["", "Resigned", "Terminated", "Dropped"],
                                                          index=["", "Resigned", "Terminated", "Dropped"].index(emp_row['Exit Type']) if pd.notna(emp_row.get('Exit Type')) and emp_row['Exit Type'] in ["Resigned", "Terminated", "Dropped"] else 0)
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
                                st.success(f"Updated {emp_row['Full Name']} successfully! Refresh to see changes.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error saving: {e}")

        elif edit_action == "Delete Record":
            st.markdown("### Delete Employee Record")
            search_del = st.text_input("Search employee by name", key="del_search")

            if search_del:
                matches = df[df['Full Name'].str.contains(search_del, case=False, na=False)]
                if len(matches) == 0:
                    st.warning("No employees found.")
                else:
                    # Show name + department + index to disambiguate duplicates
                    match_labels = [
                        f"{row['Full Name']} — {row.get('Department', 'N/A')} (#{idx})"
                        for idx, row in matches.iterrows()
                    ]
                    selected_del_label = st.selectbox("Select employee to delete", match_labels,
                                                      key="del_select")
                    del_idx = int(selected_del_label.split('(#')[-1].rstrip(')'))
                    emp_info = df.loc[del_idx]
                    st.write(f"**Name:** {emp_info['Full Name']}")
                    st.write(f"**Department:** {emp_info['Department']}")
                    st.write(f"**Status:** {emp_info['Employee Status']}")

                    confirm = st.checkbox("I confirm I want to delete this record", key="del_confirm")

                    if st.button("Delete Record", type="primary", disabled=not confirm):
                        updated_df = df.drop(index=del_idx)
                        try:
                            save_to_excel(updated_df, DATA_FILE)
                            st.success(f"Deleted {emp_info['Full Name']}. Refresh to see changes.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {e}")


# ===================== TAB 8: USER MANAGEMENT (admin only) =====================
if user_role == 'admin':
    # Tab index: 6 (overview..employee data) + 1 (edit data) = 7
    with tabs[7]:
        st.subheader("User Management")
        st.caption("Manage dashboard user accounts and credentials.")

        manage_action = st.radio("Action", ["Change Password", "Add New User", "Remove User"],
                                 horizontal=True, key="user_mgmt_action")

        # --- Change Password ---
        if manage_action == "Change Password":
            st.markdown("### Change User Password")
            all_users = list(config['credentials']['usernames'].keys())
            target_user = st.selectbox("Select user", all_users, key="pw_user")

            user_info = config['credentials']['usernames'][target_user]
            st.write(f"**Name:** {user_info['name']}")
            st.write(f"**Role:** {user_info.get('role', 'viewer')}")

            with st.form("change_password_form"):
                new_pw = st.text_input("New Password", type="password", key="new_pw")
                confirm_pw = st.text_input("Confirm Password", type="password", key="confirm_pw")
                pw_submitted = st.form_submit_button("Update Password")

                if pw_submitted:
                    if not new_pw or len(new_pw) < 8:
                        st.error("Password must be at least 8 characters.")
                    elif new_pw != confirm_pw:
                        st.error("Passwords do not match.")
                    else:
                        hashed = stauth.Hasher.hash(new_pw)
                        config['credentials']['usernames'][target_user]['password'] = hashed
                        save_auth_config(config)
                        st.success(f"Password updated for **{target_user}**. The user can log in with the new password.")

        # --- Add New User ---
        elif manage_action == "Add New User":
            st.markdown("### Add New User")
            with st.form("add_user_form"):
                acol1, acol2 = st.columns(2)
                with acol1:
                    add_username = st.text_input("Username", key="add_uname")
                    add_name = st.text_input("Display Name", key="add_dname")
                with acol2:
                    add_password = st.text_input("Password", type="password", key="add_pw")
                    add_role = st.selectbox("Role", ["viewer", "editor", "admin"], key="add_role")

                add_submitted = st.form_submit_button("Create User")

                if add_submitted:
                    if not add_username or not add_username.strip():
                        st.error("Username is required.")
                    elif add_username in config['credentials']['usernames']:
                        st.error(f"Username **{add_username}** already exists.")
                    elif not add_password or len(add_password) < 8:
                        st.error("Password must be at least 8 characters.")
                    elif not add_name:
                        st.error("Display Name is required.")
                    else:
                        hashed = stauth.Hasher.hash(add_password)
                        config['credentials']['usernames'][add_username] = {
                            'name': add_name,
                            'password': hashed,
                            'role': add_role,
                        }
                        save_auth_config(config)
                        st.success(f"User **{add_username}** created with role **{add_role}**.")

        # --- Remove User ---
        elif manage_action == "Remove User":
            st.markdown("### Remove User")
            all_users = list(config['credentials']['usernames'].keys())
            removable = [u for u in all_users if u != username]  # Can't remove yourself

            if not removable:
                st.info("No other users to remove.")
            else:
                del_user = st.selectbox("Select user to remove", removable, key="del_user")
                user_info = config['credentials']['usernames'][del_user]
                st.write(f"**Name:** {user_info['name']}")
                st.write(f"**Role:** {user_info.get('role', 'viewer')}")

                confirm_del = st.checkbox("I confirm I want to remove this user", key="del_user_confirm")
                if st.button("Remove User", type="primary", disabled=not confirm_del, key="del_user_btn"):
                    del config['credentials']['usernames'][del_user]
                    save_auth_config(config)
                    st.success(f"User **{del_user}** has been removed.")

        st.markdown("---")

        # Show current users table
        st.subheader("Current Users")
        users_table = []
        for uname, udata in config['credentials']['usernames'].items():
            users_table.append({
                'Username': uname,
                'Display Name': udata.get('name', ''),
                'Role': udata.get('role', 'viewer'),
            })
        st.dataframe(pd.DataFrame(users_table), use_container_width=True, hide_index=True)


# ===================== FOOTER =====================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "HR Analytics Dashboard | Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
