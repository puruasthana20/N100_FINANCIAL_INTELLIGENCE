from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.screener.scoring import (
    build_scoring_dataset
)


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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "radar_charts"
)


# ============================================================
# RADAR CONFIGURATION
# ============================================================

RADAR_METRICS = {

    "roe":
        "ROE",

    "roce":
        "ROCE",

    "net_profit_margin":
        "NPM",

    "debt_to_equity":
        "D/E Score",

    "free_cash_flow":
        "FCF Score",

    "pat_cagr_5yr":
        "PAT CAGR",

    "revenue_cagr_5yr":
        "Revenue CAGR"
}


RADAR_LABELS = [

    "ROE",

    "ROCE",

    "NPM",

    "D/E Score",

    "FCF Score",

    "PAT CAGR",

    "Revenue CAGR",

    "Composite Score"
]


# ============================================================
# LOAD PEER PERCENTILES
# ============================================================

def load_peer_percentiles(
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    df = pd.read_sql(
        """
        SELECT
            company_id,
            peer_group_name,
            metric,
            value,
            percentile_rank,
            year
        FROM peer_percentiles
        """,
        conn
    )

    conn.close()

    return df


# ============================================================
# LOAD PEER GROUPS
# ============================================================

def load_peer_groups(
    db_path=DB_PATH
):

    conn = sqlite3.connect(
        db_path
    )

    df = pd.read_sql(
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

    return df


# ============================================================
# SQL STYLE PERCENT RANK
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

    result.loc[
        valid.index
    ] = (
        ranks - 1
    ) / (
        count - 1
    )

    return result


# ============================================================
# LOAD DAY 17 COMPOSITE SCORES
# ============================================================

def load_composite_scores():

    scoring_df = (
        build_scoring_dataset()
    )

    required_columns = [

        "company_id",

        "composite_quality_score_v2"
    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in scoring_df.columns
    ]

    if missing_columns:

        raise ValueError(

            "Missing scoring columns: "

            + ", ".join(
                missing_columns
            )
        )

    composite = scoring_df[
        required_columns
    ].copy()

    composite = (
        composite
        .drop_duplicates(
            subset=["company_id"],
            keep="last"
        )
    )

    return composite


# ============================================================
# BUILD WIDE PEER PERCENTILE DATA
# ============================================================

def build_wide_peer_data():

    percentiles = (
        load_peer_percentiles()
    )

    peer_groups = (
        load_peer_groups()
    )

    required_metrics = list(
        RADAR_METRICS.keys()
    )

    percentiles = percentiles[
        percentiles["metric"].isin(
            required_metrics
        )
    ].copy()

    wide = (
        percentiles
        .pivot_table(

            index=[

                "company_id",

                "peer_group_name",

                "year"
            ],

            columns="metric",

            values="percentile_rank",

            aggfunc="first"
        )
        .reset_index()
    )

    wide.columns.name = None

    wide = wide.merge(

        peer_groups[

            [
                "company_id",
                "peer_group_name",
                "is_benchmark"
            ]
        ],

        on=[

            "company_id",

            "peer_group_name"
        ],

        how="left"
    )

    composite = (
        load_composite_scores()
    )

    wide = wide.merge(

        composite,

        on="company_id",

        how="left"
    )

    return wide


# ============================================================
# ADD COMPOSITE SCORE PEER PERCENTILE
# ============================================================

def add_composite_percentile(
    df
):

    result = df.copy()

    result[
        "composite_score_percentile"
    ] = np.nan

    for peer_group_name, group_df in result.groupby(
        "peer_group_name"
    ):

        percentile = calculate_percent_rank(

            group_df[
                "composite_quality_score_v2"
            ]
        )

        result.loc[

            group_df.index,

            "composite_score_percentile"

        ] = percentile

    return result


# ============================================================
# PREPARE RADAR DATASET
# ============================================================

def build_radar_dataset():

    df = build_wide_peer_data()

    df = add_composite_percentile(
        df
    )

    return df


# ============================================================
# BUILD FULL UNIVERSE PERCENTILE DATA
# Used for companies without peer groups
# ============================================================

def build_universe_radar_dataset():

    scoring_df = build_scoring_dataset()

    peer_groups = load_peer_groups()


    # --------------------------------------------------------
    # Find unassigned companies
    # --------------------------------------------------------

    assigned_companies = set(
        peer_groups["company_id"]
        .dropna()
        .unique()
    )


    unassigned = scoring_df[
        ~scoring_df["company_id"].isin(
            assigned_companies
        )
    ].copy()


    # --------------------------------------------------------
    # Required source columns
    # --------------------------------------------------------

    source_columns = {

        "roe":
            "return_on_equity_pct",

        "roce":
            "return_on_capital_employed_pct",

        "net_profit_margin":
            "net_profit_margin_pct",

        "debt_to_equity":
            "debt_to_equity",

        "free_cash_flow":
            "free_cash_flow_cr",

        "pat_cagr_5yr":
            "pat_cagr_5yr",

        "revenue_cagr_5yr":
            "revenue_cagr_5yr",

        "composite_score_percentile":
            "composite_quality_score_v2"
    }


    # --------------------------------------------------------
    # Compute Nifty 100 percentile ranks
    # --------------------------------------------------------

    universe_percentiles = pd.DataFrame()

    universe_percentiles[
        "company_id"
    ] = scoring_df[
        "company_id"
    ]


    for output_column, source_column in source_columns.items():

        if source_column not in scoring_df.columns:

            universe_percentiles[
                output_column
            ] = np.nan

            continue


        # D/E inverse ranking:
        # lower debt = better percentile

        if source_column == "debt_to_equity":

            normal_rank = calculate_percent_rank(
                scoring_df[
                    source_column
                ]
            )

            universe_percentiles[
                output_column
            ] = 1 - normal_rank


        else:

            universe_percentiles[
                output_column
            ] = calculate_percent_rank(
                scoring_df[
                    source_column
                ]
            )


    # --------------------------------------------------------
    # Keep only unassigned companies
    # --------------------------------------------------------

    universe_percentiles = (
        universe_percentiles[
            universe_percentiles[
                "company_id"
            ].isin(
                unassigned[
                    "company_id"
                ]
            )
        ]
        .copy()
        .reset_index(drop=True)
    )


    universe_percentiles[
        "peer_group_name"
    ] = "No Peer Group"


    universe_percentiles[
        "year"
    ] = "Latest"


    universe_percentiles[
        "is_benchmark"
    ] = 0


    return universe_percentiles

# ============================================================
# RADAR VALUE EXTRACTION
# ============================================================

def get_company_values(
    row
):

    values = [

        row.get(
            "roe"
        ),

        row.get(
            "roce"
        ),

        row.get(
            "net_profit_margin"
        ),

        row.get(
            "debt_to_equity"
        ),

        row.get(
            "free_cash_flow"
        ),

        row.get(
            "pat_cagr_5yr"
        ),

        row.get(
            "revenue_cagr_5yr"
        ),

        row.get(
            "composite_score_percentile"
        )
    ]

    values = [

        0.0

        if pd.isna(value)

        else float(value)

        for value in values
    ]

    return values


# ============================================================
# PEER GROUP AVERAGE
# ============================================================

def get_peer_average(
    group_df
):

    columns = [

        "roe",

        "roce",

        "net_profit_margin",

        "debt_to_equity",

        "free_cash_flow",

        "pat_cagr_5yr",

        "revenue_cagr_5yr",

        "composite_score_percentile"
    ]

    averages = []

    for column in columns:

        value = group_df[
            column
        ].mean(
            skipna=True
        )

        if pd.isna(value):

            value = 0.0

        averages.append(
            float(value)
        )

    return averages


# ============================================================
# NIFTY 100 REFERENCE AVERAGE
# ============================================================

def get_nifty100_average():

    scoring_df = build_scoring_dataset()


    source_columns = {

        "roe":
            "return_on_equity_pct",

        "roce":
            "return_on_capital_employed_pct",

        "net_profit_margin":
            "net_profit_margin_pct",

        "debt_to_equity":
            "debt_to_equity",

        "free_cash_flow":
            "free_cash_flow_cr",

        "pat_cagr_5yr":
            "pat_cagr_5yr",

        "revenue_cagr_5yr":
            "revenue_cagr_5yr",

        "composite_score_percentile":
            "composite_quality_score_v2"
    }


    percentile_data = {}


    for output_column, source_column in source_columns.items():

        if source_column not in scoring_df.columns:

            percentile_data[
                output_column
            ] = pd.Series(
                np.nan,
                index=scoring_df.index
            )

            continue


        if source_column == "debt_to_equity":

            rank = calculate_percent_rank(
                scoring_df[
                    source_column
                ]
            )

            percentile_data[
                output_column
            ] = 1 - rank


        else:

            percentile_data[
                output_column
            ] = calculate_percent_rank(
                scoring_df[
                    source_column
                ]
            )


    reference_values = []


    for column in [

        "roe",

        "roce",

        "net_profit_margin",

        "debt_to_equity",

        "free_cash_flow",

        "pat_cagr_5yr",

        "revenue_cagr_5yr",

        "composite_score_percentile"

    ]:

        value = percentile_data[
            column
        ].mean(
            skipna=True
        )


        if pd.isna(value):

            value = 0.0


        reference_values.append(
            float(value)
        )


    return reference_values

# ============================================================
# CLOSE POLYGON
# ============================================================

def close_polygon(
    values
):

    return values + [
        values[0]
    ]


# ============================================================
# GENERATE SINGLE RADAR CHART
# ============================================================

def generate_radar_chart(
    company_row,
    peer_group_df
):

    company_id = company_row[
        "company_id"
    ]

    peer_group_name = company_row[
        "peer_group_name"
    ]

    company_values = (
        get_company_values(
            company_row
        )
    )

    peer_average = (
        get_peer_average(
            peer_group_df
        )
    )

    number_of_axes = len(
        RADAR_LABELS
    )

    angles = np.linspace(

        0,

        2 * np.pi,

        number_of_axes,

        endpoint=False
    ).tolist()

    angles = close_polygon(
        angles
    )

    company_values_closed = (
        close_polygon(
            company_values
        )
    )

    peer_average_closed = (
        close_polygon(
            peer_average
        )
    )


    # ========================================================
    # CREATE POLAR FIGURE
    # ========================================================

    figure = plt.figure(
        figsize=(10, 8)
    )

    axis = figure.add_subplot(
        111,
        polar=True
    )


    # ========================================================
    # COMPANY POLYGON
    # ========================================================

    axis.plot(

        angles,

        company_values_closed,

        linewidth=2,

        label=company_id
    )

    axis.fill(

        angles,

        company_values_closed,

        alpha=0.25
    )


    # ========================================================
    # PEER AVERAGE
    # ========================================================

    axis.plot(

        angles,

        peer_average_closed,

        linewidth=2,

        linestyle="--",

        label="Peer Group Average"
    )


    # ========================================================
    # AXIS LABELS
    # ========================================================

    axis.set_xticks(
        angles[:-1]
    )

    axis.set_xticklabels(

        RADAR_LABELS,

        fontsize=10
    )


    # ========================================================
    # RADIAL SCALE
    # ========================================================

    axis.set_ylim(
        0,
        1
    )

    axis.set_yticks(

        [
            0.25,
            0.50,
            0.75,
            1.00
        ]
    )

    axis.set_yticklabels(

        [
            "25",
            "50",
            "75",
            "100"
        ],

        fontsize=8
    )


    # ========================================================
    # TITLE
    # ========================================================

    benchmark_text = ""

    if company_row.get(
        "is_benchmark",
        0
    ) == 1:

        benchmark_text = (
            " | Benchmark"
        )


    axis.set_title(

        (
            f"{company_id} Radar Profile\n"
            f"{peer_group_name}"
            f"{benchmark_text}"
        ),

        fontsize=14,

        pad=25
    )


    # ========================================================
    # LEGEND
    # ========================================================

    axis.legend(

        loc="upper right",

        bbox_to_anchor=(
            1.30,
            1.15
        )
    )


    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (

        OUTPUT_DIR

        / f"{company_id}_radar.png"
    )

    figure.tight_layout()

    figure.savefig(

        output_path,

        dpi=180,

        bbox_inches="tight"
    )

    plt.close(
        figure
    )

    return output_path

# ============================================================
# GENERATE STANDALONE RADAR CHART
# For companies without peer groups
# ============================================================

def generate_standalone_radar_chart(
    company_row,
    nifty100_average
):

    company_id = company_row[
        "company_id"
    ]


    company_values = (
        get_company_values(
            company_row
        )
    )


    number_of_axes = len(
        RADAR_LABELS
    )


    angles = np.linspace(

        0,

        2 * np.pi,

        number_of_axes,

        endpoint=False

    ).tolist()


    angles = close_polygon(
        angles
    )


    company_values_closed = (
        close_polygon(
            company_values
        )
    )


    nifty_average_closed = (
        close_polygon(
            nifty100_average
        )
    )


    # ========================================================
    # CREATE FIGURE
    # ========================================================

    figure = plt.figure(
        figsize=(10, 8)
    )


    axis = figure.add_subplot(
        111,
        polar=True
    )


    # ========================================================
    # COMPANY PROFILE
    # ========================================================

    axis.plot(

        angles,

        company_values_closed,

        linewidth=2,

        label=company_id
    )


    axis.fill(

        angles,

        company_values_closed,

        alpha=0.25
    )


    # ========================================================
    # NIFTY 100 AVERAGE
    # ========================================================

    axis.plot(

        angles,

        nifty_average_closed,

        linewidth=2,

        linestyle="--",

        label="Nifty 100 Average"
    )


    # ========================================================
    # AXIS LABELS
    # ========================================================

    axis.set_xticks(
        angles[:-1]
    )


    axis.set_xticklabels(

        RADAR_LABELS,

        fontsize=10
    )


    axis.set_ylim(
        0,
        1
    )


    axis.set_yticks(

        [
            0.25,
            0.50,
            0.75,
            1.00
        ]
    )


    axis.set_yticklabels(

        [
            "25",
            "50",
            "75",
            "100"
        ],

        fontsize=8
    )


    # ========================================================
    # TITLE
    # ========================================================

    axis.set_title(

        (
            f"{company_id} Radar Profile\n"
            f"Nifty 100 Comparison"
        ),

        fontsize=14,

        pad=25
    )


    axis.legend(

        loc="upper right",

        bbox_to_anchor=(
            1.30,
            1.15
        )
    )


    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    output_path = (

        OUTPUT_DIR

        / f"{company_id}_radar.png"
    )


    figure.tight_layout()


    figure.savefig(

        output_path,

        dpi=180,

        bbox_inches="tight"
    )


    plt.close(
        figure
    )


    return output_path

# ============================================================
# GENERATE ALL PEER RADARS
# ============================================================

def generate_all_peer_radars():

    radar_df = (
        build_radar_dataset()
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # Remove old radar PNG files so validation count is honest.
    # Revolutionary concept: counting current output rather than
    # archaeological remains from previous runs.

    for old_file in OUTPUT_DIR.glob(
        "*_radar.png"
    ):

        old_file.unlink()


    generated_files = []


    for peer_group_name, group_df in radar_df.groupby(
        "peer_group_name"
    ):

        print(
            f"\nGenerating: "
            f"{peer_group_name}"
        )

        for _, company_row in group_df.iterrows():

            output_path = (
                generate_radar_chart(

                    company_row,

                    group_df
                )
            )

            generated_files.append(
                output_path
            )

            print(
                f"  Generated: "
                f"{output_path.name}"
            )


    return generated_files

# ============================================================
# GENERATE UNASSIGNED COMPANY RADARS
# ============================================================

def generate_unassigned_radars():

    unassigned_df = (
        build_universe_radar_dataset()
    )


    nifty100_average = (
        get_nifty100_average()
    )


    generated_files = []


    print(
        "\nGenerating standalone Nifty 100 comparison charts..."
    )


    for _, company_row in unassigned_df.iterrows():


        output_path = (
            generate_standalone_radar_chart(

                company_row,

                nifty100_average
            )
        )


        generated_files.append(
            output_path
        )


        print(
            f"  Generated: "
            f"{output_path.name}"
        )


    return generated_files

# ============================================================
# VALIDATE OUTPUT
# ============================================================

def validate_radar_output(
    generated_files,
    radar_df
):

    print(
        "\n"
        + "=" * 100
    )

    print(
        "DAY 19 — RADAR CHART VALIDATION"
    )

    print(
        "=" * 100
    )


    expected_count = (
        radar_df[
            "company_id"
        ]
        .nunique()
    )

    actual_count = len(
        generated_files
    )


    print(
        "\nExpected Charts:",
        expected_count
    )

    print(
        "Generated Charts:",
        actual_count
    )


    existing_files = list(

        OUTPUT_DIR.glob(
            "*_radar.png"
        )
    )


    print(
        "PNG Files on Disk:",
        len(existing_files)
    )


    print(
        "\nPeer Groups:",
        radar_df[
            "peer_group_name"
        ].nunique()
    )


    print(
        "Companies:",
        radar_df[
            "company_id"
        ].nunique()
    )


    missing_composite = (

        radar_df[
            "composite_score_percentile"
        ]
        .isna()
        .sum()
    )


    print(
        "Missing Composite Percentiles:",
        missing_composite
    )


    if (
        actual_count == expected_count
        and
        len(existing_files) == expected_count
    ):

        print(
            "\nRadar Chart Generation: PASS"
        )

    else:

        print(
            "\nRadar Chart Generation: FAIL"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 100
    )

    print(
        "DAY 19 — COMPLETE RADAR CHART GENERATOR"
    )

    print(
        "=" * 100
    )


    # ========================================================
    # CLEAN OLD OUTPUT
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    for old_file in OUTPUT_DIR.glob(
        "*_radar.png"
    ):

        old_file.unlink()


    # ========================================================
    # PEER RADARS
    # ========================================================

    radar_df = (
        build_radar_dataset()
    )


    print(
        "\nPeer Companies:",
        radar_df[
            "company_id"
        ].nunique()
    )


    print(
        "Peer Groups:",
        radar_df[
            "peer_group_name"
        ].nunique()
    )


    peer_files = (
        generate_all_peer_radars()
    )


    # ========================================================
    # UNASSIGNED RADARS
    # ========================================================

    unassigned_df = (
        build_universe_radar_dataset()
    )


    print(
        "\nUnassigned Companies:",
        unassigned_df[
            "company_id"
        ].nunique()
    )


    standalone_files = (
        generate_unassigned_radars()
    )


    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    all_png_files = list(

        OUTPUT_DIR.glob(
            "*_radar.png"
        )
    )


    peer_count = len(
        peer_files
    )


    standalone_count = len(
        standalone_files
    )


    total_generated = (

        peer_count

        +

        standalone_count
    )


    expected_total = (

        radar_df[
            "company_id"
        ].nunique()

        +

        unassigned_df[
            "company_id"
        ].nunique()
    )


    print(
        "\n"
        + "=" * 100
    )

    print(
        "DAY 19 — FINAL VALIDATION"
    )

    print(
        "=" * 100
    )


    print(
        "\nPeer Radar Charts:",
        peer_count
    )


    print(
        "Standalone Charts:",
        standalone_count
    )


    print(
        "Total Generated:",
        total_generated
    )


    print(
        "Expected Total:",
        expected_total
    )


    print(
        "PNG Files on Disk:",
        len(all_png_files)
    )


    if (

        total_generated
        ==
        expected_total

        and

        len(all_png_files)
        ==
        expected_total

    ):

        print(
            "\nRadar Chart Generation: PASS"
        )

    else:

        print(
            "\nRadar Chart Generation: FAIL"
        )


    print(
        "\nRadar charts saved to:"
    )


    print(
        OUTPUT_DIR
    )


if __name__ == "__main__":

    main()