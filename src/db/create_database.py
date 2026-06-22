import sqlite3

from pathlib import Path


DB_PATH = Path(
    "data/db/nifty100.db"
)

SCHEMA_PATH = Path(
    "db/schema.sql"
)


conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

with open(
    SCHEMA_PATH,
    "r",
    encoding="utf-8"
) as file:

    schema = file.read()

cursor.executescript(schema)

conn.commit()

conn.close()

print(
    "Database created successfully"
)