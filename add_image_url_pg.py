#!/usr/bin/env python3
"""
Add `image_url` (and optionally `imagen`) columns to PostgreSQL tables if they don't exist.
This script reads the DATABASE_URL environment variable (e.g. postgres://user:pass@host:port/db)
and executes ALTER TABLE statements safely.
Run with:
    python add_image_url_pg.py
"""
import os
import re
import sys
import psycopg2
from urllib.parse import urlparse

def get_connection():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL not set in environment')
        sys.exit(1)
    # psycopg2 can parse the URL directly, but we need to handle SQLAlchemy dialects
    if db_url.startswith('postgresql+psycopg2://'):
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql://', 1)
    return psycopg2.connect(db_url)

def column_exists(cur, table, column):
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name=%s)",
        (table, column)
    )
    return cur.fetchone()[0]

def add_column(cur, table, column, col_type='TEXT'):
    if column_exists(cur, table, column):
        print(f"✅ Column '{column}' already exists in {table}")
        return
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")
    print(f"✅ Added column '{column}' to {table}")

def main():
    conn = get_connection()
    cur = conn.cursor()
    for tbl in ['productos', 'negocios', 'sucursales']:
        add_column(cur, tbl, 'image_url', 'TEXT')
        # Ensure legacy 'imagen' column exists (some environments may have removed it)
        add_column(cur, tbl, 'imagen', 'TEXT')
    conn.commit()
    cur.close()
    conn.close()
    print('✅ All columns ensured in PostgreSQL')

if __name__ == '__main__':
    main()
