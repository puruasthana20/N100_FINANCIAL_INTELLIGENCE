from src.screener.presets import run_preset


# ============================================================
# DAY 16 PRESET VALIDATION
# ============================================================

PRESETS = [
    "quality_compounder",
    "value_pick",
    "growth_accelerator",
    "dividend_champion",
    "debt_free_blue_chip",
    "turnaround_watch"
]


DISPLAY_COLUMNS = [
    "company_id",
    "year",
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "revenue_cagr_3yr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "dividend_yield_pct",
    "dividend_payout_ratio_pct",
    "pe_ratio",
    "pb_ratio",
    "sales",
    "composite_quality_score"
]


# ============================================================
# VALIDATION SUMMARY
# ============================================================

summary = []


print(
    "\n"
    + "=" * 80
)

print(
    "DAY 16 — PRESET SCREENER VALIDATION"
)

print(
    "=" * 80
)


for preset_name in PRESETS:

    print(
        "\n"
        + "=" * 80
    )

    print(
        preset_name.upper()
    )

    print(
        "=" * 80
    )


    try:

        result = run_preset(
            preset_name
        )


        count = len(result)


        if 5 <= count <= 50:

            status = "PASS"

        else:

            status = "REVIEW REQUIRED"


        summary.append(
            {
                "preset": preset_name,
                "company_count": count,
                "status": status
            }
        )


        print(
            f"\nCompanies Found: {count}"
        )

        print(
            f"Validation Status: {status}"
        )


        if result.empty:

            print(
                "\nNo companies matched this preset."
            )

            continue


        available_columns = [

            column

            for column in DISPLAY_COLUMNS

            if column in result.columns
        ]


        print(
            "\nTop Results:"
        )


        print(

            result[
                available_columns
            ]
            .head(10)
            .to_string(
                index=False
            )
        )


    except Exception as error:

        summary.append(
            {
                "preset": preset_name,
                "company_count": None,
                "status": "ERROR"
            }
        )


        print(
            "\nERROR:"
        )

        print(
            error
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print(
    "\n"
    + "=" * 80
)

print(
    "DAY 16 VALIDATION SUMMARY"
)

print(
    "=" * 80
)


for item in summary:

    print(

        f"{item['preset']:<25} "
        f"Count: {str(item['company_count']):<5} "
        f"Status: {item['status']}"
    )


# ============================================================
# EXIT CRITERIA CHECK
# ============================================================

valid_presets = [

    item

    for item in summary

    if item["status"] == "PASS"
]


print(
    "\n"
    + "=" * 80
)


print(
    f"Presets Passing Count Rule: "
    f"{len(valid_presets)}/{len(PRESETS)}"
)


if len(valid_presets) == len(PRESETS):

    print(
        "DAY 16 VALIDATION PASSED"
    )

else:

    print(
        "DAY 16 REQUIRES REVIEW"
    )


print(
    "=" * 80
)