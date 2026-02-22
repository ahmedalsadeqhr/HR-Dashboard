import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

    st.markdown("---")

    # --- 3. Headcount by Department ---
    st.subheader("Headcount by Department")
    dept_hc = filtered_df.groupby('Department').agg(
        Total=('Employee Status', 'count'),
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum()),
    ).reset_index()
    dept_hc['Fill Rate %'] = (dept_hc['Active'] / dept_hc['Total'] * 100).round(1)
    dept_hc = dept_hc.sort_values('Active', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=dept_hc['Department'], y=dept_hc['Active'], name='Active',
                         marker_color=COLORS['success']))
    fig.add_trace(go.Bar(x=dept_hc['Department'], y=dept_hc['Departed'], name='Departed',
                         marker_color=COLORS['danger']))
    fig.update_layout(barmode='stack', xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    st.dataframe(dept_hc, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- 4. Workforce Risk Analysis ---
    st.subheader("Workforce Risk Analysis")
    active_df = filtered_df[filtered_df['Employee Status'] == 'Active'].copy()

    if len(active_df) > 0 and 'Age' in active_df.columns and 'Tenure (Months)' in active_df.columns:
        retirement_risk = active_df[active_df['Age'] >= 55]
        flight_risk = active_df[(active_df['Tenure (Months)'] >= 12) & (active_df['Tenure (Months)'] <= 36)]
        new_hire_risk = active_df[active_df['Tenure (Months)'] < 6]

        col1, col2, col3 = st.columns(3)
        col1.metric("Retirement Risk (55+)", f"{len(retirement_risk)} ({len(retirement_risk)/len(active_df)*100:.1f}%)")
        col2.metric("Flight Risk (1-3yr tenure)", f"{len(flight_risk)} ({len(flight_risk)/len(active_df)*100:.1f}%)")
        col3.metric("New Hire Risk (<6mo)", f"{len(new_hire_risk)} ({len(new_hire_risk)/len(active_df)*100:.1f}%)")

        fig = px.scatter(active_df[active_df['Age'] > 0], x='Tenure (Months)', y='Age',
                         color='Department', hover_data=[NAME_COL] if NAME_COL and NAME_COL in active_df.columns else None,
                         color_discrete_sequence=COLOR_SEQUENCE)
        fig.add_hrect(y0=55, y1=active_df['Age'].max() + 5, fillcolor="red", opacity=0.08,
                      annotation_text="Retirement Risk Zone", annotation_position="top left")
        fig.add_vrect(x0=12, x1=36, fillcolor="orange", opacity=0.05,
                      annotation_text="Flight Risk Window", annotation_position="top right")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        st.markdown("#### Risk Breakdown by Department")
        risk_dept = active_df.groupby('Department').apply(
            lambda g: pd.Series({
                'Headcount': len(g),
                'Retirement Risk': len(g[g['Age'] >= 55]),
                'Flight Risk': len(g[(g['Tenure (Months)'] >= 12) & (g['Tenure (Months)'] <= 36)]),
                'New Hire Risk': len(g[g['Tenure (Months)'] < 6]),
            })
        ).reset_index()
        risk_dept['Total Risk %'] = (
            (risk_dept['Retirement Risk'] + risk_dept['Flight Risk'] + risk_dept['New Hire Risk'])
            / risk_dept['Headcount'] * 100
        ).round(1)
        risk_dept = risk_dept.sort_values('Total Risk %', ascending=False)
        st.dataframe(risk_dept, use_container_width=True, hide_index=True)
    else:
        st.info("Age and Tenure data required for risk analysis.")

    st.markdown("---")

    # --- 5. Turnover Cost Estimate ---
    st.subheader("Turnover Cost Estimate")
    st.caption("Estimated using industry standard: 50% of annual salary for non-management, 100-150% for management roles.")

    if len(adv_departed) > 0:
        avg_salary_input = st.number_input(
            "Enter average annual salary (for estimation)", min_value=0, value=60000, step=5000,
            key="avg_salary"
        )

        mgmt_keywords = ['manager', 'director', 'head', 'lead', 'chief', 'vp', 'senior manager']
        if 'Position' in adv_departed.columns:
            is_mgmt = adv_departed['Position'].str.lower().str.contains('|'.join(mgmt_keywords), na=False)
            mgmt_departures = is_mgmt.sum()
            non_mgmt_departures = len(adv_departed) - mgmt_departures
        else:
            mgmt_departures = 0
            non_mgmt_departures = len(adv_departed)

        cost_non_mgmt = non_mgmt_departures * avg_salary_input * 0.5
        cost_mgmt = mgmt_departures * avg_salary_input * 1.25
        total_cost = cost_non_mgmt + cost_mgmt

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Departures", f"{len(adv_departed)}")
        col2.metric("Management Departures", f"{mgmt_departures}")
        col3.metric("Non-Management", f"{non_mgmt_departures}")
        col4.metric("Estimated Total Cost", f"${total_cost:,.0f}")

        dept_cost = adv_departed.groupby('Department').apply(
            lambda g: pd.Series({
                'Departures': len(g),
                'Mgmt Departures': g['Position'].str.lower().str.contains('|'.join(mgmt_keywords), na=False).sum() if 'Position' in g.columns else 0,
            })
        ).reset_index()
        dept_cost['Non-Mgmt'] = dept_cost['Departures'] - dept_cost['Mgmt Departures']
        dept_cost['Est. Cost'] = (dept_cost['Non-Mgmt'] * avg_salary_input * 0.5 + dept_cost['Mgmt Departures'] * avg_salary_input * 1.25)
        dept_cost = dept_cost.sort_values('Est. Cost', ascending=False)

        fig = px.bar(dept_cost, x='Department', y='Est. Cost',
                     color='Est. Cost', color_continuous_scale='Reds',
                     text=dept_cost['Est. Cost'].apply(lambda x: f"${x:,.0f}"))
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400, yaxis_title='Estimated Cost ($)')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        st.dataframe(dept_cost, use_container_width=True, hide_index=True)
    else:
        st.info("No departed employees for cost estimation.")

    st.markdown("---")

    # --- 6. Survival Analysis ---
    st.subheader("Employee Survival Curve")
    st.caption("Shows the probability of an employee staying beyond each month of tenure.")

    if 'Tenure (Months)' in filtered_df.columns and len(filtered_df) > 0:
        max_tenure = int(filtered_df['Tenure (Months)'].max())
        months = list(range(0, min(max_tenure + 1, 121)))
        survival_data = []

        total = len(filtered_df)
        for m in months:
            survived = len(filtered_df[filtered_df['Tenure (Months)'] > m])
            survival_data.append({'Month': m, 'Survived': survived, 'Survival Rate %': (survived / total * 100)})

        survival_df = pd.DataFrame(survival_data)

        fig = px.area(survival_df, x='Month', y='Survival Rate %',
                      color_discrete_sequence=[COLORS['primary']])
        fig.update_layout(
            height=400,
            xaxis_title='Tenure (Months)',
            yaxis_title='Survival Rate %',
            yaxis_range=[0, 105]
        )
        for milestone, label in [(3, '3mo'), (6, '6mo'), (12, '1yr'), (24, '2yr'), (36, '3yr')]:
            if milestone <= max(months):
                rate = survival_df[survival_df['Month'] == milestone]['Survival Rate %'].values
                if len(rate) > 0:
                    fig.add_vline(x=milestone, line_dash="dot", line_color="gray", opacity=0.5)
                    fig.add_annotation(x=milestone, y=rate[0], text=f"{label}: {rate[0]:.0f}%",
                                       showarrow=False, yshift=15, font_size=10)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

        dept_view = st.checkbox("Show survival curve by department", key="survival_dept")
        if dept_view:
            dept_survival = []
            for dept in filtered_df['Department'].unique():
                dept_df = filtered_df[filtered_df['Department'] == dept]
                dept_total = len(dept_df)
                if dept_total < 5:
                    continue
                for m in range(0, min(int(dept_df['Tenure (Months)'].max()) + 1, 61)):
                    survived = len(dept_df[dept_df['Tenure (Months)'] > m])
                    dept_survival.append({
                        'Month': m, 'Department': dept,
                        'Survival Rate %': (survived / dept_total * 100)
                    })

            if dept_survival:
                dept_surv_df = pd.DataFrame(dept_survival)
                fig = px.line(dept_surv_df, x='Month', y='Survival Rate %', color='Department',
                              color_discrete_sequence=COLOR_SEQUENCE)
                fig.update_layout(height=450, xaxis_title='Tenure (Months)', yaxis_range=[0, 105])
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Tenure data required for survival analysis.")

    st.markdown("---")

    # --- 7. Regrettable Turnover Proxy ---
    st.subheader("Regrettable Turnover (Estimated)")
    st.caption("Voluntary resignations of employees with 12+ months tenure are classified as likely regrettable losses.")

    if len(adv_departed) > 0:
        voluntary = adv_departed[adv_departed['Exit Type'].isin(['Resigned', 'Dropped'])]
        if len(voluntary) > 0 and 'Tenure (Months)' in voluntary.columns:
            regrettable = voluntary[voluntary['Tenure (Months)'] >= 12]
            non_regrettable_vol = voluntary[voluntary['Tenure (Months)'] < 12]
            involuntary = adv_departed[~adv_departed['Exit Type'].isin(['Resigned', 'Dropped'])]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Departures", f"{len(adv_departed)}")
            col2.metric("Regrettable (Vol 12+mo)", f"{len(regrettable)}",
                        delta=f"{len(regrettable)/len(adv_departed)*100:.1f}% of total",
                        delta_color="inverse")
            col3.metric("Early Vol (<12mo)", f"{len(non_regrettable_vol)}")
            col4.metric("Involuntary", f"{len(involuntary)}")

            turnover_types = pd.DataFrame({
                'Category': ['Regrettable (Vol 12+mo)', 'Early Voluntary (<12mo)', 'Involuntary'],
                'Count': [len(regrettable), len(non_regrettable_vol), len(involuntary)]
            })
            fig = px.pie(turnover_types, values='Count', names='Category',
                         color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['gray']],
                         hole=0.4)
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

            if len(regrettable) > 0:
                st.markdown("#### Regrettable Turnover by Department")
                reg_dept = regrettable.groupby('Department').agg(
                    Count=('Employee Status', 'count'),
                    Avg_Tenure=('Tenure (Months)', 'mean')
                ).reset_index()
                reg_dept['Avg_Tenure'] = reg_dept['Avg_Tenure'].round(1)
                reg_dept.columns = ['Department', 'Regrettable Losses', 'Avg Tenure (Months)']
                reg_dept = reg_dept.sort_values('Regrettable Losses', ascending=False)

                fig = px.bar(reg_dept, x='Department', y='Regrettable Losses',
                             color='Avg Tenure (Months)', color_continuous_scale='RdYlBu',
                             text='Regrettable Losses')
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

                if 'Exit Reason Category' in regrettable.columns:
                    st.markdown("#### Top Exit Reasons (Regrettable)")
                    reg_reasons = regrettable['Exit Reason Category'].value_counts().reset_index()
                    reg_reasons.columns = ['Reason', 'Count']
                    fig = px.bar(reg_reasons, x='Count', y='Reason', orientation='h',
                                 color='Count', color_continuous_scale='Reds')
                    fig.update_layout(height=max(250, len(reg_reasons) * 30),
                                      yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("No voluntary departure data available.")
    else:
        st.info("No departed employees in current filter selection.")
