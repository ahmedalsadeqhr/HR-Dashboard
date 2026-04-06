import io
import pandas as pd
from datetime import datetime


_DARK_BG   = 'rgba(0,0,0,0)'         # transparent — card provides background
_GRID      = 'rgba(255,255,255,0.05)'
_AXIS_LINE = 'rgba(255,255,255,0.08)'
_TICK_CLR  = '#475569'
_TEXT_CLR  = '#94A3B8'
_FONT_FAM  = 'Space Grotesk, Inter, system-ui, sans-serif'


def _style(fig, height=400):
    """Apply dark-neon chart styling consistent with dashboard theme."""
    fig.update_layout(
        height=height,
        font=dict(family=_FONT_FAM, size=12, color=_TEXT_CLR),
        paper_bgcolor=_DARK_BG,
        plot_bgcolor=_DARK_BG,
        margin=dict(t=44, b=36, l=36, r=20),
        legend=dict(
            bgcolor='rgba(22,23,40,0.8)',
            bordercolor=_AXIS_LINE,
            borderwidth=1,
            font=dict(size=11, color='#CBD5E1'),
        ),
        xaxis=dict(
            gridcolor=_GRID,
            linecolor=_AXIS_LINE,
            tickfont=dict(size=10, color=_TICK_CLR),
            title_font=dict(size=11, color=_TICK_CLR),
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor=_GRID,
            linecolor=_AXIS_LINE,
            tickfont=dict(size=10, color=_TICK_CLR),
            title_font=dict(size=11, color=_TICK_CLR),
            showgrid=True,
        ),
        title_font=dict(size=13, color='#E2E8F0', family=_FONT_FAM),
        hoverlabel=dict(
            bgcolor='#1E1F35',
            bordercolor='rgba(124,58,237,0.5)',
            font=dict(color='#F1F5F9', size=12),
        ),
    )
    return fig


def delta(filtered_val, all_val, suffix="", filtered_len=0, full_len=0):
    """Return delta string if filters are active, else None."""
    if filtered_len == full_len:
        return None
    diff = filtered_val - all_val
    if abs(diff) < 0.05:
        return None
    return f"{diff:+.1f}{suffix}"


def generate_summary_report(filtered_df, df, kpis):
    """Generate a text summary report of HR metrics."""
    summary_lines = [
        "HR ANALYTICS SUMMARY REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Data: {len(filtered_df)} records (filtered from {len(df)} total)",
        "",
        "=== KEY METRICS ===",
        f"Total Employees: {kpis['total']:,}",
        f"Active: {kpis['active']:,}",
        f"Departed: {kpis['departed']:,}",
        f"Departure Rate: {kpis['attrition_rate']:.1f}%",
        f"Retention Rate: {kpis['retention_rate']:.1f}%",
        f"Avg Tenure: {kpis['avg_tenure']:.1f} months",
        f"Avg Age: {kpis['avg_age']:.0f}" if not pd.isna(kpis['avg_age']) else "Avg Age: N/A",
        f"Gender (M:F): {kpis['gender_ratio']}",
        f"Contractor Ratio: {kpis['contractor_ratio']:.1f}%",
        f"Nationalities: {kpis['nationality_count']}",
        f"Probation Pass Rate: {kpis['probation_pass_rate']:.1f}%",
        f"YoY Growth: {kpis['growth_rate']:+.1f}%",
        "",
        "=== DEPARTMENT BREAKDOWN ===",
    ]
    dept_summary = filtered_df.groupby('Department').agg(
        Total=('Employee Status', 'count'),
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
    ).reset_index()
    dept_summary['Attrition %'] = (dept_summary['Departed'] / dept_summary['Total'] * 100).round(1)
    for _, row in dept_summary.iterrows():
        summary_lines.append(
            f"  {row['Department']}: {row['Total']} total, {row['Active']} active, "
            f"{row['Departed']} departed ({row['Attrition %']}% attrition)"
        )

    summary_lines += ["", "=== TOP EXIT REASONS ==="]
    departed_summary = filtered_df[filtered_df['Employee Status'] == 'Departed']
    if len(departed_summary) > 0 and 'Exit Reason Category' in departed_summary.columns:
        for reason, count in departed_summary['Exit Reason Category'].value_counts().head(10).items():
            summary_lines.append(f"  {reason}: {count}")

    return "\n".join(summary_lines)


def export_excel(filtered_df):
    """Export filtered dataframe to Excel bytes buffer."""
    excel_buffer = io.BytesIO()
    filtered_df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    return excel_buffer
