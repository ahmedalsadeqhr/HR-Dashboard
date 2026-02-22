import streamlit as st
import plotly.express as px


def _style(fig, height=400):
    fig.update_layout(
        height=height,
        font=dict(family='Inter, Segoe UI, sans-serif'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=40, l=40, r=20),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
    return fig


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    # Vendor analysis
    if 'Vendor' in filtered_df.columns:
        st.subheader("Vendor / Source Analysis")
        vendor_counts = filtered_df['Vendor'].value_counts().reset_index()
        vendor_counts.columns = ['Vendor', 'Count']

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(vendor_counts, values='Count', names='Vendor',
                         color_discrete_sequence=COLOR_SEQUENCE, hole=0.4)
            fig.update_traces(textinfo='percent+value', textfont_size=13)
            st.plotly_chart(_style(fig, 380), use_container_width=True, config=CHART_CONFIG)

        with col2:
            vendor_status = filtered_df.groupby(['Vendor', 'Employee Status']).size().reset_index(name='Count')
            fig = px.bar(vendor_status, x='Vendor', y='Count', color='Employee Status',
                         color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                         barmode='group')
            st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)

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
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(_style(fig, 350), use_container_width=True, config=CHART_CONFIG)
