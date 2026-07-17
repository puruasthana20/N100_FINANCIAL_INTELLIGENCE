import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_pl,
    get_bs,
    get_cf,
    get_ratios,
)

st.set_page_config(
    page_title="Trend Analysis",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Trend Analysis")
st.caption("Analyze historical financial performance across multiple metrics.")

companies = get_companies()

company_map = dict(
    zip(
        companies["company_name"],
        companies["company_id"],
    )
)

selected_company = st.selectbox(
    "Select Company",
    companies["company_name"].tolist(),
)

ticker = company_map[selected_company]

pl = get_pl(ticker)
bs = get_bs(ticker)
cf = get_cf(ticker)
ratios = get_ratios(ticker)

for df in [pl, bs, cf, ratios]:
    if not df.empty:
        df["year"] = df["year"].astype(str)

metric_sources = {}

# -------------------------
# Profit & Loss Metrics
# -------------------------

if not pl.empty:

    mapping = {
        "Revenue": "sales",
        "Operating Profit": "operating_profit",
        "Net Profit": "net_profit",
        "EPS": "eps",
    }

    for label, column in mapping.items():
        if column in pl.columns:
            metric_sources[label] = (
                pl[["year", column]]
                .rename(columns={column: "value"})
                .copy()
            )

# -------------------------
# Balance Sheet Metrics
# -------------------------

if not bs.empty:

    bs_mapping = {
        "Total Assets": "total_assets",
        "Net Worth": "equity_capital",
        "Borrowings": "borrowings",
    }

    for label, column in bs_mapping.items():
        if column in bs.columns:
            metric_sources[label] = (
                bs[["year", column]]
                .rename(columns={column: "value"})
                .copy()
            )

# -------------------------
# Cash Flow Metrics
# -------------------------

if not cf.empty:

    cf_mapping = {
        "Operating Cash Flow": "cash_from_operating_activity",
        "Investing Cash Flow": "cash_from_investing_activity",
        "Financing Cash Flow": "cash_from_financing_activity",
        "Free Cash Flow": "free_cash_flow",
    }

    for label, column in cf_mapping.items():
        if column in cf.columns:
            metric_sources[label] = (
                cf[["year", column]]
                .rename(columns={column: "value"})
                .copy()
            )

# -------------------------
# Ratio Metrics
# -------------------------

if not ratios.empty:

    ratio_mapping = {
        "ROE (%)": "roe",
        "ROCE (%)": "roce",
        "Debt / Equity": "de_ratio",
        "Current Ratio": "current_ratio",
        "Interest Coverage": "interest_coverage_ratio",
        "Operating Margin (%)": "opm",
        "Net Margin (%)": "npm",
    }

    for label, column in ratio_mapping.items():
        if column in ratios.columns:
            metric_sources[label] = (
                ratios[["year", column]]
                .rename(columns={column: "value"})
                .copy()
            )

metric_list = sorted(metric_sources.keys())

selected_metrics = st.multiselect(
    "Select up to 3 Metrics",
    metric_list,
    default=metric_list[:1],
    max_selections=3,
)

if not selected_metrics:
    st.warning("Please select at least one metric.")
    st.stop()

# ==========================================================
# Trend Chart
# ==========================================================

fig = go.Figure()

summary_rows = []

for metric in selected_metrics:

    df = metric_sources[metric].copy()

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    if df.empty:
        continue

    try:
        df["year_sort"] = (
            df["year"]
            .str.extract(r"(\d{4})")
            .astype(float)
        )
        df = df.sort_values("year_sort")
    except Exception:
        pass

    df["YoY"] = df["value"].pct_change() * 100

    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["value"],
            mode="lines+markers+text",
            name=metric,
            text=[
                ""
                if pd.isna(v)
                else f"{v:.1f}%"
                for v in df["YoY"]
            ],
            textposition="top center",
            hovertemplate=(
                "<b>%{x}</b><br>"
                + metric
                + ": %{y:,.2f}"
                + "<extra></extra>"
            ),
        )
    )

    summary_rows.append(
        {
            "Metric": metric,
            "Latest": round(df["value"].iloc[-1], 2),
            "Average": round(df["value"].mean(), 2),
            "Maximum": round(df["value"].max(), 2),
            "Minimum": round(df["value"].min(), 2),
        }
    )

fig.update_layout(
    height=650,
    hovermode="x unified",
    template="plotly_white",
    title=f"{selected_company} - Historical Trends",
    xaxis_title="Year",
    yaxis_title="Value",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# ==========================================================
# Summary Statistics
# ==========================================================

if summary_rows:

    st.subheader("Summary Statistics")

    summary_df = pd.DataFrame(summary_rows)

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

# ==========================================================
# Raw Data
# ==========================================================

st.subheader("Historical Data")

combined = None

for metric in selected_metrics:

    temp = metric_sources[metric].copy()

    temp = temp.rename(
        columns={"value": metric}
    )

    if combined is None:
        combined = temp

    else:
        combined = combined.merge(
            temp,
            on="year",
            how="outer",
        )

if combined is not None:

    try:
        combined = combined.sort_values("year")
    except Exception:
        pass

    st.dataframe(
        combined,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="📥 Download CSV",
        data=combined.to_csv(index=False),
        file_name=f"{ticker}_trend_analysis.csv",
        mime="text/csv",
    )

st.divider()

st.caption(
    "Trend Analysis Dashboard • Multi-Metric Historical Performance"
)