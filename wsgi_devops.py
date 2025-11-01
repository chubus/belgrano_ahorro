#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Gunicorn - DevOps
Punto de entrada desde la raíz del proyecto
"""

import sys
import os

# Agregar el directorio actual al path para que Python encuentre el módulo devops
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar la aplicación desde devops
from devops.app import app

# Aplicación WSGI para Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

