"""Build all dashboard charts and export them as images into a multi-sheet Excel workbook."""

import io
from datetime import datetime, date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, PatternFill, Alignment
from PIL import Image as PILImage

from src.utils import _style

_NEON = ['#06B6D4', '#7C3AED', '#D946EF', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#F97316']
_VOLUNTARY_TYPES = ['Resigned', 'Dropped']
_INVOLUNTARY_TYPES = ['Terminated']


def _fig_to_xl_image(fig, width=900, height=420) -> XLImage:
    """Convert a Plotly figure to an openpyxl Image object."""
    png_bytes = pio.to_image(fig, format='png', width=width, height=height, scale=2)
    buf = io.BytesIO(png_bytes)
    img = XLImage(buf)
    img.width = width
    img.height = height
    return img


def _add_chart_sheet(wb: Workbook, sheet_name: str, fig, title: str, width=900, height=420):
    """Add a new sheet with a title row and the chart image."""
    ws = wb.create_sheet(title=sheet_name[:31])
    # Title row
    ws['A1'] = title
    ws['A1'].font = Font(bold=True, size=13, color='FFFFFF')
    ws['A1'].fill = PatternFill('solid', fgColor='1E1F35')
    ws['A1'].alignment = Alignment(horizontal='left', vertical='center')
    ws.row_dimensions[1].height = 22
    ws.column_dimensions['A'].width = 120
    # Chart image anchored at A3
    img = _fig_to_xl_image(fig, width=width, height=height)
    ws.add_image(img, 'A3')
    return ws


def build_charts_excel(filtered_df: pd.DataFrame, kpis: dict) -> io.BytesIO:
    """
    Generate an Excel workbook where every sheet contains one chart image.
    Returns a BytesIO buffer ready for st.download_button.
    """
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
    wb = Workbook()
    # Remove default empty sheet
    wb.remove(wb.active)

    today = pd.Timestamp(datetime.now())

    # ── 1. Gender Distribution ────────────────────────────────────────────
    gender_counts = filtered_df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.pie(gender_counts, values='Count', names='Gender',
                 color_discrete_sequence=['#7C3AED', '#D946EF'], hole=0.62)
    fig.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='#E2E8F0',
                      marker=dict(line=dict(color='#0D0E1A', width=3)))
    fig.update_layout(showlegend=True)
    _add_chart_sheet(wb, 'Gender Distribution', _style(fig, 420), 'Gender Distribution')

    # ── 2. Employment Status ──────────────────────────────────────────────
    status_counts = filtered_df['Employee Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig = px.pie(status_counts, values='Count', names='Status',
                 color_discrete_sequence=['#06B6D4', '#EF4444'], hole=0.62)
    fig.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='#E2E8F0',
                      marker=dict(line=dict(color='#0D0E1A', width=3)))
    fig.update_layout(showlegend=True)
    _add_chart_sheet(wb, 'Employment Status', _style(fig, 420), 'Employment Status')

    # ── 3. Department Breakdown ───────────────────────────────────────────
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': '#06B6D4', 'Departed': '#EF4444'},
                 barmode='group', text_auto=True)
    fig.update_traces(textfont_size=9, textposition='outside', marker_line_width=0, opacity=0.9)
    fig.update_layout(xaxis_tickangle=-35, bargap=0.28)
    _add_chart_sheet(wb, 'Department Breakdown', _style(fig, 440), 'Department Breakdown', height=440)

    # ── 4. Age Distribution ───────────────────────────────────────────────
    if 'Age' in filtered_df.columns:
        age_df = filtered_df[filtered_df['Age'] > 0]
        if len(age_df) > 0:
            fig = px.histogram(age_df, x='Age', nbins=20,
                               color_discrete_sequence=['#7C3AED'], marginal='box', opacity=0.85)
            fig.update_traces(marker_line_color='#0D0E1A', marker_line_width=1)
            _add_chart_sheet(wb, 'Age Distribution', _style(fig, 440), 'Age Distribution', height=440)

    # ── 5. Exit Types ─────────────────────────────────────────────────────
    if len(departed_df) > 0:
        exit_counts = departed_df['Exit Type'].value_counts().reset_index()
        exit_counts.columns = ['Exit Type', 'Count']
        fig = px.pie(exit_counts, values='Count', names='Exit Type',
                     color_discrete_sequence=['#F59E0B', '#EF4444', '#A78BFA', '#06B6D4'], hole=0.62)
        fig.update_traces(textinfo='percent+label', textfont_size=12, textfont_color='#E2E8F0',
                          marker=dict(line=dict(color='#0D0E1A', width=3)))
        _add_chart_sheet(wb, 'Exit Types', _style(fig, 420), 'Exit Types')

    # ── 6. Exit Reason Categories ─────────────────────────────────────────
    if len(departed_df) > 0 and 'Exit Reason Category' in departed_df.columns:
        reason_counts = departed_df['Exit Reason Category'].value_counts().reset_index()
        reason_counts.columns = ['Category', 'Count']
        fig = px.bar(reason_counts, x='Count', y='Category', orientation='h',
                     color='Count',
                     color_continuous_scale=[[0, '#3B0764'], [0.5, '#7C3AED'], [1, '#D946EF']])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
        _add_chart_sheet(wb, 'Exit Reason Categories', _style(fig, 440),
                         'Exit Reason Categories', height=440)

    # ── 7. Departure Rate by Department ──────────────────────────────────
    dept_attrition = filtered_df.groupby('Department').agg(
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
        Total=('Employee Status', 'count')
    ).reset_index()
    dept_attrition['Departure Rate %'] = (
        dept_attrition['Departed'] / dept_attrition['Total'] * 100
    ).round(1)
    dept_attrition = dept_attrition.sort_values('Departure Rate %', ascending=False)
    fig = px.bar(dept_attrition, x='Department', y='Departure Rate %',
                 color='Departure Rate %',
                 color_continuous_scale=[[0, '#064E3B'], [0.5, '#7C3AED'], [1, '#EF4444']],
                 text='Departure Rate %')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                      marker_line_width=0, opacity=0.92)
    fig.update_layout(xaxis_tickangle=-35, coloraxis_showscale=False)
    _add_chart_sheet(wb, 'Dept Departure Rate', _style(fig, 440),
                     'Departure Rate by Department', height=440)

    # ── 8. Tenure Distribution ────────────────────────────────────────────
    if 'Tenure (Months)' in filtered_df.columns:
        fig = px.histogram(filtered_df, x='Tenure (Months)', nbins=30,
                           color='Employee Status',
                           color_discrete_map={'Active': '#10B981', 'Departed': '#EF4444'},
                           marginal='box')
        _add_chart_sheet(wb, 'Tenure Distribution', _style(fig, 420), 'Tenure Distribution')

        # ── 9. Avg Tenure by Department ───────────────────────────────────
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
        _add_chart_sheet(wb, 'Tenure by Dept', _style(fig, 450),
                         'Average Tenure by Department', height=450)

    # ── 10. Time-to-Departure by Department ──────────────────────────────
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
        _add_chart_sheet(wb, 'Time to Departure', _style(fig, max(360, len(ttd_dept) * 38)),
                         'Avg Tenure at Exit (Time-to-Departure)',
                         height=max(360, len(ttd_dept) * 38))

    # ── 11. Early Departure Rate by Department ────────────────────────────
    if len(departed_df) > 0 and 'Tenure (Months)' in departed_df.columns:
        dept_stats = departed_df.groupby('Department').agg(
            Total_Departed=('Tenure (Months)', 'count'),
            Early_Departed=('Tenure (Months)', lambda x: (x <= 3).sum()),
        ).reset_index()
        dept_stats['Early Departure Rate %'] = (
            dept_stats['Early_Departed'] / dept_stats['Total_Departed'] * 100
        ).round(1)
        dept_stats = dept_stats.sort_values('Early Departure Rate %', ascending=False)
        fig = px.bar(dept_stats, x='Department', y='Early Departure Rate %',
                     text='Early Departure Rate %', color='Early Departure Rate %',
                     color_continuous_scale=[[0, '#064E3B'], [0.5, '#F59E0B'], [1, '#EF4444']])
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                          marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        _add_chart_sheet(wb, 'Early Departure Rate', _style(fig, 460),
                         'Early Departure Rate by Dept (Left ≤3 Months)', height=460)

    # ── 12. Monthly Hiring vs Departures ─────────────────────────────────
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
        _add_chart_sheet(wb, 'Monthly Hiring vs Departures', _style(fig, 460),
                         'Monthly Hiring vs Departures', height=460)

    # ── 13. Headcount by Year ─────────────────────────────────────────────
    if 'Join Year' in filtered_df.columns:
        headcount = (
            filtered_df[filtered_df['Join Year'] > 2000]
            .groupby(['Join Year', 'Employee Status']).size().reset_index(name='Count')
        )
        if len(headcount) > 0:
            fig = px.bar(headcount, x='Join Year', y='Count', color='Employee Status',
                         color_discrete_map={'Active': '#10B981', 'Departed': '#EF4444'},
                         barmode='stack')
            _add_chart_sheet(wb, 'Headcount by Year', _style(fig, 420),
                             'Headcount Summary by Year')

    # ── 14. Vendor Analysis ───────────────────────────────────────────────
    if 'Vendor' in filtered_df.columns:
        vendor_counts = filtered_df['Vendor'].value_counts().reset_index()
        vendor_counts.columns = ['Vendor', 'Count']
        fig = px.pie(vendor_counts, values='Count', names='Vendor',
                     color_discrete_sequence=_NEON, hole=0.4)
        fig.update_traces(textinfo='percent+value', textfont_size=13)
        _add_chart_sheet(wb, 'Vendor Analysis', _style(fig, 420), 'Vendor / Source Analysis')

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
