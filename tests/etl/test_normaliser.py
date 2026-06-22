import sys
from pathlib import Path
import pytest

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year
)

# =====================================
# TICKER TESTS (15)
# =====================================

@pytest.mark.parametrize(
    "input_ticker,expected",
    [
        ("tcs", "TCS"),
        ("infy", "INFY"),
        ("wipro", "WIPRO"),
        ("reliance", "RELIANCE"),
        ("hdfcbank", "HDFCBANK"),
        (" axisbank ", "AXISBANK"),
        ("sbin", "SBIN"),
        ("itc", "ITC"),
        ("lt", "LT"),
        ("nestleind", "NESTLEIND"),
        ("maruti", "MARUTI"),
        ("bajaj-auto", "BAJAJ-AUTO"),
        ("ultracemco", "ULTRACEMCO"),
        ("vedl", "VEDL"),
        ("zomato", "ZOMATO")
    ]
)
def test_normalize_ticker(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected


# =====================================
# YEAR TESTS (20)
# =====================================

@pytest.mark.parametrize(
    "input_year,expected",
    [
        ("Mar-24", "2024-03"),
        ("Mar-23", "2023-03"),
        ("Mar-22", "2022-03"),
        ("Mar-21", "2021-03"),
        ("Mar-20", "2020-03"),
        ("Mar-19", "2019-03"),
        ("Mar-18", "2018-03"),
        ("Mar-17", "2017-03"),
        ("Mar-16", "2016-03"),
        ("Mar-15", "2015-03"),
        ("Mar-14", "2014-03"),
        ("Mar-13", "2013-03"),
        ("Mar-12", "2012-03"),
        ("Mar-11", "2011-03"),
        ("Mar-10", "2010-03"),
        ("Mar-09", "2009-03"),
        ("Mar-08", "2008-03"),
        ("Mar-07", "2007-03"),
        ("Mar-06", "2006-03"),
        ("Mar-05", "2005-03")
    ]
)
def test_normalize_year(input_year, expected):
    assert normalize_year(input_year) == expected