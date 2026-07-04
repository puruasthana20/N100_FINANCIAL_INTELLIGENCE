import sqlite3
import pandas as pd
from pathlib import Path


DB_PATH = "data/db/nifty100.db"

conn = sqlite3.connect(DB_PATH)


# ============================================================
# 1. FINANCIAL RATIOS ROW COUNT
# ============================================================

row_count = pd.read_sql(
    """
    SELECT COUNT(*) AS row_count
    FROM financial_ratios
    """,
    conn
)

print("\n===== FINANCIAL RATIOS ROW COUNT =====")
print(row_count)


# ============================================================
# 2. NULL-ONLY COLUMN CHECK
# ============================================================

ratios = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    """,
    conn
)

null_only_columns = [
    column
    for column in ratios.columns
    if ratios[column].isna().all()
]

print("\n===== NULL-ONLY COLUMNS =====")

if null_only_columns:
    print(null_only_columns)
else:
    print("None")


# ============================================================
# 3. SCREENER PREVIEW
# Latest available annual financial period per company
# TTM excluded because balance-sheet inputs are incomplete
# ============================================================

screener = pd.read_sql(
    """
    WITH parsed_periods AS
    (
        SELECT
            *,

            CASE
                WHEN year = 'TTM'
                THEN NULL

                ELSE CAST(
                    SUBSTR(year, -4)
                    AS INTEGER
                )
            END AS fiscal_year,

            CASE
                WHEN year LIKE 'Dec %' THEN 12
                WHEN year LIKE 'Sep %' THEN 9
                WHEN year LIKE 'Jun %' THEN 6
                WHEN year LIKE 'Mar %' THEN 3
                ELSE 0
            END AS fiscal_month

        FROM financial_ratios

        WHERE year != 'TTM'
    ),

    ranked_records AS
    (
        SELECT
            *,

            ROW_NUMBER() OVER
            (
                PARTITION BY company_id

                ORDER BY
                    fiscal_year DESC,
                    fiscal_month DESC
            ) AS rn

        FROM parsed_periods
    )

    SELECT
        company_id,
        year,
        return_on_equity_pct,
        debt_to_equity,
        net_profit_margin_pct,
        revenue_cagr_5yr,
        composite_quality_score

    FROM ranked_records

    WHERE rn = 1
      AND return_on_equity_pct > 15
      AND debt_to_equity < 1

    ORDER BY
        return_on_equity_pct DESC
    """,
    conn
)


print("\n===== SCREENER PREVIEW =====")

print(
    screener.to_string(
        index=False
    )
)


print(
    "\nScreener Result Count:",
    len(screener)
)

# ============================================================
# 4. FIVE-COMPANY DEMO
# ============================================================

demo_companies = [
    "ABB",
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY"
]

placeholders = ",".join(
    ["?"] * len(demo_companies)
)

demo = pd.read_sql(
    f"""
    SELECT *
    FROM financial_ratios
    WHERE company_id IN ({placeholders})
    ORDER BY company_id, year DESC
    """,
    conn,
    params=demo_companies
)

latest_demo = (
    demo
    .groupby("company_id", as_index=False)
    .first()
)

print("\n===== FIVE COMPANY KPI DEMO =====")
print(latest_demo.to_string(index=False))


conn.close()

print("\nDay 14 Review Completed")