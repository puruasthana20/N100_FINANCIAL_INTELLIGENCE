import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

print(pd.read_sql("PRAGMA table_info(analysis)", conn))
print(pd.read_sql("SELECT * FROM analysis LIMIT 10", conn))

conn.close()