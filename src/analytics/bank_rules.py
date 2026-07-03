FINANCIAL_COMPANIES = {

    "AXISBANK",
    "BANKBARODA",
    "CANBK",
    "CHOLAFIN",
    "HDFCBANK",
    "HDFCLIFE",
    "ICICIBANK",
    "ICICIGI",
    "ICICIPRULI",
    "INDUSINDBK",
    "KOTAKBANK",
    "LICI",
    "PFC",
    "PNB",
    "RECLTD",
    "SBILIFE",
    "SBIN",
    "SHRIRAMFIN",
    "UNIONBANK"

}


def high_leverage_flag(
    company_id,
    debt_to_equity
):
    """
    Suppress leverage warning
    for Financial companies.
    """

    if company_id in FINANCIAL_COMPANIES:
        return False

    return debt_to_equity > 5