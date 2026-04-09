"""Build all dashboard charts and export them as a single interactive HTML report."""

import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from src.utils import _style

_NEON = ['#06B6D4', '#7C3AED', '#D946EF', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#F97316']


def _chart_html(fig, title: str, first: bool = False) -> str:
    """Return an HTML block with a section title + embedded Plotly chart."""
    plotlyjs = 'cdn' if first else False
    chart = pio.to_html(fig, include_plotlyjs=plotlyjs, full_html=False,
                        config={'displayModeBar': True, 'responsive': True})
    return f"""
    <div class="chart-block">
        <h2>{title}</h2>
        {chart}
    </div>
    """


def build_charts_excel(filtered_df: pd.DataFrame, kpis: dict) -> io.BytesIO:
    """
    Generate a single HTML report with all dashboard charts embedded.
    Returns a BytesIO buffer ready for st.download_button.
    (Named build_charts_excel for API compatibility — returns HTML bytes.)
    """
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
    sections = []
    first = True

    def add(fig, title, height=420):
        nonlocal first
        sections.append(_chart_html(_style(fig, height), title, first))
        first = False

    # ── 1. Gender Distribution ────────────────────────────────────────────
    gender_counts = filtered_df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.pie(gender_counts, values='Count', names='Gender',
                 color_discrete_sequence=['#7C3AED', '#D946EF'], hole=0.62)
    fig.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='#E2E8F0',
                      marker=dict(line=dict(color='#0D0E1A', width=3)))
    add(fig, 'Gender Distribution')

    # ── 2. Employment Status ──────────────────────────────────────────────
    status_counts = filtered_df['Employee Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig = px.pie(status_counts, values='Count', names='Status',
                 color_discrete_sequence=['#06B6D4', '#EF4444'], hole=0.62)
    fig.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='#E2E8F0',
                      marker=dict(line=dict(color='#0D0E1A', width=3)))
    add(fig, 'Employment Status')

    # ── 3. Department Breakdown ───────────────────────────────────────────
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': '#06B6D4', 'Departed': '#EF4444'},
                 barmode='group', text_auto=True)
    fig.update_traces(textfont_size=9, textposition='outside', marker_line_width=0, opacity=0.9)
    fig.update_layout(xaxis_tickangle=-35, bargap=0.28)
    add(fig, 'Department Breakdown', 460)

    # ── 4. Age Distribution ───────────────────────────────────────────────
    if 'Age' in filtered_df.columns:
        age_df = filtered_df[filtered_df['Age'] > 0]
        if len(age_df) > 0:
            fig = px.histogram(age_df, x='Age', nbins=20,
                               color_discrete_sequence=['#7C3AED'], marginal='box', opacity=0.85)
            add(fig, 'Age Distribution', 460)

    # ── 5. Exit Types ─────────────────────────────────────────────────────
    if len(departed_df) > 0:
        exit_counts = departed_df['Exit Type'].value_counts().reset_index()
        exit_counts.columns = ['Exit Type', 'Count']
        fig = px.pie(exit_counts, values='Count', names='Exit Type',
                     color_discrete_sequence=['#F59E0B', '#EF4444', '#A78BFA', '#06B6D4'], hole=0.62)
        fig.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='#E2E8F0',
                          marker=dict(line=dict(color='#0D0E1A', width=3)))
        add(fig, 'Exit Types')

    # ── 6. Exit Reason Categories ─────────────────────────────────────────
    if len(departed_df) > 0 and 'Exit Reason Category' in departed_df.columns:
        reason_counts = departed_df['Exit Reason Category'].value_counts().reset_index()
        reason_counts.columns = ['Category', 'Count']
        fig = px.bar(reason_counts, x='Count', y='Category', orientation='h',
                     color='Count',
                     color_continuous_scale=[[0, '#3B0764'], [0.5, '#7C3AED'], [1, '#D946EF']])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
        add(fig, 'Exit Reason Categories', 460)

    # ── 7. Departure Rate by Department ──────────────────────────────────
    dept_attrition = filtered_df.groupby('Department').agg(
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
        Total=('Employee Status', 'count')
    ).reset_index()
    dept_attrition['Departure Rate %'] = (
        dept_attrition['Departed'] / dept_attrition['Total'] * 100
    ).round(1)
    fig = px.bar(dept_attrition.sort_values('Departure Rate %', ascending=False),
                 x='Department', y='Departure Rate %',
                 color='Departure Rate %',
                 color_continuous_scale=[[0, '#064E3B'], [0.5, '#7C3AED'], [1, '#EF4444']],
                 text='Departure Rate %')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                      marker_line_width=0, opacity=0.92)
    fig.update_layout(xaxis_tickangle=-35, coloraxis_showscale=False)
    add(fig, 'Departure Rate by Department', 460)

    # ── 8. Tenure Distribution ────────────────────────────────────────────
    if 'Tenure (Months)' in filtered_df.columns:
        fig = px.histogram(filtered_df, x='Tenure (Months)', nbins=30,
                           color='Employee Status',
                           color_discrete_map={'Active': '#10B981', 'Departed': '#EF4444'},
                           marginal='box')
        add(fig, 'Tenure Distribution')

        tenure_dept = (
            filtered_df.groupby('Department')['Tenure (Months)']
            .agg(['mean', 'median', 'count']).round(1)
            .rename(columns={'mean': 'Avg Tenure', 'median': 'Median Tenure', 'count': 'Count'})
            .reset_index().sort_values('Avg Tenure', ascending=False)
        )
        fig = px.bar(tenure_dept, x='Department', y='Avg Tenure',
                     color='Avg Tenure', color_continuous_scale='Blues',
                     text='Avg Tenure', hover_data=['Median Tenure', 'Count'])
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)
        add(fig, 'Average Tenure by Department', 460)

    # ── 9. Time-to-Departure ──────────────────────────────────────────────
    if len(departed_df) > 0 and 'Tenure (Months)' in departed_df.columns:
        ttd_dept = (
            departed_df.groupby('Department')['Tenure (Months)']
            .agg(Avg='mean', Median='median', Count='count')
            .round(1).reset_index().sort_values('Avg')
        )
        fig = px.bar(ttd_dept, x='Avg', y='Department', orientation='h',
                     text='Avg', color='Avg',
                     color_continuous_scale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']])
        fig.update_traces(texttemplate='%{text:.1f} mo', textposition='outside',
                          textfont=dict(color='#CBD5E1', size=11), marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False,
                          xaxis=dict(title='Avg Months Before Departure'))
        add(fig, 'Avg Tenure at Exit (Time-to-Departure)', max(380, len(ttd_dept) * 40))

    # ── 10. Early Departure Rate by Department ────────────────────────────
    if len(departed_df) > 0 and 'Tenure (Months)' in departed_df.columns:
        dept_stats = departed_df.groupby('Department').agg(
            Total_Departed=('Tenure (Months)', 'count'),
            Early_Departed=('Tenure (Months)', lambda x: (x <= 3).sum()),
        ).reset_index()
        dept_stats['Early Departure Rate %'] = (
            dept_stats['Early_Departed'] / dept_stats['Total_Departed'] * 100
        ).round(1)
        fig = px.bar(dept_stats.sort_values('Early Departure Rate %', ascending=False),
                     x='Department', y='Early Departure Rate %',
                     text='Early Departure Rate %', color='Early Departure Rate %',
                     color_continuous_scale=[[0, '#064E3B'], [0.5, '#F59E0B'], [1, '#EF4444']])
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        add(fig, 'Early Departure Rate by Dept (Left ≤3 Months)', 460)

    # ── 11. Monthly Hiring vs Departures ─────────────────────────────────
    if 'Join Month' in filtered_df.columns:
        hiring = filtered_df.groupby('Join Month').size().rename('Hires')
        exits = (
            departed_df.groupby('Exit Month').size().rename('Exits')
            if len(departed_df) > 0 and 'Exit Month' in departed_df.columns
            else pd.Series(dtype=int)
        )
        all_months = sorted(set(hiring.index.tolist() + exits.index.tolist()))
        combined = pd.DataFrame({'Month': all_months})
        combined['Hires'] = combined['Month'].map(hiring).fillna(0).astype(int)
        combined['Exits'] = combined['Month'].map(exits).fillna(0).astype(int)
        combined['Net'] = combined['Hires'] - combined['Exits']

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=combined['Month'], y=combined['Hires'],
                                 name='Hires', mode='lines+markers',
                                 line=dict(color='#10B981', width=2.5),
                                 fill='tozeroy', fillcolor='rgba(16,185,129,0.07)'))
        fig.add_trace(go.Scatter(x=combined['Month'], y=combined['Exits'],
                                 name='Departures', mode='lines+markers',
                                 line=dict(color='#EF4444', width=2.5),
                                 fill='tozeroy', fillcolor='rgba(239,68,68,0.07)'))
        fig.update_layout(xaxis=dict(tickangle=-45), legend=dict(orientation='h', y=1.08),
                          hovermode='x unified')
        add(fig, 'Monthly Hiring vs Departures', 460)

    # ── 12. Headcount by Year ─────────────────────────────────────────────
    if 'Join Year' in filtered_df.columns:
        headcount = (
            filtered_df[filtered_df['Join Year'] > 2000]
            .groupby(['Join Year', 'Employee Status']).size().reset_index(name='Count')
        )
        if len(headcount) > 0:
            fig = px.bar(headcount, x='Join Year', y='Count', color='Employee Status',
                         color_discrete_map={'Active': '#10B981', 'Departed': '#EF4444'},
                         barmode='stack')
            add(fig, 'Headcount by Year')

    # ── 13. Vendor Analysis ───────────────────────────────────────────────
    if 'Vendor' in filtered_df.columns:
        vendor_counts = filtered_df['Vendor'].value_counts().reset_index()
        vendor_counts.columns = ['Vendor', 'Count']
        fig = px.pie(vendor_counts, values='Count', names='Vendor',
                     color_discrete_sequence=_NEON, hole=0.4)
        fig.update_traces(textinfo='percent+value', textfont_size=13)
        add(fig, 'Vendor / Source Analysis')

    # ── Assemble HTML ─────────────────────────────────────────────────────
    generated = datetime.now().strftime('%Y-%m-%d %H:%M')
    total = len(filtered_df)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HR Analytics — Chart Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0D0E1A;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #F1F5F9;
    padding: 2rem;
  }}
  .report-header {{
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }}
  .report-header h1 {{
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #A78BFA, #67E8F9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .report-header p {{ color: #475569; font-size: 0.85rem; margin-top: 0.4rem; }}
  .chart-block {{
    background: #161728;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .chart-block h2 {{
    font-size: 0.95rem;
    font-weight: 700;
    color: #E2E8F0;
    margin-bottom: 1rem;
    padding-left: 10px;
    border-left: 3px solid #7C3AED;
  }}
</style>
</head>
<body>
<div class="report-header">
  <h1>HR Analytics — Chart Report</h1>
  <p>Generated: {generated} &nbsp;|&nbsp; {total:,} employees in current filter</p>
</div>
{''.join(sections)}
</body>
</html>"""

    buffer = io.BytesIO(html.encode('utf-8'))
    buffer.seek(0)
    return buffer
