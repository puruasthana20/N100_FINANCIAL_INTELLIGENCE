from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "db"
    / "nifty100.db"
)


# ============================================================
# METRIC CONFIGURATION
# ============================================================

METRICS = {

    "roe": {
        "column": "return_on_equity_pct",
        "inverse": False
    },

    "roce": {
        "column": "return_on_capital_employed_pct",
        "inverse": False
    },

    "net_profit_margin": {
        "column": "net_profit_margin_pct",
        "inverse": False
    },

    "debt_to_equity": {
        "column": "debt_to_equity",
        "inverse": True
    },

    "free_cash_flow": {
        "column": "free_cash_flow_cr",
        "inverse": False
    },

    "pat_cagr_5yr": {
        "column": "pat_cagr_5yr",
        "inverse": False
    },

    "revenue_cagr_5yr": {
        "column": "revenue_cagr_5yr",
        "inverse": False
    },

    "eps_cagr_5yr": {
        "column": "eps_cagr_5yr",
        "inverse": False
    },

    "interest_coverage": {
        "column": "interest_coverage",
        "inverse": False
    },

    "asset_turnover": {
        "column": "asset_turnover",
        "inverse": False
    }
}


# ============================================================
# LOAD PEER GROUPS
# ============================================================

def load_peer_groups(
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    peer_groups = pd.read_sql(
        """
        SELECT
            peer_group_name,
            company_id,
            is_benchmark
        FROM peer_groups
        """,
        conn
    )

    conn.close()

    return peer_groups


# ============================================================
# LOAD FINANCIAL RATIOS
# ============================================================

def load_financial_ratios(
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE year != 'TTM'
        """,
        conn
    )

    conn.close()

    return ratios


# ============================================================
# GET LATEST ANNUAL RECORD
# ============================================================

def get_latest_annual_records(
    ratios
):

    df = ratios.copy()

    df["fiscal_year"] = (
        df["year"]
        .astype(str)
        .str.extract(
            r"(\d{4})"
        )[0]
    )

    df["fiscal_year"] = pd.to_numeric(
        df["fiscal_year"],
        errors="coerce"
    )

    month_map = {

        "Mar": 3,

        "Jun": 6,

        "Sep": 9,

        "Dec": 12
    }

    df["fiscal_month"] = (
        df["year"]
        .astype(str)
        .str[:3]
        .map(month_map)
        .fillna(0)
    )

    df = df.sort_values(
        by=[
            "company_id",
            "fiscal_year",
            "fiscal_month"
        ]
    )

    latest = (
        df
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
        .reset_index(drop=True)
    )

    latest = latest.drop(
        columns=[
            "fiscal_year",
            "fiscal_month"
        ]
    )

    return latest


# ============================================================
# BUILD PEER DATASET
# ============================================================

def build_peer_dataset():

    peer_groups = load_peer_groups()

    ratios = load_financial_ratios()

    latest_ratios = (
        get_latest_annual_records(
            ratios
        )
    )

    peer_df = peer_groups.merge(
        latest_ratios,
        on="company_id",
        how="left"
    )

    return peer_df


# ============================================================
# SQL-STYLE PERCENT_RANK
#
# Formula:
#
# (rank - 1) / (count - 1)
#
# Lowest value  = 0.0
# Highest value = 1.0
#
# ============================================================

def calculate_percent_rank(
    series
):

    result = pd.Series(
        np.nan,
        index=series.index,
        dtype=float
    )

    valid = series.dropna()

    count = len(valid)

    if count == 0:

        return result

    if count == 1:

        result.loc[
            valid.index
        ] = 0.0

        return result

    ranks = valid.rank(
        method="min",
        ascending=True
    )

    percent_rank = (
        ranks - 1
    ) / (
        count - 1
    )

    result.loc[
        valid.index
    ] = percent_rank

    return result


# ============================================================
# COMPUTE PEER PERCENTILES
# ============================================================

def compute_peer_percentiles(
    peer_df
):

    output_rows = []

    for peer_group_name, group_df in peer_df.groupby(
        "peer_group_name"
    ):

        group_df = group_df.copy()

        for metric_name, metric_rule in METRICS.items():

            column = metric_rule[
                "column"
            ]

            inverse = metric_rule[
                "inverse"
            ]

            if column not in group_df.columns:

                continue

            percentiles = (
                calculate_percent_rank(
                    group_df[column]
                )
            )

            if inverse:

                valid_mask = (
                    percentiles.notna()
                )

                percentiles.loc[
                    valid_mask
                ] = (
                    1
                    -
                    percentiles.loc[
                        valid_mask
                    ]
                )

            for index, row in group_df.iterrows():

                value = row[
                    column
                ]

                percentile_rank = (
                    percentiles.loc[
                        index
                    ]
                )

                if pd.isna(value):

                    percentile_value = None

                else:

                    percentile_value = round(
                        float(
                            percentile_rank
                        ),
                        6
                    )

                output_rows.append({

                    "company_id":
                        row["company_id"],

                    "peer_group_name":
                        peer_group_name,

                    "metric":
                        metric_name,

                    "value":
                        (
                            None
                            if pd.isna(value)
                            else float(value)
                        ),

                    "percentile_rank":
                        percentile_value,

                    "year":
                        row["year"]
                })

    result = pd.DataFrame(
        output_rows
    )

    return result


# ============================================================
# POPULATE SQLITE TABLE
# ============================================================

def populate_peer_percentiles(
    result,
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    result.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


# ============================================================
# COMPANY PEER LOOKUP
# ============================================================

def get_company_peer_group(
    company_id,
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    query = pd.read_sql(
        """
        SELECT DISTINCT
            peer_group_name
        FROM peer_groups
        WHERE company_id = ?
        """,
        conn,
        params=[
            company_id
        ]
    )

    conn.close()

    if query.empty:

        return (
            "No peer group assigned"
        )

    return query.iloc[
        0
    ][
        "peer_group_name"
    ]


# ============================================================
# VALIDATION
# ============================================================

def validate_results(
    result
):

    print(
        "\n"
        + "=" * 100
    )

    print(
        "DAY 18 — PEER PERCENTILE RANKINGS"
    )

    print(
        "=" * 100
    )


    print(
        "\n===== SUMMARY ====="
    )

    print(
        "Peer Groups:",
        result[
            "peer_group_name"
        ].nunique()
    )

    print(
        "Companies Ranked:",
        result[
            "company_id"
        ].nunique()
    )

    print(
        "Metrics:",
        result[
            "metric"
        ].nunique()
    )

    print(
        "Total Rows:",
        len(result)
    )


    print(
        "\n===== ROWS PER PEER GROUP ====="
    )

    summary = (
        result
        .groupby(
            "peer_group_name"
        )
        .agg(
            companies=(
                "company_id",
                "nunique"
            ),
            rows=(
                "company_id",
                "size"
            )
        )
        .reset_index()
    )

    print(
        summary.to_string(
            index=False
        )
    )


    print(
        "\n===== IT SERVICES — ROE RANKING ====="
    )

    it_roe = result[
        (
            result[
                "peer_group_name"
            ]
            ==
            "IT Services"
        )
        &
        (
            result[
                "metric"
            ]
            ==
            "roe"
        )
    ].sort_values(
        by="percentile_rank",
        ascending=False,
        na_position="last"
    )

    print(
        it_roe[
            [
                "company_id",
                "value",
                "percentile_rank"
            ]
        ].to_string(
            index=False
        )
    )


    print(
        "\n===== IT SERVICES — D/E INVERSE RANKING ====="
    )

    it_de = result[
        (
            result[
                "peer_group_name"
            ]
            ==
            "IT Services"
        )
        &
        (
            result[
                "metric"
            ]
            ==
            "debt_to_equity"
        )
    ].sort_values(
        by="percentile_rank",
        ascending=False,
        na_position="last"
    )

    print(
        it_de[
            [
                "company_id",
                "value",
                "percentile_rank"
            ]
        ].to_string(
            index=False
        )
    )


    print(
        "\n===== UNASSIGNED COMPANY TEST ====="
    )

    print(
        "ABB:",
        get_company_peer_group(
            "ABB"
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    peer_df = build_peer_dataset()

    result = compute_peer_percentiles(
        peer_df
    )

    populate_peer_percentiles(
        result
    )

    validate_results(
        result
    )

    print(
        "\nPeer percentile table populated successfully."
    )


if __name__ == "__main__":

    main()