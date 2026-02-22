import streamlit as st
import pandas as pd
from datetime import datetime

from src.config import DATA_FILE
from src.data_processing import save_to_excel
from src.utils import generate_summary_report, export_excel


def _search_employees(df, query, NAME_COL):
    """Search employees by Name, PS ID, CRM, or National ID."""
    mask = pd.Series(False, index=df.index)
    if NAME_COL and NAME_COL in df.columns:
        mask |= df[NAME_COL].astype(str).str.contains(query, case=False, na=False)
    for col in ['PS ID', 'CRM', 'Identity number']:
        if col in df.columns:
            mask |= df[col].astype(str).str.contains(query, case=False, na=False)
    return df[mask]


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    view_mode = st.radio("Mode", ["View Data", "Add Employee", "Edit Employee", "Delete Employee"],
                         horizontal=True)

    if view_mode == "View Data":
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

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        export_col1.download_button("Download as CSV", csv, "hr_data_export.csv", "text/csv")

        excel_buffer = export_excel(filtered_df)
        export_col2.download_button("Download as Excel", excel_buffer, "hr_data_export.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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

    elif view_mode == "Add Employee":
        st.subheader("Add New Employee")
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
                        NAME_COL or 'Full Name': new_name,
                        'Gender': new_gender,
                        'Birthday Date': pd.Timestamp(new_birthday),
                        'Nationality': new_nationality,
                        'Department': new_department,
                        'Position': new_position,
                        'Employee Status': new_status,
                        'Join Date': pd.Timestamp(new_join_date),
                        'Employment Type': new_type,
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

    elif view_mode == "Edit Employee":
        st.subheader("Edit Existing Employee")

        search_edit = st.text_input("Search by Name, PS ID, CRM, or National ID", key="edit_search")

        if search_edit:
            matches = _search_employees(df, search_edit, NAME_COL)
            if len(matches) == 0:
                st.warning("No employees found.")
            else:
                match_labels = [
                    f"{row.get(NAME_COL, 'N/A') if NAME_COL else 'N/A'} -- {row.get('Department', 'N/A')} (#{idx})"
                    for idx, row in matches.iterrows()
                ]
                selected_label = st.selectbox("Select employee", match_labels)
                emp_idx = int(selected_label.split('(#')[-1].rstrip(')'))
                emp_row = df.loc[emp_idx]

                with st.form("edit_employee_form"):
                    ecol1, ecol2 = st.columns(2)

                    with ecol1:
                        dept_list = sorted(df['Department'].dropna().unique().tolist())
                        edit_dept = st.selectbox("Department", dept_list,
                                                 index=dept_list.index(emp_row['Department']) if emp_row['Department'] in dept_list else 0)
                        edit_position = st.text_input("Position", value=str(emp_row.get('Position', '')))
                        edit_status = st.selectbox("Employee Status", ["Active", "Departed"],
                                                   index=0 if emp_row.get('Employee Status') == 'Active' else 1)

                    with ecol2:
                        edit_exit_date = st.date_input("Exit Date",
                                                       value=emp_row['Exit Date'].date() if pd.notna(emp_row.get('Exit Date')) else None)
                        exit_options = ["", "Resigned", "Terminated", "Dropped"]
                        edit_exit_type = st.selectbox("Exit Type", exit_options,
                                                      index=exit_options.index(emp_row['Exit Type']) if pd.notna(emp_row.get('Exit Type')) and emp_row['Exit Type'] in exit_options else 0)
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
                            st.success(f"Updated {emp_row[NAME_COL]} successfully! Refresh to see changes.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {e}")

    elif view_mode == "Delete Employee":
        st.subheader("Delete Employee Record")

        search_del = st.text_input("Search by Name, PS ID, CRM, or National ID", key="del_search")

        if search_del:
            matches = _search_employees(df, search_del, NAME_COL)
            if len(matches) == 0:
                st.warning("No employees found.")
            else:
                match_labels = [
                    f"{row.get(NAME_COL, 'N/A') if NAME_COL else 'N/A'} -- {row.get('Department', 'N/A')} (#{idx})"
                    for idx, row in matches.iterrows()
                ]
                selected_del_label = st.selectbox("Select employee to delete", match_labels,
                                                  key="del_select")
                del_idx = int(selected_del_label.split('(#')[-1].rstrip(')'))
                emp_info = df.loc[del_idx]
                if NAME_COL:
                    st.write(f"**Name:** {emp_info[NAME_COL]}")
                st.write(f"**Department:** {emp_info['Department']}")
                st.write(f"**Status:** {emp_info['Employee Status']}")

                confirm = st.checkbox("I confirm I want to delete this record", key="del_confirm")

                if st.button("Delete Record", type="primary", disabled=not confirm):
                    updated_df = df.drop(index=del_idx)
                    try:
                        save_to_excel(updated_df, DATA_FILE)
                        st.success(f"Deleted {emp_info.get(NAME_COL, 'record') if NAME_COL else 'record'}. Refresh to see changes.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving: {e}")
