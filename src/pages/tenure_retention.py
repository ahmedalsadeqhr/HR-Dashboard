import streamlit as st
import plotly.express as px

from src.utils import _style


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

    # ── Time-to-Departure ─────────────────────────────────────────────────
    st.subheader("Average Tenure at Exit (Time-to-Departure)")
    dep_all = filtered_df[filtered_df['Employee Status'] == 'Departed']

    if len(dep_all) > 0 and 'Tenure (Months)' in dep_all.columns:
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Time-to-Departure", f"{dep_all['Tenure (Months)'].mean():.1f} mo")
        col2.metric("Median", f"{dep_all['Tenure (Months)'].median():.1f} mo")
        col3.metric("Left ≤ 1 Month", f"{(dep_all['Tenure (Months)'] <= 1).sum():,}")

        # By Department
        ttd_dept = (
            dep_all.groupby('Department')['Tenure (Months)']
            .agg(Avg='mean', Median='median', Count='count')
            .round(1).reset_index()
            .sort_values('Avg')
        )
        fig = px.bar(
            ttd_dept, x='Avg', y='Department', orientation='h',
            text='Avg', color='Avg',
            color_continuous_scale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
            hover_data=['Median', 'Count'],
        )
        fig.update_traces(texttemplate='%{text:.1f} mo', textposition='outside',
                          textfont=dict(color='#CBD5E1', size=11), marker_line_width=0)
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis=dict(title='Avg Months Before Departure'),
            yaxis=dict(title=None, tickfont=dict(size=11, color='#94A3B8')),
            margin=dict(t=10, b=40, l=160, r=80),
        )
        st.plotly_chart(_style(fig, max(360, len(ttd_dept) * 38)),
                        use_container_width=True, config=CHART_CONFIG)

        # By Vendor and by Exit Type side-by-side
        col1, col2 = st.columns(2)

        with col1:
            if 'Vendor' in dep_all.columns:
                ttd_vendor = (
                    dep_all.groupby('Vendor')['Tenure (Months)']
                    .agg(Avg='mean', Count='count').round(1).reset_index().sort_values('Avg')
                )
                st.subheader("By Vendor")
                fig = px.bar(
                    ttd_vendor, x='Avg', y='Vendor', orientation='h',
                    text='Avg', color='Avg',
                    color_continuous_scale=[[0, '#7C3AED'], [1, '#06B6D4']],
                    hover_data=['Count'],
                )
                fig.update_traces(texttemplate='%{text:.1f} mo', textposition='outside',
                                  textfont=dict(color='#CBD5E1', size=11), marker_line_width=0)
                fig.update_layout(coloraxis_showscale=False,
                                  yaxis=dict(title=None, tickfont=dict(size=11, color='#94A3B8')),
                                  margin=dict(t=10, b=30, l=130, r=80))
                st.plotly_chart(_style(fig, max(300, len(ttd_vendor) * 42)),
                                use_container_width=True, config=CHART_CONFIG)

        with col2:
            if 'Exit Type' in dep_all.columns:
                ttd_exit = (
                    dep_all.groupby('Exit Type')['Tenure (Months)']
                    .agg(Avg='mean', Count='count').round(1).reset_index().sort_values('Avg')
                )
                st.subheader("By Exit Type")
                fig = px.bar(
                    ttd_exit, x='Avg', y='Exit Type', orientation='h',
                    text='Avg', color='Avg',
                    color_continuous_scale=[[0, '#D946EF'], [1, '#F59E0B']],
                    hover_data=['Count'],
                )
                fig.update_traces(texttemplate='%{text:.1f} mo', textposition='outside',
                                  textfont=dict(color='#CBD5E1', size=11), marker_line_width=0)
                fig.update_layout(coloraxis_showscale=False,
                                  yaxis=dict(title=None, tickfont=dict(size=11, color='#94A3B8')),
                                  margin=dict(t=10, b=30, l=130, r=80))
                st.plotly_chart(_style(fig, max(300, len(ttd_exit) * 42)),
                                use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("No departure data available for time-to-departure analysis.")

    st.markdown("---")

    # ── Probation Pass/Fail Rate by Department ────────────────────────────
    st.subheader("Probation Pass / Fail Rate by Department")
    if 'Probation Completed' in filtered_df.columns:
        prob_df = filtered_df[filtered_df['Probation Completed'] != 'No Data'].copy()
        if len(prob_df) > 0:
            prob_df['Outcome'] = prob_df['Probation Completed'].map(
                lambda s: 'Passed' if s in ('Completed', 'Completed Before Exit') else
                          'Left During Probation' if s == 'Left During Probation' else 'In Probation'
            )
            prob_dept = (
                prob_df.groupby(['Department', 'Outcome']).size()
                .reset_index(name='Count')
            )
            dept_totals = prob_dept.groupby('Department')['Count'].transform('sum')
            prob_dept['Pct'] = (prob_dept['Count'] / dept_totals * 100).round(1)

            # Summary metrics
            passed = (prob_df['Outcome'] == 'Passed').sum() if 'Outcome' in prob_df.columns else 0
            left   = (prob_df['Probation Completed'] == 'Left During Probation').sum()
            total_prob = len(prob_df)
            c1, c2, c3 = st.columns(3)
            c1.metric("Passed Probation", f"{passed:,} ({passed/total_prob*100:.1f}%)")
            c2.metric("Left During Probation", f"{left:,} ({left/total_prob*100:.1f}%)")
            c3.metric("Employees in Scope", f"{total_prob:,}")

            fig = px.bar(
                prob_dept, x='Department', y='Pct', color='Outcome',
                color_discrete_map={
                    'Passed':               '#10B981',
                    'Left During Probation':'#EF4444',
                    'In Probation':         '#F59E0B',
                },
                barmode='stack', text='Pct',
            )
            fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside',
                              textfont=dict(color='#FFFFFF', size=10))
            fig.update_layout(
                xaxis_tickangle=-35,
                yaxis=dict(title='% of Employees', ticksuffix='%'),
                legend=dict(orientation='h', y=1.08),
            )
            st.plotly_chart(_style(fig, 460), use_container_width=True, config=CHART_CONFIG)

            # Detail table
            prob_table = (
                prob_df.groupby('Department')['Outcome']
                .value_counts().unstack(fill_value=0).reset_index()
            )
            if 'Passed' in prob_table.columns and 'Left During Probation' in prob_table.columns:
                prob_table['Pass Rate %'] = (
                    prob_table['Passed'] / prob_table.iloc[:, 1:].sum(axis=1) * 100
                ).round(1)
            st.dataframe(prob_table, use_container_width=True, hide_index=True)
        else:
            st.info("No probation data available.")
    else:
        st.info("Probation Completed column not found in data.")

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
