import sys
from pathlib import Path
import pytest

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from src.analytics.ratios import *


def test_debt_to_equity():

    assert debt_to_equity(
        200,
        100,
        100
    ) == 1.0


def test_debt_free():

    assert debt_to_equity(
        0,
        100,
        100
    ) == 0


def test_negative_equity():

    assert debt_to_equity(
        200,
        -300,
        100
    ) is None


def test_interest_coverage():

    assert interest_coverage_ratio(
        200,
        20,
        20
    ) == 11.0


def test_interest_zero():

    assert interest_coverage_ratio(
        200,
        20,
        0
    ) is None


def test_icr_label():

    assert icr_label(0) == "Debt Free"


def test_high_leverage():

    assert high_leverage_flag(
        6,
        "Industrials"
    )


def test_asset_turnover():

    assert asset_turnover(
        1000,
        500
    ) == 2.0