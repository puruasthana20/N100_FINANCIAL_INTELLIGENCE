import sys
from pathlib import Path

import pandas as pd
import pytest


sys.path.append(
    str(
        Path(__file__)
        .resolve()
        .parents[2]
    )
)


from src.screener.presets import (
    run_preset,
    run_turnaround_watch
)


# ============================================================
# TEST CONFIG
# ============================================================

@pytest.fixture
def preset_config():

    return {

        "metrics": {

            "roe_min": {
                "column":
                "return_on_equity_pct",

                "operator":
                "min"
            },

            "debt_to_equity_max": {
                "column":
                "debt_to_equity",

                "operator":
                "max",

                "financial_sector_bypass":
                True
            },

            "fcf_min": {
                "column":
                "free_cash_flow_cr",

                "operator":
                "min"
            },

            "revenue_cagr_5yr_min": {
                "column":
                "revenue_cagr_5yr",

                "operator":
                "min"
            },

            "pat_cagr_5yr_min": {
                "column":
                "pat_cagr_5yr",

                "operator":
                "min"
            },

            "pe_max": {
                "column":
                "pe_ratio",

                "operator":
                "max"
            },

            "pb_max": {
                "column":
                "pb_ratio",

                "operator":
                "max"
            },

            "dividend_yield_min": {
                "column":
                "dividend_yield_pct",

                "operator":
                "min"
            },

            "dividend_payout_max": {
                "column":
                "dividend_payout_ratio_pct",

                "operator":
                "max"
            },

            "debt_to_equity_equal": {
                "column":
                "debt_to_equity",

                "operator":
                "equal"
            },

            "sales_min": {
                "column":
                "sales",

                "operator":
                "min"
            },

            "revenue_cagr_3yr_min": {
                "column":
                "revenue_cagr_3yr",

                "operator":
                "min"
            }
        },


        "presets": {

            "quality_compounder": {

                "roe_min": 15,

                "debt_to_equity_max":
                1,

                "fcf_min": 0,

                "revenue_cagr_5yr_min":
                10
            },


            "value_pick": {

                "pe_max": 20,

                "pb_max": 3,

                "debt_to_equity_max":
                2,

                "dividend_yield_min":
                1
            },


            "growth_accelerator": {

                "pat_cagr_5yr_min":
                20,

                "revenue_cagr_5yr_min":
                15,

                "debt_to_equity_max":
                2
            },


            "dividend_champion": {

                "dividend_yield_min":
                2,

                "dividend_payout_max":
                80,

                "fcf_min":
                0
            },


            "debt_free_blue_chip": {

                "debt_to_equity_equal":
                0,

                "roe_min":
                12,

                "sales_min":
                5000
            },


            "turnaround_watch": {

                "revenue_cagr_3yr_min":
                10,

                "fcf_min":
                0,

                "de_declining":
                True
            }
        }
    }


# ============================================================
# STANDARD SAMPLE DATA
# ============================================================

@pytest.fixture
def sample_df():

    return pd.DataFrame({

        "company_id": [
            "A",
            "B",
            "C"
        ],

        "year": [
            "Mar 2024",
            "Mar 2024",
            "Mar 2024"
        ],

        "broad_sector": [
            "Industrials",
            "Financials",
            "Technology"
        ],

        "return_on_equity_pct": [
            20,
            18,
            10
        ],

        "debt_to_equity": [
            0.5,
            8.0,
            0
        ],

        "free_cash_flow_cr": [
            100,
            50,
            -20
        ],

        "revenue_cagr_5yr": [
            15,
            12,
            5
        ],

        "pat_cagr_5yr": [
            25,
            10,
            5
        ],

        "pe_ratio": [
            15,
            18,
            30
        ],

        "pb_ratio": [
            2,
            2.5,
            5
        ],

        "dividend_yield_pct": [
            2,
            3,
            0.5
        ],

        "dividend_payout_ratio_pct": [
            50,
            70,
            90
        ],

        "sales": [
            10000,
            8000,
            6000
        ],

        "revenue_cagr_3yr": [
            15,
            12,
            8
        ],

        "composite_quality_score": [
            80,
            70,
            50
        ]
    })


# ============================================================
# TEST 1
# QUALITY COMPOUNDER
# ============================================================

def test_quality_compounder(
    sample_df,
    preset_config
):

    result = run_preset(
        "quality_compounder",
        df=sample_df,
        config=preset_config
    )

    assert set(
        result["company_id"]
    ) == {
        "A",
        "B"
    }


# ============================================================
# TEST 2
# VALUE PICK
# ============================================================

def test_value_pick(
    sample_df,
    preset_config
):

    result = run_preset(
        "value_pick",
        df=sample_df,
        config=preset_config
    )

    assert set(
        result["company_id"]
    ) == {
        "A",
        "B"
    }


# ============================================================
# TEST 3
# GROWTH ACCELERATOR
# ============================================================

def test_growth_accelerator(
    sample_df,
    preset_config
):

    result = run_preset(
        "growth_accelerator",
        df=sample_df,
        config=preset_config
    )

    assert list(
        result["company_id"]
    ) == ["A"]


# ============================================================
# TEST 4
# DIVIDEND CHAMPION
# ============================================================

def test_dividend_champion(
    sample_df,
    preset_config
):

    result = run_preset(
        "dividend_champion",
        df=sample_df,
        config=preset_config
    )

    assert set(
        result["company_id"]
    ) == {
        "A",
        "B"
    }


# ============================================================
# TEST 5
# DEBT-FREE BLUE CHIP
# ============================================================

def test_debt_free_blue_chip(
    sample_df,
    preset_config
):

    modified = sample_df.copy()

    modified.loc[
        modified["company_id"] == "C",
        "return_on_equity_pct"
    ] = 15


    result = run_preset(
        "debt_free_blue_chip",
        df=modified,
        config=preset_config
    )


    assert list(
        result["company_id"]
    ) == ["C"]


# ============================================================
# TEST 6
# UNKNOWN PRESET
# ============================================================

def test_unknown_preset(
    sample_df,
    preset_config
):

    with pytest.raises(
        ValueError
    ):

        run_preset(
            "imaginary_money_machine",
            df=sample_df,
            config=preset_config
        )


# ============================================================
# TEST 7
# TURNAROUND WATCH
# ============================================================

def test_turnaround_watch(
    preset_config
):

    df = pd.DataFrame({

        "company_id": [
            "A",
            "A",
            "B",
            "B"
        ],

        "year": [
            "Mar 2023",
            "Mar 2024",
            "Mar 2023",
            "Mar 2024"
        ],

        "broad_sector": [
            "Industrials",
            "Industrials",
            "Technology",
            "Technology"
        ],

        "debt_to_equity": [
            2.0,
            1.0,
            1.0,
            2.0
        ],

        "free_cash_flow_cr": [
            50,
            100,
            50,
            100
        ],

        "revenue_cagr_3yr": [
            12,
            15,
            12,
            15
        ],

        "composite_quality_score": [
            50,
            60,
            50,
            60
        ]
    })


    result = run_turnaround_watch(
        df=df,
        config=preset_config
    )


    assert list(
        result["company_id"]
    ) == ["A"]