import streamlit as st
import pandas as pd
import plotly.express as px


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    trends_dep_df = filtered_df[filtered_df['Employee Status'] == 'Departed']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hiring Trend by Month")
        if 'Join Month' in filtered_df.columns:
            hiring = filtered_df.groupby('Join Month').size().reset_index(name='Hires')
            fig = px.line(hiring, x='Join Month', y='Hires', markers=True,
                          color_discrete_sequence=[COLORS['success']])
            fig.update_traces(line_width=3)
            fig.update_layout(xaxis_tickangle=-45, height=350)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Attrition Trend by Month")
        if len(trends_dep_df) > 0 and 'Exit Month' in trends_dep_df.columns:
            attrition = trends_dep_df.groupby('Exit Month').size().reset_index(name='Exits')
            fig = px.line(attrition, x='Exit Month', y='Exits', markers=True,
                          color_discrete_sequence=[COLORS['danger']])
            fig.update_traces(line_width=3)
            fig.update_layout(xaxis_tickangle=-45, height=350)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No departed employees in current selection.")

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
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
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
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
