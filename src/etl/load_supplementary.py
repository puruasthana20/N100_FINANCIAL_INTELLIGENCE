import sqlite3
import pandas as pd

from pathlib import Path

DB_PATH = "data/db/nifty100.db"

RAW_PATH = Path("data/raw")

conn = sqlite3.connect(DB_PATH)

# ==========================================
# ANALYSIS
# ==========================================

analysis = pd.read_excel(
    RAW_PATH / "analysis.xlsx",
    header=1
)

analysis = analysis.drop(
    columns=["id"],
    errors="ignore"
)

analysis.to_sql(
    "analysis",
    conn,
    if_exists="append",
    index=False
)

print("Analysis Loaded:", len(analysis))

# ==========================================
# DOCUMENTS
# ==========================================

documents = pd.read_excel(
    RAW_PATH / "documents.xlsx",
    header=1
)

documents = documents.drop(
    columns=["id"],
    errors="ignore"
)

documents.columns = [
    "company_id",
    "year",
    "annual_report"
]

documents.to_sql(
    "documents",
    conn,
    if_exists="append",
    index=False
)

print("Documents Loaded:", len(documents))

# ==========================================
# PROS & CONS
# ==========================================

prosandcons = pd.read_excel(
    RAW_PATH / "prosandcons.xlsx",
    header=1
)

prosandcons = prosandcons.drop(
    columns=["id"],
    errors="ignore"
)

prosandcons.to_sql(
    "prosandcons",
    conn,
    if_exists="append",
    index=False
)

print("ProsCons Loaded:", len(prosandcons))

# ==========================================
# SECTORS
# ==========================================

sectors = pd.read_excel(
    RAW_PATH / "sectors.xlsx"
)

sectors = sectors.drop(
    columns=["id"]
)

sectors.to_sql(
    "sectors",
    conn,
    if_exists="append",
    index=False
)

print("Sectors Loaded:", len(sectors))

# ==========================================
# STOCK PRICES
# ==========================================

stock_prices = pd.read_excel(
    RAW_PATH / "stock_prices.xlsx"
)

stock_prices = stock_prices.drop(
    columns=["id"]
)

stock_prices.to_sql(
    "stock_prices",
    conn,
    if_exists="append",
    index=False
)

print("Stock Prices Loaded:", len(stock_prices))

# ==========================================
# FINANCIAL RATIOS
# ==========================================

financial_ratios = pd.read_excel(
    RAW_PATH / "financial_ratios.xlsx"
)

financial_ratios = financial_ratios.drop(
    columns=["id"]
)

financial_ratios = financial_ratios.drop_duplicates()

financial_ratios.to_sql(
    "financial_ratios",
    conn,
    if_exists="append",
    index=False
)

print("Financial Ratios Loaded:", len(financial_ratios))

# ==========================================
# PEER GROUPS
# ==========================================

peer_groups = pd.read_excel(
    RAW_PATH / "peer_groups.xlsx"
)

peer_groups = peer_groups.drop(
    columns=["id"]
)

peer_groups.to_sql(
    "peer_groups",
    conn,
    if_exists="append",
    index=False
)

print("Peer Groups Loaded:", len(peer_groups))

# ==========================================
# MARKET CAP
# ==========================================

market_cap = pd.read_excel(
    RAW_PATH / "market_cap.xlsx"
)

market_cap = market_cap.drop(
    columns=["id"]
)

market_cap.to_sql(
    "market_cap",
    conn,
    if_exists="append",
    index=False
)

print("Market Cap Loaded:", len(market_cap))

conn.commit()
conn.close()

print("\nAll Supplementary Tables Loaded")