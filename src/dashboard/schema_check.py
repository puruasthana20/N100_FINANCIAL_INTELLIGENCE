import sqlite3
import pandas as pd

conn = sqlite3.connect("data/db/nifty100.db")

print("\n===== PROFIT & LOSS =====")
print(pd.read_sql("PRAGMA table_info(profitandloss)", conn)[["name","type"]])

print("\n===== BALANCE SHEET =====")
print(pd.read_sql("PRAGMA table_info(balancesheet)", conn)[["name","type"]])

print("\n===== CASHFLOW =====")
print(pd.read_sql("PRAGMA table_info(cashflow)", conn)[["name","type"]])

conn.close()