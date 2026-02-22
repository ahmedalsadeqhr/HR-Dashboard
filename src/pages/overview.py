import streamlit as st
import plotly.express as px


def render(df, filtered_df, kpis, NAME_COL, COLORS, COLOR_SEQUENCE, CHART_CONFIG):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        gender_counts = filtered_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(gender_counts, values='Count', names='Gender',
                     color_discrete_sequence=[COLORS['primary'], COLORS['pink']],
                     hole=0.4)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Employee Status")
        status_counts = filtered_df['Employee Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status',
                     color_discrete_sequence=[COLORS['success'], COLORS['danger']],
                     hole=0.4)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    st.subheader("Department Breakdown")
    dept_data = filtered_df.groupby(['Department', 'Employee Status']).size().reset_index(name='Count')
    fig = px.bar(dept_data, x='Department', y='Count', color='Employee Status',
                 color_discrete_map={'Active': COLORS['success'], 'Departed': COLORS['danger']},
                 barmode='group')
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 15 Positions")
        pos_counts = filtered_df['Position'].value_counts().head(15).reset_index()
        pos_counts.columns = ['Position', 'Count']
        fig = px.bar(pos_counts, x='Count', y='Position', orientation='h',
                     color='Count', color_continuous_scale='Blues')
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with col2:
        st.subheader("Age Distribution")
        age_df = filtered_df[filtered_df['Age'] > 0]
        if len(age_df) > 0:
            fig = px.histogram(age_df, x='Age', nbins=20,
                               color_discrete_sequence=[COLORS['primary']],
                               marginal='box')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    if 'Nationality' in filtered_df.columns:
        st.markdown("---")
        st.subheader("Nationality Distribution")
        nat_counts = filtered_df['Nationality'].value_counts().reset_index()
        nat_counts.columns = ['Nationality', 'Count']
        fig = px.pie(nat_counts, values='Count', names='Nationality',
                     color_discrete_sequence=COLOR_SEQUENCE)
        fig.update_traces(textinfo='percent+value')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
