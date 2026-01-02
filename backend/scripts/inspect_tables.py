import sqlite3
import os

DB_PATH = "backend/sql_app.db"
if not os.path.exists(DB_PATH) and os.path.exists("sql_app.db"):
    DB_PATH = "sql_app.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Current Tables:")
for t in tables:
    print(t[0])

conn.close()
