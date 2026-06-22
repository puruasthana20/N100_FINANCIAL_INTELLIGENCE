import pandas as pd
from pathlib import Path

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year
)

RAW_PATH = Path("data/raw")

# =====================================
# LOAD DATA
# =====================================

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

documents = pd.read_excel(
    RAW_PATH / "documents.xlsx",
    header=1
)

# =====================================
# NORMALIZATION
# =====================================

for df in [profit_loss, balance_sheet, cashflow]:

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

# =====================================
# DQ-01 Duplicate Company IDs
# =====================================

duplicates = companies[
    companies["id"].duplicated()
]

# =====================================
# DQ-02 Duplicate P&L Keys
# =====================================

pl_duplicates = profit_loss[
    profit_loss.duplicated(
        subset=["company_id", "year"]
    )
]

# =====================================
# DQ-03 FK Integrity
# =====================================

company_ids = set(
    companies["id"]
)

invalid_fk = profit_loss[
    ~profit_loss["company_id"]
    .isin(company_ids)
]

# =====================================
# DQ-04 Balance Sheet Balance Check
# =====================================

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

# =====================================
# DQ-05 OPM Cross Check
# =====================================

profit_loss["calculated_opm"] = (
    profit_loss["operating_profit"]
    /
    profit_loss["sales"]
) * 100

profit_loss["opm_diff"] = abs(
    profit_loss["calculated_opm"]
    -
    profit_loss["opm_percentage"]
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

# =====================================
# DQ-06 Positive Sales
# =====================================

negative_sales = profit_loss[
    profit_loss["sales"] <= 0
]

# =====================================
# DQ-07 Missing Website
# =====================================

missing_websites = companies[
    companies["website"].isna()
]

# =====================================
# DQ-08 Invalid Website
# =====================================

invalid_websites = companies[
    ~companies["website"]
    .astype(str)
    .str.startswith("http")
]

# =====================================
# DQ-09 Invalid Tax Rate
# =====================================

invalid_tax = profit_loss[
    (profit_loss["tax_percentage"] < 0)
    |
    (profit_loss["tax_percentage"] > 100)
]

# =====================================
# DQ-10 Dividend >100
# =====================================

invalid_dividend = profit_loss[
    profit_loss["dividend_payout"] > 100
]

# =====================================
# DQ-11 Missing EPS
# =====================================

missing_eps = profit_loss[
    profit_loss["eps"].isna()
]

# =====================================
# DQ-12 Coverage <3 Years
# =====================================

coverage = (
    profit_loss
    .groupby("company_id")
    .size()
)

low_coverage = coverage[
    coverage < 3
]

# =====================================
# DQ-13 Null Company ID
# =====================================

null_company_ids = profit_loss[
    profit_loss["company_id"].isna()
]

# =====================================
# DQ-14 Duplicate Annual Reports
# =====================================

duplicate_reports = documents[
    documents["Annual_Report"]
    .duplicated()
]

# =====================================
# DQ-15 Negative Book Value
# =====================================

negative_book_value = companies[
    companies["book_value"] < 0
]

# =====================================
# DQ-16 Missing Annual Reports
# =====================================

missing_reports = documents[
    documents["Annual_Report"].isna()
]

# =====================================
# SUMMARY
# =====================================

print("\n===== DATA QUALITY SUMMARY =====")

print("DQ-01:", len(duplicates))
print("DQ-02:", len(pl_duplicates))
print("DQ-03:", len(invalid_fk))
print("DQ-04:", len(bs_failures))
print("DQ-05:", len(opm_failures))
print("DQ-06:", len(negative_sales))
print("DQ-07:", len(missing_websites))
print("DQ-08:", len(invalid_websites))
print("DQ-09:", len(invalid_tax))
print("DQ-10:", len(invalid_dividend))
print("DQ-11:", len(missing_eps))
print("DQ-12:", len(low_coverage))
print("DQ-13:", len(null_company_ids))
print("DQ-14:", len(duplicate_reports))
print("DQ-15:", len(negative_book_value))
print("DQ-16:", len(missing_reports))

# =====================================
# VALIDATION FAILURES CSV
# =====================================

failures = []

missing_companies = sorted(
    set(profit_loss["company_id"])
    -
    set(companies["id"])
)

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

for _, row in missing_websites.iterrows():
    failures.append([
        "DQ-07",
        "WARNING",
        row["id"],
        "Missing website"
    ])

for _, row in invalid_tax.iterrows():
    failures.append([
        "DQ-09",
        "WARNING",
        row["company_id"],
        "Invalid tax percentage"
    ])

for _, row in invalid_dividend.iterrows():
    failures.append([
        "DQ-10",
        "WARNING",
        row["company_id"],
        "Dividend payout > 100"
    ])

for _, row in missing_eps.iterrows():
    failures.append([
        "DQ-11",
        "WARNING",
        row["company_id"],
        "Missing EPS"
    ])

for company in low_coverage.index:
    failures.append([
        "DQ-12",
        "WARNING",
        company,
        "Coverage less than 3 years"
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

print("\nvalidation_failures.csv generated")