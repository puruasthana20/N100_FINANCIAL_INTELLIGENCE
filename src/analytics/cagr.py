from math import pow


def calculate_cagr(start, end, years):
    """
    CAGR Formula

    ((End / Start)^(1/n) - 1) * 100
    """

    if years <= 0:
        return None, "INVALID_PERIOD"

    if start == 0:
        return None, "ZERO_BASE"

    if start > 0 and end > 0:

        cagr = (
            pow(end / start, 1 / years) - 1
        ) * 100

        return round(cagr, 2), None

    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None, "TURNAROUND"

    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "UNKNOWN"


def revenue_cagr(start_sales, end_sales, years):
    return calculate_cagr(
        start_sales,
        end_sales,
        years
    )


def pat_cagr(start_pat, end_pat, years):
    return calculate_cagr(
        start_pat,
        end_pat,
        years
    )


def eps_cagr(start_eps, end_eps, years):
    return calculate_cagr(
        start_eps,
        end_eps,
        years
    )


def insufficient_data(num_years, required_years):

    if num_years < required_years:
        return None, "INSUFFICIENT"

    return "OK", None