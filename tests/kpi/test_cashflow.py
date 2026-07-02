import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from src.analytics.cashflow_kpis import *


def test_fcf():

    assert free_cash_flow(
        100,
        -30
    ) == 70


def test_negative_fcf():

    assert free_cash_flow(
        -50,
        -100
    ) == -150


def test_cfo_quality_high():

    assert (
        cfo_quality_score(
            120,
            100
        )
        ==
        "High Quality"
    )


def test_cfo_quality_moderate():

    assert (
        cfo_quality_score(
            70,
            100
        )
        ==
        "Moderate"
    )


def test_cfo_quality_low():

    assert (
        cfo_quality_score(
            20,
            100
        )
        ==
        "Accrual Risk"
    )


def test_capex():

    value, label = capex_intensity(
        -200,
        5000
    )

    assert label == "Moderate"


def test_fcf_conversion():

    assert (
        fcf_conversion_rate(
            100,
            200
        )
        ==
        50
    )


def test_pattern():

    _, _, _, pattern = capital_allocation_pattern(
        100,
        -50,
        -20
    )

    assert pattern == "Reinvestor"


def test_shareholder_returns():

    _, _, _, pattern = capital_allocation_pattern(
        100,
        -20,
        -30,
        1.5
    )

    assert pattern == "Shareholder Returns"


def test_distress():

    _, _, _, pattern = capital_allocation_pattern(
        -100,
        20,
        50
    )

    assert pattern == "Distress Signal"