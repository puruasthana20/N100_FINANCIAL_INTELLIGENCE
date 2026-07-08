import sqlite3
from pathlib import Path

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
# CONNECT
# ============================================================

conn = sqlite3.connect(DB_PATH)


# ============================================================
# TABLE LIST
# ============================================================

print(
    "\n"
    + "=" * 80
)

print(
    "DAY 17 — SCORING INPUT AUDIT"
)

print(
    "=" * 80
)


tables = pd.read_sql(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    conn
)


print(
    "\n===== DATABASE TABLES ====="
)

print(
    tables.to_string(
        index=False
    )
)


# ============================================================
# FINANCIAL RATIOS SCHEMA
# ============================================================

ratios_schema = pd.read_sql(
    """
    PRAGMA table_info(financial_ratios)
    """,
    conn
)


print(
    "\n===== FINANCIAL RATIOS COLUMNS ====="
)

print(
    ratios_schema[
        [
            "name",
            "type"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# CASH FLOW SCHEMA
# ============================================================

cashflow_schema = pd.read_sql(
    """
    PRAGMA table_info(cashflow)
    """,
    conn
)


print(
    "\n===== CASH FLOW COLUMNS ====="
)

print(
    cashflow_schema[
        [
            "name",
            "type"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# PROFIT & LOSS SCHEMA
# ============================================================

pl_schema = pd.read_sql(
    """
    PRAGMA table_info(profitandloss)
    """,
    conn
)


print(
    "\n===== PROFIT & LOSS COLUMNS ====="
)

print(
    pl_schema[
        [
            "name",
            "type"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# REQUIRED DAY 17 METRICS
# ============================================================

required_metrics = {

    "ROE":
        "return_on_equity_pct",

    "ROCE":
        "return_on_capital_employed_pct",

    "NPM":
        "net_profit_margin_pct",

    "FCF":
        "free_cash_flow_cr",

    "CFO":
        "cash_from_operations_cr",

    "Revenue CAGR 5Y":
        "revenue_cagr_5yr",

    "PAT CAGR 5Y":
        "pat_cagr_5yr",

    "Debt to Equity":
        "debt_to_equity",

    "Interest Coverage":
        "interest_coverage"
}


ratio_columns = set(
    ratios_schema[
        "name"
    ].tolist()
)


print(
    "\n===== REQUIRED METRIC AVAILABILITY ====="
)


for metric_name, column_name in required_metrics.items():

    exists = (
        column_name
        in ratio_columns
    )


    print(
        f"{metric_name:<25} "
        f"{column_name:<40} "
        f"{'AVAILABLE' if exists else 'MISSING'}"
    )


# ============================================================
# REQUIRED RAW INPUT AVAILABILITY
# ============================================================

cashflow_columns = set(
    cashflow_schema[
        "name"
    ].tolist()
)


pl_columns = set(
    pl_schema[
        "name"
    ].tolist()
)


print(
    "\n===== RAW INPUT AVAILABILITY ====="
)


raw_inputs = [

    (
        "CFO",
        "operating_activity",
        cashflow_columns
    ),

    (
        "CFI",
        "investing_activity",
        cashflow_columns
    ),

    (
        "PAT",
        "net_profit",
        pl_columns
    )
]


for metric, column, source_columns in raw_inputs:

    exists = (
        column
        in source_columns
    )


    print(
        f"{metric:<10} "
        f"{column:<30} "
        f"{'AVAILABLE' if exists else 'MISSING'}"
    )


# ============================================================
# DATA COVERAGE
# ============================================================

print(
    "\n===== FINANCIAL RATIO DATA COVERAGE ====="
)


coverage_query = """
SELECT

    COUNT(*) AS total_rows,

    COUNT(return_on_equity_pct) AS roe_count,

    COUNT(return_on_capital_employed_pct) AS roce_count,

    COUNT(net_profit_margin_pct) AS npm_count,

    COUNT(free_cash_flow_cr) AS fcf_count,

    COUNT(cash_from_operations_cr) AS cfo_count,

    COUNT(revenue_cagr_5yr) AS revenue_cagr_count,

    COUNT(pat_cagr_5yr) AS pat_cagr_count,

    COUNT(debt_to_equity) AS de_count,

    COUNT(interest_coverage) AS icr_count

FROM financial_ratios
"""


coverage = pd.read_sql(
    coverage_query,
    conn
)


print(
    coverage.to_string(
        index=False
    )
)


# ============================================================
# CFO / PAT DERIVATION CHECK
# ============================================================

print(
    "\n===== CFO / PAT DERIVATION CHECK ====="
)


cfo_pat_check = pd.read_sql(
    """
    SELECT

        f.company_id,

        f.year,

        f.cash_from_operations_cr AS cfo,

        p.net_profit AS pat

    FROM financial_ratios f

    LEFT JOIN profitandloss p

        ON f.company_id = p.company_id

        AND f.year = p.year

    WHERE
        f.cash_from_operations_cr IS NOT NULL

        AND p.net_profit IS NOT NULL

        AND p.net_profit != 0

    LIMIT 10
    """,
    conn
)


if cfo_pat_check.empty:

    print(
        "No valid CFO/PAT rows available."
    )

else:

    cfo_pat_check[
        "cfo_pat_ratio"
    ] = (

        cfo_pat_check[
            "cfo"
        ]

        /

        cfo_pat_check[
            "pat"
        ]

    ).round(4)


    print(
        cfo_pat_check.to_string(
            index=False
        )
    )


# ============================================================
# FCF HISTORY CHECK
# ============================================================

print(
    "\n===== FCF HISTORY COVERAGE BY COMPANY ====="
)


fcf_history = pd.read_sql(
    """
    SELECT

        company_id,

        COUNT(free_cash_flow_cr) AS fcf_periods

    FROM financial_ratios

    WHERE free_cash_flow_cr IS NOT NULL

    GROUP BY company_id

    ORDER BY fcf_periods DESC
    """,
    conn
)


print(
    fcf_history.head(
        20
    ).to_string(
        index=False
    )
)


print(
    "\nCompanies with at least 6 FCF periods:",
    int(
        (
            fcf_history[
                "fcf_periods"
            ]
            >=
            6
        ).sum()
    )
)


# ============================================================
# CLOSE
# ============================================================

conn.close()


print(
    "\n"
    + "=" * 80
)

print(
    "DAY 17 INPUT AUDIT COMPLETED"
)

print(
    "=" * 80
)