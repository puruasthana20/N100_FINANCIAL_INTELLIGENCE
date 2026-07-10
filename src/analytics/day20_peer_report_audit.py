from pathlib import Path
import sqlite3

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
# MAIN
# ============================================================

def main():

    conn = sqlite3.connect(
        DB_PATH
    )


    print(
        "\n"
        + "=" * 100
    )

    print(
        "DAY 20 — PEER COMPARISON REPORT INPUT AUDIT"
    )

    print(
        "=" * 100
    )


    # ========================================================
    # DATABASE TABLES
    # ========================================================

    print(
        "\n===== DATABASE TABLES ====="
    )

    tables = pd.read_sql(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """,
        conn
    )

    print(
        tables.to_string(
            index=False
        )
    )


    # ========================================================
    # COMPANIES COLUMNS
    # ========================================================

    print(
        "\n===== COMPANIES TABLE COLUMNS ====="
    )

    company_columns = pd.read_sql(
        """
        PRAGMA table_info(companies)
        """,
        conn
    )

    print(
        company_columns[
            [
                "name",
                "type"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # PEER GROUP SUMMARY
    # ========================================================

    print(
        "\n===== PEER GROUP SUMMARY ====="
    )

    peer_summary = pd.read_sql(
        """
        SELECT
            peer_group_name,
            COUNT(DISTINCT company_id) AS companies,
            SUM(
                CASE
                    WHEN is_benchmark = 1
                    THEN 1
                    ELSE 0
                END
            ) AS benchmarks
        FROM peer_groups
        GROUP BY peer_group_name
        ORDER BY peer_group_name
        """,
        conn
    )

    print(
        peer_summary.to_string(
            index=False
        )
    )


    # ========================================================
    # PEER PERCENTILE SUMMARY
    # ========================================================

    print(
        "\n===== PEER PERCENTILE SUMMARY ====="
    )

    percentile_summary = pd.read_sql(
        """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT company_id) AS companies,
            COUNT(DISTINCT peer_group_name) AS peer_groups,
            COUNT(DISTINCT metric) AS metrics
        FROM peer_percentiles
        """,
        conn
    )

    print(
        percentile_summary.to_string(
            index=False
        )
    )


    # ========================================================
    # AVAILABLE PERCENTILE METRICS
    # ========================================================

    print(
        "\n===== AVAILABLE PERCENTILE METRICS ====="
    )

    metrics = pd.read_sql(
        """
        SELECT DISTINCT metric
        FROM peer_percentiles
        ORDER BY metric
        """,
        conn
    )

    print(
        metrics.to_string(
            index=False
        )
    )


    # ========================================================
    # FINANCIAL RATIO COLUMNS
    # ========================================================

    print(
        "\n===== FINANCIAL RATIOS COLUMNS ====="
    )

    ratio_columns = pd.read_sql(
        """
        PRAGMA table_info(financial_ratios)
        """,
        conn
    )

    print(
        ratio_columns[
            [
                "name",
                "type"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # MARKET CAP COLUMNS
    # ========================================================

    print(
        "\n===== MARKET CAP COLUMNS ====="
    )

    market_columns = pd.read_sql(
        """
        PRAGMA table_info(market_cap)
        """,
        conn
    )

    print(
        market_columns[
            [
                "name",
                "type"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # LATEST FINANCIAL RATIO COVERAGE
    # ========================================================

    print(
        "\n===== PEER COMPANY RATIO COVERAGE ====="
    )

    coverage = pd.read_sql(
        """
        SELECT
            COUNT(DISTINCT pg.company_id) AS peer_companies,

            COUNT(
                DISTINCT fr.company_id
            ) AS companies_with_ratios

        FROM peer_groups pg

        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
        """,
        conn
    )

    print(
        coverage.to_string(
            index=False
        )
    )


    # ========================================================
    # BENCHMARK COMPANIES
    # ========================================================

    print(
        "\n===== BENCHMARK COMPANIES ====="
    )

    benchmarks = pd.read_sql(
        """
        SELECT
            peer_group_name,
            company_id
        FROM peer_groups
        WHERE is_benchmark = 1
        ORDER BY peer_group_name
        """,
        conn
    )

    print(
        benchmarks.to_string(
            index=False
        )
    )


    # ========================================================
    # SAMPLE IT SERVICES DATA
    # ========================================================

    print(
        "\n===== IT SERVICES PERCENTILE SAMPLE ====="
    )

    sample = pd.read_sql(
        """
        SELECT
            company_id,
            metric,
            value,
            percentile_rank,
            year
        FROM peer_percentiles
        WHERE peer_group_name = 'IT Services'
        ORDER BY company_id, metric
        """,
        conn
    )

    print(
        sample.head(
            30
        ).to_string(
            index=False
        )
    )


    conn.close()


    print(
        "\n"
        + "=" * 100
    )

    print(
        "DAY 20 PEER REPORT INPUT AUDIT COMPLETED"
    )

    print(
        "=" * 100
    )


if __name__ == "__main__":

    main()