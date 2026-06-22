SELECT COUNT(*) FROM companies;

SELECT company_id, company_name
FROM companies
LIMIT 10;

SELECT COUNT(*) FROM profitandloss;

SELECT company_id, COUNT(*) AS years_available
FROM profitandloss
GROUP BY company_id
ORDER BY years_available DESC;

SELECT company_id, sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

SELECT company_id, net_profit
FROM profitandloss
ORDER BY net_profit DESC
LIMIT 10;

SELECT company_id, total_assets
FROM balancesheet
ORDER BY total_assets DESC
LIMIT 10;

SELECT company_id, net_cash_flow
FROM cashflow
ORDER BY net_cash_flow DESC
LIMIT 10;

SELECT broad_sector, COUNT(*)
FROM sectors
GROUP BY broad_sector;

SELECT COUNT(*) AS total_stock_records
FROM stock_prices;