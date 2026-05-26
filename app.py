

import pandas as pd
import streamlit as st
import plotly.express as px

df = pd.read_csv('Kittchen PNL Data.csv', header=1)
df2 = pd.read_csv('monthly_store_df.csv')

df2['MONTH'] = pd.to_datetime(df['MONTH'])

df2['MONTH'] = df2['MONTH'].dt.strftime('%b-%Y')




st.set_page_config(
    page_title = "Kitchen Level P&L Dashboard",
    layout="wide"
)
st.title('Kitchen Level P&L Dashboard')
st.markdown("Operational and Profitability analysis of kitchen/store performance")


ebitda_range = st.slider(
    "Select EBITDA Range (₹)",
    int(df['KITCHEN EBITDA'].min()),
    int(df['KITCHEN EBITDA'].max()),
    (
        int(df['KITCHEN EBITDA'].min()),
        int(df['KITCHEN EBITDA'].max())
    )
)


# st.columns(1)


filter1, filter2, filter3, filter4, filter5, filter6 = st.columns(6)

with filter1:

    store_options = ['All'] + sorted(df['STORE'].unique().tolist())

    selected_store = st.selectbox(
        "Store",
        options=store_options
    )

with filter2:

    zone_options = ['All'] + sorted(df['ZONE MAPPING'].unique().tolist())

    selected_zone = st.selectbox(
        "Zone",
        options=zone_options
    )
with filter3:

    ebitda_options = ['All'] + sorted(df['EBITDA CATEGORY'].unique().tolist())

    selected_ebitda_category = st.selectbox(
        "EBITDA Category",
        options=ebitda_options
    )
with filter4:

    month_options = ['All'] + sorted(df['MONTH'].unique().tolist())

    selected_month = st.selectbox(
        "Month",
        options=month_options
    )
with filter5:

    revenue_options = ['All'] + sorted(df['REVENUE COHORT'].unique().tolist())

    selected_revenue_cohort = st.selectbox(
        "Revenue Cohort",
        options=revenue_options
    )

with filter6:

    status_options = ['All'] + sorted(df['STATUS'].unique().tolist())

    selected_status = st.selectbox(
        "STATUS",
        options=status_options
    )


filtered_df = df2.copy()

if selected_store != 'All':
    filtered_df = filtered_df[
        filtered_df['STORE'] == selected_store
    ]

if selected_status != 'All':
    filtered_df = filtered_df[
        filtered_df['STATUS'] == selected_status
    ]

if selected_zone != 'All':
    filtered_df = filtered_df[
        filtered_df['ZONE MAPPING'] == selected_zone
    ]

if selected_ebitda_category != 'All':
    filtered_df = filtered_df[
        filtered_df['EBITDA CATEGORY'] == selected_ebitda_category
    ]

if selected_month != 'All':
    filtered_df = filtered_df[
        filtered_df['MONTH'] == selected_month
    ]

if selected_revenue_cohort != 'All':
    filtered_df = filtered_df[
        filtered_df['REVENUE COHORT'] == selected_revenue_cohort
    ]

filtered_df = filtered_df[
    filtered_df['KITCHEN EBITDA'].between(
        ebitda_range[0],
        ebitda_range[1]
    )
]

st.markdown("---")

TotalNetRevenue = filtered_df['NET REVENUE'].sum()
TotalKitchenEbitda = filtered_df['KITCHEN EBITDA'].sum()
EbitdaPercentage = (filtered_df['KITCHEN EBITDA'].sum()/filtered_df['NET REVENUE'].sum())*100
TotalOrders = filtered_df['ORDER COUNT'].sum()
AOV = (filtered_df['NET REVENUE'].sum()/filtered_df['ORDER COUNT'].sum())
GMPercentage = (filtered_df['GROSS MARGIN'].sum()/filtered_df['NET REVENUE'].sum())*100

c1, c2, c3, c4, c5, c6 = st.columns(6)


with c1:
 
    st.metric(label="Total Net Revenue", value=f"₹{TotalNetRevenue / 1e7:.2f} Cr")

with c2:

    st.metric(label="Kitchen EBITDA", value=f"₹{TotalKitchenEbitda / 1e7:.2f} Cr")

with c3:
    st.metric(label="EBITDA %", value=f"{EbitdaPercentage:.2f}%")

with c4:
 
    st.metric(label="Total Orders", value=f"{TotalOrders:,.0f}")

with c5:
   
    st.metric(label="AOV", value=f"₹{AOV:,.2f}")

with c6:
    st.metric(label="GM %", value=f"{GMPercentage:.2f}%")

st.subheader("Kitchen Snapshot")

snapshot_df = filtered_df[
    [
        'MONTH',
        'STORE',
        'STATUS',
        'ZONE MAPPING',
        'NET REVENUE',
        'GM %',
        'EBITDA %',
        'KITCHEN EBITDA',
        'REVENUE COHORT',
        'EBITDA CATEGORY'
    ]
]


st.dataframe(
    snapshot_df,
    use_container_width=True
)

# -------------------------------------------------------------------------------------------------------------


col1, col2 = st.columns(2)


with col1: 
    top_ebitda = (
        filtered_df
        .sort_values('KITCHEN EBITDA', ascending=False)
        .head(10)
    )

    fig1 = px.bar(
        top_ebitda,
        x='STORE',
        y='KITCHEN EBITDA',
        title='Top 10 Stores by EBITDA',
        text_auto='.2s' 
    )

    fig1.update_traces(textposition='outside')
    fig1.update_layout(yaxis=dict(range=[0, top_ebitda['KITCHEN EBITDA'].max() * 1.15]))
    
    # Changed HEIGHT to lowercase height
    fig1.update_layout(height=450)

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# -----------------------------------------------------------------------------------------


with col2: 
    fig2 = px.pie(
        filtered_df,
        names='REVENUE COHORT',
        title='Revenue Cohort Distribution'
    )


    fig2.update_traces(
        textposition='inside',
        textinfo='percent+value',
        texttemplate='%{label}<br>%{value} stores<br>%{percent:.1%}' 
    )


    fig2.update_layout(height=450)

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


#---------------------------------------------------------------------------------------------------------------------


monthly_revenue = (
    filtered_df
    .groupby('MONTH_SORT', as_index=False)['NET REVENUE']
    .sum()
    .sort_values('MONTH_SORT')
)

fig4 = px.line(
    monthly_revenue,
    x='MONTH_SORT',
    y='NET REVENUE',
    title='Monthly Revenue Trend',
    markers=True,
    text='NET REVENUE' 
)

fig4.update_traces(
    textposition="top center", 
    texttemplate='%{text:.3s}'  
)


fig4.update_layout(
    yaxis=dict(range=[monthly_revenue['NET REVENUE'].min() * 0.99, monthly_revenue['NET REVENUE'].max() * 1.01])
)

st.plotly_chart(
    fig4,
    use_container_width=True
)




