import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/db/nifty100.db"
)

companies = pd.read_sql(
    """
    SELECT
        company_id,
        roce_percentage,
        roe_percentage
    FROM companies
    """,
    conn
)

ratios = pd.read_sql(
    """
    SELECT
        company_id,
        MAX(return_on_equity_pct) AS roe,
        MAX(return_on_capital_employed_pct) AS roce
    FROM financial_ratios
    GROUP BY company_id
    """,
    conn
)

merged = companies.merge(
    ratios,
    on="company_id",
    how="left"
)

log = []

for _, row in merged.iterrows():

    # ROE Check
    if pd.notna(row["roe"]):

        diff = abs(
            row["roe_percentage"]
            - row["roe"]
        )

        if diff > 5:

            log.append({

                "company_id": row["company_id"],

                "metric": "ROE",

                "source": row["roe_percentage"],

                "computed": row["roe"],

                "difference": round(diff, 2),

                "category": "Version Difference"

            })

    # ROCE Check
    if pd.notna(row["roce"]):

        diff = abs(
            row["roce_percentage"]
            - row["roce"]
        )

        if diff > 5:

            log.append({

                "company_id": row["company_id"],

                "metric": "ROCE",

                "source": row["roce_percentage"],

                "computed": row["roce"],

                "difference": round(diff, 2),

                "category": "Formula Discrepancy"

            })

with open(
    "output/ratio_edge_cases.log",
    "w"
) as f:

    for item in log:

        f.write(
            f"{item['company_id']} | "
            f"{item['metric']} | "
            f"Source={item['source']} | "
            f"Computed={item['computed']} | "
            f"Difference={item['difference']} | "
            f"Category={item['category']}\n"
        )

print(
    "Edge Cases Logged:",
    len(log)
)

conn.close()