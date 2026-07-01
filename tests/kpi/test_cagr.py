import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from src.analytics.cagr import *


def test_normal_cagr():

    value, flag = calculate_cagr(
        100,
        200,
        5
    )

    assert flag is None
    assert round(value,2) == 14.87


def test_turnaround():

    value, flag = calculate_cagr(
        -100,
        100,
        5
    )

    assert value is None
    assert flag == "TURNAROUND"


def test_decline_to_loss():

    value, flag = calculate_cagr(
        100,
        -50,
        5
    )

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():

    value, flag = calculate_cagr(
        -100,
        -20,
        5
    )

    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():

    value, flag = calculate_cagr(
        0,
        200,
        5
    )

    assert value is None
    assert flag == "ZERO_BASE"


def test_insufficient():

    value, flag = insufficient_data(
        3,
        5
    )

    assert value is None
    assert flag == "INSUFFICIENT"


def test_revenue_cagr():

    value, flag = revenue_cagr(
        100,
        200,
        5
    )

    assert flag is None


def test_pat_cagr():

    value, flag = pat_cagr(
        100,
        180,
        5
    )

    assert flag is None


def test_eps_cagr():

    value, flag = eps_cagr(
        20,
        40,
        5
    )

    assert flag is None


def test_sufficient_data():

    value, flag = insufficient_data(
        10,
        5
    )

    assert value == "OK"
    assert flag is None