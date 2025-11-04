#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Render.com
Carga la aplicación Flask de DevOps de forma robusta
"""
import os
import sys
import importlib.util

# Obtener directorio actual (raíz del proyecto)
current_dir = os.path.dirname(os.path.abspath(__file__))
devops_dir = os.path.join(current_dir, 'devops')
app_py_path = os.path.join(devops_dir, 'app.py')

# Asegurar que la raíz esté en PYTHONPATH
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Intentar cargar la aplicación de múltiples formas
application = None

# Método 1: Import estándar (si el paquete está disponible)
# Asegurar que devops sea reconocido como paquete
if os.path.exists(os.path.join(devops_dir, '__init__.py')):
    # Verificar que __init__.py existe para que Python reconozca devops como paquete
    pass

try:
    from devops.app import app as application
    print("✅ Aplicación cargada vía import estándar")
except Exception as e1:
    print(f"⚠️ Import estándar falló: {e1}")
    print(f"   Intentando métodos alternativos...")
    
    # Método 2: Cargar directamente con importlib
    try:
        if os.path.exists(app_py_path):
            spec = importlib.util.spec_from_file_location("devops.app", app_py_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # CRÍTICO: Asegurar que la raíz del proyecto esté en sys.path PRIMERO
                # Esto permite que 'from devops.routes import ...' funcione
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                # También añadir devops_dir para imports absolutos dentro de devops
                if devops_dir not in sys.path:
                    sys.path.insert(0, devops_dir)
                # Ejecutar el módulo (esto ejecutará devops/app.py)
                spec.loader.exec_module(module)
                application = getattr(module, 'app', None)
                if application:
                    print("✅ Aplicación cargada vía importlib directo")
                else:
                    raise AttributeError("No se encontró 'app' en devops/app.py")
            else:
                raise ImportError("No se pudo crear spec desde devops/app.py")
        else:
            raise FileNotFoundError(f"No existe devops/app.py en {app_py_path}")
    except Exception as e2:
        print(f"⚠️ Importlib falló: {e2}")
        # Método 3: Ejecutar el archivo directamente
        try:
            import runpy
            # Cambiar al directorio devops temporalmente
            old_cwd = os.getcwd()
            old_path = sys.path[:]
            try:
                os.chdir(devops_dir)
                sys.path.insert(0, devops_dir)
                sys.path.insert(0, current_dir)
                module_dict = runpy.run_path(app_py_path, run_name="__main__")
                application = module_dict.get('app')
                if application:
                    print("✅ Aplicación cargada vía runpy")
            finally:
                os.chdir(old_cwd)
                sys.path[:] = old_path
        except Exception as e3:
            print(f"⚠️ runpy falló: {e3}")
            raise RuntimeError(
                f"Todos los métodos de carga fallaron.\n"
                f"  Método 1 (import): {e1}\n"
                f"  Método 2 (importlib): {e2}\n"
                f"  Método 3 (runpy): {e3}\n"
                f"  current_dir: {current_dir}\n"
                f"  devops_dir: {devops_dir}\n"
                f"  app_py_path existe: {os.path.exists(app_py_path)}\n"
                f"  sys.path: {sys.path[:5]}"
            )

if application is None:
    raise RuntimeError("No se pudo cargar la aplicación Flask desde devops/app.py")

# Para ejecución directa
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
