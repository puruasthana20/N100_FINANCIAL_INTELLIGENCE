## Features

### Data Pipeline
- Automated ETL pipeline for Nifty 100 financial statements
- SQLite-based financial data warehouse
- Data validation and normalization

### Financial Ratio Engine
- 50+ financial KPIs across 100 companies
- Profitability, leverage, efficiency and cash-flow metrics
- CAGR engine with edge-case handling
- Composite quality scoring

### Financial Screener
- Configurable rule-based screener
- 6 predefined screening presets
- Analyst-editable YAML configuration
- Sector-aware filtering logic
- Automatic financial sector exceptions

### Peer Comparison Engine
- Peer group percentile rankings
- 10 ranked financial metrics
- Inverse Debt-to-Equity ranking
- SQLite peer_percentiles table

### Reporting
- Excel screener workbook
- Peer comparison workbook
- Radar chart visualizations
- Automated validation reports

src/
 ├── analytics/
 │     ratios.py
 │     cagr.py
 │     cashflow_kpis.py
 │     peer.py
 │     radar.py
 │     peer_report.py
 │
 ├── screener/
 │     engine.py
 │     scoring.py
 │     export.py
 │
tests/
config/
output/
reports/

## Generated Outputs

The project automatically generates:

- output/screener_output.xlsx
- output/peer_comparison.xlsx
- reports/radar_charts/*.png
- output/capital_allocation.csv
- output/ratio_edge_cases.log

## Validation

The project includes automated validation for:

- KPI formula correctness
- CAGR edge cases
- Screener filters
- Preset screeners
- Peer percentile rankings
- Excel report generation
- Radar chart generation
- Data quality checks

Current Status

- 90 automated tests passing

## Tech Stack

- Python
- Pandas
- SQLite
- NumPy
- OpenPyXL
- Matplotlib
- PyYAML
- PyTest

## Development Status

- Sprint 1 — ETL Pipeline ✅
- Sprint 2 — Financial Ratio Engine ✅
- Sprint 3 — Screener & Peer Comparison Engine ✅