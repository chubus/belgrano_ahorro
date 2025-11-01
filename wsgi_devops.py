#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Gunicorn - DevOps
Punto de entrada desde la raíz del proyecto para Render
"""

import sys
import os

# CRÍTICO: Agregar el directorio actual (raíz del proyecto) al PYTHONPATH
# Esto permite que Python encuentre el módulo 'devops'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Verificar que el módulo devops existe
try:
    import devops
    print(f"✅ Módulo devops encontrado en: {os.path.dirname(devops.__file__)}")
except ImportError as e:
    print(f"❌ Error: No se pudo importar devops desde {current_dir}")
    print(f"   Contenido del directorio: {os.listdir(current_dir)}")
    raise

# Importar la aplicación Flask desde devops.app
try:
    from devops.app import app
    print(f"✅ Aplicación Flask importada correctamente")
except ImportError as e:
    print(f"❌ Error importando devops.app: {e}")
    import traceback
    traceback.print_exc()
    raise

# Aplicación WSGI para Gunicorn (requerido)
application = app

# Para ejecución directa (testing local)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

