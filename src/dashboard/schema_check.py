import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

print(pd.read_sql("""
SELECT company_id,
       COUNT(*) AS years
FROM market_cap
GROUP BY company_id
ORDER BY years DESC
LIMIT 10
""", conn))

conn.close()

import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

print(pd.read_sql("""
SELECT DISTINCT year
FROM market_cap
ORDER BY year DESC
LIMIT 10
""", conn))

conn.close()