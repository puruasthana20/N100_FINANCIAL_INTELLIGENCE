import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_sectors,
    latest_ratios,
    latest_market_data,
    get_companies,
    _read_sql,
)

st.set_page_config(
    page_title="Sector Analysis",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 Sector Analysis")
st.caption(
    "Compare companies within a sector using Revenue, ROE and Market Capitalization."
)

# ==========================================================
# Load Data
# ==========================================================

sector_df = get_sectors()
ratio_df = latest_ratios()
market_df = latest_market_data()
companies = get_companies()

# Latest Revenue
pl = _read_sql("""
WITH ranked AS(
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY company_id
               ORDER BY CAST(substr(year,-4) AS INTEGER) DESC
           ) rn
    FROM profitandloss
)
SELECT company_id,sales
FROM ranked
WHERE rn=1
""")

# ==========================================================
# Merge
# ==========================================================

df = (
    companies
    .merge(sector_df,on="company_id",how="left")
    .merge(ratio_df,on="company_id",how="left")
    .merge(market_df,on="company_id",how="left")
    .merge(pl,on="company_id",how="left")
)

# ==========================================================
# Numeric Conversion
# ==========================================================

numeric_cols = [
    "sales",
    "roe",
    "market_cap_crore",
]

for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(
    subset=[
        "sales",
        "roe",
        "market_cap_crore",
    ]
)

# ==========================================================
# Sidebar
# ==========================================================

sector_list = sorted(
    df["broad_sector"]
    .dropna()
    .unique()
)

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    sector_list,
)

sector_df = df[
    df["broad_sector"] == selected_sector
].copy()

# ==========================================================
# KPI Cards
# ==========================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(sector_df),
)

c2.metric(
    "Median ROE",
    f"{sector_df['roe'].median():.2f} %",
)

c3.metric(
    "Median Revenue",
    f"{sector_df['sales'].median():,.0f}",
)

c4.metric(
    "Total Market Cap",
    f"{sector_df['market_cap_crore'].sum():,.0f} Cr",
)

st.divider()

# ==========================================================
# Bubble Chart
# ==========================================================

st.subheader("Revenue vs ROE")

fig = px.scatter(
    sector_df,
    x="sales",
    y="roe",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    hover_data={
        "sales": ":,.0f",
        "roe": ":.2f",
        "market_cap_crore": ":,.0f",
        "sub_sector": True,
    },
    title=f"{selected_sector} Companies",
    labels={
        "sales": "Revenue",
        "roe": "ROE (%)",
        "market_cap_crore": "Market Cap (Cr)"
    },
)

fig.update_layout(
    template="plotly_white",
    height=650,
    legend_title="Sub Sector",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.divider()

# ==========================================================
# Sector Median KPI Chart
# ==========================================================

st.subheader("Sector Median KPIs")

median_metrics = {}

if "roe" in sector_df.columns:
    median_metrics["Median ROE"] = sector_df["roe"].median()

if "sales" in sector_df.columns:
    median_metrics["Median Revenue"] = sector_df["sales"].median()

if "market_cap_crore" in sector_df.columns:
    median_metrics["Median Market Cap"] = sector_df["market_cap_crore"].median()

median_df = pd.DataFrame(
    {
        "Metric": list(median_metrics.keys()),
        "Value": list(median_metrics.values()),
    }
)

bar = px.bar(
    median_df,
    x="Metric",
    y="Value",
    text="Value",
    title=f"{selected_sector} Median KPIs",
)

bar.update_traces(
    texttemplate="%{text:,.2f}",
    textposition="outside",
)

bar.update_layout(
    template="plotly_white",
    height=450,
    showlegend=False,
)

st.plotly_chart(
    bar,
    use_container_width=True,
)

st.divider()

# ==========================================================
# Company Table
# ==========================================================

st.subheader("Companies in Sector")

display_cols = [
    "company_name",
    "sub_sector",
    "sales",
    "roe",
    "market_cap_crore",
]

display_cols = [
    c for c in display_cols
    if c in sector_df.columns
]

table = (
    sector_df[display_cols]
    .sort_values(
        "market_cap_crore",
        ascending=False,
    )
)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
)

# ==========================================================
# Download
# ==========================================================

st.download_button(
    label="📥 Download Sector Data",
    data=table.to_csv(index=False),
    file_name=f"{selected_sector.lower().replace(' ','_')}_sector_analysis.csv",
    mime="text/csv",
)

st.divider()

st.caption(
    "Sector Analysis Dashboard • Revenue vs ROE Bubble Visualization"
)