import pandas as pd

from src.screener.scoring import load_scoring_data


# ============================================================
# LOAD DATA
# ============================================================

df = load_scoring_data()


# ============================================================
# PREPARE YEAR
# ============================================================

df["fiscal_year"] = (
    df["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["fiscal_year"] = pd.to_numeric(
    df["fiscal_year"],
    errors="coerce"
)


annual = df[
    df["year"] != "TTM"
].copy()


annual = annual.sort_values(
    by=[
        "company_id",
        "fiscal_year"
    ]
)


# ============================================================
# PREVIOUS YEAR D/E
# ============================================================

annual["previous_de"] = (
    annual
    .groupby("company_id")[
        "debt_to_equity"
    ]
    .shift(1)
)


annual["de_declining"] = (
    annual["debt_to_equity"]
    <
    annual["previous_de"]
)


# ============================================================
# LATEST RECORD
# ============================================================

latest = (
    annual
    .groupby(
        "company_id",
        as_index=False
    )
    .tail(1)
    .copy()
)


# ============================================================
# INDIVIDUAL CONDITIONS
# ============================================================

latest["revenue_growth_pass"] = (
    latest["revenue_cagr_3yr"] >= 10
)


latest["fcf_positive_pass"] = (
    latest["free_cash_flow_cr"] > 0
)


latest["de_declining_pass"] = (
    latest["de_declining"] == True
)


# ============================================================
# COUNTS
# ============================================================

print(
    "\n===== TURNAROUND WATCH DIAGNOSTIC ====="
)


print(
    "\nTotal Companies:",
    latest["company_id"].nunique()
)


print(
    "\n===== INDIVIDUAL CONDITION COUNTS ====="
)


print(
    "Revenue CAGR 3Y >= 10:",
    latest["revenue_growth_pass"].sum()
)


print(
    "FCF > 0:",
    latest["fcf_positive_pass"].sum()
)


print(
    "D/E Declining:",
    latest["de_declining_pass"].sum()
)


# ============================================================
# FILTER FUNNEL
# ============================================================

step1 = latest[
    latest["revenue_growth_pass"]
]


step2 = step1[
    step1["fcf_positive_pass"]
]


step3 = step2[
    step2["de_declining_pass"]
]


print(
    "\n===== FILTER FUNNEL ====="
)


print(
    "After Revenue CAGR filter:",
    len(step1)
)


print(
    "After FCF filter:",
    len(step2)
)


print(
    "After D/E declining filter:",
    len(step3)
)


# ============================================================
# FINAL MATCHES
# ============================================================

print(
    "\n===== FINAL TURNAROUND WATCH MATCHES ====="
)


display_columns = [

    "company_id",

    "year",

    "revenue_cagr_3yr",

    "free_cash_flow_cr",

    "previous_de",

    "debt_to_equity",

    "de_declining"
]


print(
    step3[
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


latest["conditions_passed"] = (

    latest[
        [
            "revenue_growth_pass",
            "fcf_positive_pass",
            "de_declining_pass"
        ]
    ]
    .sum(axis=1)
)


near_misses = (

    latest[
        latest["conditions_passed"] >= 2
    ]

    .sort_values(
        by="conditions_passed",
        ascending=False
    )
)


near_miss_columns = [

    "company_id",

    "year",

    "revenue_cagr_3yr",

    "free_cash_flow_cr",

    "previous_de",

    "debt_to_equity",

    "revenue_growth_pass",

    "fcf_positive_pass",

    "de_declining_pass",

    "conditions_passed"
]


print(
    near_misses[
        near_miss_columns
    ].to_string(
        index=False
    )
)