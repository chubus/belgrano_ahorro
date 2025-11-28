#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI config for Belgrano Ahorro project.
This file serves as the WSGI entry point for the main Belgrano Ahorro application.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wsgi')

def setup_paths():
    """Set up Python paths for the application."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    paths_to_add = [
        current_dir,
        '/opt/render/project/src',  # Render deployment path
    ]
    
    for path in paths_to_add:
        if path not in sys.path and os.path.exists(path):
            sys.path.insert(0, path)
            logger.info(f"Added to sys.path: {path}")

def load_env():
    """Load environment variables from .env file if present."""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env loading")

# Setup environment
load_env()
setup_paths()

# Check Ticketera service availability
try:
    import requests
    ticketera_url = os.getenv('TICKETERA_URL') or os.getenv('BELGRANO_AHORRO_URL')
    if ticketera_url:
        health_endpoint = f"{ticketera_url.rstrip('/')}/api/ofertas"
        resp = requests.get(health_endpoint, timeout=5)
        if resp.status_code == 200:
            logger.info(f"✅ Ticketera endpoint reachable: {health_endpoint}")
        else:
            logger.warning(f"⚠️ Ticketera endpoint returned {resp.status_code}: {health_endpoint}")
    else:
        logger.warning("⚠️ No Ticketera URL configured (TICKETERA_URL or BELGRANO_AHORRO_URL).")
except Exception as e:
    logger.error(f"❌ Error checking Ticketera health: {e}")

# Ejecutar migración automática de columnas de imagen
try:
    from ensure_image_columns import ensure_image_columns
    ensure_image_columns()
except Exception as e:
    # Capturar cualquier error (incluyendo Deadlocks) para no detener el inicio
    logger.warning(f"⚠️ No se pudo ejecutar migración automática (posible concurrencia): {e}")


try:
    # Import the main application from app.py
    # app.py imports app_unificado.py and exposes 'app'
    from app import app as application
    logger.info("✅ Belgrano Ahorro application imported successfully")
except ImportError as e:
    logger.critical(f"❌ Failed to import application: {e}")
    # Attempt to print more info about the error
    import traceback
    traceback.print_exc()
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
