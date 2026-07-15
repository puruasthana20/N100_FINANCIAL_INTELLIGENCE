import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_sectors
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Company Profile",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Company Profile")

st.caption(
    "Detailed Financial Analysis of Individual Companies"
)


# ============================================================
# LOAD MASTER DATA
# ============================================================

companies = get_companies()

sectors = get_sectors()


# ============================================================
# BUILD SEARCH LIST
# ============================================================

search_items = []

company_lookup = {}

for _, row in companies.iterrows():

    ticker = str(row["company_id"])

    company = str(row["company_name"])

    display = f"{ticker} - {company}"

    search_items.append(display)

    company_lookup[display] = ticker


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Company Search"
)

selected = st.sidebar.selectbox(

    "Select Company",

    search_items

)


ticker = company_lookup[selected]


# ============================================================
# LOAD COMPANY DATA
# ============================================================

ratio_df = get_ratios(
    ticker
)

pl_df = get_pl(
    ticker
)

bs_df = get_bs(
    ticker
)

cf_df = get_cf(
    ticker
)


sector_df = sectors[
    sectors["company_id"] == ticker
]


company_df = companies[
    companies["company_id"] == ticker
]


# ============================================================
# VALIDATION
# ============================================================

if company_df.empty:

    st.error(
        "Ticker not found — please try another."
    )

    st.stop()


# ============================================================
# COMPANY DETAILS
# ============================================================

company = company_df.iloc[0]

company_name = company["company_name"]

website = company["website"]


if sector_df.empty:

    broad_sector = "N/A"

    sub_sector = "N/A"

else:

    broad_sector = sector_df.iloc[0]["broad_sector"]

    sub_sector = sector_df.iloc[0]["sub_sector"]


# ============================================================
# LATEST FINANCIAL DATA
# ============================================================

if len(ratio_df):

    latest_ratio = (

        ratio_df

        .sort_values("year")

        .iloc[-1]

    )

else:

    latest_ratio = pd.Series()


if len(pl_df):

    latest_pl = (

        pl_df

        .sort_values("year")

        .iloc[-1]

    )

else:

    latest_pl = pd.Series()


if len(cf_df):

    latest_cf = (

        cf_df

        .sort_values("year")

        .iloc[-1]

    )

else:

    latest_cf = pd.Series()


# ============================================================
# HEADER CARD
# ============================================================

st.markdown("---")

left, right = st.columns([3, 1])

with left:

    st.subheader(company_name)

    st.write(f"**Ticker:** {ticker}")

    st.write(f"**Sector:** {broad_sector}")

    st.write(f"**Sub Sector:** {sub_sector}")

    if pd.notna(website):

        st.write(f"**Website:** {website}")

    else:

        st.write("**Website:** N/A")

with right:

    st.metric(

        "Latest Year",

        latest_ratio.get(

            "year",

            "N/A"

        )

    )

st.markdown("---")

# ============================================================
# KPI SECTION
# ============================================================

st.subheader(
    "Financial Snapshot"
)

roe = latest_ratio.get(
    "return_on_equity_pct",
    None
)

roce = latest_ratio.get(
    "return_on_capital_employed_pct",
    None
)

npm = latest_ratio.get(
    "net_profit_margin_pct",
    None
)

de = latest_ratio.get(
    "debt_to_equity",
    None
)

revenue_cagr = latest_ratio.get(
    "revenue_cagr_5yr",
    None
)

fcf = latest_ratio.get(
    "free_cash_flow_cr",
    None
)


def format_percent(value):

    if pd.isna(value):

        return "N/A"

    return f"{value:.2f}%"


def format_number(value):

    if pd.isna(value):

        return "N/A"

    return f"{value:,.2f}"


kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:

    st.metric(
        "ROE",
        format_percent(roe)
    )

with kpi2:

    st.metric(
        "ROCE",
        format_percent(roce)
    )

with kpi3:

    st.metric(
        "Net Profit Margin",
        format_percent(npm)
    )

with kpi4:

    st.metric(
        "Debt / Equity",
        format_number(de)
    )

with kpi5:

    st.metric(
        "Revenue CAGR (5Y)",
        format_percent(revenue_cagr)
    )

with kpi6:

    st.metric(
        "Free Cash Flow",
        format_number(fcf)
    )

st.markdown("---")


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

summary_left, summary_right = st.columns(2)

with summary_left:

    st.subheader(
        "Latest Profit & Loss"
    )

    if not latest_pl.empty:

        pl_summary = pd.DataFrame({

            "Metric": [

                "Revenue",

                "Operating Profit",

                "Net Profit",

                "EPS"

            ],

            "Value": [

                latest_pl.get("sales"),

                latest_pl.get("operating_profit"),

                latest_pl.get("net_profit"),

                latest_pl.get("eps")

            ]

        })

        st.dataframe(
            pl_summary,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Profit & Loss data unavailable."
        )


