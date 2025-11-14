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

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env ANTES de importar la app
try:
    from dotenv import load_dotenv
    # Buscar .env en múltiples ubicaciones
    env_paths = [
        os.path.join(current_dir, '.env'),
        os.path.join(current_dir, 'env', '.env'),
        os.path.join(parent_dir, '.env'),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=False)  # No sobrescribir variables ya existentes
            logger.info(f"[INIT] ✅ Variables de entorno cargadas desde: {env_path}")
            break
except ImportError:
    # python-dotenv no está instalado, usar solo variables de entorno del sistema
    pass
except Exception as e:
    logger.warning(f"[INIT] ⚠️ Error cargando .env: {e}")

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
            # No hacer raise para evitar que gunicorn crashee
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

