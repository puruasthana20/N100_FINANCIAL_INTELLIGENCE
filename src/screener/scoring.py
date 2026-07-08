from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "db"
    / "nifty100.db"
)


# ============================================================
# METRIC WEIGHTS
# ============================================================

METRIC_WEIGHTS = {

    # Profitability = 35%

    "return_on_equity_pct": 0.15,

    "return_on_capital_employed_pct": 0.10,

    "net_profit_margin_pct": 0.10,


    # Cash Quality = 30%

    "fcf_cagr_5yr": 0.15,

    "cfo_pat_ratio_5yr": 0.10,

    "fcf_positive_score": 0.05,


    # Growth = 20%

    "revenue_cagr_5yr": 0.10,

    "pat_cagr_5yr": 0.10,


    # Leverage = 15%

    "debt_to_equity_score": 0.10,

    "interest_coverage_score": 0.05
}


# ============================================================
# LOAD SOURCE DATA
# ============================================================

def load_scoring_data(
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )


    # ========================================================
    # FINANCIAL RATIOS
    # ========================================================

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn
    )


    # ========================================================
    # SECTOR DATA
    # ========================================================

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn
    )


    # ========================================================
    # PROFIT & LOSS DATA
    # ========================================================

    profit_loss = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit
        FROM profitandloss
        """,
        conn
    )


    # ========================================================
    # MARKET VALUATION DATA
    # ========================================================

    market_cap = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            dividend_yield_pct
        FROM market_cap
        """,
        conn
    )


    conn.close()


    # ========================================================
    # MERGE RATIOS + SECTORS
    # ========================================================

    df = ratios.merge(
        sectors,
        on="company_id",
        how="left"
    )


    # ========================================================
    # MERGE P&L
    # ========================================================

    df = df.merge(
        profit_loss,
        on=[
            "company_id",
            "year"
        ],
        how="left"
    )


    # ========================================================
    # LATEST MARKET DATA PER COMPANY
    # ========================================================

    if not market_cap.empty:

        market_cap = (
            market_cap
            .sort_values(
                by="year"
            )
            .groupby(
                "company_id",
                as_index=False
            )
            .last()
        )


        market_cap = market_cap.drop(
            columns=[
                "year"
            ],
            errors="ignore"
        )


        df = df.merge(
            market_cap,
            on="company_id",
            how="left"
        )


    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    numeric_columns = [

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "net_profit_margin_pct",

        "operating_profit_margin_pct",

        "debt_to_equity",

        "interest_coverage",

        "asset_turnover",

        "free_cash_flow_cr",

        "cash_from_operations_cr",

        "revenue_cagr_3yr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "eps_cagr_5yr",

        "dividend_payout_ratio_pct",

        "sales",

        "net_profit",

        "market_cap_crore",

        "enterprise_value_crore",

        "pe_ratio",

        "pb_ratio",

        "dividend_yield_pct"
    ]


    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


    return df

# ============================================================
# PERIOD SORTING
# ============================================================

def add_period_sort_columns(
    df
):

    result = df.copy()


    result["fiscal_year"] = (

        result["year"]
        .astype(str)
        .str.extract(
            r"(\d{4})"
        )[0]
    )


    result["fiscal_year"] = pd.to_numeric(

        result["fiscal_year"],

        errors="coerce"
    )


    month_map = {

        "Mar": 3,

        "Jun": 6,

        "Sep": 9,

        "Dec": 12,

        "TTM": 13
    }


    result["fiscal_month"] = (

        result["year"]
        .astype(str)
        .str[:3]
        .map(
            month_map
        )
        .fillna(0)
    )


    result["period_order"] = (

        result["fiscal_year"]
        .fillna(9999)
        *
        100

        +

        result["fiscal_month"]
    )


    return result


# ============================================================
# FCF CAGR CALCULATION
# ============================================================

def calculate_fcf_cagr_5yr(
    start_value,
    end_value
):

    if pd.isna(start_value):

        return np.nan


    if pd.isna(end_value):

        return np.nan


    if start_value <= 0:

        return np.nan


    if end_value <= 0:

        return np.nan


    return (

        (
            end_value
            /
            start_value
        )
        **
        (
            1
            /
            5
        )

        -

        1

    ) * 100


