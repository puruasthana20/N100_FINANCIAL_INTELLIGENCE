import sqlite3

conn = sqlite3.connect(
    "data/db/nifty100.db"
)

conn.execute(
    "PRAGMA foreign_keys = ON;"
)

cursor = conn.cursor()

cursor.execute(
    "PRAGMA foreign_keys;"
)

print(
    cursor.fetchone()
)

conn.close()

