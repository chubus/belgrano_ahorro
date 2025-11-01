#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Gunicorn - DevOps
Ejecutar desde el directorio devops
"""

import sys
import os

# Agregar el directorio padre al path para que pueda encontrar devops si es necesario
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar la aplicación
try:
    # Intentar importar desde la raíz del proyecto
    from devops.app import app
except ImportError:
    # Si estamos dentro del directorio devops, importar directamente
    try:
        from app import app
    except ImportError as e:
        import traceback
        print(f"Error importando app: {e}")
        traceback.print_exc()
        raise

# Aplicación WSGI para Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

