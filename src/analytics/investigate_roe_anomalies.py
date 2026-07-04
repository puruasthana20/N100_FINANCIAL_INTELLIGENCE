import sqlite3
import pandas as pd
from pathlib import Path


DB_PATH = "data/db/nifty100.db"
LOG_PATH = Path("output/ratio_edge_cases.log")

COMPANIES = [
    "BEL",
    "HAL",
    "INDIGO"
]


conn = sqlite3.connect(DB_PATH)


query = """
SELECT
    fr.company_id,
    fr.year,

    pl.net_profit,

    bs.equity_capital,
    bs.reserves,
    bs.borrowings,
    bs.total_assets,

    fr.return_on_equity_pct AS computed_roe,
    c.roe_percentage AS source_roe

FROM financial_ratios fr

LEFT JOIN profitandloss pl
    ON fr.company_id = pl.company_id
    AND fr.year = pl.year

LEFT JOIN balancesheet bs
    ON fr.company_id = bs.company_id
    AND fr.year = bs.year

LEFT JOIN companies c
    ON fr.company_id = c.company_id

WHERE fr.company_id IN (?, ?, ?)

AND fr.year = 'Mar 2024'

ORDER BY fr.company_id
"""


df = pd.read_sql(
    query,
    conn,
    params=COMPANIES
)


numeric_columns = [
    "net_profit",
    "equity_capital",
    "reserves",
    "borrowings",
    "total_assets",
    "computed_roe",
    "source_roe"
]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


print("\n===== EXTREME ROE INVESTIGATION =====")


findings = []


for _, row in df.iterrows():

    company = row["company_id"]

    equity = (
        row["equity_capital"]
        +
        row["reserves"]
    )


    if (
        pd.notna(equity)
        and
        equity > 0
    ):

        manual_roe = (
            row["net_profit"]
            /
            equity
        ) * 100

    else:

        manual_roe = None


    print("\n" + "=" * 60)

    print("Company:", company)

    print(
        "Net Profit:",
        row["net_profit"]
    )

    print(
        "Equity Capital:",
        row["equity_capital"]
    )

    print(
        "Reserves:",
        row["reserves"]
    )

    print(
        "Total Equity:",
        equity
    )

    print(
        "Computed ROE:",
        row["computed_roe"]
    )

    print(
        "Manual ROE:",
        round(manual_roe, 4)
        if manual_roe is not None
        else None
    )

    print(
        "Source ROE:",
        row["source_roe"]
    )


    # ========================================================
    # CLASSIFICATION
    # ========================================================

    if (
        manual_roe is not None
        and
        manual_roe > 500
    ):

        category = "Data Source Issue"

        explanation = (
            "Extreme ROE caused by unusually small reported "
            "equity denominator relative to net profit. "
            "Requires source balance-sheet unit review."
        )

    elif (
        pd.notna(row["source_roe"])
        and
        pd.notna(row["computed_roe"])
        and
        abs(
            row["source_roe"]
            -
            row["computed_roe"]
        ) > 5
    ):

        category = "Formula Discrepancy"

        explanation = (
            "Computed ROE differs materially from source ROE. "
            "Likely denominator definition or averaging-method difference."
        )

    else:

        category = "Version Difference"

        explanation = (
            "Difference likely caused by reporting-period or "
            "source-version mismatch."
        )


    findings.append(
        {
            "company_id": company,
            "metric": "ROE",
            "source": row["source_roe"],
            "computed": row["computed_roe"],
            "category": category,
            "explanation": explanation
        }
    )


# ============================================================
# APPEND REVIEWED FINDINGS TO LOG
# ============================================================

LOG_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    LOG_PATH,
    "a",
    encoding="utf-8"
) as f:

    f.write(
        "\n\n===== DAY 14 EXTREME ROE REVIEW =====\n"
    )

    for item in findings:

        f.write(
            f"{item['company_id']} | "
            f"{item['metric']} | "
            f"Source={item['source']} | "
            f"Computed={item['computed']} | "
            f"Category={item['category']} | "
            f"Explanation={item['explanation']}\n"
        )


print(
    "\nExtreme ROE review appended to "
    "output/ratio_edge_cases.log"
)


conn.close()