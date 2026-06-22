def normalize_ticker(ticker):
    """
    Normalize company ticker.
    """

    if ticker is None:
        return None

    return str(ticker).strip().upper()


def normalize_year(year):
    """
    Convert:
    Mar-24 -> 2024-03
    Mar-23 -> 2023-03
    """

    if year is None:
        return None

    year = str(year).strip()

    if year == "TTM":
        return "TTM"

    if "Mar-" in year:
        yy = year.split("-")[1]

        if int(yy) <= 30:
            return f"20{yy}-03"
        else:
            return f"19{yy}-03"

    return year