PRAGMA foreign_keys = ON;

CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT,
    website TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

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

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

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

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE cashflow (
    company_id TEXT,
    year TEXT,

    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE analysis (
    company_id TEXT PRIMARY KEY,

    pros TEXT,
    cons TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE documents (
    company_id TEXT PRIMARY KEY,

    annual_report_url TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE prosandcons (
    company_id TEXT PRIMARY KEY,

    pros TEXT,
    cons TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE sectors (
    company_id TEXT PRIMARY KEY,

    sector TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE stock_prices (
    company_id TEXT,
    trade_date TEXT,
    close_price REAL,

    PRIMARY KEY (
        company_id,
        trade_date
    ),

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE peer_groups (
    company_id TEXT PRIMARY KEY,

    peer_group TEXT,

    FOREIGN KEY (company_id)
    REFERENCES companies(company_id)
);