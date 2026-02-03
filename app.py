import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="HR Analytics Dashboard", page_icon="👥", layout="wide")

st.title("👥 HR Analytics Dashboard")

# ================== DATA SOURCE SELECTION ==================
st.sidebar.header("📁 Data Source")

data_source = st.sidebar.radio(
    "Choose data source:",
    ["Default (Master.xlsx)", "Upload New File"]
)

@st.cache_data
def load_default_data():
    df = pd.read_excel("Master.xlsx")
    return process_data(df)

def process_data(df):
    # Clean column names
    df.columns = df.columns.str.replace('\n', ' ').str.strip()

    # Rename columns
    df = df.rename(columns={
        'Join Date (yyyy/mm/dd)': 'Join Date',
        'Exit Date yyyy/mm/dd': 'Exit Date',
        'Position (After Joining)': 'Position After Joining'
    })

    # Convert dates
    df['Join Date'] = pd.to_datetime(df['Join Date'], errors='coerce')
    df['Exit Date'] = pd.to_datetime(df['Exit Date'], errors='coerce')
    df['Birthday Date'] = pd.to_datetime(df['Birthday Date'], errors='coerce')

    # Calculate Age
    today = pd.Timestamp(datetime.now())
    df['Age'] = ((today - df['Birthday Date']).dt.days / 365.25).fillna(0).astype(int)

    # Calculate Tenure (in months)
    df['Tenure (Months)'] = np.where(
        df['Employee Status'] == 'Active',
        ((today - df['Join Date']).dt.days / 30.44).fillna(0),
        ((df['Exit Date'] - df['Join Date']).dt.days / 30.44).fillna(0)
    )
    df['Tenure (Months)'] = df['Tenure (Months)'].round(1)

    # Extract Year and Month
    df['Join Year'] = df['Join Date'].dt.year
    df['Join Month'] = df['Join Date'].dt.to_period('M').astype(str)
    df['Exit Year'] = df['Exit Date'].dt.year
    df['Exit Month'] = df['Exit Date'].dt.to_period('M').astype(str)

    return df

# Load data based on selection
df = None

if data_source == "Upload New File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel file",
        type=['xlsx', 'xls'],
        help="Upload your HR data file. Must have same column structure as Master.xlsx"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df = process_data(df)
            st.sidebar.success(f"✅ Loaded {len(df)} records")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            df = None
    else:
        st.sidebar.info("👆 Please upload an Excel file")
else:
    try:
        df = load_default_data()
        st.sidebar.success(f"✅ Using Master.xlsx ({len(df)} records)")
    except Exception as e:
        st.sidebar.error(f"Error loading Master.xlsx: {e}")
        df = None

# Show required columns info
with st.sidebar.expander("ℹ️ Required Columns"):
    st.markdown("""
    Your Excel file should have these columns:
    - Full Name
    - Gender (M/F)
    - Birthday Date
    - Department
    - Position
    - Employee Status (Active/Departed)
    - Join Date
    - Exit Date
    - Exit Type
    - Exit Reason Category
    - Exit Reason
    """)

if df is None:
    st.warning("⚠️ No data loaded. Please upload a file or check Master.xlsx exists.")
    st.stop()

# ================== SIDEBAR FILTERS ==================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

dept_filter = st.sidebar.selectbox(
    "Department",
    ["All"] + sorted(df['Department'].dropna().unique().tolist())
)

status_filter = st.sidebar.selectbox(
    "Employee Status",
    ["All"] + df['Employee Status'].dropna().unique().tolist()
)

gender_filter = st.sidebar.selectbox(
    "Gender",
    ["All"] + df['Gender'].dropna().unique().tolist()
)

exit_type_filter = st.sidebar.selectbox(
    "Exit Type",
    ["All"] + df['Exit Type'].dropna().unique().tolist()
)

# Apply filters
filtered_df = df.copy()
if dept_filter != "All":
    filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df['Employee Status'] == status_filter]
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df['Gender'] == gender_filter]
if exit_type_filter != "All":
    filtered_df = filtered_df[filtered_df['Exit Type'] == exit_type_filter]

