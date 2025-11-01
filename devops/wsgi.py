#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Gunicorn - DevOps
Punto de entrada para despliegue en Render
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importar la aplicación Flask desde devops.app
from devops.app import app as application

# Si se ejecuta directamente (no recomendado en producción)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=False)

