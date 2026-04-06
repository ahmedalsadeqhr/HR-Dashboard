import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_processing import get_manager_attrition
from src.utils import _style


_VOLUNTARY_TYPES   = ['Resigned', 'Dropped']
_INVOLUNTARY_TYPES = ['Terminated']

_NEON = ['#06B6D4', '#7C3AED', '#D946EF', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#F97316']


def _tenure_bucket(months: float) -> str:
    days = months * 30.44
    if days <= 10:
        return '≤ 10 Days'
    elif months <= 1:
        return '10 Days – 1 Month'
    elif months <= 3:
        return '1 – 3 Months'
    elif months <= 6:
        return '3 – 6 Months'
    elif months <= 12:
        return '6 – 12 Months'
    else:
        return '> 1 Year'


_BUCKET_ORDER = ['≤ 10 Days', '10 Days – 1 Month', '1 – 3 Months',
                 '3 – 6 Months', '6 – 12 Months', '> 1 Year']


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
                     color_discrete_sequence=['#F59E0B', '#EF4444', '#A78BFA', '#06B6D4'],
                     hole=0.62)
        fig.update_traces(
            textinfo='percent+label', textfont_size=11, textfont_color='#E2E8F0',
            marker=dict(line=dict(color='#0D0E1A', width=3)), pull=[0.04, 0, 0, 0],
        )
        fig.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.12,
                          font=dict(color='#94A3B8')))
        st.plotly_chart(_style(fig, 360), use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Exit Reason Categories")
        reason_counts = departed_df['Exit Reason Category'].value_counts().reset_index()
        reason_counts.columns = ['Category', 'Count']
        fig = px.bar(reason_counts, x='Count', y='Category', orientation='h',
                     color='Count',
                     color_continuous_scale=[[0, '#3B0764'], [0.5, '#7C3AED'], [1, '#D946EF']])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
        fig.update_traces(marker_line_width=0, opacity=0.9)
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
        'Type': ['Voluntary', 'Involuntary'],
        'Count': [voluntary, involuntary]
    })
    fig = px.pie(vol_data, values='Count', names='Type',
                 color_discrete_sequence=['#06B6D4', '#EF4444'], hole=0.62)
    fig.update_traces(
        textinfo='percent+label', textfont_size=11, textfont_color='#E2E8F0',
        marker=dict(line=dict(color='#0D0E1A', width=3)), pull=[0.04, 0],
    )
    fig.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.12,
                      font=dict(color='#94A3B8')))
    st.plotly_chart(_style(fig, 360), use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    # ── 1. Departed employees: tenure-at-exit bucket distribution ──────────
    st.subheader("Departed Employees by Tenure at Exit")
    if 'Tenure (Months)' in departed_df.columns:
        tenure_data = departed_df[departed_df['Tenure (Months)'] >= 0].copy()
        tenure_data['Tenure Bucket'] = tenure_data['Tenure (Months)'].apply(_tenure_bucket)
        bucket_counts = (
            tenure_data['Tenure Bucket']
            .value_counts()
            .reindex(_BUCKET_ORDER)
            .dropna()
            .reset_index()
        )
        bucket_counts.columns = ['Tenure Bucket', 'Count']
        total_dep = len(tenure_data)
        fig = px.pie(
            bucket_counts, values='Count', names='Tenure Bucket',
            color_discrete_sequence=_NEON,
        )
        fig.update_traces(
            texttemplate='<b>%{label}</b><br>%{value} (%{percent})',
            textposition='outside',
            textfont_size=12, textfont_color='#CBD5E1',
            marker=dict(line=dict(color='#0D0E1A', width=2)),
            pull=[0.04] * len(bucket_counts),
        )
        fig.update_layout(
            title=None,
            showlegend=True,
            legend=dict(orientation='h', y=-0.08, font=dict(color='#94A3B8', size=12)),
            margin=dict(t=20, b=80, l=80, r=80),
        )
        st.plotly_chart(_style(fig, 540), use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Tenure data not available.")

    st.markdown("---")

    # ── 2. Voluntary exit reason breakdown ────────────────────────────────
    if 'Exit Reason Category' in departed_df.columns:
        vol_df   = departed_df[departed_df['Exit Type'].isin(_VOLUNTARY_TYPES)]
        invol_df = departed_df[departed_df['Exit Type'].isin(_INVOLUNTARY_TYPES)]

        st.subheader(f"Voluntary Exit Reasons — {len(vol_df)} employees (Resigned / Dropped)")
        if len(vol_df) > 0:
            vol_reasons = (
                vol_df['Exit Reason Category'].dropna()
                .value_counts().reset_index()
            )
            vol_reasons.columns = ['Reason', 'Count']
            vol_total = vol_reasons['Count'].sum()
            vol_reasons['Pct'] = (vol_reasons['Count'] / vol_total * 100).round(1)
            vol_reasons['Label'] = vol_reasons.apply(
                lambda r: f"{r['Count']}  ({r['Pct']}%)", axis=1
            )
            fig = px.bar(
                vol_reasons.sort_values('Count'),
                x='Count', y='Reason', orientation='h',
                text='Label',
                color='Count',
                color_continuous_scale=[[0, '#1E1B4B'], [0.5, '#7C3AED'], [1, '#06B6D4']],
            )
            fig.update_traces(
                textposition='outside',
                textfont=dict(color='#CBD5E1', size=12),
                marker_line_width=0,
            )
            fig.update_layout(
                title=None,
                coloraxis_showscale=False,
                xaxis=dict(title='Number of Employees'),
                yaxis=dict(title=None, tickfont=dict(size=12, color='#94A3B8')),
                margin=dict(t=10, b=40, l=200, r=100),
            )
            st.plotly_chart(_style(fig, max(380, len(vol_reasons) * 44)),
                            use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No voluntary departures in current selection.")

        st.markdown("---")

        # ── 3. Involuntary exit reason breakdown ──────────────────────────
        st.subheader(f"Involuntary Exit Reasons — {len(invol_df)} employees (Terminated)")
        if len(invol_df) > 0:
            invol_reasons = (
                invol_df['Exit Reason Category'].dropna()
                .value_counts().reset_index()
            )
            invol_reasons.columns = ['Reason', 'Count']
            invol_total = invol_reasons['Count'].sum()
            invol_reasons['Pct'] = (invol_reasons['Count'] / invol_total * 100).round(1)
            invol_reasons['Label'] = invol_reasons.apply(
                lambda r: f"{r['Count']}  ({r['Pct']}%)", axis=1
            )
            fig = px.bar(
                invol_reasons.sort_values('Count'),
                x='Count', y='Reason', orientation='h',
                text='Label',
                color='Count',
                color_continuous_scale=[[0, '#450A0A'], [0.5, '#EF4444'], [1, '#F97316']],
            )
            fig.update_traces(
                textposition='outside',
                textfont=dict(color='#CBD5E1', size=12),
                marker_line_width=0,
            )
            fig.update_layout(
                title=None,
                coloraxis_showscale=False,
                xaxis=dict(title='Number of Employees'),
                yaxis=dict(title=None, tickfont=dict(size=12, color='#94A3B8')),
                margin=dict(t=10, b=40, l=200, r=100),
            )
            st.plotly_chart(_style(fig, max(380, len(invol_reasons) * 44)),
                            use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No involuntary departures in current selection.")

    st.markdown("---")

    # Attrition by department
    st.subheader("Departure Rate by Department")
    dept_attrition = filtered_df.groupby('Department').agg(
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
        Total=('Employee Status', 'count')
    ).reset_index()
    dept_attrition['Departure Rate %'] = (dept_attrition['Departed'] / dept_attrition['Total'] * 100).round(1)
    dept_attrition = dept_attrition.sort_values('Departure Rate %', ascending=False)

    fig = px.bar(dept_attrition, x='Department', y='Departure Rate %',
                 color='Departure Rate %',
                 color_continuous_scale=[[0, '#064E3B'], [0.5, '#7C3AED'], [1, '#EF4444']],
                 text='Departure Rate %')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                      marker_line_width=0, opacity=0.92,
                      textfont=dict(color='#94A3B8', size=10))
    fig.update_layout(xaxis_tickangle=-35, coloraxis_showscale=False)
    st.plotly_chart(_style(fig, 440), use_container_width=True, config=CHART_CONFIG)

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
