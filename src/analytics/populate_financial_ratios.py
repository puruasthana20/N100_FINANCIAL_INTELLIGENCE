import sqlite3

import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover
)

from src.analytics.cashflow_kpis import (
    free_cash_flow
)

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)


# ============================================================
# DATABASE
# ============================================================

DB = "data/db/nifty100.db"

conn = sqlite3.connect(DB)


# ============================================================
# LOAD SOURCE TABLES
# ============================================================

pl = pd.read_sql(
    """
    SELECT *
    FROM profitandloss
    """,
    conn
)


bs = pd.read_sql(
    """
    SELECT *
    FROM balancesheet
    """,
    conn
)


cf = pd.read_sql(
    """
    SELECT *
    FROM cashflow
    """,
    conn
)


# ============================================================
# MERGE SOURCE DATA
# ============================================================

df = (
    pl
    .merge(
        bs,
        on=[
            "company_id",
            "year"
        ],
        how="left"
    )
    .merge(
        cf,
        on=[
            "company_id",
            "year"
        ],
        how="left"
    )
)


print(
    "\n===== MERGED FINANCIAL DATA ====="
)

print(
    df.head()
)


# ============================================================
# PROFITABILITY RATIOS
# ============================================================

df["net_profit_margin_pct"] = df.apply(

    lambda x:

    net_profit_margin(
        x.net_profit,
        x.sales
    ),

    axis=1
)


df["operating_profit_margin_pct"] = df.apply(

    lambda x:

    operating_profit_margin(
        x.operating_profit,
        x.sales
    ),

    axis=1
)


df["return_on_equity_pct"] = df.apply(

    lambda x:

    return_on_equity(
        x.net_profit,
        x.equity_capital,
        x.reserves
    ),

    axis=1
)


df["return_on_capital_employed_pct"] = df.apply(

    lambda x:

    return_on_capital_employed(

        x.operating_profit
        +
        x.other_income,

        x.equity_capital,

        x.reserves,

        x.borrowings
    ),

    axis=1
)


# ============================================================
# LEVERAGE AND EFFICIENCY RATIOS
# ============================================================

df["debt_to_equity"] = df.apply(

    lambda x:

    debt_to_equity(
        x.borrowings,
        x.equity_capital,
        x.reserves
    ),

    axis=1
)


df["interest_coverage"] = df.apply(

    lambda x:

    interest_coverage_ratio(
        x.operating_profit,
        x.other_income,
        x.interest
    ),

    axis=1
)


df["asset_turnover"] = df.apply(

    lambda x:

    asset_turnover(
        x.sales,
        x.total_assets
    ),

    axis=1
)


# ============================================================
# CASH FLOW KPIs
# ============================================================

df["free_cash_flow_cr"] = df.apply(

    lambda x:

    free_cash_flow(
        x.operating_activity,
        x.investing_activity
    ),

    axis=1
)


df["capex_cr"] = abs(
    df["investing_activity"]
)


df["cash_from_operations_cr"] = (
    df["operating_activity"]
)


# ============================================================
# PER-SHARE AND CAPITAL METRICS
# ============================================================

df["earnings_per_share"] = (
    df["eps"]
)


df["book_value_per_share"] = df.apply(

    lambda x: (

        (
            x.equity_capital
            +
            x.reserves
        )
        /
        x.equity_capital

        if (
            pd.notna(
                x.equity_capital
            )
            and
            x.equity_capital != 0
        )

        else None
    ),

    axis=1
)


df["dividend_payout_ratio_pct"] = (
    df["dividend_payout"]
)


df["total_debt_cr"] = (
    df["borrowings"]
)


# ============================================================
# PERIOD SORTING
# ============================================================

month_map = {

    "Mar": 3,

    "Jun": 6,

    "Sep": 9,

    "Dec": 12,

    "TTM": 13
}


df["fiscal_year"] = pd.to_numeric(

    df["year"]
    .astype(str)
    .str.extract(
        r"(\d{4})"
    )[0],

    errors="coerce"
)


# TTM has no explicit year.
# Assign it after the latest annual year for each company.

max_year_by_company = (

    df
    .groupby(
        "company_id"
    )[
        "fiscal_year"
    ]
    .transform(
        "max"
    )
)


df.loc[
    df["year"] == "TTM",
    "fiscal_year"
] = (

    max_year_by_company[
        df["year"] == "TTM"
    ]
    +
    1
)


df["fiscal_month"] = (

    df["year"]
    .astype(str)
    .str[:3]
    .map(month_map)
    .fillna(0)
)


df = df.sort_values(

    by=[
        "company_id",
        "fiscal_year",
        "fiscal_month"
    ]

).reset_index(
    drop=True
)


# ============================================================
# INITIALISE CAGR COLUMNS
# ============================================================

df["revenue_cagr_3yr"] = None

df["revenue_cagr_5yr"] = None

df["pat_cagr_5yr"] = None

df["eps_cagr_5yr"] = None


# ============================================================
# CAGR CALCULATION
# ============================================================

