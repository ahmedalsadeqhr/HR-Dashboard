import streamlit as st
import plotly.express as px


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
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