def add_fcf_cagr(
    df
):

    result = add_period_sort_columns(
        df
    )


    result = result.sort_values(

        by=[

            "company_id",

            "period_order"
        ]
    )


    result["fcf_cagr_5yr"] = np.nan


    for company_id in result[
        "company_id"
    ].unique():


        company_mask = (

            result[
                "company_id"
            ]

            ==

            company_id
        )


        company_df = result[
            company_mask
        ].copy()


        indexes = company_df.index.tolist()


        for position in range(
            5,
            len(indexes)
        ):


            current_index = indexes[
                position
            ]


            old_index = indexes[
                position - 5
            ]


            start_fcf = result.loc[

                old_index,

                "free_cash_flow_cr"
            ]


            end_fcf = result.loc[

                current_index,

                "free_cash_flow_cr"
            ]


            value = calculate_fcf_cagr_5yr(

                start_fcf,

                end_fcf
            )


            result.loc[

                current_index,

                "fcf_cagr_5yr"

            ] = value


    return result


# ============================================================
# FIVE-YEAR CFO / PAT QUALITY
# ============================================================

def add_cfo_pat_ratio_5yr(
    df
):

    result = df.copy()


    result["annual_cfo_pat_ratio"] = np.where(

        (
            result["net_profit"].notna()
        )

        &

        (
            result["net_profit"] != 0
        ),

        (
            result[
                "cash_from_operations_cr"
            ]

            /

            result[
                "net_profit"
            ]
        ),

        np.nan
    )


    result["cfo_pat_ratio_5yr"] = np.nan


    for company_id in result[
        "company_id"
    ].unique():


        company_mask = (

            result[
                "company_id"
            ]

            ==

            company_id
        )


        company_df = (

            result[
                company_mask
            ]

            .sort_values(
                by="period_order"
            )
        )


        rolling_average = (

            company_df[
                "annual_cfo_pat_ratio"
            ]

            .rolling(

                window=5,

                min_periods=5
            )

            .mean()
        )


        result.loc[

            company_df.index,

            "cfo_pat_ratio_5yr"

        ] = rolling_average.values


    return result


# ============================================================
# LATEST ANNUAL RECORDS
# ============================================================

def get_latest_annual_records(
    df
):

    annual = df[

        df["year"] != "TTM"

    ].copy()


    annual = annual.sort_values(

        by=[

            "company_id",

            "period_order"
        ]
    )


    latest = (

        annual

        .groupby(
            "company_id",
            as_index=False
        )

        .tail(1)

        .reset_index(
            drop=True
        )
    )


    return latest


# ============================================================
# P10 / P90 NORMALISATION
# ============================================================

def winsorised_score(
    series,
    inverse=False
):

    numeric = pd.to_numeric(

        series,

        errors="coerce"
    )


    valid = numeric.dropna()


    if valid.empty:

        return pd.Series(

            np.nan,

            index=series.index
        )


    p10 = valid.quantile(
        0.10
    )


    p90 = valid.quantile(
        0.90
    )


    if p90 == p10:

        score = pd.Series(

            50.0,

            index=series.index
        )


        score[
            numeric.isna()
        ] = np.nan


        return score


    clipped = numeric.clip(

        lower=p10,

        upper=p90
    )


    score = (

        (
            clipped
            -
            p10
        )

        /

        (
            p90
            -
            p10
        )

        *

        100
    )


    if inverse:

        score = (

            100
            -
            score
        )


    return score


# ============================================================
# COMPONENT SCORES
# ============================================================

def add_component_scores(
    df
):

    result = df.copy()


    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    result["roe_score"] = winsorised_score(

        result[
            "return_on_equity_pct"
        ]
    )


    result["roce_score"] = winsorised_score(

        result[
            "return_on_capital_employed_pct"
        ]
    )


    result["npm_score"] = winsorised_score(

        result[
            "net_profit_margin_pct"
        ]
    )


    # --------------------------------------------------------
    # Cash Quality
    # --------------------------------------------------------

    result["fcf_cagr_score"] = winsorised_score(

        result[
            "fcf_cagr_5yr"
        ]
    )


    result["cfo_pat_score"] = winsorised_score(

        result[
            "cfo_pat_ratio_5yr"
        ]
    )


    result["fcf_positive_score"] = np.where(

        result[
            "free_cash_flow_cr"
        ]

        >

        0,

        100.0,

        0.0
    )


    # --------------------------------------------------------
    # Growth
    # --------------------------------------------------------

    result["revenue_growth_score"] = winsorised_score(

        result[
            "revenue_cagr_5yr"
        ]
    )


    result["pat_growth_score"] = winsorised_score(

        result[
            "pat_cagr_5yr"
        ]
    )


    # --------------------------------------------------------
    # Leverage
    # --------------------------------------------------------

    result["debt_to_equity_score"] = winsorised_score(

        result[
            "debt_to_equity"
        ],

        inverse=True
    )


    result["interest_coverage_score"] = winsorised_score(

        result[
            "interest_coverage"
        ]
    )


    return result


