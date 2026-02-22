import streamlit as st

from src.pages import overview, attrition, tenure_retention, workforce, trends, advanced_analytics


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    section = st.selectbox("Section", [
        "Overview",
        "Attrition Analysis",
        "Tenure & Retention",
        "Workforce Composition",
        "Trends",
        "Advanced Analytics",
    ])

    st.markdown("---")

    if section == "Overview":
        overview.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
    elif section == "Attrition Analysis":
        attrition.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
    elif section == "Tenure & Retention":
        tenure_retention.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
    elif section == "Workforce Composition":
        workforce.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
    elif section == "Trends":
        trends.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
    elif section == "Advanced Analytics":
        advanced_analytics.render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG)
