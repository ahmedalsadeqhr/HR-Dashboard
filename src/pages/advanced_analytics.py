import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.data_processing import calculate_period_turnover
from src.utils import _style, dept_group


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG, scope_df=None):

    # --- 1. New Hire 90-Day Retention ---
    st.subheader("New Hire 90-Day Retention")
    if 'Join Date' in filtered_df.columns and 'Exit Date' in filtered_df.columns:
        cutoff_90 = pd.Timestamp(datetime.now()) - pd.Timedelta(days=90)
        measurable = filtered_df[filtered_df['Join Date'] <= cutoff_90]

        if len(measurable) > 0:
            left_within_90 = measurable[
                (measurable['Employee Status'] == 'Departed') &
                (measurable['Exit Date'].notna()) &
                ((measurable['Exit Date'] - measurable['Join Date']).dt.days <= 90)
            ]
            retention_90 = (1 - len(left_within_90) / len(measurable)) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric("90-Day Retention Rate", f"{retention_90:.1f}%")
            col2.metric("Left Within 90 Days", f"{len(left_within_90)}")
            col3.metric("Measurable Employees", f"{len(measurable)}")

            left_90_mask = (
                (measurable['Employee Status'] == 'Departed') &
                measurable['Exit Date'].notna() &
                ((measurable['Exit Date'] - measurable['Join Date']).dt.days <= 90)
            )
            # Consolidated
            meas_grp = measurable.copy()
            meas_grp['Dept Group'] = meas_grp['Department'].map(dept_group)
            grp_total = meas_grp.groupby('Dept Group').size().rename('Total')
            grp_left = meas_grp[left_90_mask].groupby('Dept Group').size().rename('Left <90d')
            grp_90 = pd.concat([grp_total, grp_left], axis=1).fillna(0).reset_index()
            grp_90['Left <90d'] = grp_90['Left <90d'].astype(int)
            grp_90['Retention %'] = ((1 - grp_90['Left <90d'] / grp_90['Total']) * 100).round(1)
            grp_90 = grp_90.sort_values('Retention %')
            st.caption("Consolidated view")
            fig = px.bar(grp_90, x='Dept Group', y='Retention %',
                         color='Retention %', color_continuous_scale='RdYlGn',
                         text='Retention %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)

            # Detailed
            dept_total = measurable.groupby('Department').size().rename('Total')
            dept_left = measurable[left_90_mask].groupby('Department').size().rename('Left <90d')
            dept_90 = pd.concat([dept_total, dept_left], axis=1).fillna(0).reset_index()
            dept_90['Left <90d'] = dept_90['Left <90d'].astype(int)
            dept_90['Retention %'] = ((1 - dept_90['Left <90d'] / dept_90['Total']) * 100).round(1)
            dept_90 = dept_90.sort_values('Retention %')
            st.caption("Detailed view")
            fig = px.bar(dept_90, x='Department', y='Retention %',
                         color='Retention %', color_continuous_scale='RdYlGn',
                         text='Retention %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Not enough data to measure 90-day retention.")
    else:
        st.info("Join Date and Exit Date columns required.")

    st.markdown("---")

    # --- 2. Turnover Rate (exits / average headcount) ---
    st.subheader("Rolling Turnover Rate")
    # Headcount needs active + departed employees, so use the scope that ignores the
    # Employee Status / Exit Type filters.
    base = scope_df if scope_df is not None else filtered_df
    period_view = st.radio("View", ["Monthly", "Quarterly"], horizontal=True, key="turnover_period")
    if period_view == "Quarterly":
        turnover_df = calculate_period_turnover(base, freq='Q', periods=8)
    else:
        turnover_df = calculate_period_turnover(base, freq='M', periods=24)

    if len(turnover_df) > 0 and turnover_df['Exits'].sum() > 0:
        fig = px.bar(turnover_df, x='Period', y='Turnover Rate %',
                     color='Turnover Rate %', color_continuous_scale='RdYlGn_r',
                     text='Turnover Rate %', hover_data=['Exits', 'Avg Headcount'])
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)
        st.caption("Turnover = exits in the period / average headcount (start and end of the "
                   "period). The latest period is still in progress, so it is partial.")
    else:
        st.info("No departure data available for turnover analysis.")
