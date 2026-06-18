from pathlib import Path
import pandas as pd

from normaliser import normalize_ticker
from normaliser import normalize_year


RAW_DATA_PATH = Path("data/raw")


def load_excel(file_name, header=1):
    """
    Load Excel file.
    """

    path = RAW_DATA_PATH / file_name

    df = pd.read_excel(path, header=header)

    return df


def load_profit_loss():

    df = load_excel(
        "profitandloss.xlsx",
        header=1
    )

    df["company_id"] = (
        df["company_id"]
        .apply(normalize_ticker)
    )

    df["year"] = (
        df["year"]
        .apply(normalize_year)
    )

    return df


def load_balance_sheet():

    df = load_excel(
        "balancesheet.xlsx",
        header=1
    )

    df["company_id"] = (
        df["company_id"]
        .apply(normalize_ticker)
    )

    df["year"] = (
        df["year"]
        .apply(normalize_year)
    )

    return df


if __name__ == "__main__":

    pl = load_profit_loss()

    print(pl.head())

    print(pl.shape)