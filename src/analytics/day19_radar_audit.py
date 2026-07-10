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
# REQUIRED RADAR METRICS
# ============================================================

RADAR_METRICS = [

    "roe",

    "roce",

    "net_profit_margin",

    "debt_to_equity",

    "free_cash_flow",

    "pat_cagr_5yr",

    "revenue_cagr_5yr"
]


# ============================================================
# CONNECT
# ============================================================

conn = sqlite3.connect(
    DB_PATH
)


print(
    "\n"
    + "=" * 100
)

print(
    "DAY 19 — RADAR CHART INPUT AUDIT"
)

print(
    "=" * 100
)


# ============================================================
# PEER PERCENTILE SUMMARY
# ============================================================

print(
    "\n===== PEER PERCENTILE TABLE SUMMARY ====="
)


summary = pd.read_sql(
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
    summary.to_string(
        index=False
    )
)


# ============================================================
# AVAILABLE METRICS
# ============================================================

print(
    "\n===== AVAILABLE PEER METRICS ====="
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


# ============================================================
# REQUIRED RADAR METRIC CHECK
# ============================================================

available_metrics = set(
    metrics["metric"]
)


print(
    "\n===== REQUIRED RADAR METRIC CHECK ====="
)


for metric in RADAR_METRICS:

    status = (

        "AVAILABLE"

        if metric in available_metrics

        else "MISSING"
    )

    print(
        f"{metric:<30} {status}"
    )


# ============================================================
# NULL PERCENTILE COVERAGE
# ============================================================

print(
    "\n===== NULL PERCENTILE COVERAGE ====="
)


null_coverage = pd.read_sql(
    """
    SELECT
        metric,
        COUNT(*) AS total_rows,
        SUM(
            CASE
                WHEN percentile_rank IS NULL
                THEN 1
                ELSE 0
            END
        ) AS null_percentiles
    FROM peer_percentiles
    GROUP BY metric
    ORDER BY metric
    """,
    conn
)


print(
    null_coverage.to_string(
        index=False
    )
)


# ============================================================
# PEER GROUP MEMBERSHIP
# ============================================================

print(
    "\n===== PEER GROUP MEMBERSHIP ====="
)


membership = pd.read_sql(
    """
    SELECT
        peer_group_name,
        COUNT(DISTINCT company_id) AS companies
    FROM peer_groups
    GROUP BY peer_group_name
    ORDER BY peer_group_name
    """,
    conn
)


print(
    membership.to_string(
        index=False
    )
)


# ============================================================
# BENCHMARK CHECK
# ============================================================

print(
    "\n===== BENCHMARK CHECK ====="
)


benchmarks = pd.read_sql(
    """
    SELECT
        peer_group_name,
        SUM(
            CASE
                WHEN is_benchmark = 1
                THEN 1
                ELSE 0
            END
        ) AS benchmark_count
    FROM peer_groups
    GROUP BY peer_group_name
    ORDER BY peer_group_name
    """,
    conn
)


print(
    benchmarks.to_string(
        index=False
    )
)


invalid_benchmarks = benchmarks[
    benchmarks["benchmark_count"] != 1
]


if invalid_benchmarks.empty:

    print(
        "\nAll peer groups have exactly one benchmark company."
    )

else:

    print(
        "\nWARNING: Benchmark configuration issue detected."
    )

    print(
        invalid_benchmarks.to_string(
            index=False
        )
    )


# ============================================================
# COMPOSITE SCORE AVAILABILITY
# ============================================================

print(
    "\n===== COMPOSITE SCORE AVAILABILITY ====="
)


composite = pd.read_sql(
    """
    SELECT
        COUNT(DISTINCT company_id) AS companies_with_score
    FROM financial_ratios
    WHERE composite_quality_score IS NOT NULL
    """,
    conn
)


print(
    composite.to_string(
        index=False
    )
)


# ============================================================
# PEER COMPANY SCORE COVERAGE
# ============================================================

print(
    "\n===== PEER COMPANY SCORE COVERAGE ====="
)


peer_score_coverage = pd.read_sql(
    """
    SELECT
        COUNT(DISTINCT pg.company_id)
            AS peer_companies,

        COUNT(
            DISTINCT CASE
                WHEN fr.composite_quality_score IS NOT NULL
                THEN pg.company_id
            END
        )
            AS peer_companies_with_score

    FROM peer_groups pg

    LEFT JOIN financial_ratios fr
        ON pg.company_id = fr.company_id
    """,
    conn
)


print(
    peer_score_coverage.to_string(
        index=False
    )
)


# ============================================================
# UNASSIGNED COMPANY COUNT
# ============================================================

print(
    "\n===== UNASSIGNED COMPANY COUNT ====="
)


unassigned = pd.read_sql(
    """
    SELECT COUNT(*) AS unassigned_companies

    FROM companies c

    LEFT JOIN peer_groups pg
        ON c.company_id = pg.company_id

    WHERE pg.company_id IS NULL
    """,
    conn
)


print(
    unassigned.to_string(
        index=False
    )
)


# ============================================================
# EXPECTED CHART COUNT
# ============================================================

peer_company_count = pd.read_sql(
    """
    SELECT COUNT(
        DISTINCT company_id
    ) AS peer_companies

    FROM peer_groups
    """,
    conn
).iloc[0]["peer_companies"]


print(
    "\n===== EXPECTED PEER RADAR CHART COUNT ====="
)


print(
    "Expected Peer Radar Charts:",
    peer_company_count
)


# ============================================================
# SAMPLE IT SERVICES DATA
# ============================================================

print(
    "\n===== IT SERVICES RADAR INPUT SAMPLE ====="
)


sample = pd.read_sql(
    """
    SELECT
        company_id,
        metric,
        value,
        percentile_rank

    FROM peer_percentiles

    WHERE peer_group_name = 'IT Services'

    ORDER BY
        company_id,
        metric
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


# ============================================================
# CLOSE
# ============================================================

conn.close()


print(
    "\n"
    + "=" * 100
)

print(
    "DAY 19 RADAR INPUT AUDIT COMPLETED"
)

print(
    "=" * 100
)