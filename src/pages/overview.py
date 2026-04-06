import streamlit as st
import plotly.express as px

from src.utils import _style

def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(gender_counts, values='Count', names='Gender',
                     color_discrete_sequence=['#7C3AED', '#D946EF'],
                     hole=0.62)
        fig.update_traces(
            textinfo='percent+label', textfont_size=11, textfont_color='#E2E8F0',
            marker=dict(line=dict(color='#0D0E1A', width=3)),
            pull=[0.04, 0],
        )
        fig.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.12,
                          font=dict(color='#94A3B8')))
        st.plotly_chart(_style(fig, 360), use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Employment Status")
        status_counts = filtered_df['Employee Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status',
                     color_discrete_sequence=['#06B6D4', '#EF4444'],
                     hole=0.62)
        fig.update_traces(
            textinfo='percent+label', textfont_size=11, textfont_color='#E2E8F0',
            marker=dict(line=dict(color='#0D0E1A', width=3)),
            pull=[0.04, 0],
        )
        fig.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.12,
                          font=dict(color='#94A3B8')))
        st.plotly_chart(_style(fig, 360), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Department Breakdown")
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': '#06B6D4', 'Departed': '#EF4444'},
                 barmode='group', text_auto=True)
    fig.update_traces(textfont_size=9, textfont_color='#94A3B8', textposition='outside',
                      marker_line_width=0, opacity=0.9)
    fig.update_layout(xaxis_tickangle=-35, bargap=0.28,
                      xaxis=dict(tickfont=dict(color='#475569')))
    st.plotly_chart(_style(fig, 440), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Age Distribution")
    age_df = filtered_df[filtered_df['Age'] > 0]
    if len(age_df) > 0:
        fig = px.histogram(age_df, x='Age', nbins=20,
                           color_discrete_sequence=['#7C3AED'],
                           marginal='box', opacity=0.85)
        fig.update_traces(marker_line_color='#0D0E1A', marker_line_width=1)
        st.plotly_chart(_style(fig, 440), use_container_width=True, config=CHART_CONFIG)
