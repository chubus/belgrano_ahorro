#!/usr/bin/env python3
"""ensure_image_columns.py

Utility module that ensures the required image columns exist in the database.
It supports both PostgreSQL (via DATABASE_URL) and SQLite fallback.
"""
import os
import logging

logger = logging.getLogger(__name__)

def ensure_columns():
    """Run the appropriate migration script based on the database configuration.

    - If ``DATABASE_URL`` is set and appears valid, use the PostgreSQL migration
      script ``add_image_url_pg.py``.
    - Otherwise, fall back to the SQLite migration script ``add_image_url_sqlite.py``.
    """
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        # Simple validation: must start with a known scheme
        if db_url.startswith(('postgresql://', 'postgres://', 'postgresql+psycopg2://')):
            try:
                from add_image_url_pg import main as migrate
                migrate()
                logger.info("✅ PostgreSQL image columns migration completed")
                return
            except Exception as e:
                logger.error(f"❌ PostgreSQL migration failed: {e}")
                raise
        else:
            logger.warning("DATABASE_URL present but does not look like PostgreSQL; using SQLite fallback")
    # SQLite fallback
    try:
        from add_image_url_sqlite import main as migrate_sqlite
        migrate_sqlite()
        logger.info("✅ SQLite image columns migration completed")
    except Exception as e:
        logger.error(f"❌ SQLite migration failed: {e}")
        raise

if __name__ == '__main__':
    ensure_columns()
