# Sprint 2 Retrospective
## Financial Ratio Engine

### Sprint Objective

The objective of Sprint 2 was to build a reusable financial ratio engine capable of computing profitability, leverage, efficiency, growth, and cash-flow KPIs across all available company-year records.

The sprint also focused on handling financial edge cases, sector-specific rules, CAGR sign transitions, and source-to-engine ratio discrepancies.

---

## Completed Work

### Profitability Engine

Implemented:

- Net Profit Margin
- Operating Profit Margin
- Return on Equity
- Return on Capital Employed
- Return on Assets
- OPM source cross-check logic
- Zero-denominator handling
- Negative-equity handling

### Leverage and Efficiency Engine

Implemented:

- Debt-to-Equity Ratio
- High Leverage Flag
- Interest Coverage Ratio
- Debt Free label
- ICR warning flag
- Net Debt
- Asset Turnover

Financial-sector companies are excluded from standard leverage warnings because high leverage is structurally normal for banks, NBFCs, and insurance companies.

### CAGR Engine

Implemented Revenue, PAT, and EPS CAGR calculations.

Supported windows:

- 3 years
- 5 years
- 10 years

Handled edge cases:

- NORMAL
- DECLINE_TO_LOSS
- TURNAROUND
- BOTH_NEGATIVE
- ZERO_BASE
- INSUFFICIENT

Each invalid CAGR condition returns a null CAGR value together with an explanatory flag.

### Cash Flow KPI Engine

Implemented:

- Free Cash Flow
- CFO Quality Score
- CapEx Intensity
- FCF Conversion Rate
- Eight-pattern Capital Allocation Classifier

Capital allocation classifications include:

- Reinvestor
- Shareholder Returns
- Liquidating Assets
- Distress Signal
- Growth Funded by Debt
- Cash Accumulator
- Pre-Revenue
- Mixed

### Financial Ratio Database Population

The financial_ratios table was populated successfully.

Final row count:

1,263 company-year records

The table contains more than the required 14 KPI columns and no KPI column is entirely null.

### Ratio Edge-Case Validation

Implemented source comparison for:

- ROE
- ROCE

Generated:

output/ratio_edge_cases.log

A total of 116 ratio anomalies were initially detected and logged.

Anomalies are reviewed under:

- Data Source Issue
- Version Difference
- Formula Discrepancy

Extreme ROE cases identified during screener validation were investigated separately and documented in the edge-case log.

---

## Manual KPI Validation

Three companies were manually validated:

- ABB
- RELIANCE
- TCS

### ROE Validation Results

ABB difference: 0.0018%

RELIANCE difference: 0.0013%

TCS difference: 0.0043%

All results are within the required 0.1% tolerance.

### Revenue CAGR Validation Results

ABB difference: 0.0037%

RELIANCE difference: 0.0022%

TCS difference: 0.0002%

All results are within the required 0.1% tolerance.

---

## Screener Preview

The screener condition used was:

ROE > 15%

Debt-to-Equity < 1

The screener uses the latest available annual reporting period per company and excludes TTM records where required Balance Sheet inputs are incomplete.

Final qualifying company count:

38 companies

The result satisfies the expected range of 15 to 50 companies.

---

## Testing Results

All automated project tests passed successfully.

The test suite covers:

- Profitability ratios
- Zero denominators
- Negative equity
- OPM mismatch detection
- Debt-free companies
- Interest coverage edge cases
- High leverage flags
- CAGR calculations
- CAGR sign-transition cases
- Cash-flow KPIs
- Capital allocation patterns

Final status:

0 test failures

---

## Key Technical Decisions

1. Ratio calculations return null where the denominator makes the result financially meaningless.

2. Debt-free companies return zero Debt-to-Equity rather than null.

3. Interest Coverage returns null when interest expense is zero and uses a Debt Free display label.

4. Financial-sector companies are exempt from standard high-leverage warnings.

5. Engine-computed ROE and ROCE values are used for analytics.

6. Source ROE and ROCE values are retained for reference and display.

7. CAGR sign transitions are represented with explicit status flags rather than misleading numerical growth rates.

8. TTM periods are excluded from calculations requiring unavailable matching Balance Sheet inputs.

9. Financial periods are parsed chronologically rather than sorted as raw text.

---

## What Went Well

- Modular analytics architecture made formula testing straightforward.
- Unit testing caught denominator and sign edge cases early.
- Manual calculations closely matched database values.
- The ratio table exceeded the required row-count target.
- Screener validation exposed period-selection issues before downstream dashboard development.
- Edge-case logging improved transparency around source and formula discrepancies.

---

## Challenges

- Financial periods were stored as text and required explicit chronological parsing.
- TTM data did not always have matching Balance Sheet inputs.
- Financial-sector leverage required separate interpretation.
- Source ROE and ROCE values did not always align with engine calculations.
- Extreme ROE values required investigation of denominator quality and source-data consistency.

---

## Lessons Learned

1. Financial formulas must be validated against both automated tests and real company data.

2. Financial period alignment is as important as the formula itself.

3. Sector context is necessary when interpreting leverage and capital efficiency.

4. Source financial datasets should not be assumed internally consistent.

5. Edge cases should be logged and explained instead of silently corrected.

6. Analytics pipelines should preserve raw source values while maintaining separate computed analytical values.

---

## Sprint Outcome

Sprint 2 successfully delivered a tested Financial Ratio Engine with:

- 1,263 financial ratio records
- 14+ KPI columns
- CAGR edge-case handling
- Cash-flow analytics
- Capital allocation classification
- Financial-sector carve-outs
- Ratio anomaly logging
- Manual KPI validation
- Screener preview validation
- Automated formula testing

Sprint 2 technical implementation is complete and ready for review and downstream analytics development.