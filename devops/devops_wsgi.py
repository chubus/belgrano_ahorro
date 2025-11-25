#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point for Gunicorn - DevOps
Production entry point for the DevOps service
"""

import os
import sys
import logging

# Configurar paths para asegurar que el paquete devops sea importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Agregar el directorio padre al path si no está
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Agregar el directorio actual al path si no está
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configuración básica de logging para WSGI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('devops_wsgi')

try:
    from devops.app import create_app
    logger.info("✅ Importación exitosa de devops.app")
except ImportError as e:
    logger.error(f"❌ Error importando devops.app: {e}")
    # Intentar importación relativa como fallback
    try:
        from app import create_app
        logger.info("✅ Importación exitosa de app (fallback)")
    except ImportError as e2:
        logger.critical(f"❌ Error crítico: No se pudo importar create_app: {e2}")
        raise

# Crear la aplicación
try:
    application = create_app()
    logger.info("🚀 Aplicación WSGI inicializada correctamente")
except Exception as e:
    logger.critical(f"❌ Error al crear la aplicación: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
