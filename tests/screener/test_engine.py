import sys
from pathlib import Path

import pandas as pd
import pytest


# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parents[2])
)


from src.screener.engine import (
    apply_single_filter,
    apply_de_filter,
    apply_icr_filter,
    apply_filters
)

# ============================================================
# SAMPLE DATA
# ============================================================

@pytest.fixture
def sample_df():

    return pd.DataFrame(
        {
            "company_id": [
                "A",
                "B",
                "C",
                "D"
            ],

            "broad_sector": [
                "Information Technology",
                "Financials",
                "Industrials",
                "Financials"
            ],

            "return_on_equity_pct": [
                20,
                18,
                10,
                25
            ],

            "debt_to_equity": [
                0.5,
                8.0,
                2.5,
                10.0
            ],

            "interest_coverage": [
                5.0,
                1.0,
                None,
                0.5
            ],

            "free_cash_flow_cr": [
                100,
                -50,
                200,
                300
            ],

            "composite_quality_score": [
                70,
                80,
                50,
                90
            ]
        }
    )


# ============================================================
# TEST 1
# Minimum threshold
# ============================================================

def test_min_filter(sample_df):

    result = apply_single_filter(
        sample_df,
        "return_on_equity_pct",
        "min",
        15
    )

    assert len(result) == 3


# ============================================================
# TEST 2
# Maximum threshold
# ============================================================

def test_max_filter(sample_df):

    result = apply_single_filter(
        sample_df,
        "debt_to_equity",
        "max",
        1
    )

    assert len(result) == 1


# ============================================================
# TEST 3
# Equality filter
# ============================================================

def test_equal_filter(sample_df):

    result = apply_single_filter(
        sample_df,
        "debt_to_equity",
        "equal",
        0.5
    )

    assert len(result) == 1


# ============================================================
# TEST 4
# Financial sector bypass
# ============================================================

def test_financial_sector_de_bypass(
    sample_df
):

    result = apply_de_filter(
        sample_df,
        threshold=1
    )

    assert set(
        result["company_id"]
    ) == {
        "A",
        "B",
        "D"
    }


# ============================================================
# TEST 5
# Debt-free ICR pass
# ============================================================

def test_debt_free_icr_pass():

    df = pd.DataFrame(
        {
            "company_id": [
                "A",
                "B"
            ],

            "interest_coverage": [
                None,
                1.0
            ],

            "debt_to_equity": [
                0,
                1.5
            ]
        }
    )


    result = apply_icr_filter(
        df,
        threshold=2
    )


    assert list(
        result["company_id"]
    ) == ["A"]


# ============================================================
# TEST 6
# Unknown filter
# ============================================================

def test_unknown_filter(sample_df):

    config = {
        "metrics": {}
    }


    with pytest.raises(
        ValueError
    ):

        apply_filters(
            sample_df,
            {
                "unknown_metric": 10
            },
            config
        )


# ============================================================
# TEST 7
# Combined filters
# ============================================================

def test_combined_filters(sample_df):

    config = {

        "metrics": {

            "roe_min": {
                "column":
                "return_on_equity_pct",

                "operator":
                "min"
            },

            "fcf_min": {
                "column":
                "free_cash_flow_cr",

                "operator":
                "min"
            }
        }
    }


    result = apply_filters(
        sample_df,
        {
            "roe_min": 15,
            "fcf_min": 0
        },
        config
    )


    assert set(
        result["company_id"]
    ) == {
        "A",
        "D"
    }


# ============================================================
# TEST 8
# Composite score sorting
# ============================================================

def test_composite_score_sorting(
    sample_df
):

    config = {

        "metrics": {

            "roe_min": {
                "column":
                "return_on_equity_pct",

                "operator":
                "min"
            }
        }
    }


    result = apply_filters(
        sample_df,
        {
            "roe_min": 15
        },
        config
    )


    scores = result[
        "composite_quality_score"
    ].tolist()


    assert scores == sorted(
        scores,
        reverse=True
    )