with summary_right:

    st.subheader(
        "Latest Balance Sheet"
    )

    if not bs_df.empty:

        latest_bs = (

            bs_df

            .sort_values("year")

            .iloc[-1]

        )

        bs_summary = pd.DataFrame({

            "Metric": [

                "Equity Capital",

                "Reserves",

                "Borrowings",

                "Total Assets"

            ],

            "Value": [

                latest_bs.get("equity_capital"),

                latest_bs.get("reserves"),

                latest_bs.get("borrowings"),

                latest_bs.get("total_assets")

            ]

        })

        st.dataframe(

            bs_summary,

            use_container_width=True,

            hide_index=True

        )

    else:

        st.info(
            "Balance Sheet data unavailable."
        )

st.markdown("---")

# ============================================================
# REVENUE & NET PROFIT TREND
# ============================================================

st.subheader(
    "Revenue & Net Profit Trend"
)

if not pl_df.empty:

    chart_df = (

        pl_df

        .copy()

        .sort_values(
            "year"
        )

    )

    fig = px.bar(

        chart_df,

        x="year",

        y=[

            "sales",

            "net_profit"

        ],

        barmode="group",

        title="Revenue vs Net Profit"

    )

    fig.update_layout(

        xaxis_title="Financial Year",

        yaxis_title="₹ Crore",

        legend_title="Metric",

        height=500

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

else:

    st.info(

        "Historical Profit & Loss data unavailable."

    )


st.markdown("---")


# ============================================================
# ROE & ROCE TREND
# ============================================================

st.subheader(

    "ROE & ROCE Trend"

)

if not ratio_df.empty:

    ratio_chart = (

        ratio_df

        .copy()

        .sort_values(

            "year"

        )

    )


    fig = px.line(

        ratio_chart,

        x="year",

        y=[

            "return_on_equity_pct",

            "return_on_capital_employed_pct"

        ],

        markers=True,

        title="ROE vs ROCE"

    )


    fig.update_layout(

        xaxis_title="Financial Year",

        yaxis_title="Percentage",

        legend_title="Metric",

        height=500

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )

else:

    st.info(

        "Historical ratio data unavailable."

    )


st.markdown("---")


# ============================================================
# CASH FLOW TREND
# ============================================================

st.subheader(

    "Cash Flow Trend"

)

if not cf_df.empty:

    cf_chart = (

        cf_df

        .copy()

        .sort_values(

            "year"

        )

    )


    fig = px.bar(

        cf_chart,

        x="year",

        y=[

            "operating_activity",

            "investing_activity",

            "financing_activity"

        ],

        barmode="group",

        title="Cash Flow Activities"

    )


    fig.update_layout(

        xaxis_title="Financial Year",

        yaxis_title="₹ Crore",

        legend_title="Activity",

        height=500

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )

else:

    st.info(

        "Cash Flow history unavailable."

    )


st.markdown("---")

# ============================================================
# PROS & CONS
# ============================================================

st.subheader(
    "Pros & Cons"
)

from src.dashboard.utils.db import _read_sql

pros_cons = _read_sql(
    """
    SELECT *
    FROM prosandcons
    WHERE company_id=?
    """,
    [ticker]
)


if pros_cons.empty:

    st.info(
        "Pros & Cons not available."
    )

else:

    pros_text = str(
        pros_cons.iloc[0]["pros"]
    )

    cons_text = str(
        pros_cons.iloc[0]["cons"]
    )

    left, right = st.columns(2)

    with left:

        st.success("Pros")

        if pros_text.strip():

            for item in pros_text.split(";"):

                item = item.strip()

                if item:

                    st.markdown(
                        f"✅ {item}"
                    )

        else:

            st.write(
                "No Pros Available"
            )


    with right:

        st.error("Cons")

        if cons_text.strip():

            for item in cons_text.split(";"):

                item = item.strip()

                if item:

                    st.markdown(
                        f"❌ {item}"
                    )

        else:

            st.write(
                "No Cons Available"
            )


st.markdown("---")


# ============================================================
# FINANCIAL RATIOS TABLE
# ============================================================

st.subheader(
    "Financial Ratio History"
)

if not ratio_df.empty:

    ratio_display = ratio_df.copy()

    st.dataframe(

        ratio_display,

        use_container_width=True,

        hide_index=True

    )

else:

    st.info(
        "Financial ratios unavailable."
    )


# ============================================================
# DOWNLOAD DATA
# ============================================================

st.subheader(
    "Download Data"
)

if not ratio_df.empty:

    csv = ratio_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="📥 Download Ratio History",

        data=csv,

        file_name=f"{ticker}_financial_ratios.csv",

        mime="text/csv"

    )


# ============================================================
# PAGE FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Nifty 100 Financial Intelligence Dashboard • Company Profile"
)