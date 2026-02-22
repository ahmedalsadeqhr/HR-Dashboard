import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    adv_departed = filtered_df[filtered_df['Employee Status'] == 'Departed']

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

            dept_90 = measurable.groupby('Department').apply(
                lambda g: pd.Series({
                    'Total': len(g),
                    'Left <90d': len(g[(g['Employee Status'] == 'Departed') & g['Exit Date'].notna() & ((g['Exit Date'] - g['Join Date']).dt.days <= 90)]),
                })
            ).reset_index()
            dept_90['Retention %'] = ((1 - dept_90['Left <90d'] / dept_90['Total']) * 100).round(1)
            dept_90 = dept_90.sort_values('Retention %')

            fig = px.bar(dept_90, x='Department', y='Retention %',
                         color='Retention %', color_continuous_scale='RdYlGn',
                         text='Retention %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Not enough data to measure 90-day retention.")
    else:
        st.info("Join Date and Exit Date columns required.")

    st.markdown("---")

    # --- 2. Rolling Turnover Rate ---
    st.subheader("Rolling Turnover Rate")
    if len(adv_departed) > 0 and 'Exit Date' in adv_departed.columns:
        monthly_exits = adv_departed.groupby(
            adv_departed['Exit Date'].dt.to_period('M')
        ).size().reset_index(name='Exits')
        monthly_exits.columns = ['Period', 'Exits']
        monthly_exits['Period'] = monthly_exits['Period'].astype(str)

        monthly_hires = filtered_df.groupby(
            filtered_df['Join Date'].dt.to_period('M')
        ).size().reset_index(name='Hires')
        monthly_hires.columns = ['Period', 'Hires']
        monthly_hires['Period'] = monthly_hires['Period'].astype(str)

        turnover_df = pd.merge(monthly_hires, monthly_exits, on='Period', how='outer').fillna(0)
        turnover_df = turnover_df.sort_values('Period').tail(24)
        turnover_df['Cumulative Hires'] = turnover_df['Hires'].cumsum()
        turnover_df['Turnover Rate %'] = (turnover_df['Exits'] / turnover_df['Cumulative Hires'].replace(0, 1) * 100).round(1)

        period_view = st.radio("View", ["Monthly", "Quarterly"], horizontal=True, key="turnover_period")

        if period_view == "Quarterly":
            turnover_df['Quarter'] = pd.to_datetime(turnover_df['Period']).dt.to_period('Q').astype(str)
            q_df = turnover_df.groupby('Quarter').agg({'Exits': 'sum', 'Hires': 'sum'}).reset_index()
            q_df['Turnover Rate %'] = (q_df['Exits'] / q_df['Hires'].replace(0, 1) * 100).round(1)
            fig = px.bar(q_df, x='Quarter', y='Turnover Rate %',
                         color='Turnover Rate %', color_continuous_scale='RdYlGn_r',
                         text='Turnover Rate %')
        else:
            fig = px.bar(turnover_df, x='Period', y='Turnover Rate %',
                         color='Turnover Rate %', color_continuous_scale='RdYlGn_r',
                         text='Turnover Rate %')

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("No departure data available for turnover analysis.")
