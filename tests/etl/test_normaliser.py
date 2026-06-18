import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[2]
    )
)


from src.etl.normaliser import normalize_ticker
from src.etl.normaliser import normalize_year


def test_ticker_uppercase():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_strip():
    assert normalize_ticker("  infy ") == "INFY"


def test_year_2024():
    assert normalize_year("Mar-24") == "2024-03"


def test_year_2023():
    assert normalize_year("Mar-23") == "2023-03"