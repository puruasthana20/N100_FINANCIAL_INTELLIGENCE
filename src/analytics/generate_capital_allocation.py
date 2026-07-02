import sqlite3
import pandas as pd

from src.analytics.cashflow_kpis import (
    capital_allocation_pattern
)

conn = sqlite3.connect(
    "data/db/nifty100.db"
)

df = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

rows = []

for _, row in df.iterrows():

    s1, s2, s3, pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"]
    )

    rows.append({

        "company_id":
        row["company_id"],

        "year":
        row["year"],

        "cfo_sign":
        s1,

        "cfi_sign":
        s2,

        "cff_sign":
        s3,

        "pattern_label":
        pattern
    })

pd.DataFrame(rows).to_csv(
    "output/capital_allocation.csv",
    index=False
)

print(
    "capital_allocation.csv generated"
)