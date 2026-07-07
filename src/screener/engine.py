from pathlib import Path
import sqlite3

import pandas as pd
import yaml


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

CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "screener_config.yaml"
)


# ============================================================
# LOAD CONFIG
# ============================================================

def load_config(
    config_path=CONFIG_PATH
):

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:

        config = yaml.safe_load(file)

    return config


# ============================================================
# LOAD SCREENER DATA
# ============================================================

def load_screener_data(
    db_path=DB_PATH
):

    conn = sqlite3.connect(db_path)


    # --------------------------------------------------------
    # Financial ratios
    # --------------------------------------------------------

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn
    )


    # --------------------------------------------------------
    # Sector information
    # --------------------------------------------------------

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        """,
        conn
    )


    # --------------------------------------------------------
    # Market valuation data
    # --------------------------------------------------------

    market_cap = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            dividend_yield_pct
        FROM market_cap
        """,
        conn
    )


    # --------------------------------------------------------
    # P&L fields required by screener
    # --------------------------------------------------------

    profit_loss = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit,
            dividend_payout
        FROM profitandloss
        """,
        conn
    )


    conn.close()


    # ========================================================
    # MERGE DATA
    # ========================================================

    df = ratios.merge(
        sectors,
        on="company_id",
        how="left"
    )


    df = df.merge(
        profit_loss,
        on=[
            "company_id",
            "year"
        ],
        how="left"
    )


    # --------------------------------------------------------
    # Dividend payout fallback
    # --------------------------------------------------------
    #
    # financial_ratios already contains
    # dividend_payout_ratio_pct.
    #
    # If it is missing for any reason, use the source
    # profitandloss dividend_payout field.

    if (
        "dividend_payout_ratio_pct"
        not in df.columns
        and
        "dividend_payout" in df.columns
    ):

        df[
            "dividend_payout_ratio_pct"
        ] = df[
            "dividend_payout"
        ]


    # --------------------------------------------------------
    # Market cap year may be INTEGER while ratio year may
    # contain values such as "Mar 2024".
    #
    # Use latest available market valuation per company.
    # --------------------------------------------------------

    if not market_cap.empty:

        market_cap = (
            market_cap
            .sort_values(
                by="year"
            )
            .groupby(
                "company_id",
                as_index=False
            )
            .last()
        )


        df = df.merge(
            market_cap.drop(
                columns=["year"],
                errors="ignore"
            ),
            on="company_id",
            how="left"
        )


    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    numeric_columns = [

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "debt_to_equity",

        "free_cash_flow_cr",

        "revenue_cagr_3yr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "operating_profit_margin_pct",

        "net_profit_margin_pct",

        "pe_ratio",

        "pb_ratio",

        "dividend_yield_pct",

        "dividend_payout_ratio_pct",

        "interest_coverage",

        "market_cap_crore",

        "net_profit",

        "eps_cagr_5yr",

        "asset_turnover",

        "sales",

        "composite_quality_score"
    ]


    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


    return df


# ============================================================
# LATEST ANNUAL PERIOD
# ============================================================

def get_latest_annual_records(df):

    annual = df[
        df["year"] != "TTM"
    ].copy()


    annual["fiscal_year"] = (
        annual["year"]
        .astype(str)
        .str.extract(
            r"(\d{4})"
        )[0]
    )


    annual["fiscal_year"] = pd.to_numeric(
        annual["fiscal_year"],
        errors="coerce"
    )


    month_map = {

        "Mar": 3,

        "Jun": 6,

        "Sep": 9,

        "Dec": 12
    }


    annual["fiscal_month"] = (
        annual["year"]
        .astype(str)
        .str[:3]
        .map(month_map)
        .fillna(0)
    )


    annual = annual.sort_values(
        by=[
            "company_id",
            "fiscal_year",
            "fiscal_month"
        ]
    )


    latest = (
        annual
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
        .reset_index(
            drop=True
        )
    )


    latest = latest.drop(
        columns=[
            "fiscal_year",
            "fiscal_month"
        ]
    )


    return latest


# ============================================================
# GENERIC FILTER
# ============================================================

def apply_single_filter(
    df,
    column,
    operator,
    threshold
):

    if column not in df.columns:

        raise ValueError(
            f"Column '{column}' "
            f"not found in screener data"
        )


    if operator == "min":

        return df[
            df[column]
            >=
            threshold
        ]


    if operator == "max":

        return df[
            df[column]
            <=
            threshold
        ]


    if operator == "equal":

        return df[
            df[column]
            ==
            threshold
        ]


    raise ValueError(
        f"Unsupported operator: {operator}"
    )


# ============================================================
# DEBT-TO-EQUITY FILTER
# Financials bypass
# ============================================================

def apply_de_filter(
    df,
    threshold
):

    financial_mask = (
        df["broad_sector"]
        .fillna("")
        .str.strip()
        .str.lower()
        ==
        "financials"
    )


    de_pass = (
        df["debt_to_equity"]
        <=
        threshold
    )


    return df[
        financial_mask
        |
        de_pass
    ]


# ============================================================
# INTEREST COVERAGE FILTER
# Debt-free companies always pass
# ============================================================

def apply_icr_filter(
    df,
    threshold
):

    icr_pass = (
        df["interest_coverage"]
        >=
        threshold
    )


    # Sprint 2 represents debt-free companies
    # using D/E = 0 and potentially NULL ICR.

    debt_free = (
        df["debt_to_equity"]
        ==
        0
    )


    return df[
        icr_pass
        |
        debt_free
    ]


# ============================================================
# MAIN FILTER ENGINE
# ============================================================

def apply_filters(
    df,
    filters,
    config=None
):

    if config is None:

        config = load_config()


    metric_config = config[
        "metrics"
    ]


    result = df.copy()


    for filter_name, threshold in filters.items():

        if threshold is None:

            continue


        if filter_name not in metric_config:

            raise ValueError(
                f"Unknown filter: {filter_name}"
            )


        rule = metric_config[
            filter_name
        ]


        column = rule[
            "column"
        ]


        operator = rule[
            "operator"
        ]


        # ----------------------------------------------------
        # D/E special rule
        # ----------------------------------------------------

        if rule.get(
            "financial_sector_bypass",
            False
        ):

            result = apply_de_filter(
                result,
                threshold
            )

            continue


        # ----------------------------------------------------
        # ICR special rule
        # ----------------------------------------------------

        if rule.get(
            "debt_free_pass",
            False
        ):

            result = apply_icr_filter(
                result,
                threshold
            )

            continue


        # ----------------------------------------------------
        # Standard filter
        # ----------------------------------------------------

        result = apply_single_filter(
            result,
            column,
            operator,
            threshold
        )


    # ========================================================
    # SORT RESULT
    # ========================================================

    if (
        "composite_quality_score"
        in result.columns
    ):

        result = result.sort_values(
            by="composite_quality_score",
            ascending=False,
            na_position="last"
        )


    return result.reset_index(
        drop=True
    )


# ============================================================
# RUN CUSTOM SCREENER
# ============================================================

def run_screener(
    filters,
    latest_only=True
):

    config = load_config()


    df = load_screener_data()


    if latest_only:

        df = get_latest_annual_records(
            df
        )


    result = apply_filters(
        df=df,
        filters=filters,
        config=config
    )


    return result


# ============================================================
# RUN STANDARD PRESET
# ============================================================

def run_preset(
    preset_name,
    latest_only=True
):

    config = load_config()


    presets = config.get(
        "presets",
        {}
    )


    if preset_name not in presets:

        raise ValueError(
            f"Preset '{preset_name}' "
            f"not found"
        )


    filters = presets[
        preset_name
    ]


    # Turnaround Watch requires historical D/E comparison.
    # It is handled by src/screener/presets.py rather than
    # this generic latest-row preset runner.

    if preset_name == "turnaround_watch":

        raise ValueError(
            "turnaround_watch requires historical "
            "trend analysis. Use "
            "src.screener.presets.run_preset()"
        )


    return run_screener(
        filters=filters,
        latest_only=latest_only
    )


# ============================================================
# DIRECT TEST RUN
# ============================================================

if __name__ == "__main__":

    filters = {

        "roe_min": 15,

        "debt_to_equity_max": 1.0
    }


    result = run_screener(
        filters
    )


    display_columns = [

        "company_id",

        "year",

        "broad_sector",

        "return_on_equity_pct",

        "debt_to_equity",

        "composite_quality_score"
    ]


    display_columns = [

        column

        for column in display_columns

        if column in result.columns
    ]


    print(
        "\n===== SCREENER RESULT ====="
    )


    print(
        result[
            display_columns
        ].to_string(
            index=False
        )
    )


    print(
        "\nCompanies Found:",
        len(result)
    )