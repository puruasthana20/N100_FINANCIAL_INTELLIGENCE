import sqlite3
import pandas as pd

from pathlib import Path

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year
)

DB_PATH = "data/db/nifty100.db"

RAW_PATH = Path("data/raw")

conn = sqlite3.connect(DB_PATH)

# ==================================================
# COMPANIES
# ==================================================

companies = pd.read_excel(
    RAW_PATH / "companies.xlsx",
    header=1
)

companies = companies[
    [
        "id",
        "company_name",
        "website",
        "face_value",
        "book_value",
        "roce_percentage",
        "roe_percentage"
    ]
]

companies.columns = [
    "company_id",
    "company_name",
    "website",
    "face_value",
    "book_value",
    "roce_percentage",
    "roe_percentage"
]

companies["company_id"] = (
    companies["company_id"]
    .apply(normalize_ticker)
)

companies.to_sql(
    "companies",
    conn,
    if_exists="append",
    index=False
)

print(
    "Companies Loaded:",
    len(companies)
)

# ==================================================
# PROFIT & LOSS
# ==================================================

profit_loss = pd.read_excel(
    RAW_PATH / "profitandloss.xlsx",
    header=1
)

profit_loss = profit_loss.drop(
    columns=["id"],
    errors="ignore"
)

profit_loss["company_id"] = (
    profit_loss["company_id"]
    .apply(normalize_ticker)
)

profit_loss["year"] = (
    profit_loss["year"]
    .apply(normalize_year)
)

profit_loss = profit_loss.drop_duplicates(
    subset=["company_id", "year"]
)

profit_loss.to_sql(
    "profitandloss",
    conn,
    if_exists="append",
    index=False
)

print(
    "Profit & Loss Loaded:",
    len(profit_loss)
)

# ==================================================
# BALANCE SHEET
# ==================================================

balance_sheet = pd.read_excel(
    RAW_PATH / "balancesheet.xlsx",
    header=1
)

balance_sheet = balance_sheet.drop(
    columns=["id"],
    errors="ignore"
)

balance_sheet["company_id"] = (
    balance_sheet["company_id"]
    .apply(normalize_ticker)
)

balance_sheet["year"] = (
    balance_sheet["year"]
    .apply(normalize_year)
)

balance_sheet = balance_sheet.drop_duplicates(
    subset=["company_id", "year"]
)

balance_sheet.to_sql(
    "balancesheet",
    conn,
    if_exists="append",
    index=False
)

print(
    "Balance Sheet Loaded:",
    len(balance_sheet)
)

# ==================================================
# CASHFLOW
# ==================================================

cashflow = pd.read_excel(
    RAW_PATH / "cashflow.xlsx",
    header=1
)

cashflow = cashflow.drop(
    columns=["id"],
    errors="ignore"
)

cashflow["company_id"] = (
    cashflow["company_id"]
    .apply(normalize_ticker)
)

cashflow["year"] = (
    cashflow["year"]
    .apply(normalize_year)
)

cashflow = cashflow.drop_duplicates(
    subset=["company_id", "year"]
)

cashflow.to_sql(
    "cashflow",
    conn,
    if_exists="append",
    index=False
)

print(
    "Cashflow Loaded:",
    len(cashflow)
)

# ==================================================
# DONE
# ==================================================

conn.commit()
conn.close()

print(
    "\nCore Financial Tables Loaded Successfully"
)
audit = pd.DataFrame({
    "table_name": [
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow"
    ],
    "row_count": [
        len(companies),
        len(profit_loss),
        len(balance_sheet),
        len(cashflow)
    ]
})

audit.to_csv(
    "output/load_audit.csv",
    index=False
)

print(
    "load_audit.csv generated"
)