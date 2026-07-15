import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    latest_ratios,
    latest_market_data,
    get_sectors,
    get_companies
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Home",
    layout="wide"
)

st.title("🏠 Nifty 100 Analytics Dashboard")
st.caption(
    "Financial Intelligence Dashboard"
)


# ============================================================
# SIDEBAR
# ============================================================

selected_year = st.sidebar.selectbox(
    "Financial Year",
    [
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
        "2024"
    ],
    index=5
)


# ============================================================
# LOAD DATA
# ============================================================

ratios = latest_ratios()

market = latest_market_data()

sectors = get_sectors()

companies = get_companies()


# ============================================================
# FILTER YEAR
# ============================================================

ratios = ratios[
    ratios["year"]
    .astype(str)
    .str.contains(
        selected_year,
        na=False
    )
]


# ============================================================
# MERGE TABLES
# ============================================================

df = (

    ratios

    .merge(

        sectors,

        on="company_id",

        how="left"

    )

    .merge(

        market.drop(
            columns=["year"],
            errors="ignore"
        ),

        on="company_id",

        how="left"

    )

)


# ============================================================
# KPI VALUES
# ============================================================

average_roe = round(

    df[
        "return_on_equity_pct"
    ].mean(),

    2

)

median_pe = round(

    df[
        "pe_ratio"
    ].median(),

    2

)

median_de = round(

    df[
        "debt_to_equity"
    ].median(),

    2

)

median_revenue_cagr = round(

    df[
        "revenue_cagr_5yr"
    ].median(),

    2

)

total_companies = (

    df[
        "company_id"
    ]

    .nunique()

)

debt_free_companies = (

    df[
        df[
            "debt_to_equity"
        ] == 0
    ]

    .shape[0]

)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader(
    "Dashboard Summary"
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:

    st.metric(

        "Average ROE",

        f"{average_roe}%"

    )

with col2:

    st.metric(

        "Median P/E",

        median_pe

    )

with col3:

    st.metric(

        "Median D/E",

        median_de

    )

with col4:

    st.metric(

        "Companies",

        total_companies

    )

with col5:

    st.metric(

        "Median Revenue CAGR",

        f"{median_revenue_cagr}%"

    )

with col6:

    st.metric(

        "Debt-Free",

        debt_free_companies

    )


st.divider()


# ============================================================
# LAYOUT
# ============================================================

left, right = st.columns(
    [2, 1]
)

# ============================================================
# SECTOR BREAKDOWN
# ============================================================

with left:

    st.subheader(
        "Sector Breakdown"
    )

    sector_summary = (

        df

        .groupby(
            "broad_sector"
        )[
            "company_id"
        ]

        .nunique()

        .reset_index(
            name="Company Count"
        )

        .sort_values(
            by="Company Count",
            ascending=False
        )

    )


    if len(sector_summary):

        fig = px.pie(

            sector_summary,

            names="broad_sector",

            values="Company Count",

            hole=0.55,

            title="Companies by Sector"

        )

        fig.update_traces(

            textposition="inside",

            textinfo="percent+label"

        )

        fig.update_layout(

            legend_title="Sector",

            height=520

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    else:

        st.warning(
            "Sector data unavailable."
        )


# ============================================================
# TOP 5 COMPANIES
# ============================================================

with right:

    st.subheader(
        "Top 5 Companies"
    )

    top5 = (

        df

        .sort_values(

            by="composite_quality_score",

            ascending=False

        )

        [[

            "company_id",

            "return_on_equity_pct",

            "revenue_cagr_5yr",

            "composite_quality_score"

        ]]

        .head(5)

        .rename(

            columns={

                "company_id":"Ticker",

                "return_on_equity_pct":"ROE",

                "revenue_cagr_5yr":"Revenue CAGR 5Y",

                "composite_quality_score":"Composite Score"

            }

        )

    )


    st.dataframe(

        top5,

        use_container_width=True,

        hide_index=True

    )


st.divider()


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.subheader(
    "Dataset Overview"
)

overview1, overview2 = st.columns(2)


with overview1:

    st.write(
        "### Financial Coverage"
    )

    st.write(
        f"• Companies Loaded: **{total_companies}**"
    )

    st.write(
        f"• Selected Year: **{selected_year}**"
    )

    st.write(
        f"• Debt-Free Companies: **{debt_free_companies}**"
    )

    st.write(
        f"• Average ROE: **{average_roe}%**"
    )

    st.write(
        f"• Median Revenue CAGR: **{median_revenue_cagr}%**"
    )


with overview2:

    st.write(
        "### Database Status"
    )

    st.write(
        f"• Ratio Records: **{len(ratios)}**"
    )

    st.write(
        f"• Market Records: **{len(market)}**"
    )

    st.write(
        f"• Sector Records: **{len(sectors)}**"
    )

    st.write(
        f"• Company Master: **{len(companies)}**"
    )


st.divider()


# ============================================================
# COMPLETE DATA TABLE
# ============================================================

st.subheader(
    "Latest Financial Snapshot"
)

display_columns = [

    "company_id",

    "broad_sector",

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "debt_to_equity",

    "pe_ratio",

    "pb_ratio",

    "revenue_cagr_5yr",

    "composite_quality_score"

]

display_columns = [

    column

    for column in display_columns

    if column in df.columns

]

st.dataframe(

    df[
        display_columns
    ]

    .sort_values(

        by="composite_quality_score",

        ascending=False

    ),

    use_container_width=True,

    hide_index=True

)


st.success(
    "Home Dashboard loaded successfully."
)