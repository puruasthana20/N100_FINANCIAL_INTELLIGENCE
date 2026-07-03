import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

companies = [
    "ABB",
    "RELIANCE",
    "HDFCBANK"
]

for company in companies:

    print("\n" + "=" * 60)
    print(company)

    df = pd.read_sql(
        f"""
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            revenue_cagr_5yr
        FROM financial_ratios
        WHERE company_id='{company}'
        ORDER BY year
        """,
        conn
    )

    print(df)

conn.close()