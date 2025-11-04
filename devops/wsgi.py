#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Gunicorn - DevOps
Punto de entrada para despliegue en Render
"""

import sys
import os

"""
Loader robusto que garantiza que el paquete `devops` sea importable en
entornos donde el working directory no es la raíz del repo.
"""

# Asegurar que el directorio raíz del proyecto esté en sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Ruta absoluta a devops/app.py
app_py_path = os.path.join(current_dir, "app.py")

# Intentar: import estándar -> importlib -> runpy
application = None

try:
    from devops.app import app as application  # type: ignore
except Exception as e1:
    # Fallback 1: importlib
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("devops.app", app_py_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Garantizar rutas por si inside imports usan `from devops...`
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            spec.loader.exec_module(module)
            application = getattr(module, "app", None)
            if application is None:
                raise AttributeError("'app' no encontrado en devops/app.py")
        else:
            raise ImportError("No se pudo crear spec para devops/app.py")
    except Exception as e2:
        # Fallback 2: runpy
        try:
            import runpy
            old_path = sys.path[:]
            try:
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                module_dict = runpy.run_path(app_py_path, run_name="__main__")
                application = module_dict.get("app")
                if application is None:
                    raise RuntimeError("'app' no disponible tras runpy")
            finally:
                sys.path[:] = old_path
        except Exception as e3:
            raise RuntimeError(
                "Fallo cargando la aplicación Flask desde devops/app.py",
            ) from e3

# Si se ejecuta directamente (no recomendado en producción)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=False)

