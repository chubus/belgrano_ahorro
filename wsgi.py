#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point para Render.com
Carga la aplicación Flask de DevOps de forma robusta
"""
import os
import sys
import importlib.util
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener directorio actual (raíz del proyecto)
current_dir = os.path.dirname(os.path.abspath(__file__))
devops_dir = os.path.join(current_dir, 'devops')
app_py_path = os.path.join(devops_dir, 'app.py')

# Asegurar que la raíz esté en PYTHONPATH
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Inicializar base de datos PostgreSQL PRIMERO
# Solo si DATABASE_URL está correctamente configurada
_db_initialized = False
try:
    # Verificar que DATABASE_URL esté configurada antes de intentar conectar
    database_url = os.getenv('DATABASE_URL', '') or os.getenv('POSTGRES_URL', '')
    
    if not database_url:
        logger.warning("[INIT] ⚠️ DATABASE_URL no configurada. La aplicación puede no funcionar correctamente.")
        logger.warning("[INIT] ⚠️ Configure DATABASE_URL o POSTGRES_URL en Render Dashboard.")
    else:
        # Validar formato básico de la URL
        from urllib.parse import urlparse
        try:
            parsed = urlparse(database_url)
            if not parsed.hostname:
                logger.error("[INIT] ❌ DATABASE_URL no tiene un hostname válido")
                raise ValueError("DATABASE_URL inválida: falta hostname")
            
            # Verificar que el hostname sea completo
            if parsed.hostname.startswith('dpg-') and '.' not in parsed.hostname:
                logger.error(f"[INIT] ❌ Hostname incompleto en DATABASE_URL: '{parsed.hostname}'")
                logger.error("[INIT] ❌ La URL debe incluir el dominio completo (ej: dpg-xxx.frankfurt-postgres.render.com)")
                raise ValueError(f"Hostname incompleto: {parsed.hostname}")
            
            # Intentar inicializar la base de datos
            from init_db import init_db
            logger.info("[INIT] Inicializando base de datos PostgreSQL...")
            init_db()
            _db_initialized = True
            logger.info("[INIT] ✅ Base de datos inicializada correctamente")
        except ValueError as ve:
            logger.error(f"[INIT] ❌ Error de validación: {ve}")
            logger.error("[INIT] ❌ La aplicación no puede iniciar sin una DATABASE_URL válida")
            # No hacer raise para evitar que gunicorn crashee - la app puede intentar funcionar
        except Exception as e:
            error_msg = str(e)
            if "could not translate host name" in error_msg or "Name or service not known" in error_msg:
                logger.error("[INIT] ❌ ERROR: No se puede resolver el hostname de la base de datos")
                logger.error(f"[INIT]    Error: {error_msg}")
                logger.error("[INIT]    Verifique que DATABASE_URL tenga el formato correcto en Render Dashboard")
                logger.error("[INIT]    Formato esperado: postgresql://user:password@hostname:port/database?sslmode=require")
                # No hacer raise para evitar que gunicorn crashee
            else:
                logger.error(f"[INIT] ❌ Error inicializando base de datos: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # No hacer raise para evitar que gunicorn crashee
except ImportError as ie:
    logger.warning(f"[INIT] ⚠️ No se pudo importar init_db: {ie}")
    logger.warning("[INIT] ⚠️ La aplicación puede no funcionar correctamente sin la base de datos")
except Exception as e:
    logger.error(f"[INIT] ❌ Error crítico inicializando base de datos: {e}")
    import traceback
    logger.error(traceback.format_exc())
    # No hacer raise para evitar que gunicorn crashee
    logger.warning("[INIT] ⚠️ Continuando sin inicialización de base de datos (funcionalidad limitada)")

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
