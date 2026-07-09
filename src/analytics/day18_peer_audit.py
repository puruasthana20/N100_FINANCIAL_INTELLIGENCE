import sqlite3
import pandas as pd


DB_PATH = "data/db/nifty100.db"


# ============================================================
# CONNECT
# ============================================================

conn = sqlite3.connect(
    DB_PATH
)


# ============================================================
# PEER GROUP TABLE STRUCTURE
# ============================================================

print(
    "\n"
    + "=" * 80
)

print(
    "DAY 18 — PEER GROUP INPUT AUDIT"
)

print(
    "=" * 80
)


print(
    "\n===== PEER GROUP TABLE COLUMNS ====="
)


columns = pd.read_sql(
    """
    PRAGMA table_info(peer_groups)
    """,
    conn
)


print(
    columns[
        [
            "name",
            "type"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# PEER GROUP SAMPLE
# ============================================================

print(
    "\n===== PEER GROUP SAMPLE ====="
)


peer_sample = pd.read_sql(
    """
    SELECT *
    FROM peer_groups
    LIMIT 20
    """,
    conn
)


print(
    peer_sample.to_string(
        index=False
    )
)


# ============================================================
# FINANCIAL RATIOS STRUCTURE
# ============================================================

print(
    "\n===== FINANCIAL RATIOS REQUIRED METRICS ====="
)


ratio_columns = pd.read_sql(
    """
    PRAGMA table_info(financial_ratios)
    """,
    conn
)


required_metrics = {

    "ROE":
        "return_on_equity_pct",

    "ROCE":
        "return_on_capital_employed_pct",

    "Net Profit Margin":
        "net_profit_margin_pct",

    "Debt to Equity":
        "debt_to_equity",

    "Free Cash Flow":
        "free_cash_flow_cr",

    "PAT CAGR 5Y":
        "pat_cagr_5yr",

    "Revenue CAGR 5Y":
        "revenue_cagr_5yr",

    "EPS CAGR 5Y":
        "eps_cagr_5yr",

    "Interest Coverage":
        "interest_coverage",

    "Asset Turnover":
        "asset_turnover"
}


available_columns = set(
    ratio_columns["name"]
)


for metric_name, column_name in required_metrics.items():

    status = (

        "AVAILABLE"

        if column_name in available_columns

        else "MISSING"
    )


    print(
        f"{metric_name:<25} "
        f"{column_name:<40} "
        f"{status}"
    )


# ============================================================
# PEER GROUP ROW COUNT
# ============================================================

print(
    "\n===== PEER GROUP ROW COUNT ====="
)


peer_count = pd.read_sql(
    """
    SELECT COUNT(*) AS peer_rows
    FROM peer_groups
    """,
    conn
)


print(
    peer_count.to_string(
        index=False
    )
)


# ============================================================
# COMPLETE PEER GROUP DATA
# ============================================================

peer_data = pd.read_sql(
    """
    SELECT *
    FROM peer_groups
    """,
    conn
)


# ============================================================
# IDENTIFY POSSIBLE GROUP COLUMN
# ============================================================

possible_group_columns = [

    column

    for column in peer_data.columns

    if "group" in column.lower()
]


print(
    "\n===== POSSIBLE PEER GROUP COLUMNS ====="
)


print(
    possible_group_columns
)


# ============================================================
# COMPANY COVERAGE
# ============================================================

companies = pd.read_sql(
    """
    SELECT DISTINCT company_id
    FROM companies
    """,
    conn
)


peer_company_ids = set(
    peer_data["company_id"]
) if "company_id" in peer_data.columns else set()


all_company_ids = set(
    companies["company_id"]
)


assigned = (
    all_company_ids
    &
    peer_company_ids
)


unassigned = (
    all_company_ids
    -
    peer_company_ids
)


print(
    "\n===== COMPANY PEER COVERAGE ====="
)


print(
    "Total Companies:",
    len(all_company_ids)
)


print(
    "Companies Assigned to Peer Group:",
    len(assigned)
)


print(
    "Companies Without Peer Group:",
    len(unassigned)
)


# ============================================================
# UNASSIGNED COMPANIES
# ============================================================

print(
    "\n===== UNASSIGNED COMPANIES ====="
)


if unassigned:

    for company_id in sorted(
        unassigned
    ):

        print(
            company_id
        )

else:

    print(
        "None"
    )


# ============================================================
# LATEST ANNUAL RATIO COVERAGE
# ============================================================

ratios = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    WHERE year != 'TTM'
    """,
    conn
)


ratios["fiscal_year"] = (

    ratios["year"]
    .astype(str)
    .str.extract(
        r"(\d{4})"
    )[0]
)


ratios["fiscal_year"] = pd.to_numeric(
    ratios["fiscal_year"],
    errors="coerce"
)


month_map = {

    "Mar": 3,

    "Jun": 6,

    "Sep": 9,

    "Dec": 12
}


ratios["fiscal_month"] = (

    ratios["year"]
    .astype(str)
    .str[:3]
    .map(month_map)
    .fillna(0)
)


ratios = ratios.sort_values(

    by=[

        "company_id",

        "fiscal_year",

        "fiscal_month"
    ]
)


latest_ratios = (

    ratios

    .groupby(
        "company_id",
        as_index=False
    )

    .tail(1)

    .copy()
)


print(
    "\n===== LATEST RATIO COVERAGE ====="
)


for metric_name, column_name in required_metrics.items():

    if column_name not in latest_ratios.columns:

        continue


    available = (
        latest_ratios[
            column_name
        ]
        .notna()
        .sum()
    )


    missing = (
        latest_ratios[
            column_name
        ]
        .isna()
        .sum()
    )


    print(

        f"{metric_name:<25} "

        f"Available: {available:<4} "

        f"Missing: {missing}"
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
    "DAY 18 PEER INPUT AUDIT COMPLETED"
)


print(
    "=" * 80
)