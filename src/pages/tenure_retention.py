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
    st.subheader("Tenure Distribution")

    col1, col2 = st.columns(2)
    max_tenure_years = filtered_df['Tenure (Months)'].max() / 12
    col1.metric("Max Tenure", f"{max_tenure_years:.1f} yr")
    col2.metric("Avg Tenure", f"{filtered_df['Tenure (Months)'].mean():.1f} mo")

    fig = px.histogram(filtered_df, x='Tenure (Months)', nbins=30,
                       color='Employee Status',
                       color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                       marginal='box')
    st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Average Tenure by Department")
    tenure_dept = filtered_df.groupby('Department')['Tenure (Months)'].agg(['mean', 'median', 'count']).round(1)
    tenure_dept.columns = ['Avg Tenure', 'Median Tenure', 'Count']
    tenure_dept = tenure_dept.sort_values('Avg Tenure', ascending=False).reset_index()

    fig = px.bar(tenure_dept, x='Department', y='Avg Tenure',
                 color='Avg Tenure', color_continuous_scale='Blues',
                 text='Avg Tenure', hover_data=['Median Tenure', 'Count'])
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(_style(fig, 450), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # Early leavers
    st.subheader("Early Leavers (Left within 3 months)")
    dep_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
    early_leavers = dep_df[dep_df['Tenure (Months)'] <= 3]

    if len(early_leavers) > 0 and len(dep_df) > 0:
        col1, col2, col3 = st.columns(3)
        col1.metric("Early Leavers", len(early_leavers))
        col2.metric("% of Departures", f"{len(early_leavers) / len(dep_df) * 100:.1f}%")
        col3.metric("Avg Tenure", f"{early_leavers['Tenure (Months)'].mean():.1f} mo")

        early_reasons = early_leavers['Exit Reason Category'].value_counts().reset_index()
        early_reasons.columns = ['Reason', 'Count']
        fig = px.bar(early_reasons, x='Count', y='Reason', orientation='h',
                     color='Count', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(_style(fig, 300), use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("No early leavers in current selection.")
