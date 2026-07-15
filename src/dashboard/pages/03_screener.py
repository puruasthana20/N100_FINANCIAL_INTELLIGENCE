import streamlit as st
import pandas as pd

from src.screener.engine import (
    load_config,
    apply_filters,
    load_screener_data,
    get_latest_annual_records
)

from src.screener.scoring import (
    build_scoring_dataset
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(

    page_title="Financial Screener",

    page_icon="🔍",

    layout="wide"

)

st.title("🔍 Financial Screener")

st.caption(
    "Interactive Stock Screening Engine"
)


# ============================================================
# LOAD DATA
# ============================================================

config = load_config()

metric_config = config["metrics"]

preset_config = config["presets"]


@st.cache_data(ttl=600)
def load_dashboard_data():

    try:

        return build_scoring_dataset()

    except Exception:

        df = load_screener_data()

        return get_latest_annual_records(df)


df = load_dashboard_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Screening Filters"
)


# ============================================================
# PRESET
# ============================================================

preset = st.sidebar.selectbox(

    "Preset",

    [

        "Custom",

        "Quality Compounder",

        "Value Pick",

        "Growth Accelerator",

        "Dividend Champion",

        "Debt-Free Blue Chip",

        "Turnaround Watch"

    ]

)


# ============================================================
# DEFAULT FILTER VALUES
# ============================================================

filters = {

    "roe_min": 0,

    "debt_to_equity_max": 10.0,

    "fcf_min": -100000.0,

    "revenue_cagr_5yr_min": -100.0,

    "pat_cagr_5yr_min": -100.0,

    "opm_min": -100.0,

    "pe_max": 100.0,

    "pb_max": 20.0,

    "dividend_yield_min": 0.0,

    "icr_min": 0.0

}


# ============================================================
# APPLY PRESET
# ============================================================

if preset == "Quality Compounder":

    filters.update(
        preset_config[
            "quality_compounder"
        ]
    )

elif preset == "Value Pick":

    filters.update(
        preset_config[
            "value_pick"
        ]
    )

elif preset == "Growth Accelerator":

    filters.update(
        preset_config[
            "growth_accelerator"
        ]
    )

elif preset == "Dividend Champion":

    filters.update(
        preset_config[
            "dividend_champion"
        ]
    )

elif preset == "Debt-Free Blue Chip":

    filters.update(
        preset_config[
            "debt_free_blue_chip"
        ]
    )

elif preset == "Turnaround Watch":

    temp = preset_config[
        "turnaround_watch"
    ].copy()

    temp.pop(
        "de_declining",
        None
    )

    filters.update(
        temp
    )


# ============================================================
# SIDEBAR SLIDERS
# ============================================================

filters["roe_min"] = st.sidebar.slider(

    "Minimum ROE (%)",

    0.0,

    50.0,

    float(filters["roe_min"])

)

filters["debt_to_equity_max"] = st.sidebar.slider(

    "Maximum Debt/Equity",

    0.0,

    10.0,

    float(filters["debt_to_equity_max"])

)

filters["fcf_min"] = st.sidebar.number_input(

    "Minimum Free Cash Flow",

    value=float(filters["fcf_min"])

)

filters["revenue_cagr_5yr_min"] = st.sidebar.slider(

    "Revenue CAGR 5Y (%)",

    -50.0,

    50.0,

    float(filters["revenue_cagr_5yr_min"])

)

filters["pat_cagr_5yr_min"] = st.sidebar.slider(

    "PAT CAGR 5Y (%)",

    -50.0,

    100.0,

    float(filters["pat_cagr_5yr_min"])

)

filters["opm_min"] = st.sidebar.slider(

    "Operating Margin (%)",

    -50.0,

    60.0,

    float(filters["opm_min"])

)

filters["pe_max"] = st.sidebar.slider(

    "Maximum P/E",

    0.0,

    100.0,

    float(filters["pe_max"])

)

filters["pb_max"] = st.sidebar.slider(

    "Maximum P/B",

    0.0,

    20.0,

    float(filters["pb_max"])

)

filters["dividend_yield_min"] = st.sidebar.slider(

    "Dividend Yield (%)",

    0.0,

    10.0,

    float(filters["dividend_yield_min"])

)

filters["icr_min"] = st.sidebar.slider(

    "Interest Coverage",

    0.0,

    50.0,

    float(filters["icr_min"])

)

st.sidebar.markdown("---")
st.sidebar.success(
    "Filters update results automatically."
)

# ============================================================
# APPLY FILTERS
# ============================================================

try:

    result = apply_filters(
        df=df,
        filters=filters,
        config=config
    )

except Exception as e:

    st.error(
        f"Filtering Error: {e}"
    )

    st.stop()


# ============================================================
# RESULT COUNT
# ============================================================

st.subheader(
    "Screening Results"
)

st.success(
    f"{len(result)} companies match your filters."
)


# ============================================================
# DISPLAY COLUMNS
# ============================================================

display_columns = [

    "company_id",

    "broad_sector",

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "net_profit_margin_pct",

    "operating_profit_margin_pct",

    "debt_to_equity",

    "interest_coverage",

    "pe_ratio",

    "pb_ratio",

    "dividend_yield_pct",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "free_cash_flow_cr",

    "composite_quality_score_v2"

]


display_columns = [

    col

    for col in display_columns

    if col in result.columns

]


# ============================================================
# RESULTS TABLE
# ============================================================

st.dataframe(

    result[
        display_columns
    ],

    use_container_width=True,

    hide_index=True

)


# ============================================================
# CSV EXPORT
# ============================================================

csv = (

    result[
        display_columns
    ]

    .to_csv(
        index=False
    )

    .encode(
        "utf-8"
    )

)

st.download_button(

    label="📥 Download Results as CSV",

    data=csv,

    file_name="screener_results.csv",

    mime="text/csv"

)


# ============================================================
# SUMMARY
# ============================================================

st.markdown("---")

left, right = st.columns(2)

with left:

    st.metric(

        "Companies Found",

        len(result)

    )

with right:

    if len(result):

        avg_score = round(

            result[
                "composite_quality_score_v2"
            ].mean(),

            2

        ) if "composite_quality_score_v2" in result.columns else "N/A"

        st.metric(

            "Average Composite Score",

            avg_score

        )


# ============================================================
# TOP PICKS
# ============================================================

if (

    "composite_quality_score_v2"

    in result.columns

):

    st.subheader(
        "Top Ranked Companies"
    )

    top = (

        result

        .sort_values(

            "composite_quality_score_v2",

            ascending=False

        )

        .head(10)

    )

    cols = [

        c

        for c in [

            "company_id",

            "broad_sector",

            "composite_quality_score_v2",

            "return_on_equity_pct",

            "revenue_cagr_5yr"

        ]

        if c in top.columns

    ]

    st.dataframe(

        top[cols],

        use_container_width=True,

        hide_index=True

    )


st.markdown("---")

st.caption(

    "Nifty 100 Financial Intelligence Dashboard • Financial Screener"

)