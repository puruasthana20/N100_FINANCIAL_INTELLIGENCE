import sys
from pathlib import Path
import pytest

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from src.analytics.ratios import *


def test_net_profit_margin():

    assert net_profit_margin(
        200,
        1000
    ) == 20.0


def test_net_profit_zero_sales():

    assert net_profit_margin(
        100,
        0
    ) is None


def test_operating_profit_margin():

    assert operating_profit_margin(
        300,
        1000
    ) == 30.0


def test_opm_crosscheck():

    assert opm_crosscheck(
        29.8,
        30.2
    )


def test_opm_crosscheck_fail():

    assert not opm_crosscheck(
        25,
        30
    )


def test_roe():

    assert return_on_equity(
        100,
        200,
        300
    ) == 20.0


def test_negative_equity():

    assert return_on_equity(
        100,
        -500,
        200
    ) is None


def test_roce():

    assert return_on_capital_employed(
        200,
        300,
        400,
        300
    ) == 20.0


def test_roa():

    assert return_on_assets(
        200,
        1000
    ) == 20.0


def test_roa_zero_assets():

    assert return_on_assets(
        200,
        0
    ) is None

def test_financial_roce_rating():
    assert roce_rating(10, "Financials") == "GOOD"


def test_non_financial_roce_rating():
    assert roce_rating(10, "Industrials") == "LOW"