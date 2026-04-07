import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils import _style


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    trends_dep_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    # ── Combined Hiring vs Departure trend ────────────────────────────────
    st.subheader("Monthly Hiring vs Departures")
    if 'Join Month' in filtered_df.columns:
        hiring  = filtered_df.groupby('Join Month').size().rename('Hires')
        exits   = (
            trends_dep_df.groupby('Exit Month').size().rename('Exits')
            if len(trends_dep_df) > 0 and 'Exit Month' in trends_dep_df.columns
            else pd.Series(dtype=int)
        )
        all_months = sorted(set(hiring.index.tolist() + exits.index.tolist()))
        combined = pd.DataFrame({'Month': all_months})
        combined['Hires']  = combined['Month'].map(hiring).fillna(0).astype(int)
        combined['Exits']  = combined['Month'].map(exits).fillna(0).astype(int)
        combined['Net']    = combined['Hires'] - combined['Exits']

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=combined['Month'], y=combined['Hires'],
            name='Hires', mode='lines+markers',
            line=dict(color='#10B981', width=2.5),
            marker=dict(size=6),
            fill='tozeroy', fillcolor='rgba(16,185,129,0.07)',
        ))
        fig.add_trace(go.Scatter(
            x=combined['Month'], y=combined['Exits'],
            name='Departures', mode='lines+markers',
            line=dict(color='#EF4444', width=2.5),
            marker=dict(size=6),
            fill='tozeroy', fillcolor='rgba(239,68,68,0.07)',
        ))
        fig.add_trace(go.Bar(
            x=combined['Month'], y=combined['Net'],
            name='Net Headcount Change',
            marker_color=[('#10B981' if v >= 0 else '#EF4444') for v in combined['Net']],
            opacity=0.35, yaxis='y2',
        ))
        fig.update_layout(
            yaxis2=dict(overlaying='y', side='right', showgrid=False,
                        title='Net Change', title_font=dict(color='#475569'),
                        tickfont=dict(color='#475569')),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation='h', y=1.08),
            hovermode='x unified',
        )
        st.plotly_chart(_style(fig, 460), use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Join Month data not available.")

    st.markdown("---")

    # Headcount by join year and status
    st.subheader("Headcount Summary by Year")
    headcount = filtered_df.groupby(['Join Year', 'Employee Status']).size().unstack(fill_value=0)
    headcount = headcount[headcount.index > 2000]
    if len(headcount) > 0:
        fig = px.bar(headcount.reset_index().melt(id_vars='Join Year', var_name='Status', value_name='Count'),
                     x='Join Year', y='Count', color='Status',
                     color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                     barmode='stack')
        st.plotly_chart(_style(fig, 400), use_container_width=True, config=CHART_CONFIG)
        st.dataframe(headcount, use_container_width=True)

    st.markdown("---")

    # Hire-to-Exit ratio
    st.subheader("Hire-to-Exit Ratio by Year")
    if 'Join Year' in filtered_df.columns:
        hires_yr = filtered_df.groupby('Join Year').size().rename('Hires')
        exits_yr = trends_dep_df.groupby('Exit Year').size().rename('Exits') if len(trends_dep_df) > 0 else pd.Series(dtype=int)

        years = sorted(set(hires_yr.index.tolist() + exits_yr.index.tolist()))
        years = [y for y in years if y > 2000]
        net_df = pd.DataFrame({'Year': years})
        net_df['Hires'] = net_df['Year'].map(hires_yr).fillna(0).astype(int)
        net_df['Exits'] = net_df['Year'].map(exits_yr).fillna(0).astype(int)

        ratio_df = net_df[net_df['Exits'] > 0].copy()
        if len(ratio_df) > 0:
            ratio_df['Ratio'] = (ratio_df['Hires'] / ratio_df['Exits']).round(2)
            fig = px.line(ratio_df, x='Year', y='Ratio', markers=True,
                          color_discrete_sequence=[COLORS['purple']])
            fig.add_hline(y=1, line_dash="dash", line_color="gray",
                          annotation_text="Breakeven (1:1)")
            st.plotly_chart(_style(fig, 350), use_container_width=True, config=CHART_CONFIG)
