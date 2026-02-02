import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Dashboard", layout="wide")

st.title("HR Analytics Dashboard")

@st.cache_data
def load_data():
    return pd.read_excel("Master.xlsx")

try:
    df = load_data()

    # Clean column names
    df.columns = df.columns.str.replace('\n', ' ').str.strip()

    # KPI Metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    total = len(df)
    active = len(df[df['Employee Status'] == 'Active'])
    departed = len(df[df['Employee Status'] == 'Departed'])
    attrition = (departed / total * 100) if total > 0 else 0

    col1.metric("Total Employees", f"{total:,}")
    col2.metric("Active", f"{active:,}")
    col3.metric("Departed", f"{departed:,}")
    col4.metric("Attrition Rate", f"{attrition:.1f}%")

    st.markdown("---")

    # Two columns layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        gender_counts = df['Gender'].value_counts()
        st.bar_chart(gender_counts)

    with col2:
        st.subheader("Employee Status")
        status_counts = df['Employee Status'].value_counts()
        st.bar_chart(status_counts)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Department Distribution")
        dept_counts = df['Department'].value_counts().head(10)
        st.bar_chart(dept_counts)

    with col2:
        st.subheader("Exit Types")
        departed_df = df[df['Employee Status'] == 'Departed']
        if len(departed_df) > 0:
            exit_counts = departed_df['Exit Type'].value_counts()
            st.bar_chart(exit_counts)

    st.markdown("---")

    # Exit Reasons
    st.subheader("Exit Reason Categories")
    if len(departed_df) > 0:
        reason_counts = departed_df['Exit Reason Category'].value_counts()
        st.bar_chart(reason_counts)

    st.markdown("---")

    # Data Table
    st.subheader("Employee Data")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.selectbox("Department", ["All"] + sorted(df['Department'].dropna().unique().tolist()))
    with col2:
        status_filter = st.selectbox("Status", ["All"] + df['Employee Status'].dropna().unique().tolist())
    with col3:
        gender_filter = st.selectbox("Gender", ["All"] + df['Gender'].dropna().unique().tolist())

    # Apply filters
    filtered_df = df.copy()
    if dept_filter != "All":
        filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Employee Status'] == status_filter]
    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender_filter]

    # Display columns
    display_cols = ['Full Name', 'Gender', 'Department', 'Position', 'Employee Status', 'Exit Type', 'Exit Reason Category']
    available_cols = [c for c in display_cols if c in filtered_df.columns]

    st.dataframe(filtered_df[available_cols], use_container_width=True, height=400)

    # Download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "hr_data.csv", "text/csv")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure Master.xlsx is in the same folder as app.py")
