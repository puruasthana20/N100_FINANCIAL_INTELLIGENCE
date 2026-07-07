import pandas as pd

from src.screener.engine import (
    load_config,
    load_screener_data,
    get_latest_annual_records,
    apply_filters
)


# ============================================================
# STANDARD PRESET NAMES
# ============================================================

STANDARD_PRESETS = [
    "quality_compounder",
    "value_pick",
    "growth_accelerator",
    "dividend_champion",
    "debt_free_blue_chip"
]


ALL_PRESETS = STANDARD_PRESETS + [
    "turnaround_watch"
]


# ============================================================
# STANDARD PRESET RUNNER
# ============================================================

def run_standard_preset(
    preset_name,
    df=None,
    config=None
):

    if config is None:
        config = load_config()


    if preset_name not in STANDARD_PRESETS:

        raise ValueError(
            f"'{preset_name}' is not a standard preset"
        )


    if df is None:

        df = load_screener_data()


    latest = get_latest_annual_records(
        df
    )


    filters = config[
        "presets"
    ][
        preset_name
    ]


    result = apply_filters(
        df=latest,
        filters=filters,
        config=config
    )


    return result


# ============================================================
# PERIOD PARSER
# ============================================================

def add_period_sort_columns(df):

    result = df.copy()


    result = result[
        result["year"] != "TTM"
    ].copy()


    result["fiscal_year"] = pd.to_numeric(

        result["year"]
        .astype(str)
        .str.extract(
            r"(\d{4})"
        )[0],

        errors="coerce"
    )


    month_map = {
        "Mar": 3,
        "Jun": 6,
        "Sep": 9,
        "Dec": 12
    }


    result["fiscal_month"] = (

        result["year"]
        .astype(str)
        .str[:3]
        .map(month_map)
        .fillna(0)
    )


    return result


# ============================================================
# TURNAROUND WATCH
# ============================================================

def run_turnaround_watch(
    df=None,
    config=None
):

    if config is None:
        config = load_config()


    if df is None:

        df = load_screener_data()


    ordered = add_period_sort_columns(
        df
    )


    ordered = ordered.sort_values(
        by=[
            "company_id",
            "fiscal_year",
            "fiscal_month"
        ]
    )


    # --------------------------------------------------------
    # Previous D/E for each company
    # --------------------------------------------------------

    ordered["previous_debt_to_equity"] = (

        ordered
        .groupby("company_id")[
            "debt_to_equity"
        ]
        .shift(1)
    )


    # --------------------------------------------------------
    # D/E declining condition
    # --------------------------------------------------------

    ordered["de_declining"] = (

        ordered["debt_to_equity"]
        <
        ordered["previous_debt_to_equity"]
    )


    # --------------------------------------------------------
    # Latest annual row per company
    # --------------------------------------------------------

    latest = (

        ordered
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
        .copy()
    )


    filters = config[
        "presets"
    ][
        "turnaround_watch"
    ].copy()


    # Remove special trend condition before generic filtering

    filters.pop(
        "de_declining",
        None
    )


    result = apply_filters(
        df=latest,
        filters=filters,
        config=config
    )


    result = result[
        result["de_declining"]
        ==
        True
    ]


    if (
        "composite_quality_score"
        in result.columns
    ):

        result = result.sort_values(
            by="composite_quality_score",
            ascending=False,
            na_position="last"
        )


    return result.reset_index(
        drop=True
    )


# ============================================================
# GENERAL PRESET RUNNER
# ============================================================

def run_preset(
    preset_name,
    df=None,
    config=None
):

    if preset_name not in ALL_PRESETS:

        raise ValueError(
            f"Unknown preset: {preset_name}"
        )


    if preset_name == "turnaround_watch":

        return run_turnaround_watch(
            df=df,
            config=config
        )


    return run_standard_preset(
        preset_name=preset_name,
        df=df,
        config=config
    )


# ============================================================
# RUN ALL SIX PRESETS
# ============================================================

def run_all_presets(
    df=None,
    config=None
):

    if config is None:
        config = load_config()


    if df is None:
        df = load_screener_data()


    results = {}


    for preset_name in ALL_PRESETS:

        results[preset_name] = run_preset(
            preset_name=preset_name,
            df=df.copy(),
            config=config
        )


    return results