import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_processing import get_manager_attrition


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
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    if len(departed_df) == 0:
        st.info("No departed employees in current filter selection.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Exit Types")
        exit_counts = departed_df['Exit Type'].value_counts().reset_index()
        exit_counts.columns = ['Exit Type', 'Count']
        fig = px.pie(exit_counts, values='Count', names='Exit Type',
                     color_discrete_sequence=[COLORS['warning'], COLORS['danger'], COLORS['brown']])
        fig.update_traces(textinfo='percent+value', textfont_size=13)
        st.plotly_chart(_style(fig, 380), use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Exit Reason Categories")
        reason_counts = departed_df['Exit Reason Category'].value_counts().reset_index()
        reason_counts.columns = ['Category', 'Count']
        fig = px.bar(reason_counts, x='Count', y='Category', orientation='h',
                     color='Count', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Voluntary vs Involuntary
    st.subheader("Voluntary vs Involuntary Turnover")
    voluntary = len(departed_df[departed_df['Exit Type'].isin(['Resigned', 'Dropped'])])
    involuntary = len(departed_df[departed_df['Exit Type'] == 'Terminated'])
    total_departed = len(departed_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Voluntary (Resigned/Dropped)", f"{voluntary} ({voluntary / total_departed * 100:.1f}%)")
    col2.metric("Involuntary (Terminated)", f"{involuntary} ({involuntary / total_departed * 100:.1f}%)")
    col3.metric("Total Departures", f"{total_departed}")

    vol_data = pd.DataFrame({
        'Type': ['Voluntary (Resigned/Dropped)', 'Involuntary (Terminated)'],
        'Count': [voluntary, involuntary]
    })
    fig = px.pie(vol_data, values='Count', names='Type',
                 color_discrete_sequence=[COLORS['warning'], COLORS['danger']], hole=0.4)
    fig.update_traces(textinfo='percent+value', textfont_size=13)
    st.plotly_chart(_style(fig, 380), use_container_width=True, config=CHART_CONFIG)

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
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(_style(fig, 450), use_container_width=True, config=CHART_CONFIG)

    st.dataframe(dept_attrition, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Exit Reasons breakdown
    if 'Exit Reason Category' in departed_df.columns:
        st.subheader("Exit Reasons (Categorized)")
        reason_list = departed_df[departed_df['Exit Reason Category'].notna()]['Exit Reason Category'].value_counts().reset_index()
        reason_list.columns = ['Reason', 'Count']
        if len(reason_list) > 0:
            fig = px.bar(reason_list, x='Count', y='Reason', orientation='h',
                         color='Count', color_continuous_scale='Oranges')
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(_style(fig, max(300, len(reason_list) * 30)), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Manager-linked attrition
    st.subheader("Manager-Linked Attrition")
    manager_data = get_manager_attrition(filtered_df)
    if len(manager_data) > 0:
        st.markdown("*Which managers had the most departures under them?*")
        mgr_chart_kwargs = dict(x='Departures', y='Manager CRM', orientation='h')
        if 'Avg Tenure (Months)' in manager_data.columns:
            mgr_chart_kwargs['color'] = 'Avg Tenure (Months)'
            mgr_chart_kwargs['color_continuous_scale'] = 'RdYlBu'
        if 'Top Exit Reason' in manager_data.columns:
            mgr_chart_kwargs['hover_data'] = ['Top Exit Reason']
        fig = px.bar(manager_data.head(15), **mgr_chart_kwargs)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(_style(fig, 500), use_container_width=True, config=CHART_CONFIG)
        st.dataframe(manager_data, use_container_width=True, hide_index=True)
    else:
        st.info("No manager attrition data available.")
