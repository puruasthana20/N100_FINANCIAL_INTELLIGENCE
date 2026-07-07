from src.screener.engine import (
    load_screener_data,
    get_latest_annual_records
)


# ============================================================
# LOAD DATA
# ============================================================

df = load_screener_data()

df = get_latest_annual_records(df)


print(
    "\n===== VALUE PICK DIAGNOSTIC ====="
)

print(
    "\nTotal Companies:",
    len(df)
)


# ============================================================
# DATA AVAILABILITY
# ============================================================

print(
    "\n===== DATA AVAILABILITY ====="
)


columns = [
    "pe_ratio",
    "pb_ratio",
    "debt_to_equity",
    "dividend_yield_pct"
]


for column in columns:

    available = df[column].notna().sum()

    missing = df[column].isna().sum()

    print(
        f"{column:<25}"
        f"Available: {available:<5}"
        f"Missing: {missing}"
    )


# ============================================================
# INDIVIDUAL FILTER COUNTS
# ============================================================

print(
    "\n===== INDIVIDUAL FILTER COUNTS ====="
)


pe_pass = df[
    df["pe_ratio"] < 20
]


pb_pass = df[
    df["pb_ratio"] < 3
]


de_pass = df[
    (
        df["debt_to_equity"] < 2
    )
    |
    (
        df["broad_sector"]
        .fillna("")
        .str.strip()
        .str.lower()
        ==
        "financials"
    )
]


dividend_pass = df[
    df["dividend_yield_pct"] > 1
]


print(
    "P/E < 20:",
    len(pe_pass)
)

print(
    "P/B < 3:",
    len(pb_pass)
)

print(
    "D/E < 2 with Financial bypass:",
    len(de_pass)
)

print(
    "Dividend Yield > 1:",
    len(dividend_pass)
)


# ============================================================
# FILTER FUNNEL
# ============================================================

print(
    "\n===== FILTER FUNNEL ====="
)


step1 = df[
    df["pe_ratio"] < 20
]


print(
    "After P/E filter:",
    len(step1)
)


step2 = step1[
    step1["pb_ratio"] < 3
]


print(
    "After P/B filter:",
    len(step2)
)


financial_mask = (
    step2["broad_sector"]
    .fillna("")
    .str.strip()
    .str.lower()
    ==
    "financials"
)


step3 = step2[
    financial_mask
    |
    (
        step2["debt_to_equity"] < 2
    )
]


print(
    "After D/E filter:",
    len(step3)
)


step4 = step3[
    step3["dividend_yield_pct"] > 1
]


print(
    "After Dividend Yield filter:",
    len(step4)
)


# ============================================================
# FINAL MATCHES
# ============================================================

print(
    "\n===== FINAL VALUE PICK MATCHES ====="
)


display_columns = [
    "company_id",
    "year",
    "broad_sector",
    "pe_ratio",
    "pb_ratio",
    "debt_to_equity",
    "dividend_yield_pct",
    "composite_quality_score"
]


print(
    step4[
        display_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# NEAR MISSES
# ============================================================

print(
    "\n===== NEAR MISSES ====="
)


near_miss = df[
    (
        df["pe_ratio"] < 25
    )
    &
    (
        df["pb_ratio"] < 4
    )
    &
    (
        df["dividend_yield_pct"] > 0.5
    )
]


print(
    near_miss[
        display_columns
    ]
    .sort_values(
        by="composite_quality_score",
        ascending=False
    )
    .head(20)
    .to_string(
        index=False
    )
)