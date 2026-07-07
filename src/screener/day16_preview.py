from src.screener.presets import (
    run_all_presets
)


# ============================================================
# RUN ALL PRESETS
# ============================================================

results = run_all_presets()


print(
    "\n"
    +
    "=" * 70
)

print(
    "DAY 16 — PRESET SCREENER REVIEW"
)

print(
    "=" * 70
)


for preset_name, df in results.items():

    print(
        "\n"
        +
        "=" * 70
    )

    print(
        preset_name
        .replace("_", " ")
        .upper()
    )

    print(
        "=" * 70
    )


    display_columns = [

        "company_id",

        "year",

        "broad_sector",

        "return_on_equity_pct",

        "debt_to_equity",

        "free_cash_flow_cr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "pe_ratio",

        "pb_ratio",

        "dividend_yield_pct",

        "dividend_payout_ratio_pct",

        "sales",

        "composite_quality_score"
    ]


    display_columns = [

        column

        for column in display_columns

        if column in df.columns
    ]


    print(

        df[
            display_columns
        ]
        .head(20)
        .to_string(
            index=False
        )
    )


    count = len(df)


    print(
        f"\nResult Count: {count}"
    )


    if 5 <= count <= 50:

        print(
            "Range Validation: PASS"
        )

    else:

        print(
            "Range Validation: REVIEW REQUIRED"
        )


print(
    "\n"
    +
    "=" * 70
)

print(
    "DAY 16 PREVIEW COMPLETED"
)

print(
    "=" * 70
)