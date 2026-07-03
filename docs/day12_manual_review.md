# Day 12 Manual KPI Validation

## Companies Reviewed

- ABB
- HDFCBANK
- RELIANCE

## KPIs Verified

- Return on Equity (ROE)
- Revenue CAGR (5-Year)

## Validation Method

ROE was recomputed manually using:

ROE = Net Profit / (Equity + Reserves) × 100

Revenue CAGR was recomputed using:

((End Revenue / Start Revenue)^(1/5)-1)×100

## Result

All manually calculated KPI values matched the database values within the acceptable tolerance (<0.1%).

## Conclusion

Financial Ratio Engine calculations validated successfully.


ABB
   company_id      year  return_on_equity_pct revenue_cagr_5yr
0         ABB  Dec 2012                 22.41             None
1         ABB  Mar 2014                 25.13             None
2         ABB  Mar 2015                 24.44             None
3         ABB  Mar 2016                 21.34             None
4         ABB  Mar 2017                 19.97             None
5         ABB  Mar 2018                 23.69            14.81
6         ABB  Mar 2019                 22.41            10.08
7         ABB  Mar 2020                 24.39            12.33
8         ABB  Mar 2021                 26.56            10.52
9         ABB  Mar 2022                 28.33             11.1
10        ABB  Mar 2023                 29.77            10.16
11        ABB  Mar 2024                 32.47             9.72
12        ABB       TTM                   NaN             8.19


RELIANCE
   company_id      year  return_on_equity_pct revenue_cagr_5yr
0    RELIANCE  Mar 2013                 11.47             None
1    RELIANCE  Mar 2014                 11.35             None
2    RELIANCE  Mar 2015                 10.82             None
3    RELIANCE  Mar 2016                 12.90             None
4    RELIANCE  Mar 2017                 11.31             None
5    RELIANCE  Mar 2018                 12.29            -0.26
6    RELIANCE  Mar 2019                 10.29             5.56
7    RELIANCE  Mar 2020                  8.88             9.77
8    RELIANCE  Mar 2021                  7.68            11.34
9    RELIANCE  Mar 2022                  8.70            17.98
10   RELIANCE  Mar 2023                 10.35            17.53
11   RELIANCE  Mar 2024                  9.96             9.61
12   RELIANCE       TTM                   NaN             9.51


HDFCBANK
   company_id      year  return_on_equity_pct revenue_cagr_5yr
0    HDFCBANK  Mar 2013                 18.84             None
1    HDFCBANK  Mar 2014                 19.85             None
2    HDFCBANK  Mar 2015                 16.95             None
3    HDFCBANK  Mar 2016                 17.25             None
4    HDFCBANK  Mar 2017                 16.69             None
5    HDFCBANK  Mar 2018                 16.94            18.92
6    HDFCBANK  Mar 2019                 14.61            19.83
7    HDFCBANK  Mar 2020                 15.48            19.25
8    HDFCBANK  Mar 2021                 15.18            15.27
9    HDFCBANK  Mar 2022                 15.43            13.16
10   HDFCBANK  Mar 2023                 15.94            14.89
11   HDFCBANK  Mar 2024                 14.34            21.95
12   HDFCBANK       TTM                   NaN            21.91
(venv) PS C:\Users\purua\projects\n100_financial_intelligence> 