# ================== KPI METRICS ==================
st.subheader("📊 Key Performance Indicators")

total = len(filtered_df)
active = len(filtered_df[filtered_df['Employee Status'] == 'Active'])
departed = len(filtered_df[filtered_df['Employee Status'] == 'Departed'])
attrition_rate = (departed / total * 100) if total > 0 else 0
avg_tenure = filtered_df['Tenure (Months)'].mean()
avg_age = filtered_df[filtered_df['Age'] > 0]['Age'].mean()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Employees", f"{total:,}")
col2.metric("Active", f"{active:,}")
col3.metric("Departed", f"{departed:,}")
col4.metric("Attrition Rate", f"{attrition_rate:.1f}%")
col5.metric("Avg Tenure (Months)", f"{avg_tenure:.1f}")
col6.metric("Avg Age", f"{avg_age:.0f}" if not pd.isna(avg_age) else "N/A")

st.markdown("---")

# ================== TABS FOR DIFFERENT ANALYSES ==================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🚪 Attrition Analysis",
    "⏱️ Tenure Analysis",
    "📅 Trends",
    "📋 Employee Data"
])

# ================== TAB 1: OVERVIEW ==================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👫 Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts()
        gender_pct = (gender_counts / gender_counts.sum() * 100).round(1)
        gender_display = pd.DataFrame({
            'Count': gender_counts,
            'Percentage': gender_pct.apply(lambda x: f"{x}%")
        })
        st.dataframe(gender_display, use_container_width=True)
        st.bar_chart(gender_counts)

    with col2:
        st.subheader("📊 Employee Status")
        status_counts = filtered_df['Employee Status'].value_counts()
        status_pct = (status_counts / status_counts.sum() * 100).round(1)
        status_display = pd.DataFrame({
            'Count': status_counts,
            'Percentage': status_pct.apply(lambda x: f"{x}%")
        })
        st.dataframe(status_display, use_container_width=True)
        st.bar_chart(status_counts)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 Top 10 Departments")
        dept_counts = filtered_df['Department'].value_counts().head(10)
        st.bar_chart(dept_counts)
        st.dataframe(dept_counts.reset_index().rename(columns={'index': 'Department', 'Department': 'Department', 'count': 'Count'}), use_container_width=True, hide_index=True)

    with col2:
        st.subheader("💼 Top 10 Positions")
        position_counts = filtered_df['Position'].value_counts().head(10)
        st.bar_chart(position_counts)
        st.dataframe(position_counts.reset_index().rename(columns={'index': 'Position', 'Position': 'Position', 'count': 'Count'}), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Age Distribution
    st.subheader("👤 Age Distribution")
    age_df = filtered_df[filtered_df['Age'] > 0]['Age']
    if len(age_df) > 0:
        age_bins = pd.cut(age_df, bins=[18, 25, 30, 35, 40, 45, 50, 100], labels=['18-25', '26-30', '31-35', '36-40', '41-45', '46-50', '50+'])
        age_dist = age_bins.value_counts().sort_index()
        st.bar_chart(age_dist)

# ================== TAB 2: ATTRITION ANALYSIS ==================
with tab2:
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    if len(departed_df) > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚪 Exit Types")
            exit_counts = departed_df['Exit Type'].value_counts()
            exit_pct = (exit_counts / exit_counts.sum() * 100).round(1)
            exit_display = pd.DataFrame({
                'Count': exit_counts,
                'Percentage': exit_pct.apply(lambda x: f"{x}%")
            })
            st.dataframe(exit_display, use_container_width=True)
            st.bar_chart(exit_counts)

        with col2:
            st.subheader("📋 Exit Reason Categories")
            reason_counts = departed_df['Exit Reason Category'].value_counts()
            reason_pct = (reason_counts / reason_counts.sum() * 100).round(1)
            reason_display = pd.DataFrame({
                'Count': reason_counts,
                'Percentage': reason_pct.apply(lambda x: f"{x}%")
            })
            st.dataframe(reason_display, use_container_width=True)
            st.bar_chart(reason_counts)

        st.markdown("---")

        # Attrition by Department
        st.subheader("🏢 Attrition Rate by Department")
        dept_attrition = filtered_df.groupby('Department').agg({
            'Employee Status': [
                lambda x: (x == 'Active').sum(),
                lambda x: (x == 'Departed').sum(),
                'count'
            ]
        }).reset_index()
        dept_attrition.columns = ['Department', 'Active', 'Departed', 'Total']
        dept_attrition['Attrition Rate %'] = (dept_attrition['Departed'] / dept_attrition['Total'] * 100).round(1)
        dept_attrition = dept_attrition.sort_values('Total', ascending=False).head(10)
        st.dataframe(dept_attrition, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Voluntary vs Involuntary
        st.subheader("📊 Voluntary vs Involuntary Turnover")
        voluntary = len(departed_df[departed_df['Exit Type'] == 'Resigned'])
        involuntary = len(departed_df[departed_df['Exit Type'].isin(['Terminated', 'Dropped'])])
        vol_invol = pd.Series({'Voluntary (Resigned)': voluntary, 'Involuntary (Terminated/Dropped)': involuntary})
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Voluntary Turnover", f"{voluntary} ({voluntary/len(departed_df)*100:.1f}%)")
        with col2:
            st.metric("Involuntary Turnover", f"{involuntary} ({involuntary/len(departed_df)*100:.1f}%)")
        st.bar_chart(vol_invol)

        st.markdown("---")

        # Exit Reasons Detail
        st.subheader("📝 Detailed Exit Reasons")
        exit_detail = departed_df['Exit Reason'].value_counts().head(15)
        st.dataframe(exit_detail.reset_index().rename(columns={'index': 'Exit Reason', 'Exit Reason': 'Exit Reason', 'count': 'Count'}), use_container_width=True, hide_index=True)
    else:
        st.info("No departed employees in current filter selection")

# ================== TAB 3: TENURE ANALYSIS ==================
with tab3:
    st.subheader("⏱️ Tenure Distribution (Months)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Tenure", f"{filtered_df['Tenure (Months)'].min():.1f}")
    col2.metric("Max Tenure", f"{filtered_df['Tenure (Months)'].max():.1f}")
    col3.metric("Avg Tenure", f"{filtered_df['Tenure (Months)'].mean():.1f}")
    col4.metric("Median Tenure", f"{filtered_df['Tenure (Months)'].median():.1f}")

    # Tenure brackets
    tenure_bins = pd.cut(
        filtered_df['Tenure (Months)'],
        bins=[0, 3, 6, 12, 24, 36, 1000],
        labels=['0-3 months', '3-6 months', '6-12 months', '1-2 years', '2-3 years', '3+ years']
    )
    tenure_dist = tenure_bins.value_counts().sort_index()
    st.bar_chart(tenure_dist)

    st.markdown("---")

    # Tenure by Department
    st.subheader("🏢 Average Tenure by Department")
    tenure_by_dept = filtered_df.groupby('Department')['Tenure (Months)'].agg(['mean', 'count']).round(1)
    tenure_by_dept.columns = ['Avg Tenure (Months)', 'Employee Count']
    tenure_by_dept = tenure_by_dept.sort_values('Avg Tenure (Months)', ascending=False).head(10)
    st.dataframe(tenure_by_dept, use_container_width=True)
    st.bar_chart(tenure_by_dept['Avg Tenure (Months)'])

    st.markdown("---")

    # Tenure by Status
    st.subheader("📊 Tenure by Employee Status")
    tenure_by_status = filtered_df.groupby('Employee Status')['Tenure (Months)'].agg(['mean', 'median', 'min', 'max']).round(1)
    tenure_by_status.columns = ['Mean', 'Median', 'Min', 'Max']
    st.dataframe(tenure_by_status, use_container_width=True)

    st.markdown("---")

    # Early Leavers Analysis (left within 6 months)
    st.subheader("⚠️ Early Leavers Analysis (Left within 6 months)")
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
    early_leavers = departed_df[departed_df['Tenure (Months)'] <= 6]

    if len(early_leavers) > 0 and len(departed_df) > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Early Leavers Count", len(early_leavers))
            st.metric("% of All Departures", f"{len(early_leavers)/len(departed_df)*100:.1f}%")
        with col2:
            early_reasons = early_leavers['Exit Reason Category'].value_counts()
            st.write("**Top Reasons for Early Departure:**")
            st.dataframe(early_reasons.head(5), use_container_width=True)
    else:
        st.info("No early leavers in current selection")

# ================== TAB 4: TRENDS ==================
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Hiring Trend by Year")
        hiring_by_year = filtered_df.groupby('Join Year').size()
        hiring_by_year = hiring_by_year[hiring_by_year.index > 2000]  # Filter valid years
        st.line_chart(hiring_by_year)
        st.dataframe(hiring_by_year.reset_index().rename(columns={'index': 'Year', 0: 'Hires', 'Join Year': 'Year'}), use_container_width=True, hide_index=True)

    with col2:
        st.subheader("📉 Attrition Trend by Year")
        departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
        if len(departed_df) > 0:
            attrition_by_year = departed_df.groupby('Exit Year').size()
            attrition_by_year = attrition_by_year[attrition_by_year.index > 2000]
            st.line_chart(attrition_by_year)
            st.dataframe(attrition_by_year.reset_index().rename(columns={'index': 'Year', 0: 'Exits', 'Exit Year': 'Year'}), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Monthly trends (last 24 months)
    st.subheader("📅 Monthly Hiring Trend (Recent)")
    monthly_hiring = filtered_df.groupby('Join Month').size().tail(24)
    if len(monthly_hiring) > 0:
        st.line_chart(monthly_hiring)

    st.markdown("---")

    # Headcount over time
    st.subheader("👥 Headcount Analysis by Join Year")
    headcount_summary = filtered_df.groupby(['Join Year', 'Employee Status']).size().unstack(fill_value=0)
    headcount_summary = headcount_summary[headcount_summary.index > 2000]
    if len(headcount_summary) > 0:
        st.dataframe(headcount_summary, use_container_width=True)

# ================== TAB 5: EMPLOYEE DATA ==================
with tab5:
    st.subheader("📋 Employee Data Table")

    # Search
    search = st.text_input("🔍 Search by name")

    display_df = filtered_df.copy()
    if search:
        display_df = display_df[display_df['Full Name'].str.contains(search, case=False, na=False)]

    # Select columns
    all_cols = ['Full Name', 'Gender', 'Age', 'Department', 'Position', 'Employee Status',
                'Join Date', 'Exit Date', 'Exit Type', 'Exit Reason Category', 'Tenure (Months)']
    available_cols = [c for c in all_cols if c in display_df.columns]

    selected_cols = st.multiselect(
        "Select columns to display",
        available_cols,
        default=available_cols[:8]
    )

    if selected_cols:
        st.dataframe(display_df[selected_cols], use_container_width=True, height=500)

    # Download
    st.markdown("---")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Filtered Data as CSV",
        csv,
        "hr_data_export.csv",
        "text/csv"
    )

    # Summary stats
    st.markdown("---")
    st.subheader("📊 Quick Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Numerical Summary:**")
        st.dataframe(filtered_df[['Age', 'Tenure (Months)']].describe().round(1), use_container_width=True)
    with col2:
        st.write("**Category Counts:**")
        st.write(f"- Unique Departments: {filtered_df['Department'].nunique()}")
        st.write(f"- Unique Positions: {filtered_df['Position'].nunique()}")
        st.write(f"- Male: {len(filtered_df[filtered_df['Gender'] == 'M'])}")
        st.write(f"- Female: {len(filtered_df[filtered_df['Gender'] == 'F'])}")

# ================== FOOTER ==================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>HR Analytics Dashboard | Built with Streamlit</div>",
    unsafe_allow_html=True
)
