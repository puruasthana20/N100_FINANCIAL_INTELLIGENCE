import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_sectors,
    latest_market_data,
)

st.set_page_config(
    page_title="Capital Allocation Map",
    page_icon="🗺️",
    layout="wide",
)

st.title("🗺️ Capital Allocation Map")
st.caption(
    "Interactive treemap of companies grouped by Market Capitalization Category."
)

# ==========================================================
# Load Data
# ==========================================================

companies = get_companies()
sectors = get_sectors()
market = latest_market_data()

df = (
    companies
    .merge(sectors, on="company_id", how="left")
    .merge(market, on="company_id", how="left")
)

# ==========================================================
# Cleaning
# ==========================================================

df["market_cap_crore"] = pd.to_numeric(
    df["market_cap_crore"],
    errors="coerce",
)

df = df.dropna(
    subset=[
        "market_cap_category",
        "market_cap_crore",
    ]
)

# ==========================================================
# Summary
# ==========================================================

c1, c2, c3 = st.columns(3)

c1.metric(
    "Companies",
    len(df),
)

c2.metric(
    "Categories",
    df["market_cap_category"].nunique(),
)

c3.metric(
    "Total Market Cap",
    f"{df['market_cap_crore'].sum():,.0f} Cr",
)

st.divider()

# ==========================================================
# Treemap
# ==========================================================

st.subheader("Market Capitalization Treemap")

fig = px.treemap(
    df,
    path=[
        "market_cap_category",
        "company_name",
    ],
    values="market_cap_crore",
    color="broad_sector",
    hover_data={
        "market_cap_crore": ":,.0f",
        "broad_sector": True,
        "sub_sector": True,
    },
)

fig.update_layout(
    template="plotly_white",
    height=700,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.divider()

# ==========================================================
# Drill-down
# ==========================================================

categories = sorted(
    df["market_cap_category"].dropna().unique()
)

selected = st.selectbox(
    "Select Market Cap Category",
    categories,
)

filtered = (
    df[df["market_cap_category"] == selected]
    .sort_values(
        "market_cap_crore",
        ascending=False,
    )
)

st.subheader(f"{selected} Companies")

display_cols = [
    "company_name",
    "broad_sector",
    "sub_sector",
    "market_cap_crore",
]

display_cols = [
    c for c in display_cols
    if c in filtered.columns
]

st.dataframe(
    filtered[display_cols],
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "📥 Download Category Data",
    filtered[display_cols].to_csv(index=False),
    file_name=f"{selected.lower().replace(' ','_')}.csv",
    mime="text/csv",
)

st.divider()

st.caption(
    "Capital Allocation Dashboard • Treemap grouped by Market Capitalization Category"
)