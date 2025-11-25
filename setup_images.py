#!/usr/bin/env python3
"""
Full setup script for Belgrano Ahorro image handling.
It will:
1️⃣ Ensure the columns `imagen` and `image_url` exist in the tables
   `productos`, `negocios` and `sucursales`.
2️⃣ Populate the `imagen` column for existing records with the filenames
   found under `static/images/<entity>/` (only for `productos` – the other
   tables already store their logos directly under `static/images/`).
3️⃣ Convert every image file referenced by `imagen` into a Base64 data‑URI
   and store it in `image_url`.
4️⃣ Commit the changes.

Run with:
    python setup_images.py
"""
import sqlite3
import base64
from pathlib import Path
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "belgrano_ahorro.db"
STATIC_ROOT = PROJECT_ROOT / "static" / "images"

# Mapping table -> subfolder where the image file lives
SUBFOLDER_MAP = {
    "productos": "productos",   # many product images are inside this subfolder
    "negocios": "",            # logos are stored directly under images/
    "sucursales": "",          # same as above (if any)
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def ensure_column(table: str, column: str, col_type: str = "TEXT"):
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if column not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")
        print(f"✅ Added column '{column}' to {table}")
    else:
        print(f"✅ Column '{column}' already exists in {table}")

def image_to_base64(path: Path) -> str:
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

def resolve_image_path(table: str, filename: str) -> Path:
    sub = SUBFOLDER_MAP.get(table, "")
    if sub:
        return STATIC_ROOT / sub / filename
    else:
        return STATIC_ROOT / filename

# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------
if not DB_PATH.exists():
    print(f"❌ Database not found at {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1️⃣ Ensure columns exist
for tbl in ["productos", "negocios", "sucursales"]:
    ensure_column(tbl, "imagen")
    ensure_column(tbl, "image_url")

conn.commit()

# 2️⃣ Populate `imagen` for productos (if empty)
prod_folder = STATIC_ROOT / "productos"
if prod_folder.is_dir():
    image_files = sorted([p.name for p in prod_folder.iterdir() if p.is_file()])
    # Assign each file to the next product without an image
    cur.execute("SELECT id FROM productos WHERE (imagen IS NULL OR imagen='')")
    empty_ids = [row[0] for row in cur.fetchall()]
    for prod_id, img_name in zip(empty_ids, image_files):
        cur.execute("UPDATE productos SET imagen = ? WHERE id = ?", (img_name, prod_id))
        print(f"🖼️  Assigned {img_name} to producto id={prod_id}")
else:
    print("⚠️  No product images folder found; skipping imagen population for productos")

conn.commit()

# 3️⃣ Populate image_url from the file referenced in `imagen`
for tbl in ["productos", "negocios", "sucursales"]:
    cur.execute(
        f"SELECT id, imagen FROM {tbl} "
        f"WHERE (image_url IS NULL OR image_url='') AND imagen IS NOT NULL AND TRIM(imagen)!=''"
    )
    rows = cur.fetchall()
    print(f"🔧 Updating {len(rows)} rows in {tbl} (image_url)")
    for rec_id, img_name in rows:
        img_path = resolve_image_path(tbl, img_name)
        if img_path.is_file():
            data_uri = image_to_base64(img_path)
            cur.execute(
                f"UPDATE {tbl} SET image_url = ? WHERE id = ?",
                (data_uri, rec_id),
            )
        else:
            print(f"⚠️  Image file not found for {tbl} id={rec_id}: {img_name} (searched at {img_path})")

conn.commit()
conn.close()
print("✅ All image columns ready and populated. Deploy can proceed.")