# ============================================================
# WEIGHTED COMPOSITE SCORE
# ============================================================

def calculate_composite_score(
    df
):

    result = df.copy()


    weighted_components = [

        (
            "roe_score",
            0.15
        ),

        (
            "roce_score",
            0.10
        ),

        (
            "npm_score",
            0.10
        ),

        (
            "fcf_cagr_score",
            0.15
        ),

        (
            "cfo_pat_score",
            0.10
        ),

        (
            "fcf_positive_score",
            0.05
        ),

        (
            "revenue_growth_score",
            0.10
        ),

        (
            "pat_growth_score",
            0.10
        ),

        (
            "debt_to_equity_score",
            0.10
        ),

        (
            "interest_coverage_score",
            0.05
        )
    ]


    weighted_sum = pd.Series(

        0.0,

        index=result.index
    )


    available_weight = pd.Series(

        0.0,

        index=result.index
    )


    for column, weight in weighted_components:


        valid = result[
            column
        ].notna()


        weighted_sum.loc[
            valid
        ] += (

            result.loc[
                valid,
                column
            ]

            *

            weight
        )


        available_weight.loc[
            valid
        ] += weight


    result[
        "composite_quality_score_v2"
    ] = np.where(

        available_weight > 0,

        weighted_sum
        /
        available_weight,

        np.nan
    )


    result[
        "composite_quality_score_v2"
    ] = (

        result[
            "composite_quality_score_v2"
        ]

        .clip(
            lower=0,
            upper=100
        )

        .round(2)
    )


    return result


# ============================================================
# SECTOR-RELATIVE SCORE
# ============================================================

def calculate_sector_relative_score(
    df
):

    result = df.copy()


    result[
        "sector_relative_score"
    ] = np.nan


    for sector in result[
        "broad_sector"
    ].dropna().unique():


        mask = (

            result[
                "broad_sector"
            ]

            ==

            sector
        )


        sector_scores = result.loc[

            mask,

            "composite_quality_score_v2"
        ]


        result.loc[

            mask,

            "sector_relative_score"

        ] = winsorised_score(

            sector_scores
        )


    result[
        "sector_relative_score"
    ] = (

        result[
            "sector_relative_score"
        ]

        .round(2)
    )


    return result


# ============================================================
# FULL SCORING PIPELINE
# ============================================================

def build_scoring_dataset():

    df = load_scoring_data()


    df = add_fcf_cagr(
        df
    )


    df = add_cfo_pat_ratio_5yr(
        df
    )


    df = get_latest_annual_records(
        df
    )


    df = add_component_scores(
        df
    )


    df = calculate_composite_score(
        df
    )


    df = calculate_sector_relative_score(
        df
    )


    df = df.sort_values(

        by="composite_quality_score_v2",

        ascending=False,

        na_position="last"
    )


    return df.reset_index(
        drop=True
    )


# ============================================================
# DIRECT RUN
# ============================================================

if __name__ == "__main__":

    result = build_scoring_dataset()


    display_columns = [

        "company_id",

        "year",

        "broad_sector",

        "composite_quality_score_v2",

        "sector_relative_score",

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "fcf_cagr_5yr",

        "cfo_pat_ratio_5yr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "debt_to_equity",

        "interest_coverage"
    ]


    print(
        "\n"
        + "=" * 100
    )


    print(
        "DAY 17 — COMPOSITE SCORING ENGINE"
    )


    print(
        "=" * 100
    )


    print(

        result[
            display_columns
        ]

        .head(20)

        .to_string(
            index=False
        )
    )


    print(
        "\nCompanies Scored:",
        result[
            "composite_quality_score_v2"
        ].notna().sum()
    )


    print(
        "\nScore Minimum:",
        result[
            "composite_quality_score_v2"
        ].min()
    )


    print(
        "Score Maximum:",
        result[
            "composite_quality_score_v2"
        ].max()
    )


    print(
        "\nSector Relative Minimum:",
        result[
            "sector_relative_score"
        ].min()
    )


    print(
        "Sector Relative Maximum:",
        result[
            "sector_relative_score"
        ].max()
    )