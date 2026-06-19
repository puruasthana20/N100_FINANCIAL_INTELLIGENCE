import pandas as pd

from pathlib import Path

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year
)

RAW_PATH = Path("data/raw")


companies = pd.read_excel(
    RAW_PATH / "companies.xlsx",
    header=1
)

profit_loss = pd.read_excel(
    RAW_PATH / "profitandloss.xlsx",
    header=1
)

balance_sheet = pd.read_excel(
    RAW_PATH / "balancesheet.xlsx",
    header=1
)

cashflow = pd.read_excel(
    RAW_PATH / "cashflow.xlsx",
    header=1
)

for df in [
    profit_loss,
    balance_sheet,
    cashflow
]:
    df["company_id"] = (
        df["company_id"]
        .apply(normalize_ticker)
    )

    df["year"] = (
        df["year"]
        .apply(normalize_year)
    )

companies["id"] = (
    companies["id"]
    .apply(normalize_ticker)
)

duplicates = companies[
    companies["id"].duplicated()
]

print(
    "DQ-01 Duplicate Companies:",
    len(duplicates)
)

pl_duplicates = profit_loss[
    profit_loss.duplicated(
        subset=["company_id","year"]
    )
]

print(
    "DQ-02 Duplicate P&L Records:",
    len(pl_duplicates)
)

company_ids = set(
    companies["id"]
)

invalid_fk = profit_loss[
    ~profit_loss["company_id"]
    .isin(company_ids)
]

print(
    "DQ-03 Invalid FK:",
    len(invalid_fk)
)

balance_sheet["difference_pct"] = (
    abs(
        balance_sheet["total_assets"]
        -
        balance_sheet["total_liabilities"]
    )
    /
    balance_sheet["total_assets"]
) * 100

bs_failures = balance_sheet[
    balance_sheet["difference_pct"] > 1
]

print(
    "DQ-04 BS Failures:",
    len(bs_failures)
)

profit_loss["calculated_opm"] = (
    profit_loss["operating_profit"]
    /
    profit_loss["sales"]
) * 100

profit_loss["opm_diff"] = (
    abs(
        profit_loss["calculated_opm"]
        -
        profit_loss["opm_percentage"]
    )
)

opm_failures = profit_loss[
    profit_loss["opm_diff"] > 1
]

print(
    "DQ-05 OPM Failures:",
    len(opm_failures)
)

negative_sales = profit_loss[
    profit_loss["sales"] <= 0
]

print(
    "DQ-06 Negative Sales:",
    len(negative_sales)
)

print("\n===== DQ SUMMARY =====")

print(
    "DQ-01:",
    len(duplicates)
)

print(
    "DQ-02:",
    len(pl_duplicates)
)

print(
    "DQ-03:",
    len(invalid_fk)
)

print(
    "DQ-04:",
    len(bs_failures)
)

print(
    "DQ-05:",
    len(opm_failures)
)

print(
    "DQ-06:",
    len(negative_sales)
)

print("\nDQ-02 SAMPLE")

print(
    pl_duplicates[
        ["company_id","year"]
    ].head(10)
)

print("\nDQ-03 SAMPLE")

print(
    invalid_fk[
        ["company_id"]
    ].head(20)
)

print("\nDQ-05 SAMPLE")

print(
    opm_failures[
        [
            "company_id",
            "year",
            "sales",
            "operating_profit",
            "opm_percentage",
            "calculated_opm"
        ]
    ].head(10)
)

print("\nDQ-06 SAMPLE")

print(
    negative_sales[
        [
            "company_id",
            "year",
            "sales"
        ]
    ]
)

print(
    profit_loss[
        profit_loss["company_id"]=="ADANIPORTS"
    ][["company_id","year"]]
)
print(
    companies[
        companies["id"]
        .isin(["ULTRACEMCO","UNIONBANK"])
    ]
)
financial_companies = [
    "AXISBANK",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "KOTAKBANK",
    "INDUSINDBK",
    "BANKBARODA",
    "PNB",
    "UNIONBANK"
]

opm_failures = profit_loss[
    (~profit_loss["company_id"].isin(financial_companies))
    &
    (profit_loss["opm_diff"] > 1)
]

print(
    companies[
        companies["id"]
        .str.contains(
            "ULTRA|UNION",
            na=False
        )
    ]
)
profit_loss = profit_loss.drop_duplicates(
    subset=["company_id", "year"]
)
missing_companies = sorted(
    set(profit_loss["company_id"])
    -
    set(companies["id"])
)

print(missing_companies)
print("Companies Count:", len(companies))
print("Unique P&L Companies:", profit_loss["company_id"].nunique())
failures = []

for company in missing_companies:
    failures.append([
        "DQ-03",
        "CRITICAL",
        company,
        "Company missing from companies.xlsx"
    ])

for _, row in negative_sales.iterrows():
    failures.append([
        "DQ-06",
        "WARNING",
        row["company_id"],
        "Sales <= 0"
    ])

failure_df = pd.DataFrame(
    failures,
    columns=[
        "rule_id",
        "severity",
        "entity",
        "issue"
    ]
)

failure_df.to_csv(
    "output/validation_failures.csv",
    index=False
)

print("validation_failures.csv generated")