for company in df["company_id"].unique():


    company_df = df[
        df["company_id"]
        ==
        company
    ]


    idx = company_df.index.tolist()


    # ========================================================
    # REVENUE CAGR — 3 YEAR
    # ========================================================

    for i in range(
        3,
        len(idx)
    ):


        current = idx[i]

        old = idx[
            i - 3
        ]


        value, _ = revenue_cagr(

            df.loc[
                old,
                "sales"
            ],

            df.loc[
                current,
                "sales"
            ],

            3
        )


        df.loc[
            current,
            "revenue_cagr_3yr"
        ] = value


    # ========================================================
    # 5-YEAR CAGR METRICS
    # ========================================================

    for i in range(
        5,
        len(idx)
    ):


        current = idx[i]

        old = idx[
            i - 5
        ]


        # ----------------------------------------------------
        # Revenue CAGR 5Y
        # ----------------------------------------------------

        value, _ = revenue_cagr(

            df.loc[
                old,
                "sales"
            ],

            df.loc[
                current,
                "sales"
            ],

            5
        )


        df.loc[
            current,
            "revenue_cagr_5yr"
        ] = value


        # ----------------------------------------------------
        # PAT CAGR 5Y
        # ----------------------------------------------------

        value, _ = pat_cagr(

            df.loc[
                old,
                "net_profit"
            ],

            df.loc[
                current,
                "net_profit"
            ],

            5
        )


        df.loc[
            current,
            "pat_cagr_5yr"
        ] = value


        # ----------------------------------------------------
        # EPS CAGR 5Y
        # ----------------------------------------------------

        value, _ = eps_cagr(

            df.loc[
                old,
                "eps"
            ],

            df.loc[
                current,
                "eps"
            ],

            5
        )


        df.loc[
            current,
            "eps_cagr_5yr"
        ] = value


# ============================================================
# NUMERIC CAGR CONVERSION
# ============================================================

cagr_columns = [

    "revenue_cagr_3yr",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "eps_cagr_5yr"
]


for column in cagr_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# CURRENT COMPOSITE QUALITY SCORE
#
# Day 17 will replace this with:
# P10/P90 winsorisation
# 0–100 scaling
# weighted score
# sector-relative score
# ============================================================

df["composite_quality_score"] = (

    (

        df[
            "return_on_equity_pct"
        ].fillna(0)

        +

        df[
            "net_profit_margin_pct"
        ].fillna(0)

    )

    /

    2

).round(2)


# ============================================================
# FINAL FINANCIAL RATIOS DATASET
# ============================================================

final = df[
    [

        "company_id",

        "year",

        "net_profit_margin_pct",

        "operating_profit_margin_pct",

        "return_on_equity_pct",

        "debt_to_equity",

        "interest_coverage",

        "asset_turnover",

        "free_cash_flow_cr",

        "capex_cr",

        "earnings_per_share",

        "book_value_per_share",

        "dividend_payout_ratio_pct",

        "total_debt_cr",

        "cash_from_operations_cr",

        "revenue_cagr_3yr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "eps_cagr_5yr",

        "composite_quality_score",

        "return_on_capital_employed_pct"
    ]
]


# ============================================================
# WRITE TO DATABASE
# ============================================================

final.to_sql(

    "financial_ratios",

    conn,

    if_exists="replace",

    index=False
)


print(
    "\nFinancial Ratios Populated:",
    len(final)
)


# ============================================================
# DATABASE VALIDATION
# ============================================================

print(
    "\n===== FINANCIAL RATIOS ROW COUNT ====="
)


print(

    pd.read_sql(

        """
        SELECT COUNT(*) AS row_count
        FROM financial_ratios
        """,

        conn
    )
)


print(
    "\n===== FINANCIAL RATIOS SAMPLE ====="
)


print(

    pd.read_sql(

        """
        SELECT *
        FROM financial_ratios
        LIMIT 5
        """,

        conn
    )
)


# ============================================================
# SOURCE TABLE COUNTS
# ============================================================

print(
    "\n===== SOURCE TABLE COUNTS ====="
)


pl_count = pd.read_sql(

    """
    SELECT COUNT(*) AS count
    FROM profitandloss
    """,

    conn
)


bs_count = pd.read_sql(

    """
    SELECT COUNT(*) AS count
    FROM balancesheet
    """,

    conn
)


cf_count = pd.read_sql(

    """
    SELECT COUNT(*) AS count
    FROM cashflow
    """,

    conn
)


print(
    "Profit & Loss:"
)

print(
    pl_count
)


print(
    "\nBalance Sheet:"
)

print(
    bs_count
)


print(
    "\nCash Flow:"
)

print(
    cf_count
)


# ============================================================
# INNER JOIN COVERAGE DIAGNOSTIC
# ============================================================

merge_count = pd.read_sql(

    """
    SELECT COUNT(*) AS count

    FROM profitandloss p

    INNER JOIN balancesheet b

        ON p.company_id = b.company_id

        AND p.year = b.year

    INNER JOIN cashflow c

        ON p.company_id = c.company_id

        AND p.year = c.year
    """,

    conn
)


print(
    "\n===== FULL THREE-TABLE MATCH COUNT ====="
)


print(
    merge_count
)


# ============================================================
# CAGR VALIDATION
# ============================================================

print(
    "\n===== CAGR NON-NULL COUNTS ====="
)


cagr_validation = pd.read_sql(

    """
    SELECT

        COUNT(
            revenue_cagr_3yr
        ) AS revenue_cagr_3yr_count,

        COUNT(
            revenue_cagr_5yr
        ) AS revenue_cagr_5yr_count,

        COUNT(
            pat_cagr_5yr
        ) AS pat_cagr_5yr_count,

        COUNT(
            eps_cagr_5yr
        ) AS eps_cagr_5yr_count

    FROM financial_ratios
    """,

    conn
)


print(
    cagr_validation
)


# ============================================================
# SAMPLE 3-YEAR CAGR VALUES
# ============================================================

print(
    "\n===== SAMPLE 3-YEAR REVENUE CAGR ====="
)


sample_cagr = pd.read_sql(

    """
    SELECT

        company_id,

        year,

        revenue_cagr_3yr,

        revenue_cagr_5yr

    FROM financial_ratios

    WHERE revenue_cagr_3yr IS NOT NULL

    LIMIT 10
    """,

    conn
)


print(
    sample_cagr
)


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()


print(
    "\nFinancial Ratio Engine Completed Successfully"
)