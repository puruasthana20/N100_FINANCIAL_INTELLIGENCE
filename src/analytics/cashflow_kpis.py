from typing import Optional


def free_cash_flow(
    operating_activity: float,
    investing_activity: float
) -> float:
    """
    Free Cash Flow
    """

    return round(
        operating_activity + investing_activity,
        2
    )


def cfo_quality_score(
    average_cfo: float,
    average_pat: float
):
    """
    CFO / PAT Quality Score
    """

    if average_pat == 0:
        return None

    ratio = average_cfo / average_pat

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(
    investing_activity: float,
    sales: float
):
    """
    CapEx Intensity
    """

    if sales == 0:
        return None

    value = (
        abs(investing_activity)
        / sales
    ) * 100

    value = round(value, 2)

    if value < 3:
        label = "Asset Light"

    elif value <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return value, label


def fcf_conversion_rate(
    free_cashflow: float,
    operating_profit: float
):
    """
    FCF Conversion
    """

    if operating_profit == 0:
        return None

    return round(
        (free_cashflow / operating_profit)
        * 100,
        2
    )


def capital_allocation_pattern(
    cfo: float,
    cfi: float,
    cff: float,
    cfo_pat_ratio: Optional[float] = None
):
    """
    Capital Allocation Pattern
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    mapping = {

        ("+", "-", "-"):
        "Reinvestor",

        ("+", "+", "-"):
        "Liquidating Assets",

        ("-", "+", "+"):
        "Distress Signal",

        ("-", "-", "+"):
        "Growth Funded by Debt",

        ("+", "+", "+"):
        "Cash Accumulator",

        ("-", "-", "-"):
        "Pre-Revenue",

        ("+", "-", "+"):
        "Mixed"
    }

    pattern = mapping.get(
        signs,
        "Unknown"
    )

    if (
        pattern == "Reinvestor"
        and
        cfo_pat_ratio is not None
        and
        cfo_pat_ratio > 1
    ):
        pattern = "Shareholder Returns"

    return (
        signs[0],
        signs[1],
        signs[2],
        pattern
    )