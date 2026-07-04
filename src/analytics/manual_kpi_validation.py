import sqlite3
import pandas as pd


DB_PATH = "data/db/nifty100.db"

COMPANIES = [
    "ABB",
    "RELIANCE",
    "TCS"
]


conn = sqlite3.connect(DB_PATH)


for company in COMPANIES:

    query = """
    SELECT
        fr.company_id,
        fr.year,

        pl.sales,
        pl.net_profit,

        bs.equity_capital,
        bs.reserves,

        fr.return_on_equity_pct AS db_roe,
        fr.revenue_cagr_5yr AS db_revenue_cagr

    FROM financial_ratios fr

    LEFT JOIN profitandloss pl
        ON fr.company_id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN balancesheet bs
        ON fr.company_id = bs.company_id
        AND fr.year = bs.year

    WHERE fr.company_id = ?

    ORDER BY fr.rowid
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company]
    )


    # ========================================================
    # CONVERT NUMERIC COLUMNS
    # ========================================================

    numeric_columns = [
        "sales",
        "net_profit",
        "equity_capital",
        "reserves",
        "db_roe",
        "db_revenue_cagr"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    print("\n" + "=" * 70)
    print(company)


    # ========================================================
    # ROE VALIDATION
    # Use latest period where all required inputs exist
    # ========================================================

    roe_valid = df[
        df["net_profit"].notna()
        &
        df["equity_capital"].notna()
        &
        df["reserves"].notna()
        &
        df["db_roe"].notna()
    ]


    if roe_valid.empty:

        roe_year = None
        manual_roe = None
        db_roe = None
        roe_difference = None

    else:

        roe_row = roe_valid.iloc[-1]

        roe_year = roe_row["year"]

        equity = (
            roe_row["equity_capital"]
            +
            roe_row["reserves"]
        )


        if equity <= 0:

            manual_roe = None
            db_roe = float(
                roe_row["db_roe"]
            )

            roe_difference = None

        else:

            manual_roe = (
                roe_row["net_profit"]
                /
                equity
            ) * 100

            db_roe = float(
                roe_row["db_roe"]
            )

            roe_difference = abs(
                manual_roe
                -
                db_roe
            )


    # ========================================================
    # CAGR VALIDATION
    # Find latest record with valid 5-year CAGR
    # ========================================================

    valid_cagr_indices = df.index[
        df["db_revenue_cagr"].notna()
    ].tolist()


    if not valid_cagr_indices:

        cagr_start_year = None
        cagr_end_year = None

        start_sales = None
        end_sales = None

        manual_cagr = None
        db_cagr = None
        cagr_difference = None

    else:

        current_index = valid_cagr_indices[-1]


        if current_index < 5:

            cagr_start_year = None
            cagr_end_year = None

            start_sales = None
            end_sales = None

            manual_cagr = None
            db_cagr = None
            cagr_difference = None

        else:

            current = df.loc[
                current_index
            ]

            start = df.loc[
                current_index - 5
            ]


            cagr_start_year = start["year"]
            cagr_end_year = current["year"]


            start_sales = float(
                start["sales"]
            )

            end_sales = float(
                current["sales"]
            )


            if (
                pd.isna(start_sales)
                or
                pd.isna(end_sales)
                or
                start_sales <= 0
                or
                end_sales <= 0
            ):

                manual_cagr = None

            else:

                manual_cagr = (
                    (
                        end_sales
                        /
                        start_sales
                    ) ** (1 / 5)
                    - 1
                ) * 100


            db_cagr = float(
                current["db_revenue_cagr"]
            )


            if manual_cagr is not None:

                cagr_difference = abs(
                    manual_cagr
                    -
                    db_cagr
                )

            else:

                cagr_difference = None


    # ========================================================
    # PRINT ROE RESULTS
    # ========================================================

    print("\nROE Validation")

    print(
        "ROE Year:",
        roe_year
    )

    print(
        "Manual ROE:",
        round(manual_roe, 4)
        if manual_roe is not None
        else None
    )

    print(
        "Database ROE:",
        round(db_roe, 4)
        if db_roe is not None
        else None
    )

    print(
        "ROE Difference:",
        round(roe_difference, 4)
        if roe_difference is not None
        else None
    )


    # ========================================================
    # PRINT CAGR RESULTS
    # ========================================================

    print("\nRevenue CAGR Validation")

    print(
        "Start Year:",
        cagr_start_year
    )

    print(
        "End Year:",
        cagr_end_year
    )

    print(
        "Start Sales:",
        start_sales
    )

    print(
        "End Sales:",
        end_sales
    )

    print(
        "Manual Revenue CAGR:",
        round(manual_cagr, 4)
        if manual_cagr is not None
        else None
    )

    print(
        "Database Revenue CAGR:",
        round(db_cagr, 4)
        if db_cagr is not None
        else None
    )

    print(
        "CAGR Difference:",
        round(cagr_difference, 4)
        if cagr_difference is not None
        else None
    )


    # ========================================================
    # VALIDATION STATUS
    # ========================================================

    roe_pass = (
        roe_difference is not None
        and
        roe_difference < 0.1
    )


    cagr_pass = (
        cagr_difference is not None
        and
        cagr_difference < 0.1
    )


    print("\nValidation Status")

    print(
        "ROE:",
        "PASS"
        if roe_pass
        else "FAIL"
    )

    print(
        "Revenue CAGR:",
        "PASS"
        if cagr_pass
        else "FAIL"
    )


conn.close()


print(
    "\nManual KPI Validation Completed"
)