#!/usr/bin/env python3
"""
Populate the `image_url` (Base64 data URI) fields for existing records.
Now skips empty or missing filenames and ensures the path points to a file.
Run with:
    python populate_image_urls.py
"""
import os
import sqlite3
import base64
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "belgrano_ahorro.db"
STATIC_ROOT = PROJECT_ROOT / "static" / "images"

# Mapping entity -> subfolder inside STATIC_ROOT where the image is stored
SUBFOLDER_MAP = {
    "productos": "productos",
    "negocios": "",          # logos are stored directly under images/
    "sucursales": "",        # same as above (if any)
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def image_to_base64(path: Path) -> str:
    """Convert an image file to a data URI (Base64)."""
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "application/octet-stream")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def resolve_image_path(entity: str, filename: str) -> Path:
    """Return the absolute path to the image file for a given entity.
    If the file does not exist, the returned Path will point to a non‑existent
    location – the caller must check ``.is_file()``.
    """
    subfolder = SUBFOLDER_MAP.get(entity, "")
    if subfolder:
        return STATIC_ROOT / subfolder / filename
    else:
        return STATIC_ROOT / filename

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------
def populate_table(table: str, id_col: str = "id"):
    """Populate ``image_url`` for *table* where it is empty and ``imagen`` is set.
    ``table`` must be one of the keys in ``SUBFOLDER_MAP``.
    """
    cur.execute(
        f"SELECT {id_col}, imagen FROM {table} "
        f"WHERE (image_url IS NULL OR image_url = '') "
        f"AND imagen IS NOT NULL AND TRIM(imagen) != ''"
    )
    rows = cur.fetchall()
    print(f"🔧 Updating {len(rows)} rows in {table}")
    for rec_id, img_name in rows:
        img_path = resolve_image_path(table, img_name)
        if img_path.is_file():
            data_uri = image_to_base64(img_path)
            cur.execute(
                f"UPDATE {table} SET image_url = ? WHERE {id_col} = ?",
                (data_uri, rec_id),
            )
        else:
            print(f"⚠️  Image not found or not a file for {table} id={rec_id}: '{img_name}' (searched at {img_path})")

if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        raise SystemExit(1)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for tbl in ["productos", "negocios", "sucursales"]:
        populate_table(tbl)

    conn.commit()
    conn.close()
    print("✅ All done!")
