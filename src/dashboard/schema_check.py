import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

print("\n===== PEER_PERCENTILES =====")
print(pd.read_sql(
    "PRAGMA table_info(peer_percentiles)",
    conn
)[["name","type"]])

print("\n===== SAMPLE =====")
print(pd.read_sql(
    "SELECT * FROM peer_percentiles LIMIT 20",
    conn
))

conn.close()