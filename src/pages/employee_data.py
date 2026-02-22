import streamlit as st
import pandas as pd

from src.utils import generate_summary_report, export_excel


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    st.subheader("Employee Data Table")

    search = st.text_input("Search by name", key="emp_search")
    display_df = filtered_df.copy()
    if search and NAME_COL:
        display_df = display_df[display_df[NAME_COL].str.contains(search, case=False, na=False)]

    all_cols = [NAME_COL, 'Gender', 'Age', 'Nationality', 'Department', 'Position',
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
    excel_buffer = export_excel(filtered_df)
    export_col2.download_button("Download as Excel", excel_buffer, "hr_data_export.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Summary report
    summary_text = generate_summary_report(filtered_df, df, kpis)
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
