from pathlib import Path
import sqlite3
import pandas as pd

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# Database
# ==========================================================

conn = sqlite3.connect(DB_PATH)

# ==========================================================
# Latest Market Valuation
# ==========================================================

market = pd.read_sql(
"""
SELECT *
FROM market_cap
WHERE year = (
    SELECT MAX(year)
    FROM market_cap
)
""",
conn,
)

# ==========================================================
# 5-Year PE History
# ==========================================================

pe_history = pd.read_sql(
"""
SELECT
company_id,
year,
pe_ratio
FROM market_cap
WHERE year>=2020
""",
conn,
)

# ==========================================================
# Latest Operating Cash Flow
# ==========================================================

cashflow = pd.read_sql(
"""
WITH ranked AS
(
SELECT *,
ROW_NUMBER() OVER
(
PARTITION BY company_id
ORDER BY CAST(substr(year,1,4) AS INTEGER) DESC
) rn
FROM cashflow
)

SELECT
company_id,
operating_activity
FROM ranked
WHERE rn=1
""",
conn,
)

# ==========================================================
# Company Information
# ==========================================================

companies = pd.read_sql(
"""
SELECT
company_id,
company_name
FROM companies
""",
conn,
)

# ==========================================================
# Sector Information
# ==========================================================

sector = pd.read_sql(
"""
SELECT
company_id,
broad_sector
FROM sectors
""",
conn,
)

conn.close()

# ==========================================================
# Merge
# ==========================================================

df = (
market
.merge(companies,on="company_id")
.merge(sector,on="company_id")
.merge(cashflow,on="company_id",how="left")
)

# ==========================================================
# Numeric Conversion
# ==========================================================

numeric_cols = [
"market_cap_crore",
"pe_ratio",
"pb_ratio",
"ev_ebitda",
"operating_activity",
]

for c in numeric_cols:
    df[c] = pd.to_numeric(df[c],errors="coerce")

# ==========================================================
# FCF Yield
# ==========================================================
# Dataset does not contain CapEx.
# Operating Cash Flow is used as FCF proxy.

df["FCF_yield_pct"] = (
df["operating_activity"]
/
df["market_cap_crore"]
)*100

# ==========================================================
# Five-Year Median PE
# ==========================================================

pe_history["pe_ratio"] = pd.to_numeric(
pe_history["pe_ratio"],
errors="coerce"
)

median_pe = (
pe_history
.groupby("company_id")["pe_ratio"]
.median()
.rename("5yr_median_PE")
.reset_index()
)

df = df.merge(
median_pe,
on="company_id",
how="left"
)

# ==========================================================
# Sector Median PE
# ==========================================================

sector_pe = (
df
.groupby("broad_sector")["pe_ratio"]
.median()
.rename("sector_median_PE")
.reset_index()
)

df = df.merge(
sector_pe,
on="broad_sector",
how="left"
)

# ==========================================================
# PE vs Sector Median
# ==========================================================

df["PE_vs_sector_median_pct"] = (
(
df["pe_ratio"]
-
df["sector_median_PE"]
)
/
df["sector_median_PE"]
)*100

# ==========================================================
# Valuation Flag
# ==========================================================

def valuation_flag(row):

    pe=row["pe_ratio"]
    median=row["sector_median_PE"]

    if pd.isna(pe) or pd.isna(median):
        return "Fair"

    if pe>median*1.5:
        return "Caution"

    if pe<median*0.7:
        return "Discount"

    return "Fair"

df["flag"] = df.apply(
valuation_flag,
axis=1
)

# ==========================================================
# Final Columns
# ==========================================================

summary = df[
[
"company_id",
"company_name",
"broad_sector",
"pe_ratio",
"pb_ratio",
"ev_ebitda",
"FCF_yield_pct",
"5yr_median_PE",
"PE_vs_sector_median_pct",
"flag",
]
].rename(
columns={
"broad_sector":"sector",
"pe_ratio":"P/E",
"pb_ratio":"P/B",
"ev_ebitda":"EV/EBITDA",
}
)

# ==========================================================
# Export
# ==========================================================

summary.to_excel(
OUTPUT_DIR/"valuation_summary.xlsx",
index=False,
)

flags = summary[
summary["flag"]!="Fair"
]

flags.to_csv(
OUTPUT_DIR/"valuation_flags.csv",
index=False,
)

# ==========================================================
# Validation
# ==========================================================

print("="*50)

print("VALUATION SUMMARY")

print("="*50)

print(f"Companies Processed : {len(summary)}")

print(f"Caution Flags      : {(summary.flag=='Caution').sum()}")

print(f"Discount Flags     : {(summary.flag=='Discount').sum()}")

print(f"Fair Companies     : {(summary.flag=='Fair').sum()}")

print()

print("Generated:")

print("output/valuation_summary.xlsx")

print("output/valuation_flags.csv")