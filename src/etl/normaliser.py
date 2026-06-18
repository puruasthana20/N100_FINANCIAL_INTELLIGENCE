import re


def normalize_ticker(ticker):
    """
    Convert ticker to uppercase and remove spaces.
    """

    if ticker is None:
        return None

    return str(ticker).strip().upper()


def normalize_year(year_value):
    """
    Convert values like:
    Mar-24 -> 2024-03
    Mar-23 -> 2023-03
    """

    if year_value is None:
        return None

    value = str(year_value).strip()

    match = re.match(r"([A-Za-z]{3})-(\d{2})", value)

    if match:
        month, yy = match.groups()

        year = int(yy)

        if year <= 30:
            year += 2000
        else:
            year += 1900

        month_map = {
            "Jan":"01",
            "Feb":"02",
            "Mar":"03",
            "Apr":"04",
            "May":"05",
            "Jun":"06",
            "Jul":"07",
            "Aug":"08",
            "Sep":"09",
            "Oct":"10",
            "Nov":"11",
            "Dec":"12"
        }

        return f"{year}-{month_map[month]}"

    return value