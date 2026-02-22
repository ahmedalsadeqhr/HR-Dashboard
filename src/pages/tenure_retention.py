import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing import get_cohort_retention


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    st.subheader("Tenure Distribution")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Tenure", f"{filtered_df['Tenure (Months)'].min():.1f} mo")
    col2.metric("Max Tenure", f"{filtered_df['Tenure (Months)'].max():.1f} mo")
    col3.metric("Avg Tenure", f"{filtered_df['Tenure (Months)'].mean():.1f} mo")
    col4.metric("Median Tenure", f"{filtered_df['Tenure (Months)'].median():.1f} mo")

    fig = px.histogram(filtered_df, x='Tenure (Months)', nbins=30,
                       color='Employee Status',
                       color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                       marginal='box')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

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
