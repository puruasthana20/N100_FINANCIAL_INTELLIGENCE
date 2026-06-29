"""
Financial Ratio Engine
Sprint 2 - Day 08
"""

from typing import Optional


def net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:
    """
    Net Profit Margin (%)

    Formula:
    Net Profit / Sales * 100
    """

    if sales is None or sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:
    """
    Operating Profit Margin (%)
    """

    if sales is None or sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)


def opm_crosscheck(
    calculated_opm: float,
    source_opm: float
) -> bool:
    """
    Returns True if difference <= 1%
    """

    if calculated_opm is None or source_opm is None:
        return False

    return abs(calculated_opm - source_opm) <= 1


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(
        (net_profit / equity) * 100,
        2
    )


def return_on_capital_employed(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:

    capital = (
        equity_capital +
        reserves +
        borrowings
    )

    if capital <= 0:
        return None

    return round(
        (ebit / capital) * 100,
        2
    )


def return_on_assets(
    net_profit: float,
    total_assets: float
) -> Optional[float]:

    if total_assets == 0:
        return None

    return round(
        (net_profit / total_assets) * 100,
        2
    )

def roce_rating(
    roce: float,
    broad_sector: str
):
    """
    Evaluate ROCE based on sector.
    """

    if roce is None:
        return None

    financial_sectors = [
        "Financials"
    ]

    if broad_sector in financial_sectors:

        if roce >= 8:
            return "GOOD"
        else:
            return "LOW"

    else:

        if roce >= 15:
            return "GOOD"
        else:
            return "LOW"