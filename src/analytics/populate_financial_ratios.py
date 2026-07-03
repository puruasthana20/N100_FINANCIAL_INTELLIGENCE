import sqlite3
import pandas as pd
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity
)

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)

DB = "data/db/nifty100.db"

conn = sqlite3.connect(DB)

pl = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn
)

bs = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn
)

cf = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

df = (
    pl.merge(
        bs,
        on=["company_id", "year"],
        how="left"
    )
    .merge(
        cf,
        on=["company_id", "year"],
        how="left"
    )
)

print(df.head())

df["net_profit_margin_pct"] = df.apply(
    lambda x:
    net_profit_margin(
        x.net_profit,
        x.sales
    ),
    axis=1
)

df["operating_profit_margin_pct"] = df.apply(
    lambda x:
    operating_profit_margin(
        x.operating_profit,
        x.sales
    ),
    axis=1
)

df["return_on_equity_pct"] = df.apply(
    lambda x:
    return_on_equity(
        x.net_profit,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)

df["debt_to_equity"] = df.apply(
    lambda x:
    debt_to_equity(
        x.borrowings,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)

df["interest_coverage"] = df.apply(
    lambda x:
    interest_coverage_ratio(
        x.operating_profit,
        x.other_income,
        x.interest
    ),
    axis=1
)

df["asset_turnover"] = df.apply(
    lambda x:
    asset_turnover(
        x.sales,
        x.total_assets
    ),
    axis=1
)

df["free_cash_flow_cr"] = df.apply(
    lambda x:
    free_cash_flow(
        x.operating_activity,
        x.investing_activity
    ),
    axis=1
)

df["capex_cr"] = abs(
    df["investing_activity"]
)

df["earnings_per_share"] = df["eps"]

df["book_value_per_share"] = df.apply(
    lambda x: (
        (x.equity_capital + x.reserves) / x.equity_capital
        if x.equity_capital not in [0, None] and pd.notna(x.equity_capital)
        else None
    ),
    axis=1
)

df["dividend_payout_ratio_pct"] = df[
    "dividend_payout"
]

df["total_debt_cr"] = df[
    "borrowings"
]

df["cash_from_operations_cr"] = df[
    "operating_activity"
]

df = df.sort_values(
    [
        "company_id",
        "year"
    ]
)

df["revenue_cagr_5yr"] = None
df["pat_cagr_5yr"] = None
df["eps_cagr_5yr"] = None

for company in df["company_id"].unique():

    company_df = df[
        df.company_id == company
    ]

    idx = company_df.index.tolist()

    for i in range(5, len(idx)):

        current = idx[i]
        old = idx[i-5]

        value, _ = revenue_cagr(
            df.loc[old,"sales"],
            df.loc[current,"sales"],
            5
        )

        df.loc[
            current,
            "revenue_cagr_5yr"
        ] = value

        value, _ = pat_cagr(
            df.loc[old,"net_profit"],
            df.loc[current,"net_profit"],
            5
        )

        df.loc[
            current,
            "pat_cagr_5yr"
        ] = value

        value, _ = eps_cagr(
            df.loc[old,"eps"],
            df.loc[current,"eps"],
            5
        )

        df.loc[
            current,
            "eps_cagr_5yr"
        ] = value

df["composite_quality_score"] = (
    (
        df["return_on_equity_pct"].fillna(0)
        +
        df["net_profit_margin_pct"].fillna(0)
    ) / 2
).round(2)

final = df[
[
"company_id",
"year",
"net_profit_margin_pct",
"operating_profit_margin_pct",
"return_on_equity_pct",
"debt_to_equity",
"interest_coverage",
"asset_turnover",
"free_cash_flow_cr",
"capex_cr",
"earnings_per_share",
"book_value_per_share",
"dividend_payout_ratio_pct",
"total_debt_cr",
"cash_from_operations_cr",
"revenue_cagr_5yr",
"pat_cagr_5yr",
"eps_cagr_5yr",
"composite_quality_score"
]
]

final.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print(
    "Financial Ratios Populated:",
    len(final)
)

import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/db/nifty100.db"
)

print(
    pd.read_sql(
        "SELECT COUNT(*) FROM financial_ratios",
        conn
    )
)

print(
    pd.read_sql(
        "SELECT * FROM financial_ratios LIMIT 5",
        conn
    )
)

import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

pl = pd.read_sql("SELECT COUNT(*) c FROM profitandloss", conn)
bs = pd.read_sql("SELECT COUNT(*) c FROM balancesheet", conn)
cf = pd.read_sql("SELECT COUNT(*) c FROM cashflow", conn)

merge = pd.read_sql("""
SELECT COUNT(*)
FROM profitandloss p
INNER JOIN balancesheet b
ON p.company_id=b.company_id
AND p.year=b.year
INNER JOIN cashflow c
ON p.company_id=c.company_id
AND p.year=c.year
""", conn)

print(pl)
print(bs)
print(cf)
print(merge)

print(pd.read_sql(
    "SELECT COUNT(*) FROM financial_ratios",
    conn
))