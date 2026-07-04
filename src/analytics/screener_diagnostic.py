import sqlite3
import pandas as pd


conn = sqlite3.connect(
    "data/db/nifty100.db"
)


# ============================================================
# TEST 1
# Distinct companies qualifying across any available year
# ============================================================

query1 = """
SELECT COUNT(DISTINCT company_id) AS qualifying_companies
FROM financial_ratios
WHERE return_on_equity_pct > 15
AND debt_to_equity < 1
"""

result1 = pd.read_sql(
    query1,
    conn
)

print("\n===== TEST 1: ANY AVAILABLE YEAR =====")
print(result1)


# ============================================================
# TEST 2
# Companies qualifying specifically for TTM
# ============================================================

query2 = """
SELECT COUNT(*) AS qualifying_ttm_companies
FROM financial_ratios
WHERE year = 'TTM'
AND return_on_equity_pct > 15
AND debt_to_equity < 1
"""

result2 = pd.read_sql(
    query2,
    conn
)

print("\n===== TEST 2: TTM ONLY =====")
print(result2)


# ============================================================
# TEST 3
# Show qualifying TTM companies
# ============================================================

query3 = """
SELECT
    company_id,
    year,
    return_on_equity_pct,
    debt_to_equity

FROM financial_ratios

WHERE year = 'TTM'
AND return_on_equity_pct > 15
AND debt_to_equity < 1

ORDER BY return_on_equity_pct DESC
"""

result3 = pd.read_sql(
    query3,
    conn
)

print("\n===== TEST 3: QUALIFYING TTM COMPANIES =====")

print(
    result3.to_string(
        index=False
    )
)

print(
    "\nTTM Result Count:",
    len(result3)
)


conn.close()