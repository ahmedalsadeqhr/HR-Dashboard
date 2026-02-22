import streamlit as st
import plotly.express as px


def _style(fig, height=400):
    """Apply consistent chart styling."""
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
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(gender_counts, values='Count', names='Gender',
                     color_discrete_sequence=[COLORS['primary'], COLORS['pink']],
                     hole=0.4)
        fig.update_traces(textinfo='percent+value', textfont_size=13)
        st.plotly_chart(_style(fig, 380), use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Employee Status")
        status_counts = filtered_df['Employee Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status',
                     color_discrete_sequence=[COLORS['success'], COLORS['danger']],
                     hole=0.4)
        fig.update_traces(textinfo='percent+value', textfont_size=13)
        st.plotly_chart(_style(fig, 380), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Department Breakdown")
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                 barmode='group')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(_style(fig, 450), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Age Distribution")
    age_df = filtered_df[filtered_df['Age'] > 0]
    if len(age_df) > 0:
        fig = px.histogram(age_df, x='Age', nbins=20,
                           color_discrete_sequence=[COLORS['primary']],
                           marginal='box')
        st.plotly_chart(_style(fig, 450), use_container_width=True, config=CHART_CONFIG)
