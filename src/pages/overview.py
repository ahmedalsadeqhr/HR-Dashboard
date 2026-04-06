import streamlit as st
import plotly.express as px

from src.utils import _style

# Modern colour palette aligned with design system
_PIE_COLORS = ['#0057B8', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4']


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(gender_counts, values='Count', names='Gender',
                     color_discrete_sequence=[COLORS['primary'], '#E879F9'],
                     hole=0.55)
        fig.update_traces(textinfo='percent+label', textfont_size=12,
                          marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.1))
        st.plotly_chart(_style(fig, 360), use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Employment Status")
        status_counts = filtered_df['Employee Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status',
                     color_discrete_sequence=['#10B981', '#EF4444'],
                     hole=0.55)
        fig.update_traces(textinfo='percent+label', textfont_size=12,
                          marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.1))
        st.plotly_chart(_style(fig, 360), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Department Breakdown")
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': '#10B981', 'Departed': '#EF4444'},
                 barmode='group', text_auto=True)
    fig.update_traces(textfont_size=10, textposition='outside',
                      marker_line_width=0)
    fig.update_layout(xaxis_tickangle=-35, bargap=0.25)
    st.plotly_chart(_style(fig, 440), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Age Distribution")
    age_df = filtered_df[filtered_df['Age'] > 0]
    if len(age_df) > 0:
        fig = px.histogram(age_df, x='Age', nbins=20,
                           color_discrete_sequence=['#0057B8'],
                           marginal='box', opacity=0.85)
        fig.update_traces(marker_line_color='#FFFFFF', marker_line_width=1)
        st.plotly_chart(_style(fig, 440), use_container_width=True, config=CHART_CONFIG)
