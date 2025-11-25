#!/usr/bin/env python3
"""
Script to add `image_url` column to SQLite tables if it does not exist.
Works for the SQLite database used by the app (default belgrano_ahorro.db).
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "belgrano_ahorro.db"

if not DB_PATH.exists():
    print(f"❌ Database not found at {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Helper to add column if missing
def add_column(table, column, col_type="TEXT"):
    # Check if column exists
    cur.execute("PRAGMA table_info(%s)" % table)
    cols = [row[1] for row in cur.fetchall()]
    if column in cols:
        print(f"✅ Column '{column}' already exists in {table}")
        return
    # Add column
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")
    print(f"✅ Added column '{column}' to {table}")

for tbl in ["negocios", "sucursales", "productos"]:
    add_column(tbl, "image_url", "TEXT")

conn.commit()
conn.close()
print("✅ All columns ensured.")
