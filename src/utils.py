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


def export_charts_excel(filtered_df, kpis):
    """
    Export the data behind every dashboard chart as a multi-sheet Excel file.
    Each sheet corresponds to one chart/section.
    """
    departed_df = filtered_df[filtered_df['Employee Status'] == 'Departed']
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:

        # ── Overview ──────────────────────────────────────────────────────
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        gender_counts.to_excel(writer, sheet_name='Gender Distribution', index=False)

        status_counts = filtered_df['Employee Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        status_counts.to_excel(writer, sheet_name='Employment Status', index=False)

        dept_data = (
            filtered_df.groupby(['Department', 'Employee Status'])
            .size().reset_index(name='Count')
        )
        dept_data.to_excel(writer, sheet_name='Department Breakdown', index=False)

        if 'Age' in filtered_df.columns:
            age_df = filtered_df[filtered_df['Age'] > 0][['Age', 'Employee Status']]
            age_df.to_excel(writer, sheet_name='Age Distribution', index=False)

        # ── Attrition ────────────────────────────────────────────────────
        if len(departed_df) > 0:
            exit_counts = departed_df['Exit Type'].value_counts().reset_index()
            exit_counts.columns = ['Exit Type', 'Count']
            exit_counts.to_excel(writer, sheet_name='Exit Types', index=False)

            if 'Exit Reason Category' in departed_df.columns:
                reason_counts = departed_df['Exit Reason Category'].value_counts().reset_index()
                reason_counts.columns = ['Category', 'Count']
                reason_counts.to_excel(writer, sheet_name='Exit Reasons', index=False)

            dept_attrition = filtered_df.groupby('Department').agg(
                Active=('Employee Status', lambda x: (x == 'Active').sum()),
                Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
                Total=('Employee Status', 'count')
            ).reset_index()
            dept_attrition['Departure Rate %'] = (
                dept_attrition['Departed'] / dept_attrition['Total'] * 100
            ).round(1)
            dept_attrition.sort_values('Departure Rate %', ascending=False).to_excel(
                writer, sheet_name='Dept Departure Rate', index=False
            )

        # ── Tenure & Retention ───────────────────────────────────────────
        if 'Tenure (Months)' in filtered_df.columns:
            tenure_dept = (
                filtered_df.groupby('Department')['Tenure (Months)']
                .agg(['mean', 'median', 'count']).round(1)
                .rename(columns={'mean': 'Avg Tenure', 'median': 'Median Tenure', 'count': 'Count'})
                .reset_index()
                .sort_values('Avg Tenure', ascending=False)
            )
            tenure_dept.to_excel(writer, sheet_name='Tenure by Department', index=False)

            if len(departed_df) > 0:
                ttd_dept = (
                    departed_df.groupby('Department')['Tenure (Months)']
                    .agg(Avg='mean', Median='median', Count='count')
                    .round(1).reset_index().sort_values('Avg')
                )
                ttd_dept.to_excel(writer, sheet_name='Time to Departure', index=False)

                dept_stats = departed_df.groupby('Department').agg(
                    Total_Departed=('Tenure (Months)', 'count'),
                    Early_Departed=('Tenure (Months)', lambda x: (x <= 3).sum()),
                ).reset_index()
                dept_stats['Early Departure Rate %'] = (
                    dept_stats['Early_Departed'] / dept_stats['Total_Departed'] * 100
                ).round(1)
                dept_stats.to_excel(writer, sheet_name='Early Departure Rate', index=False)

        # ── Workforce ────────────────────────────────────────────────────
        if 'Vendor' in filtered_df.columns:
            vendor_attrition = filtered_df.groupby('Vendor').agg(
                Total=('Employee Status', 'count'),
                Departed=('Employee Status', lambda x: (x == 'Departed').sum())
            ).reset_index()
            vendor_attrition['Departure Rate %'] = (
                vendor_attrition['Departed'] / vendor_attrition['Total'] * 100
            ).round(1)
            vendor_attrition.to_excel(writer, sheet_name='Vendor Analysis', index=False)

        # ── Trends ───────────────────────────────────────────────────────
        if 'Join Month' in filtered_df.columns:
            hiring = filtered_df.groupby('Join Month').size().rename('Hires').reset_index()
            hiring.columns = ['Month', 'Hires']
            if len(departed_df) > 0 and 'Exit Month' in departed_df.columns:
                exits = departed_df.groupby('Exit Month').size().rename('Exits').reset_index()
                exits.columns = ['Month', 'Exits']
                trend = hiring.merge(exits, on='Month', how='outer').fillna(0).sort_values('Month')
                trend['Net'] = trend['Hires'].astype(int) - trend['Exits'].astype(int)
            else:
                trend = hiring.sort_values('Month')
            trend.to_excel(writer, sheet_name='Monthly Hiring vs Departures', index=False)

        if 'Join Year' in filtered_df.columns:
            headcount = (
                filtered_df.groupby(['Join Year', 'Employee Status'])
                .size().unstack(fill_value=0).reset_index()
            )
            headcount[headcount['Join Year'] > 2000].to_excel(
                writer, sheet_name='Headcount by Year', index=False
            )

        # ── KPI Summary ──────────────────────────────────────────────────
        kpi_summary = pd.DataFrame([{
            'Metric': 'Total Employees', 'Value': kpis['total'],
        }, {
            'Metric': 'Active Employees', 'Value': kpis['active'],
        }, {
            'Metric': 'Departed Employees', 'Value': kpis['departed'],
        }, {
            'Metric': 'Departure Rate %', 'Value': round(kpis['attrition_rate'], 1),
        }, {
            'Metric': 'Retention Rate %', 'Value': round(kpis['retention_rate'], 1),
        }, {
            'Metric': 'Avg Tenure (Months)', 'Value': round(kpis['avg_tenure'], 1),
        }, {
            'Metric': 'Avg Age', 'Value': round(kpis['avg_age'], 0) if not pd.isna(kpis['avg_age']) else 'N/A',
        }, {
            'Metric': 'Gender Ratio (M:F)', 'Value': kpis['gender_ratio'],
        }])
        kpi_summary.to_excel(writer, sheet_name='KPI Summary', index=False)

    buffer.seek(0)
    return buffer
