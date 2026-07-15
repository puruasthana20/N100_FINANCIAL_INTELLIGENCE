import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_peer_groups,
    get_peers,
    get_companies,
    _read_sql
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Peer Comparison",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Peer Comparison")

st.caption(
    "Compare companies within the same peer group"
)


# ============================================================
# LOAD MASTER DATA
# ============================================================

peer_groups = get_peer_groups()

companies = get_companies()


# ============================================================
# PEER GROUP DROPDOWN
# ============================================================

selected_group = st.sidebar.selectbox(

    "Peer Group",

    peer_groups[
        "peer_group_name"
    ].tolist()

)


# ============================================================
# LOAD PEER MEMBERS
# ============================================================

peer_members = get_peers(
    selected_group
)


company_list = sorted(
    peer_members[
        "company_id"
    ].tolist()
)


selected_company = st.sidebar.selectbox(

    "Company",

    company_list

)


# ============================================================
# LOAD PEER PERCENTILES
# ============================================================

peer_data = _read_sql(

    """
    SELECT *
    FROM peer_percentiles
    WHERE peer_group_name=?
    """,

    [selected_group]

)


if peer_data.empty:

    st.warning(
        "No peer data available."
    )

    st.stop()


# ============================================================
# RADAR METRICS
# ============================================================

radar_metrics = [

    "roe",

    "roce",

    "net_profit_margin",

    "debt_to_equity",

    "free_cash_flow",

    "pat_cagr_5yr",

    "revenue_cagr_5yr",

    "interest_coverage"

]


# ============================================================
# COMPANY DATA
# ============================================================

company_radar = (

    peer_data

    [

        peer_data[
            "company_id"
        ]

        ==

        selected_company

    ]

)


company_radar = (

    company_radar

    .set_index(

        "metric"

    )

    .reindex(

        radar_metrics

    )

)


company_scores = (

    company_radar[
        "percentile_rank"
    ]

    .fillna(0)

    .tolist()

)


# ============================================================
# PEER AVERAGE
# ============================================================

peer_average = (

    peer_data

    .groupby(

        "metric"

    )[
        "percentile_rank"
    ]

    .mean()

    .reindex(

        radar_metrics

    )

)


peer_scores = (

    peer_average

    .fillna(0)

    .tolist()

)


# ============================================================
# BENCHMARK COMPANY
# ============================================================

benchmark = (

    peer_members

    [

        peer_members[
            "is_benchmark"
        ]

        ==

        1

    ]

)


benchmark_company = (

    benchmark.iloc[0][
        "company_id"
    ]

    if len(benchmark)

    else None

)


st.success(

    f"Benchmark Company: {benchmark_company}"

)

st.markdown("---")

# ============================================================
# RADAR CHART
# ============================================================

st.subheader(
    "Peer Radar Comparison"
)

categories = [

    "ROE",

    "ROCE",

    "Net Profit Margin",

    "Debt / Equity",

    "Free Cash Flow",

    "PAT CAGR 5Y",

    "Revenue CAGR 5Y",

    "Interest Coverage"

]

fig = go.Figure()

fig.add_trace(

    go.Scatterpolar(

        r=company_scores,

        theta=categories,

        fill="toself",

        name=selected_company

    )

)

fig.add_trace(

    go.Scatterpolar(

        r=peer_scores,

        theta=categories,

        fill="toself",

        name="Peer Average"

    )

)

fig.update_layout(

    polar=dict(

        radialaxis=dict(

            visible=True,

            range=[0, 1]

        )

    ),

    showlegend=True,

    height=650

)

st.plotly_chart(

    fig,

    use_container_width=True

)


st.markdown("---")


# ============================================================
# KPI COMPARISON TABLE
# ============================================================

st.subheader(
    "Peer Comparison Table"
)

comparison = (

    peer_data

    .pivot_table(

        index="company_id",

        columns="metric",

        values="percentile_rank"

    )

    .reset_index()

)

comparison.columns.name = None


comparison = comparison.merge(

    peer_members,

    on="company_id",

    how="left"

)


# ============================================================
# FORMAT PERCENTILES
# ============================================================

metric_columns = [

    c

    for c in comparison.columns

    if c not in [

        "company_id",

        "peer_group_name",

        "is_benchmark"

    ]

]

for column in metric_columns:

    comparison[column] = (

        comparison[column]

        * 100

    ).round(1)


# ============================================================
# BENCHMARK HIGHLIGHT
# ============================================================

def highlight_benchmark(row):

    if row["is_benchmark"] == 1:

        return [

            "background-color:#FFD966"

        ] * len(row)

    return [

        ""

    ] * len(row)


styled = (

    comparison

    .style

    .apply(

        highlight_benchmark,

        axis=1

    )

)


st.dataframe(

    styled,

    use_container_width=True,

    hide_index=True

)


st.markdown("---")


# ============================================================
# SUMMARY
# ============================================================

left, center, right = st.columns(3)

with left:

    st.metric(

        "Peer Group",

        selected_group

    )

with center:

    st.metric(

        "Companies",

        len(company_list)

    )

with right:

    st.metric(

        "Benchmark",

        benchmark_company

    )


st.markdown("---")


# ============================================================
# RAW METRIC VALUES
# ============================================================

st.subheader(
    "Raw Financial Values"
)

raw_table = (

    peer_data

    [

        peer_data["company_id"]

        ==

        selected_company

    ]

    [

        [

            "metric",

            "value",

            "percentile_rank"

        ]

    ]

)

raw_table["percentile_rank"] = (

    raw_table["percentile_rank"]

    * 100

).round(1)

raw_table = raw_table.rename(

    columns={

        "metric":"Metric",

        "value":"Actual Value",

        "percentile_rank":"Percentile"

    }

)

st.dataframe(

    raw_table,

    use_container_width=True,

    hide_index=True

)


st.markdown("---")

st.caption(

    "Nifty 100 Financial Intelligence Dashboard • Peer Comparison"

)