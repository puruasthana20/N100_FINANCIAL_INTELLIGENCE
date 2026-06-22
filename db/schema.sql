PRAGMA foreign_keys = ON;

-- ==========================================
-- COMPANIES
-- ==========================================

CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT,
    website TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

-- ==========================================
-- PROFIT & LOSS
-- ==========================================

CREATE TABLE profitandloss (
    company_id TEXT,
    year TEXT,

    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- BALANCE SHEET
-- ==========================================

CREATE TABLE balancesheet (
    company_id TEXT,
    year TEXT,

    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,

    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- CASHFLOW
-- ==========================================

CREATE TABLE cashflow (
    company_id TEXT,
    year TEXT,

    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- ANALYSIS
-- ==========================================

CREATE TABLE analysis (
    company_id TEXT,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- DOCUMENTS
-- ==========================================

CREATE TABLE documents (
    company_id TEXT,
    year TEXT,
    annual_report TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- PROS & CONS
-- ==========================================

CREATE TABLE prosandcons (
    company_id TEXT,
    pros TEXT,
    cons TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- SECTORS
-- ==========================================

CREATE TABLE sectors (
    company_id TEXT,
    broad_sector TEXT,
    sub_sector TEXT,
    index_weight_pct REAL,
    market_cap_category TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- STOCK PRICES
-- ==========================================

CREATE TABLE stock_prices (
    company_id TEXT,
    date TEXT,

    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume REAL,
    adjusted_close REAL,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- FINANCIAL RATIOS
-- ==========================================

CREATE TABLE financial_ratios (
    company_id TEXT,
    year TEXT,

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    free_cash_flow_cr REAL,
    capex_cr REAL,
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- PEER GROUPS
-- ==========================================

CREATE TABLE peer_groups (
    peer_group_name TEXT,
    company_id TEXT,
    is_benchmark BOOLEAN,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

-- ==========================================
-- MARKET CAP
-- ==========================================

CREATE TABLE market_cap (
    company_id TEXT,
    year INTEGER,

    market_cap_crore REAL,
    enterprise_value_crore REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    ev_ebitda REAL,
    dividend_yield_pct REAL,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);