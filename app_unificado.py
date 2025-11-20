# app.py
# =================================================================
# ARCHIVO PRINCIPAL DE LA APLICACIÓN FLASK - BELGRANO AHORRO
# =================================================================
# 
# DESCRIPCIÓN:
# Este archivo contiene toda la lógica de la aplicación web, incluyendo:
# - Rutas y endpoints de la aplicación
# - Gestión de usuarios y autenticación
# - Manejo de productos, ofertas y categorías
# - Procesamiento de carrito y pedidos
# - Funciones auxiliares para el sistema
#
# MANTENIMIENTO:
# - Para agregar nuevas rutas: agregar nuevas funciones @app.route()
# - Para modificar productos: editar productos.json (ver GUIA_MANTENIMIENTO.md)
# - Para cambiar ofertas: modificar sección "ofertas" en productos.json
# - Para agregar negocios: agregar en sección "negocios" de productos.json
#
# EJECUCIÓN:
# python app.py
# 
# DEPENDENCIAS:
# - Flask (framework web)
# - db.py (módulo de base de datos)
# - productos.json (datos de productos, ofertas, categorías)
# =================================================================

import json
import logging
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import uuid
import re
import secrets
import hashlib
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

# Configurar logging PRIMERO con prefijos estandarizados
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Cache simple en memoria para evitar recargas (solo para datos JSON, NO para datos de DB)
_data_cache = {}
_cache_timestamp = None
CACHE_DURATION = 0  # Deshabilitado - siempre obtener datos frescos desde DB

def _limpiar_cache():
    """Limpiar cache global para forzar recarga de datos"""
    global _data_cache, _cache_timestamp
    _data_cache = {}
    _cache_timestamp = None
    logger.debug("Cache limpiado")


def _normalize_host(candidate: str) -> str:
    """Normalizar host para comparar URLs locales vs externas."""
    if not candidate:
        return ''
    value = candidate.strip()
    if '://' not in value:
        value = f"https://{value}"
    try:
        parsed = urlparse(value)
    except Exception:
        return ''
    host = (parsed.netloc or parsed.path or '').lower()
    return host.rstrip('/')


_SELF_HOST_CANDIDATES = [
    os.environ.get('SELF_BASE_URL'),
    os.environ.get('BELGRANO_SELF_URL'),
    os.environ.get('RENDER_EXTERNAL_URL'),
    os.environ.get('RENDER_EXTERNAL_HOSTNAME'),
    os.environ.get('HOSTNAME'),
    os.environ.get('APP_URL'),
    os.environ.get('BELGRANO_AHORRO_URL'),
    'https://belgranoahorro-aliq.onrender.com',
    'http://localhost:5000',
    'http://127.0.0.1:5000'
]

_SELF_HOSTS = {host for host in (_normalize_host(v) for v in _SELF_HOST_CANDIDATES) if host}


def _is_self_host(url: str) -> bool:
    """Determinar si la URL apunta a esta misma instancia."""
    return _normalize_host(url) in _SELF_HOSTS


def _build_http_session() -> requests.Session:
    """Crear sesión HTTP global con reintentos controlados."""
    session = requests.Session()
    retries_total = max(1, int(os.environ.get('API_RETRY_TOTAL', '3')))
    retries_backoff = max(0.1, float(os.environ.get('API_RETRY_BACKOFF', '1.0')))
    retry_strategy = Retry(
        total=retries_total,
        backoff_factor=retries_backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


HTTP_SESSION = _build_http_session()
HTTP_TIMEOUT_SECS = max(1, min(int(os.environ.get('API_TIMEOUT_SECS', '10')), 10))

# Inicializar base de datos PostgreSQL PRIMERO
# Solo si DATABASE_URL está correctamente configurada
# Usar flag global para evitar doble inicialización
_db_initialized = False
if not _db_initialized:
    try:
        # Verificar que DATABASE_URL esté configurada antes de intentar conectar
        import os
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
                    error_msg = f"[INIT] ❌ Hostname incompleto en DATABASE_URL: '{parsed.hostname}'. La URL debe incluir el dominio completo. Ejemplo correcto: dpg-xxx.frankfurt-postgres.render.com"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Intentar inicializar la base de datos (solo una vez)
                from init_db import init_db
                logger.info("[INIT] Inicializando base de datos PostgreSQL...")
                init_db()  # init_db() ya tiene protección interna contra doble inicialización
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
        # No hacer raise aquí para evitar que gunicorn crashee
        # La app puede intentar funcionar sin DB (aunque con funcionalidad limitada)
        logger.warning("[INIT] ⚠️ Continuando sin inicialización de base de datos (funcionalidad limitada)")

# Importar base de datos con manejo de errores
try:
    import db as database
    logger.info("[INIT] ✅ Módulo db importado correctamente")
except Exception as e:
    logger.error(f"[INIT] ❌ Error importando db: {e}")
    raise  # Detén la app si el import falla

# Importar API RESTful
api_bp = None
try:
    from api_belgrano_ahorro import api_bp
    logger.info("[INIT] ✅ API RESTful importada correctamente")
except ImportError as ie:
    logger.warning(f"[INIT] ⚠️ No se pudo importar api_bp: {ie}")
    logger.warning("[INIT] ⚠️ La aplicación continuará sin API RESTful (funcionalidad limitada)")
    api_bp = None
except Exception as e:
    logger.error(f"[INIT] ❌ Error importando API: {e}")
    import traceback
    logger.error(traceback.format_exc())
    logger.warning("[INIT] ⚠️ Continuando sin API RESTful (funcionalidad limitada)")
    api_bp = None

# Función para obtener conexión a la base de datos PostgreSQL
def get_db_connection():
    """Obtener conexión a la base de datos PostgreSQL"""
    from db_abstraction import get_db_connection as get_db_conn
    return get_db_conn()

# Importar middleware de autenticación y manejo de errores
try:
    from auth_middleware import (
        login_required, admin_required, flota_required,
        validate_input_data, production_only, rate_limit
    )
    logger.info("✅ auth_middleware importado correctamente")
except Exception as e:
    logger.error(f"⚠️ Error importando auth_middleware: {e}")
    # Crear funciones stub para evitar errores
    def login_required(f): return f
    def admin_required(f): return f
    def flota_required(f): return f
    def validate_input_data(f): return f
    def production_only(f): return f
    def rate_limit(f): return f

try:
    from error_handlers import register_error_handlers, ValidationError, AuthenticationError, AuthorizationError
    logger.info("✅ error_handlers importado correctamente")
except Exception as e:
    logger.error(f"⚠️ Error importando error_handlers: {e}")
    # Crear funciones stub
    class ValidationError(Exception): pass
    class AuthenticationError(Exception): pass
    class AuthorizationError(Exception): pass
    def register_error_handlers(app): pass

try:
    from helpers.ticketera_client import fetch_ticketera_ofertas
    logger.info("✅ helpers.ticketera_client importado correctamente")
except Exception as e:
    logger.error(f"⚠️ Error importando helpers.ticketera_client: {e}")

    def fetch_ticketera_ofertas(*_, **__):
        logger.warning("⚠️ fetch_ticketera_ofertas no disponible; usando fallback vacío.")
        return False, {"ofertas": []}

# Logger ya configurado arriba

# Crear la instancia de Flask
app = Flask(__name__)
app.secret_key = 'belgrano_ahorro_secret_key_2025'  # Clave secreta para sesiones

# Configurar API_KEY para auth_middleware
app.config['API_KEY'] = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

# Registrar API RESTful (solo una vez)
if api_bp:
    blueprint_name = api_bp.name
    if blueprint_name not in [bp.name for bp in app.blueprints.values()]:
        try:
            app.register_blueprint(api_bp)
            logger.info("[INIT] ✅ API RESTful registrada en /api/*")
        except Exception as e:
            logger.error(f"[INIT] ❌ Error registrando API RESTful: {e}")
            raise
    else:
        logger.info("[INIT] ✅ API RESTful ya estaba registrada (omitiendo duplicado)")

# Importar configuración centralizada
try:
    from config import (
        BELGRANO_AHORRO_URL, BELGRANO_AHORRO_API_KEY,
        TICKETERA_URL, FLASK_ENV, SECRET_KEY
    )
    logger.info("[INIT] ✅ Configuración centralizada cargada")
except ImportError:
    logger.warning("[INIT] ⚠️ No se pudo importar config.py, usando variables de entorno directamente")
    BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
    BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
    TICKETERA_URL = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'belgrano_ahorro_secret_key_2025')

app.config['ENV'] = FLASK_ENV
app.secret_key = SECRET_KEY
app.config['API_KEY'] = BELGRANO_AHORRO_API_KEY

# Registrar manejadores de errores
register_error_handlers(app)

# NO registrar blueprint de DevOps aquí - DevOps es una app separada

# ==========================================
# CONFIGURACIÓN DE COMUNICACIÓN API
# ==========================================
# Variables de entorno para comunicación entre servicios
TICKETERA_URL = os.environ.get('TICKETERA_URL')
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY')

# Verificar que las variables de entorno estén definidas
if not BELGRANO_AHORRO_URL:
    logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_URL no está definida")
if not BELGRANO_AHORRO_API_KEY:
    logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_API_KEY no está definida")

logger.info(f"🔗 Configuración API:")
logger.info(f"   TICKETERA_URL: {TICKETERA_URL}")
logger.info(f"   BELGRANO_AHORRO_URL: {BELGRANO_AHORRO_URL}")
if BELGRANO_AHORRO_API_KEY:
    logger.info(f"   API_KEY: {BELGRANO_AHORRO_API_KEY[:10]}...")
else:
    logger.warning("   API_KEY: No definida")

# =================================================================
# FUNCIONES DE BÚSQUEDA Y FILTRADO DE PRODUCTOS
# =================================================================

def buscar_productos(productos, busqueda):
    """
    Buscar productos por nombre, descripción o categoría
    holi
    
    PARÁMETROS:
    - productos: lista de productos a buscar
    - busqueda: texto de búsqueda ingresado por el usuario
    
    RETORNA:
    - Lista de productos que coinciden con la búsqueda
    
    MANTENIMIENTO:
    - Para agregar más campos de búsqueda: agregar condiciones en el bucle
    - Para cambiar la lógica de búsqueda: modificar las comparaciones
    """
    if not busqueda:
        return productos
    
    busqueda = busqueda.lower()
    resultados = []
    
    for producto in productos:
        nombre = producto.get('nombre', '').lower()
        if busqueda in nombre:
            resultados.append(producto)
    
    return resultados

# =================================================================
# FUNCIONES DE CARGA DE DATOS DESDE JSON
# =================================================================

def cargar_productos():
    """
    Cargar productos desde el archivo productos.json
    
    RETORNA:
    - Lista de productos activos
    
    MANTENIMIENTO:
    - Para agregar productos: editar productos.json (ver GUIA_MANTENIMIENTO.md)
    - Para cambiar estructura: modificar el acceso a data.get('productos', [])
    - Para agregar validaciones: agregar condiciones antes del return
    """
    try:
        with open('productos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            productos = data.get('productos', [])
            logger.info(f"Productos cargados correctamente: {len(productos)} productos")
            return productos
    except Exception as e:
        logger.error(f"Error al cargar productos: {e}")
        return []

def cargar_datos_completos():
    """
    Cargar todos los datos del JSON (SOLO COMO FALLBACK)
    
    NOTA IMPORTANTE:
    - Esta función solo se usa como fallback cuando no hay datos en la base de datos
    - Los datos principales SIEMPRE vienen de la base de datos (DevOps)
    - El cache está deshabilitado (CACHE_DURATION = 0) para asegurar datos frescos
    
    RETORNA:
    - Diccionario completo con todos los datos del sistema desde JSON
    
    MANTENIMIENTO:
    - Para agregar nuevas secciones: agregar en productos.json
    - Para cambiar estructura: modificar el acceso a los datos
    """
    global _data_cache, _cache_timestamp
    
    # Verificar si el cache es válido
    current_time = time.time()
    if (_cache_timestamp is None or 
        current_time - _cache_timestamp > CACHE_DURATION or 
        not _data_cache):
        
        try:
            with open('productos.json', 'r', encoding='utf-8') as file:
                datos = json.load(file)
                _data_cache = datos
                _cache_timestamp = current_time
                logger.info(f"✅ Datos locales cargados correctamente (cache actualizado)")
                return datos
        except FileNotFoundError:
            logger.warning("⚠️ Archivo productos.json no encontrado, usando datos vacíos")
            _data_cache = {
                'negocios': {},
                'categorias': {},
                'ofertas': {},
                'productos': [],
                'sucursales': {}
            }
            _cache_timestamp = current_time
            return _data_cache
        except Exception as e:
            logger.error(f"❌ Error al cargar datos completos: {e}")
            _data_cache = {
                'negocios': {},
                'categorias': {},
                'ofertas': {},
                'productos': [],
                'sucursales': {}
            }
            _cache_timestamp = current_time
            return _data_cache
    else:
        logger.info(f"📋 Usando datos desde cache (válido por {CACHE_DURATION - (current_time - _cache_timestamp):.0f}s más)")
        return _data_cache

def obtener_negocios():
    """
    Obtener lista de negocios activos
    SIEMPRE desde base de datos (DevOps) - SIN CACHE para datos frescos
    
    RETORNA:
    - Diccionario con todos los negocios del sistema
    
    NOTA:
    - Esta función SIEMPRE consulta la base de datos directamente
    - No usa cache para asegurar datos frescos desde DevOps
    - Los cambios en DevOps se reflejan inmediatamente
    """
    # Obtener SIEMPRE desde base de datos (donde se guardan los creados desde DevOps)
    # Sin cache para asegurar datos actualizados en tiempo real
    negocios_db = obtener_negocios_desde_db()
    
    if negocios_db:
        logger.info(f"✅ Negocios obtenidos desde DevOps (DB): {len(negocios_db)}")
        return negocios_db
    else:
        logger.info("ℹ️ No hay negocios en la base de datos (DevOps)")
        return {}

def obtener_categorias_desde_db():
    """
    Obtener categorías desde la base de datos PostgreSQL (donde se guardan las creadas desde DevOps)
    Retorna diccionario con estructura {categoria_id: categoria_data} y también {nombre: categoria_data}
    para permitir búsqueda por ID o por nombre
    """
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT id, nombre, descripcion, activa, fecha_creacion
                FROM categorias 
                WHERE activa = TRUE
                ORDER BY nombre
            '''))
            rows = result.fetchall()
            categorias = {}
            for row in rows:
                categoria_id = str(row[0])
                categoria_nombre = row[1] or ''
                categoria_data = {
                    'id': categoria_id,
                    'nombre': categoria_nombre,
                    'descripcion': row[2] or '',
                    'activa': bool(row[3]),
                    'icono': '📦',  # Icono por defecto
                    'fecha_creacion': str(row[4]) if row[4] else ''
                }
                # Indexar por ID
                categorias[categoria_id] = categoria_data
                # También indexar por nombre (en minúsculas para búsqueda case-insensitive)
                if categoria_nombre:
                    categorias[categoria_nombre.lower()] = categoria_data
            if categorias:
                logger.info(f"[DB] ✅ Categorías obtenidas desde PostgreSQL: {len(rows)} categorías")
            else:
                logger.info("[DB] ℹ️ No hay categorías activas en la base de datos")
            return categorias
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ No se pudieron obtener categorías desde DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}

def obtener_categorias():
    """
    Obtener todas las categorías del sistema
    SIEMPRE desde base de datos (DevOps) - SIN CACHE para datos frescos
    
    RETORNA:
    - Diccionario con todas las categorías del sistema
    
    NOTA:
    - Esta función SIEMPRE consulta la base de datos directamente
    - No usa cache para asegurar datos frescos desde DevOps
    - Los cambios en DevOps se reflejan inmediatamente
    - Si no hay categorías en DB, retorna diccionario vacío
    """
    # Obtener SIEMPRE desde base de datos (donde se guardan las creadas desde DevOps)
    # Sin cache para asegurar datos actualizados en tiempo real
    categorias_db = obtener_categorias_desde_db()
    if categorias_db:
        logger.info(f"✅ Categorías obtenidas desde DevOps (DB): {len(categorias_db) // 2} categorías")  # Dividido por 2 porque se indexan por ID y nombre
        return categorias_db
    
    logger.info("ℹ️ No hay categorías en la base de datos (DevOps)")
    return {}

def obtener_ofertas():
    """
    Obtener ofertas activas
    SIEMPRE desde base de datos (DevOps) - SIN CACHE para datos frescos
    
    RETORNA:
    - Diccionario con todas las ofertas del sistema organizadas por negocio
    
    NOTA:
    - Esta función SIEMPRE consulta la base de datos directamente
    - No usa cache para asegurar datos frescos desde DevOps
    - Los cambios en DevOps se reflejan inmediatamente
    """
    # Obtener SIEMPRE desde base de datos (donde se guardan las creadas desde DevOps)
    # Sin cache para asegurar datos actualizados en tiempo real
    ofertas_db = obtener_ofertas_desde_db()
    
    if ofertas_db:
        total_ofertas = sum(len(ofertas) for ofertas in ofertas_db.values())
        logger.info(f"✅ Ofertas obtenidas desde DevOps (DB): {total_ofertas} en {len(ofertas_db)} negocios")
        return ofertas_db
    else:
        logger.info("ℹ️ No hay ofertas en la base de datos (DevOps)")
        return {}

def obtener_sucursales_desde_db():
    """
    Obtener sucursales desde la base de datos PostgreSQL (donde se guardan las creadas desde DevOps)
    Retorna diccionario con estructura {negocio_id: {sucursal_id: sucursal_data}} o {} si falla
    """
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT s.id, s.nombre, s.direccion, s.telefono, s.email, s.negocio_id, s.activo,
                       s.fecha_creacion, s.fecha_actualizacion, n.nombre as negocio_nombre
                FROM sucursales s
                LEFT JOIN negocios n ON s.negocio_id = n.id
                WHERE s.activo = TRUE
                ORDER BY s.nombre
            '''))
            rows = result.fetchall()
            sucursales_por_negocio = {}
            
            for row in rows:
                negocio_id = str(row[5]) if row[5] else 'sin_negocio'
                sucursal_id = str(row[0])
                
                if negocio_id not in sucursales_por_negocio:
                    sucursales_por_negocio[negocio_id] = {}
                
                sucursales_por_negocio[negocio_id][sucursal_id] = {
                    'id': sucursal_id,
                    'nombre': row[1] or '',
                    'direccion': row[2] or '',
                    'telefono': row[3] or '',
                    'email': row[4] or '',
                    'negocio_id': negocio_id,
                    'negocio': row[9] or 'Sin negocio',
                    'activo': bool(row[6]),
                    'fecha_creacion': str(row[7]) if row[7] else '',
                    'fecha_actualizacion': str(row[8]) if row[8] else ''
                }
            
            if sucursales_por_negocio:
                total_sucursales = sum(len(sucs) for sucs in sucursales_por_negocio.values())
                logger.info(f"[DB] ✅ Sucursales obtenidas desde PostgreSQL: {total_sucursales} en {len(sucursales_por_negocio)} negocios")
            else:
                logger.info("[DB] ℹ️ No hay sucursales activas en la base de datos")
            return sucursales_por_negocio
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ No se pudieron obtener sucursales desde DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}

def obtener_sucursales():
    """
    Obtener todas las sucursales del sistema
    SIEMPRE desde base de datos (DevOps) - SIN CACHE para datos frescos
    
    RETORNA:
    - Diccionario con todas las sucursales organizadas por negocio
    
    NOTA:
    - Esta función SIEMPRE consulta la base de datos directamente
    - No usa cache para asegurar datos frescos desde DevOps
    - Los cambios en DevOps se reflejan inmediatamente
    """
    # Obtener SIEMPRE desde base de datos (donde se guardan las creadas desde DevOps)
    # Sin cache para asegurar datos actualizados en tiempo real
    sucursales_db = obtener_sucursales_desde_db()
    
    if sucursales_db:
        logger.info(f"✅ Sucursales obtenidas desde DevOps (DB): {len(sucursales_db)} negocios")
        return sucursales_db
    else:
        logger.info("ℹ️ No hay sucursales en la base de datos (DevOps)")
        return {}

def obtener_sucursales_por_negocio(negocio_id):
    """
    Obtener sucursales de un negocio específico
    
    PARÁMETROS:
    - negocio_id: ID del negocio
    
    RETORNA:
    - Lista de sucursales activas del negocio
    """
    sucursales = obtener_sucursales()
    if negocio_id in sucursales:
        return [suc for suc in sucursales[negocio_id].values() if suc.get('activo', True)]
    return []

def obtener_productos_por_sucursal(negocio_id, sucursal_id):
    """
    Obtener productos disponibles en una sucursal específica
    SOLO desde base de datos (DevOps) - TODOS los datos vienen de DevOps
    
    PARÁMETROS:
    - negocio_id: ID del negocio
    - sucursal_id: ID de la sucursal
    
    RETORNA:
    - Lista de productos disponibles en la sucursal
    """
    # Obtener productos del negocio desde DB
    productos_negocio = obtener_productos_por_negocio(negocio_id)
    
    # Por ahora, retornar todos los productos del negocio
    # (la relación producto-sucursal se puede implementar después si es necesario)
    return productos_negocio

def obtener_productos_por_negocio(negocio_id):
    """
    Obtener productos de un negocio específico
    SOLO desde base de datos (DevOps) - TODOS los datos vienen de DevOps
    """
    # Obtener todos los productos desde DB y filtrar por negocio
    productos = obtener_productos_desde_db()
    # Filtrar por negocio_id (puede ser string o número)
    negocio_id_str = str(negocio_id)
    return [p for p in productos if str(p.get('negocio_id', '')) == negocio_id_str and p.get('activo', True)]

def obtener_productos_destacados():
    """
    Obtener productos destacados de todos los negocios
    SOLO desde base de datos (DevOps) - TODOS los datos vienen de DevOps
    """
    # Obtener todos los productos desde DB y filtrar destacados
    productos = obtener_productos_desde_db()
    return [p for p in productos if p.get('destacado', False) and p.get('activo', True)]

def obtener_ofertas_activas():
    """
    Obtener ofertas activas
    Prioridad: Base de datos (DevOps) > Ticketera > JSON local
    """
    try:
        ofertas_activas = {}
        
        # PRIORIDAD 1: Obtener desde base de datos (DevOps) - FUENTE PRINCIPAL
        try:
            ofertas_db = obtener_ofertas_desde_db()
            if ofertas_db:
                total_ofertas_db = sum(len(o) for o in ofertas_db.values())
                logger.info(f"✅ Ofertas obtenidas desde DevOps (DB): {total_ofertas_db} ofertas en {len(ofertas_db)} negocios")
                # Usar ofertas de DB como base
                ofertas_activas = ofertas_db.copy()
            else:
                logger.info("ℹ️ No hay ofertas en la base de datos (DevOps)")
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo ofertas desde DB: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # PRIORIDAD 2: Intentar obtener ofertas adicionales desde Ticketera (opcional)
        ticketera_url = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com').rstrip('/')
        ticketera_timeout = min(float(os.environ.get('TICKETERA_TIMEOUT_SECS', '2.5')), 3.0)
        ticketera_retries = max(0, min(int(os.environ.get('TICKETERA_RETRY_TOTAL', '1')), 3))
        
        if ticketera_url and not _is_self_host(ticketera_url):
            logger.info(f"🔍 Intentando obtener ofertas adicionales desde Ticketera (timeout={ticketera_timeout}s, retries={ticketera_retries})")
            ticketera_success, ticketera_payload = fetch_ticketera_ofertas(
                timeout=ticketera_timeout,
                retries=ticketera_retries
            )
            ticketera_ofertas = ticketera_payload.get('ofertas', [])
            
            if ticketera_success and ticketera_ofertas:
                logger.info(f"✅ Ofertas obtenidas desde Ticketera: {len(ticketera_ofertas)}")
                for oferta in ticketera_ofertas:
                    if not isinstance(oferta, dict):
                        continue
                    negocio = (
                        oferta.get('negocio')
                        or oferta.get('negocio_nombre')
                        or oferta.get('negocio_id')
                        or 'Ticketera'
                    )
                    negocio = str(negocio)
                    if negocio not in ofertas_activas:
                        ofertas_activas[negocio] = []
                    ofertas_existentes_ids = {o.get('id') for o in ofertas_activas[negocio] if isinstance(o, dict)}
                    if oferta.get('id') not in ofertas_existentes_ids:
                        ofertas_activas[negocio].append(oferta)
                logger.info(f"✅ Ofertas combinadas (DB + Ticketera): {sum(len(o) for o in ofertas_activas.values())} totales")
            else:
                logger.info("ℹ️ Ticketera no respondió a tiempo; continuando sin ofertas adicionales.")
        else:
            logger.debug("ℹ️ Ticketera apunta a esta misma instancia; se omite la llamada externa.")
        
        # PRIORIDAD 3: Si aún no hay ofertas, intentar desde JSON local (último recurso)
        if not ofertas_activas:
            logger.info("📋 No se obtuvieron ofertas de DB ni Ticketera, intentando desde JSON local...")
            try:
                datos = cargar_datos_completos()
                ofertas = datos.get('ofertas', {})
                
                if isinstance(ofertas, list):
                    for oferta in ofertas:
                        if isinstance(oferta, dict):
                            negocio = oferta.get('negocio', 'Sin negocio')
                            if negocio not in ofertas_activas:
                                ofertas_activas[negocio] = []
                            ofertas_activas[negocio].append(oferta)
                elif isinstance(ofertas, dict):
                    for negocio, ofertas_negocio in ofertas.items():
                        if isinstance(ofertas_negocio, list):
                            ofertas_activas[negocio] = ofertas_negocio
                        elif isinstance(ofertas_negocio, dict):
                            ofertas_activas[negocio] = [ofertas_negocio]
            except Exception as e:
                logger.error(f"❌ Error cargando ofertas desde JSON: {e}")
        
        # Agregar información de productos a las ofertas (obtener desde DB)
        productos = obtener_productos_desde_db()
        
        for negocio, ofertas_negocio in ofertas_activas.items():
            if isinstance(ofertas_negocio, list):
                for oferta in ofertas_negocio:
                    if isinstance(oferta, dict):
                        # Agregar información de productos a la oferta
                        productos_oferta = []
                        for producto_id in oferta.get('productos', []):
                            producto = next((p for p in productos if p.get('id') == producto_id), None)
                            if producto:
                                productos_oferta.append(producto)
                        
                        oferta['productos_info'] = productos_oferta
        
        logger.info(f"✅ Ofertas activas procesadas: {len(ofertas_activas)} negocios")
        return ofertas_activas
        
    except Exception as e:
        logger.warning(f"⚠️ Error en obtener_ofertas_activas: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {}  # Retornar dict vacío en lugar de fallar

# ==========================================
# BASE DE DATOS SIMPLE (USUARIOS Y PEDIDOS)
# ==========================================
# Base de datos PostgreSQL para persistencia
# Por ahora usamos diccionarios en memoria para simplicidad

# usuarios = {
#     'admin@belgrano.com': {
#         'password': generate_password_hash('admin123'),
#         'nombre': 'Administrador',
#         'email': 'admin@belgrano.com',
#         'rol': 'admin'
#     }
# }

# Almacenar pedidos (en una app real sería una base de datos)
# pedidos = {}

# ==========================================
# CARGA DE DATOS
# ==========================================
# Esta sección carga los productos desde el archivo JSON
# Si hay algún error, crea una lista vacía para evitar que la app falle
try:
    with open("productos.json", "r", encoding="utf-8") as f:
        productos = json.load(f)
    logger.info(f"Productos cargados correctamente: {len(productos['productos'])} productos")
except Exception as e:
    logger.error(f"Error al cargar productos.json: {e}")
    productos = {"productos": []}  # Lista vacía para evitar fallos

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def obtener_producto_por_id(producto_id):
    """
    Obtener un producto por su ID
    SOLO desde base de datos (DevOps) - TODOS los datos vienen de DevOps
    """
    try:
        # Obtener productos desde DB
        productos_lista = obtener_productos_desde_db()
        
        for producto in productos_lista:
            if str(producto.get('id', '')) == str(producto_id):
                return producto
        return None
    except Exception as e:
        logger.error(f"Error obteniendo producto {producto_id}: {e}")
        return None

def calcular_total_carrito():
    """
    Calcula el total del carrito de compras
    """
    total = 0
    if 'carrito' in session:
        for producto_id, cantidad in session['carrito'].items():
            producto = obtener_producto_por_id(producto_id)
            if producto:
                total += producto['precio'] * cantidad
    return total

def usuario_logueado():
    """
    Verifica si hay un usuario logueado
    """
    return 'usuario_id' in session

def obtener_usuario_actual():
    """
    Obtener información del usuario actualmente logueado
    """
    if not usuario_logueado():
        return None
    
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None
    
    if database is None:
        return None
    
    return database.obtener_usuario_por_id(usuario_id)

def generar_numero_pedido():
    """
    Genera un número único de pedido
    """
    fecha = datetime.now().strftime("%Y%m%d")
    codigo = str(uuid.uuid4())[:8].upper()
    return f"PED-{fecha}-{codigo}"

# ==========================================
# FUNCIONES DE RECUPERACIÓN DE CONTRASEÑA
# ==========================================

def generar_token_recuperacion():
    """Genera un token seguro para recuperación de contraseña"""
    return secrets.token_urlsafe(32)

def sanitizar_email(email):
    """Sanitiza y valida el formato del email"""
    if not email:
        return None, "Email es requerido"
    
    email = email.strip().lower()
    
    # Validación básica de formato
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return None, "Formato de email inválido"
    
    # Sanitización adicional
    email = re.sub(r'[<>"\']', '', email)  # Remover caracteres peligrosos
    
    return email, None

def sanitizar_codigo(codigo):
    """Sanitiza el código de verificación"""
    if not codigo:
        return None, "Código es requerido"
    
    codigo = codigo.strip()
    
    # Solo permitir números y letras
    if not re.match(r"^[A-Za-z0-9]{6,8}$", codigo):
        return None, "Código inválido"
    
    return codigo, None

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route("/login", methods=['GET', 'POST'])
@rate_limit(max_requests=5, window=300)  # 5 intentos por 5 minutos
def login():
    """
    RUTA DE LOGIN - Página de inicio de sesión
    """
    if usuario_logueado():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Debug logs
        logger.info(f"Intento de login - Email: {email}")
        
        # Validación de campos
        if not email or not password:
            logger.warning("Login fallido - Campos incompletos")
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'error': 'Campos requeridos: email y password'}), 400
            flash('❌ Por favor completa todos los campos obligatorios', 'danger')
            return render_template('login.html')
        
        # Validación de formato de email
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            logger.warning(f"Login fallido - Email inválido: {email}")
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'error': 'Formato de email inválido'}), 400
            flash('❌ Por favor ingresa un email válido', 'danger')
            return render_template('login.html')
        
        # Verificar credenciales
        if database is None:
            logger.error("Login fallido - Database es None")
            flash('❌ Error del sistema. Intenta más tarde.', 'danger')
            return render_template('login.html')
        
        logger.info("Intentando verificar credenciales...")
        resultado = database.verificar_usuario(email, password)
        logger.info(f"Resultado de verificar_usuario: {resultado}")
        
        if isinstance(resultado, dict) and resultado.get('exito'):
            # Login exitoso
            usuario = resultado.get('usuario', {})
            session['usuario_id'] = usuario.get('id')
            session['usuario_nombre'] = usuario.get('nombre')
            session['usuario_email'] = usuario.get('email')
            session['usuario_rol'] = usuario.get('rol', 'cliente')
            
            logger.info(f"Login exitoso - Usuario: {usuario.get('nombre')}, ID: {usuario.get('id')}")
            flash(f'✅ ¡Bienvenido, {usuario.get("nombre", "Usuario")}! Has iniciado sesión correctamente', 'success')
            return redirect(url_for('index'))
        else:
            # Login fallido
            logger.warning(f"Login fallido - Email: {email}")
            flash('❌ Email o contraseña incorrectos. Verifica tus credenciales', 'danger')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
@rate_limit(max_requests=3, window=600)  # 3 intentos por 10 minutos
def register():
    """
    RUTA DE REGISTRO - Nueva página de registro con validación mejorada
    """
    if usuario_logueado():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')
        telefono = request.form.get('telefono', '')
        direccion = request.form.get('direccion', '')
        terminos = request.form.get('terminos')
        
        # Debug logs
        logger.info(f"Intento de registro - Email: {email}, Nombre: {nombre}, Apellido: {apellido}")
        
        # Validaciones mejoradas
        if not all([nombre, apellido, email, password, confirmar_password]):
            logger.warning("Registro fallido - Campos obligatorios incompletos")
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'error': 'Todos los campos son obligatorios'}), 400
            flash('Por favor completa todos los campos obligatorios', 'danger')
            return render_template('register.html')
        
        # Validación de formato de email
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            logger.warning(f"Registro fallido - Email inválido: {email}")
            flash('Por favor ingresa un email válido', 'danger')
            return render_template('register.html')
        
        # Validar términos y condiciones
        if not terminos:
            logger.warning("Registro fallido - Términos y condiciones no aceptados")
            flash('❌ Debes aceptar los términos y condiciones', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            logger.warning("Registro fallido - Contraseña muy corta")
            flash('❌ La contraseña debe tener al menos 6 caracteres', 'danger')
            return render_template('register.html')
        
        if password != confirmar_password:
            logger.warning("Registro fallido - Contraseñas no coinciden")
            flash('❌ Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
        
        # Validar email
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            logger.warning("Registro fallido - Email inválido")
            flash('❌ Por favor ingresa un email válido', 'danger')
            return render_template('register.html')
        
        # Validar teléfono (opcional)
        if telefono and not re.match(r"^[\d\-\+\s]+$", telefono):
            logger.warning("Registro fallido - Teléfono inválido")
            flash('❌ Por favor ingresa un teléfono válido', 'danger')
            return render_template('register.html')
        
        # Crear usuario
        if database is None:
            logger.error("Registro fallido - Database es None")
            flash('❌ Error del sistema. Intenta más tarde.', 'danger')
            return render_template('register.html')
        
        logger.info("Intentando crear usuario en la base de datos...")
        resultado = database.crear_usuario(nombre, apellido, email, password, telefono, direccion)
        logger.info(f"Resultado de crear_usuario: {resultado}")
        
        if resultado['exito']:
            logger.info(f"Usuario creado exitosamente - ID: {resultado.get('usuario_id')}")
            flash(f'¡Registro exitoso! Bienvenido {nombre}, ya puedes iniciar sesión con tu cuenta', 'success')
            return redirect(url_for('index'))
        else:
            logger.error(f"Error al crear usuario: {resultado.get('mensaje')}")
            flash(f'❌ Error al crear usuario: {resultado["mensaje"]}', 'danger')
    
    return render_template('register.html')

@app.route("/logout")
def logout():
    """
    RUTA DE LOGOUT - Cerrar sesión
    """
    session.clear()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('index'))

@app.route("/perfil")
def perfil():
    """
    RUTA DE PERFIL - Página del perfil del usuario
    
    MANTENIMIENTO:
    - Para agregar campos al perfil: modificar obtener_usuario_por_id en db.py
    - Para cambiar información mostrada: modificar template perfil.html
    - Para agregar validaciones: agregar verificaciones aquí
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver tu perfil', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Asegurar que el usuario tenga todos los campos necesarios
    usuario = {
        'id': usuario.get('id'),
        'nombre': usuario.get('nombre', 'Usuario'),
        'email': usuario.get('email', ''),
        'telefono': usuario.get('telefono', ''),
        'direccion': usuario.get('direccion', ''),
        'rol': usuario.get('rol', 'cliente'),
        'fecha_registro': usuario.get('fecha_registro')
    }
    
    # Obtener pedidos del usuario
    if database is None:
        pedidos = []
        total_gastado = 0
    else:
        usuario_id = usuario.get('id')
        if usuario_id:
            pedidos = database.obtener_pedidos_usuario(usuario_id)
            total_gastado = sum(pedido.get('total', 0) for pedido in pedidos)
        else:
            pedidos = []
            total_gastado = 0
    
    return render_template('perfil.html', 
                         usuario=usuario, 
                         pedidos=pedidos,
                         total_gastado=total_gastado,
                         sesiones=[])

@app.route("/editar-perfil", methods=['POST'])
def editar_perfil():
    """
    RUTA PARA EDITAR PERFIL - Procesar cambios del perfil
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para editar tu perfil', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono', '')
    direccion = request.form.get('direccion', '')
    
    if not nombre:
        flash('El nombre es obligatorio', 'danger')
        return redirect(url_for('perfil'))
    
    if database is None:
        flash('Error del sistema. Intenta más tarde.', 'danger')
        return redirect(url_for('perfil'))
    
    resultado = database.actualizar_usuario(usuario.get('id', 0), nombre, telefono, direccion)
    
    if resultado:
        session['usuario_nombre'] = nombre
        flash('Perfil actualizado exitosamente', 'success')
    else:
        flash('Error al actualizar el perfil', 'danger')
    
    return redirect(url_for('perfil'))

@app.route("/cambiar-password", methods=['POST'])
def cambiar_password():
    """
    RUTA PARA CAMBIAR CONTRASEÑA - Procesar cambio de contraseña
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para cambiar tu contraseña', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    password_actual = request.form.get('password_actual')
    password_nuevo = request.form.get('password_nuevo')
    confirmar_password = request.form.get('confirmar_password')
    
    if not all([password_actual, password_nuevo, confirmar_password]):
        flash('Por favor completa todos los campos', 'danger')
        return redirect(url_for('perfil'))
    
    if len(password_nuevo) < 6:
        flash('La nueva contraseña debe tener al menos 6 caracteres', 'danger')
        return redirect(url_for('perfil'))
    
    if password_nuevo != confirmar_password:
        flash('Las contraseñas no coinciden', 'danger')
        return redirect(url_for('perfil'))
    
    if database is None:
        flash('Error del sistema. Intenta más tarde.', 'danger')
        return redirect(url_for('perfil'))
    
    resultado = database.cambiar_password(usuario.get('id', 0), password_actual, password_nuevo)
    
    if resultado:
        flash('Contraseña cambiada exitosamente', 'success')
    else:
        flash('Contraseña actual incorrecta', 'danger')
    
    return redirect(url_for('perfil'))

# ==========================================
# RUTAS DE RECUPERACIÓN DE CONTRASEÑA
# ==========================================

@app.route("/recuperar-password", methods=['GET', 'POST'])
def recuperar_password():
    """
    RUTA PARA RECUPERAR CONTRASEÑA - Paso 1: Solicitar email
    """
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Sanitizar y validar email
        email_limpio, error = sanitizar_email(email)
        if error:
            flash(error, 'danger')
            return render_template("recuperar_password.html")
        
        # Verificar si el usuario existe
        if database is None:
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template("recuperar_password.html")
        
        usuario = database.buscar_usuario_por_email(email_limpio)
        if not usuario:
            # Por seguridad, no revelar si el email existe o no
            flash('Si el email está registrado, recibirás instrucciones de recuperación', 'info')
            return render_template("recuperar_password.html")
        
        # Generar token de recuperación
        token = generar_token_recuperacion()
        expiracion = datetime.now() + timedelta(hours=24)
        
        # Guardar token en la base de datos
        exito = database.guardar_token_recuperacion(usuario['id'], token, expiracion)
        
        if exito:
            # En una aplicación real, aquí enviarías un email
            # Por ahora, simulamos el envío
            flash(f'Se han enviado instrucciones de recuperación a {email_limpio}', 'success')
            logger.info(f"Token de recuperación generado para {email_limpio}: {token}")
        else:
            flash('Error al procesar la solicitud. Contacta soporte.', 'danger')
        
        return render_template("recuperar_password.html")
    
    return render_template("recuperar_password.html")

@app.route("/verificar-codigo", methods=['GET', 'POST'])
def verificar_codigo():
    """
    RUTA PARA VERIFICAR CÓDIGO - Paso 2: Verificar código enviado
    """
    if request.method == 'POST':
        email = request.form.get('email')
        codigo = request.form.get('codigo')
        
        # Sanitizar campos
        email_limpio, error_email = sanitizar_email(email)
        codigo_limpio, error_codigo = sanitizar_codigo(codigo)
        
        if error_email:
            flash(error_email, 'danger')
            return render_template("verificar_codigo.html")
        
        if error_codigo:
            flash(error_codigo, 'danger')
            return render_template("verificar_codigo.html")
        
        # Verificar token en la base de datos
        if database is None:
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template("verificar_codigo.html")
        
        token_valido = database.verificar_token_recuperacion(email_limpio, codigo_limpio)
        
        if token_valido and token_valido.get('exito'):
            # Generar token de sesión temporal para cambio de contraseña
            session['recuperacion_token'] = token_valido
            session['recuperacion_email'] = email_limpio
            return redirect(url_for('cambiar_password_recuperacion'))
        else:
            flash('Código inválido o expirado', 'danger')
            return render_template("verificar_codigo.html")
    
    return render_template("verificar_codigo.html")

@app.route("/cambiar-password-recuperacion", methods=['GET', 'POST'])
def cambiar_password_recuperacion():
    """
    RUTA PARA CAMBIAR CONTRASEÑA - Paso 3: Nueva contraseña
    """
    # Verificar que el usuario viene del proceso de recuperación
    if not session.get('recuperacion_token') or not session.get('recuperacion_email'):
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password_nuevo = request.form.get('password_nuevo')
        confirmar_password = request.form.get('confirmar_password')
        
        # Validaciones de contraseña
        if not password_nuevo or not confirmar_password:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        if password_nuevo != confirmar_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        if len(password_nuevo) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        # Validar fortaleza de contraseña
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password_nuevo):
            flash('La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        # Cambiar contraseña
        if database is None:
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        exito = database.cambiar_password_por_token(
            session['recuperacion_email'],
            session['recuperacion_token']['token_id'],
        password_nuevo
    )
    
    if exito:
            # Limpiar sesión de recuperación
            session.pop('recuperacion_token', None)
            session.pop('recuperacion_email', None)
            
            flash('Contraseña cambiada exitosamente. Ya puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
    else:
            flash('Error al cambiar la contraseña. Contacta soporte', 'danger')
            return render_template("cambiar_password_recuperacion.html")
    
    return render_template("cambiar_password_recuperacion.html")

@app.route("/contacto-soporte")
def contacto_soporte():
    """
    RUTA PARA CONTACTO CON SOPORTE - Cuando falla la recuperación automática
    """
    return render_template("contacto_soporte.html")

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

def obtener_negocios_desde_db():
    """
    Obtener negocios desde la base de datos PostgreSQL (donde se guardan los creados desde DevOps)
    Retorna diccionario con estructura {negocio_id: negocio_data} o {} si falla
    """
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT id, nombre, descripcion, direccion, telefono, email, activo,
                       fecha_creacion, fecha_actualizacion
                FROM negocios 
                WHERE activo = TRUE
                ORDER BY nombre
            '''))
            rows = result.fetchall()
            negocios = {}
            for row in rows:
                negocio_id = str(row[0])  # id es la primera columna
                negocios[negocio_id] = {
                    'id': negocio_id,
                    'nombre': row[1] or '',
                    'descripcion': row[2] or '',
                    'direccion': row[3] or '',
                    'telefono': row[4] or '',
                    'email': row[5] or '',
                    'activo': bool(row[6]),
                    'categoria': 'General',  # Valor por defecto
                    'color': '#007bff',  # Color por defecto
                    'fecha_creacion': str(row[7]) if row[7] else '',
                    'fecha_actualizacion': str(row[8]) if row[8] else ''
                }
            if negocios:
                logger.info(f"[DB] ✅ Negocios obtenidos desde PostgreSQL: {len(negocios)}")
            else:
                logger.info("[DB] ℹ️ No hay negocios activos en la base de datos")
            return negocios
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ No se pudieron obtener negocios desde DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}

def obtener_productos_desde_db():
    """
    Obtener productos desde la base de datos PostgreSQL (donde se guardan los creados desde DevOps)
    Retorna lista de productos o [] si falla
    """
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT p.id, p.nombre, p.store as descripcion, p.precio, p.original_price, 
                       p.categoria, p.imagen, p.stock, p.stock_minimo, p.negocio_id, 
                       p.activo, p.destacado, p.fecha_creacion, p.fecha_actualizacion,
                       n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.activo = TRUE
                ORDER BY p.destacado DESC, p.nombre
            '''))
            rows = result.fetchall()
            productos = []
            for row in rows:
                categoria_raw = row[5] or 'General'
                producto = {
                    'id': str(row[0]),
                    'nombre': row[1] or '',
                    'descripcion': row[2] or '',
                    'precio': float(row[3]) if row[3] else 0.0,
                    'precio_original': float(row[4]) if row[4] else float(row[3]) if row[3] else 0.0,
                    'categoria': categoria_raw,
                    'imagen': row[6] or '/static/images/producto-default.jpg',
                    'stock': int(row[7]) if row[7] else 0,
                    'negocio_id': str(row[9]) if row[9] else '1',
                    'negocio': row[14] or 'Sin negocio',
                    'activo': bool(row[10]),
                    'destacado': bool(row[11]),
                    'fecha_creacion': str(row[12]) if row[12] else '',
                    'fecha_actualizacion': str(row[13]) if row[13] else ''
                }
                productos.append(producto)
            if productos:
                logger.info(f"[DB] ✅ Productos obtenidos desde PostgreSQL: {len(productos)}")
            else:
                logger.info("[DB] ℹ️ No hay productos activos en la base de datos")
            return productos
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ No se pudieron obtener productos desde DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def obtener_ofertas_desde_db():
    """
    Obtener ofertas desde la base de datos PostgreSQL (donde se guardan las creadas desde DevOps)
    Retorna diccionario con estructura {negocio: [ofertas]} o {} si falla
    """
    try:
        from sqlalchemy import text
        from datetime import datetime
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT o.id, o.nombre as titulo, o.descripcion, o.descuento, 
                       o.fecha_inicio, o.fecha_fin, o.producto_id, o.negocio_id, 
                       o.activo, o.fecha_creacion, o.fecha_actualizacion,
                       n.nombre as negocio_nombre, p.nombre as producto_nombre
                FROM ofertas o
                LEFT JOIN negocios n ON o.negocio_id = n.id
                LEFT JOIN productos p ON o.producto_id = p.id
                WHERE o.activo = TRUE
                ORDER BY o.fecha_creacion DESC
            '''))
            rows = result.fetchall()
            ofertas_por_negocio = {}
            fecha_actual = datetime.now().date()
            
            for row in rows:
                # Verificar si la oferta está activa por fechas
                fecha_inicio = None
                fecha_fin = None
                if row[4]:  # fecha_inicio
                    try:
                        fecha_inicio = row[4].date() if hasattr(row[4], 'date') else datetime.strptime(str(row[4]), '%Y-%m-%d').date()
                    except:
                        pass
                if row[5]:  # fecha_fin
                    try:
                        fecha_fin = row[5].date() if hasattr(row[5], 'date') else datetime.strptime(str(row[5]), '%Y-%m-%d').date()
                    except:
                        pass
                
                # Verificar si está dentro del rango de fechas
                if fecha_inicio and fecha_actual < fecha_inicio:
                    continue
                if fecha_fin and fecha_actual > fecha_fin:
                    continue
                
                negocio_nombre = row[11] or 'Sin negocio'
                if negocio_nombre not in ofertas_por_negocio:
                    ofertas_por_negocio[negocio_nombre] = []
                
                oferta = {
                    'id': str(row[0]),
                    'titulo': row[1] or '',
                    'descripcion': row[2] or '',
                    'descuento': float(row[3]) if row[3] else 0.0,
                    'producto_id': str(row[6]) if row[6] else '',
                    'producto_nombre': row[12] or '',
                    'negocio_id': str(row[7]) if row[7] else '',
                    'negocio': negocio_nombre,
                    'fecha_inicio': str(row[4]) if row[4] else '',
                    'fecha_fin': str(row[5]) if row[5] else '',
                    'activa': bool(row[8]),
                    'fecha_creacion': str(row[9]) if row[9] else ''
                }
                ofertas_por_negocio[negocio_nombre].append(oferta)
            
            if ofertas_por_negocio:
                total_ofertas = sum(len(ofertas) for ofertas in ofertas_por_negocio.values())
                logger.info(f"[DB] ✅ Ofertas obtenidas desde PostgreSQL: {total_ofertas} en {len(ofertas_por_negocio)} negocios")
            else:
                logger.info("[DB] ℹ️ No hay ofertas activas en la base de datos")
            return ofertas_por_negocio
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ No se pudieron obtener ofertas desde DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}


def obtener_productos():
    """
    Obtener lista de productos
    SIEMPRE desde base de datos (DevOps) - SIN CACHE para datos frescos
    
    RETORNA:
    - Lista de productos activos
    
    NOTA:
    - Esta función SIEMPRE consulta la base de datos directamente
    - No usa cache para asegurar datos frescos desde DevOps
    - Los cambios en DevOps se reflejan inmediatamente
    - Si no hay productos en DB, retorna lista vacía (no fallback a JSON)
    """
    # Obtener SIEMPRE desde base de datos (donde se guardan los creados desde DevOps)
    # Sin cache para asegurar datos actualizados en tiempo real
    productos_db = obtener_productos_desde_db()
    if productos_db:
        logger.info(f"✅ Productos obtenidos desde DevOps (DB): {len(productos_db)}")
        return productos_db
    
    logger.info("ℹ️ No hay productos en la base de datos (DevOps)")
    return []

@app.route("/", methods=['GET', 'HEAD'])
def index():
    """
    RUTA PRINCIPAL - Página de inicio con productos organizados por negocios
    """
    # Obtener parámetro de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    
    # TODOS los datos se obtienen SOLO desde DevOps (base de datos)
    # Obtener negocios desde DevOps (DB)
    negocios_raw = obtener_negocios()
    
    # Obtener productos desde DevOps (DB)
    productos_db = obtener_productos()
    
    # Obtener ofertas desde DevOps (DB) y también intentar desde Ticketera
    ofertas_activas = obtener_ofertas_activas()  # Esta función prioriza DB y luego Ticketera
    
    # Obtener categorías desde DevOps (DB)
    categorias_raw = obtener_categorias()
    
    # Obtener sucursales desde DevOps (DB)
    sucursales_raw = obtener_sucursales()
    
    # Obtener productos destacados desde DevOps (DB)
    productos_destacados = obtener_productos_destacados()
    
    # Manejar negocios - puede ser lista o diccionario
    negocios = {}
    if isinstance(negocios_raw, list):
        logger.info(f"📋 Negocios como lista: {len(negocios_raw)} items")
        # Convertir lista a diccionario
        for negocio in negocios_raw:
            negocio_id = negocio.get('id', negocio.get('nombre', 'sin_id'))
            negocios[negocio_id] = negocio
    elif isinstance(negocios_raw, dict):
        logger.info(f"📋 Negocios como diccionario: {len(negocios_raw)} items")
        negocios = negocios_raw
    else:
        logger.warning("⚠️ Negocios en formato no reconocido, usando diccionario vacío")
        negocios = {}
    
    # Manejar categorías - puede ser lista o diccionario
    categorias = {}
    if isinstance(categorias_raw, list):
        logger.info(f"📋 Categorías como lista: {len(categorias_raw)} items")
        # Convertir lista a diccionario
        for categoria in categorias_raw:
            categoria_id = categoria.get('id', categoria.get('nombre', 'sin_id'))
            categorias[categoria_id] = categoria
    elif isinstance(categorias_raw, dict):
        logger.info(f"📋 Categorías como diccionario: {len(categorias_raw)} items")
        categorias = categorias_raw
    else:
        logger.warning("⚠️ Categorías en formato no reconocido, usando diccionario vacío")
        categorias = {}
    
    # Manejar sucursales - SIEMPRE como diccionario con estructura {negocio_id: {sucursal_id: sucursal_data}}
    sucursales = {}
    if isinstance(sucursales_raw, list):
        logger.info(f"📋 Sucursales como lista: {len(sucursales_raw)} items")
        for sucursal in sucursales_raw:
            negocio_id = sucursal.get('negocio_id', 'sin_negocio')
            sucursal_id = sucursal.get('id', sucursal.get('nombre', 'sin_id'))
            if negocio_id not in sucursales:
                sucursales[negocio_id] = {}
            sucursales[negocio_id][sucursal_id] = sucursal
    elif isinstance(sucursales_raw, dict):
        logger.info(f"📋 Sucursales como diccionario: {len(sucursales_raw)} negocios")
        # Asegurar que cada negocio tenga diccionario de sucursales
        for negocio_id, sucursales_negocio in sucursales_raw.items():
            if isinstance(sucursales_negocio, list):
                sucursales[negocio_id] = {}
                for sucursal in sucursales_negocio:
                    sucursal_id = sucursal.get('id', sucursal.get('nombre', 'sin_id'))
                    sucursales[negocio_id][sucursal_id] = sucursal
            elif isinstance(sucursales_negocio, dict):
                sucursales[negocio_id] = sucursales_negocio
            else:
                sucursales[negocio_id] = {}
    else:
        logger.warning("⚠️ Sucursales en formato no reconocido, usando diccionario vacío")
        sucursales = {}
    
    # Obtener productos por negocio
    productos_por_negocio = {}
    for negocio_id in negocios.keys():
        productos_por_negocio[negocio_id] = obtener_productos_por_negocio(negocio_id)
    
    # Filtrar productos si hay búsqueda
    productos_filtrados = []
    if busqueda:
        todos_productos = datos.get('productos', [])
        productos_filtrados = [
            p for p in todos_productos 
            if busqueda.lower() in p['nombre'].lower() and p.get('activo', True)
        ]
    
    # Para requests HEAD, devolver solo headers sin contenido
    if request.method == 'HEAD':
        response = make_response('', 200)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    
    # Validar que todas las variables sean diccionarios antes del render
    if not isinstance(negocios, dict):
        logger.warning("⚠️ Negocios no es diccionario, convirtiendo...")
        negocios = {}
    
    if not isinstance(categorias, dict):
        logger.warning("⚠️ Categorías no es diccionario, convirtiendo...")
        categorias = {}
    
    if not isinstance(sucursales, dict):
        logger.warning("⚠️ Sucursales no es diccionario, convirtiendo...")
        sucursales = {}
    
    if not isinstance(ofertas_activas, dict):
        logger.warning("⚠️ Ofertas no es diccionario, convirtiendo...")
        ofertas_activas = {}
    
    if not isinstance(productos_por_negocio, dict):
        logger.warning("⚠️ Productos por negocio no es diccionario, convirtiendo...")
        productos_por_negocio = {}
    
    logger.info(f"✅ Datos validados para render: negocios={len(negocios)}, categorias={len(categorias)}, sucursales={len(sucursales)}, ofertas={len(ofertas_activas)}")
    
    return render_template("index.html", 
                         negocios=negocios,
                         categorias=categorias,
                         sucursales=sucursales,
                         ofertas=ofertas_activas,
                         productos_destacados=productos_destacados,
                         productos_por_negocio=productos_por_negocio,
                         busqueda=busqueda,
                         productos_filtrados=productos_filtrados)

@app.route("/productos")
def productos():
    """
    RUTA DE PRODUCTOS - Página de todos los productos
    """
    # Obtener parámetro de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    
    # Cargar datos completos
    datos = cargar_datos_completos()
    productos = datos.get('productos', [])
    categorias = datos.get('categorias', {})
    
    # Filtrar productos activos
    productos_activos = [p for p in productos if p.get('activo', True)]
    
    # Filtrar por búsqueda si existe
    if busqueda:
        productos_activos = [
            p for p in productos_activos 
            if busqueda.lower() in p['nombre'].lower()
        ]
    
    return render_template("productos.html", 
                         productos=productos_activos,
                         categorias=categorias,
                         busqueda=busqueda)

@app.route("/negocio/<negocio_id>")
def ver_negocio(negocio_id):
    """
    RUTA PARA VER PRODUCTOS DE UN NEGOCIO ESPECÍFICO
    
    PARÁMETROS:
    - negocio_id: ID del negocio a mostrar
    
    MANTENIMIENTO:
    - Para agregar nuevos negocios: editar productos.json sección "negocios"
    - Para cambiar información del negocio: modificar datos en productos.json
    - Para agregar productos al negocio: agregar en productos.json con negocio correcto
    """
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    sucursales = datos.get('sucursales', {})
    
    if negocio_id not in negocios:
        flash('Negocio no encontrado', 'danger')
        return redirect(url_for('index'))
    
    negocio = negocios[negocio_id]
    productos = obtener_productos_por_negocio(negocio_id)
    sucursales_negocio = sucursales.get(negocio_id, {})
    
    return render_template("negocio.html", 
                         negocio=negocio,
                         productos=productos,
                         categorias=categorias,
                         sucursales=sucursales_negocio)

@app.route("/categoria/<categoria_id>")
def ver_categoria(categoria_id):
    """
    RUTA PARA VER PRODUCTOS DE UNA CATEGORÍA ESPECÍFICA
    
    PARÁMETROS:
    - categoria_id: ID de la categoría a mostrar
    
    MANTENIMIENTO:
    - Para agregar categorías: editar productos.json sección "categorias"
    - Para cambiar iconos: modificar campo "icono" en la categoría
    - Para agregar productos a categoría: asignar categoria_id correcto en productos.json
    """
    datos = cargar_datos_completos()
    categorias = datos.get('categorias', {})
    negocios = datos.get('negocios', {})
    
    if categoria_id not in categorias:
        flash('Categoría no encontrada', 'danger')
        return redirect(url_for('index'))
    
    categoria = categorias[categoria_id]
    productos = datos.get('productos', [])
    productos_categoria = [p for p in productos if p.get('categoria') == categoria_id and p.get('activo', True)]
    
    return render_template("categoria.html", 
                         categoria=categoria,
                         productos=productos_categoria,
                         negocios=negocios)

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - redirige a la página principal"""
    return redirect(url_for('index'))

@app.route("/agregar_al_carrito", methods=['POST'])
def agregar_al_carrito():
    """
    RUTA PARA AGREGAR PRODUCTOS AL CARRITO
    """
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if not producto_id:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Producto no especificado'}), 400
        flash('Producto no especificado', 'danger')
        return redirect(url_for('index'))
    
    # Inicializar carrito si no existe
    if 'carrito' not in session:
        session['carrito'] = {}
    
    # Agregar o actualizar cantidad
    if producto_id in session['carrito']:
        session['carrito'][producto_id] += cantidad
    else:
        session['carrito'][producto_id] = cantidad
    
    # Guardar cambios en la sesión
    session.modified = True
    
    logger.info(f"Producto agregado al carrito: {producto_id} x{cantidad}")
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        return jsonify({
            'success': True,
            'mensaje': f'¡Producto agregado al carrito!',
            'carrito_count': len(session['carrito']),
            'producto_id': producto_id,
            'cantidad': cantidad
        })
    
    # Si es una petición normal, redirigir
    flash(f'¡Producto agregado al carrito!', 'success')
    return redirect(url_for('index'))

@app.route("/carrito")
def carrito():
    """
    RUTA PARA VER EL CARRITO DE COMPRAS
    Muestra todos los productos en el carrito con sus cantidades
    """
    try:
        carrito_items = []
        total = 0
        
        # Verificar que la sesión existe y tiene carrito
        if not session:
            session['carrito'] = {}
        
        if 'carrito' in session and session['carrito']:
            for producto_id, cantidad in session['carrito'].items():
                try:
                    # Validar que cantidad sea un número válido
                    cantidad = int(cantidad) if cantidad else 0
                    if cantidad <= 0:
                        continue
                        
                    producto = obtener_producto_por_id(producto_id)
                    if producto and producto.get('activo', True):
                        # Validar que el producto tenga precio
                        precio = float(producto.get('precio', 0))
                        if precio > 0:
                            subtotal = precio * cantidad
                            carrito_items.append({
                                'producto': producto,
                                'cantidad': cantidad,
                                'subtotal': subtotal
                            })
                            total += subtotal
                        else:
                            logger.warning(f"Producto {producto_id} sin precio válido")
                    else:
                        logger.warning(f"Producto ID {producto_id} no encontrado o inactivo")
                        # Remover producto del carrito si no existe
                        if producto_id in session['carrito']:
                            del session['carrito'][producto_id]
                            session.modified = True
                except Exception as e:
                    logger.error(f"Error procesando producto {producto_id}: {e}")
                    continue
        
        logger.info(f"Carrito cargado: {len(carrito_items)} items, total: ${total}")
        return render_template("carrito.html", carrito_items=carrito_items, total=total)
        
    except Exception as e:
        logger.error(f"Error en función carrito: {e}")
        flash('Error al cargar el carrito. Intente nuevamente.', 'error')
        return render_template("carrito.html", carrito_items=[], total=0)

@app.route("/actualizar_cantidad", methods=['POST'])
def actualizar_cantidad():
    """
    RUTA PARA ACTUALIZAR CANTIDADES EN EL CARRITO
    """
    producto_id = request.form.get('producto_id')
    nueva_cantidad = int(request.form.get('cantidad', 0))
    
    if nueva_cantidad <= 0:
        # Eliminar producto del carrito
        if 'carrito' in session and producto_id in session['carrito']:
            # Obtener nombre del producto para el mensaje
            producto = obtener_producto_por_id(producto_id)
            nombre_producto = producto['nombre'] if producto else f'Producto {producto_id}'
            del session['carrito'][producto_id]
            session.modified = True
            flash(f'{nombre_producto} eliminado del carrito', 'info')
    else:
        # Actualizar cantidad
        if 'carrito' in session:
            # Obtener nombre del producto para el mensaje
            producto = obtener_producto_por_id(producto_id)
            nombre_producto = producto['nombre'] if producto else f'Producto {producto_id}'
            session['carrito'][producto_id] = nueva_cantidad
            session.modified = True
            flash(f'Cantidad de {nombre_producto} actualizada', 'success')
    
    return redirect(url_for('carrito'))

@app.route("/vaciar_carrito")
def vaciar_carrito():
    """
    RUTA PARA VACIAR EL CARRITO DE COMPRAS
    """
    session.pop('carrito', None)
    flash('Carrito vaciado', 'info')
    return redirect(url_for('carrito'))

# ==========================================
# RUTAS DEL SISTEMA DE PAGO
# ==========================================

@app.route("/checkout")
def checkout():
    """
    RUTA PARA EL PROCESO DE PAGO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('carrito'):
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))
    
    carrito_items = []
    total = 0
    
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template("checkout.html", carrito_items=carrito_items, total=total)

@app.route("/procesar_pago", methods=['POST'])
def procesar_pago():
    """
    RUTA PARA PROCESAR EL PAGO CON VALIDACIÓN DE STOCK
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('carrito'):
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))
    
    # Obtener datos del formulario
    metodo_pago = request.form.get('metodo_pago')
    direccion = request.form.get('direccion')
    notas = request.form.get('notas')
    
    # Validaciones básicas
    if not direccion:
        flash('Por favor ingresa una dirección de entrega', 'danger')
        return redirect(url_for('checkout'))
    
    # Crear el pedido
    numero_pedido = generar_numero_pedido()
    usuario = obtener_usuario_actual()
    
    carrito_items = []
    total = 0
    
    # Preparar items del carrito con información completa
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'producto_id': producto['id'],
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    # VALIDAR STOCK ANTES DE PROCESAR LA COMPRA
    items_para_validar = [
        {
            'producto_id': item['producto_id'],
            'cantidad': item['cantidad'],
            'producto': item['producto']
        }
        for item in carrito_items
    ]
    
    stock_valido, errores_stock, productos_validos = database.validar_stock_carrito(items_para_validar)
    
    if not stock_valido:
        # Mostrar errores de stock y redirigir al carrito
        mensaje_error = 'No se puede procesar la compra debido a problemas de stock:\n' + '\n'.join(errores_stock)
        flash(mensaje_error, 'danger')
        logger.warning(f"⚠️ Compra rechazada por stock insuficiente: {errores_stock}")
        return redirect(url_for('carrito'))
    
    # Guardar pedido en la base de datos
    pedido_id = database.guardar_pedido(
        usuario_id=usuario['id'],
        numero_pedido=numero_pedido,
        total=total,
        metodo_pago=metodo_pago,
        direccion_entrega=direccion,
        notas=notas
    )
    
    if pedido_id:
        # Guardar items del pedido
        items_db = []
        for item in carrito_items:
            items_db.append({
                'producto_id': item['producto']['id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['producto']['precio'],
                'subtotal': item['subtotal']
            })
        
        database.guardar_items_pedido(pedido_id, items_db)
        
        # ACTUALIZAR STOCK DESPUÉS DE GUARDAR EL PEDIDO
        stock_actualizado, resultados_stock, errores_stock = database.actualizar_stock_carrito(items_para_validar)
        
        if not stock_actualizado:
            # Si falla la actualización de stock, registrar error pero no revertir el pedido
            logger.error(f"❌ Error actualizando stock después de la compra: {errores_stock}")
            # El pedido ya está guardado, pero el stock no se actualizó correctamente
            flash('Pedido procesado, pero hubo un problema actualizando el stock. Contacta al administrador.', 'warning')
        else:
            logger.info(f"✅ Stock actualizado correctamente para pedido {numero_pedido}")
    
    # Limpiar carrito
    session.pop('carrito', None)
    
    if pedido_id:
        # ENVIAR PEDIDO AUTOMÁTICAMENTE A LA TICKETERA
        enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas)
        
        flash(f'¡Pedido confirmado! Número: {numero_pedido}', 'success')
        return redirect(url_for('confirmacion_pedido', numero_pedido=numero_pedido))
    else:
        flash('Error al procesar el pedido. Intenta nuevamente.', 'danger')
        return redirect(url_for('checkout'))

@app.route("/confirmacion/<numero_pedido>")
def confirmacion_pedido(numero_pedido):
    """
    RUTA PARA MOSTRAR LA CONFIRMACIÓN DEL PEDIDO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver esta página', 'warning')
        return redirect(url_for('login'))
    
    # pedido = pedidos.get(numero_pedido)
    # if not pedido:
    #     flash('Pedido no encontrado', 'danger')
    #     return redirect(url_for('index'))
    
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    hora_actual = datetime.now().strftime("%H:%M")
    
    return render_template("confirmacion.html", 
                         numero_pedido=numero_pedido,
                         fecha_actual=fecha_actual,
                         hora_actual=hora_actual)

@app.route("/mis_pedidos")
def mis_pedidos():
    """
    RUTA PARA VER HISTORIAL DE PEDIDOS
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver tus pedidos', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Obtener pedidos del usuario desde la base de datos
    pedidos = database.obtener_pedidos_usuario(usuario['id'])
    
    return render_template("mis_pedidos.html", pedidos=pedidos, usuario=usuario)

@app.route("/repetir_pedido/<int:pedido_id>")
def repetir_pedido(pedido_id):
    """
    RUTA PARA REPETIR UN PEDIDO ANTERIOR
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para repetir pedidos', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Repetir pedido
    exito, resultado = database.repetir_pedido(pedido_id, usuario['id'])
    
    if exito:
        flash(f'Pedido repetido exitosamente. Nuevo número: {resultado}', 'success')
        return redirect(url_for('confirmacion_pedido', numero_pedido=resultado))
    else:
        flash(f'Error al repetir pedido: {resultado}', 'danger')
        return redirect(url_for('mis_pedidos'))

@app.route("/ver_pedido/<int:pedido_id>")
def ver_pedido(pedido_id):
    """
    RUTA PARA VER DETALLES DE UN PEDIDO ESPECÍFICO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver pedidos', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Obtener pedido completo
    pedido = database.obtener_pedido_completo(pedido_id)
    
    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('mis_pedidos'))
    
    # Asegurar que items sea una lista
    if 'items' not in pedido or not isinstance(pedido['items'], list):
        pedido['items'] = []
    
    return render_template("ver_pedido.html", pedido=pedido, usuario=usuario, pedido_id=pedido_id)

@app.route("/test")
def test():
    """
    RUTA DE PRUEBA - Para verificar que la app funciona
    Esta función se ejecuta cuando alguien visita http://localhost:5000/test
    """
    return jsonify({
        "status": "ok",
        "message": "Belgrano Ahorro está funcionando correctamente",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/healthz")
def healthz():
    """Endpoint de health check para Render"""
    return "ok", 200

@app.route("/api/actualizar-db", methods=['POST'])
def actualizar_base_datos_produccion():
    """Endpoint para actualizar la base de datos en producción"""
    try:
        # Verificar API key para seguridad (usar la variable de entorno configurada)
        api_key = request.headers.get('X-API-Key')
        if api_key != BELGRANO_AHORRO_API_KEY:
            return jsonify({'error': 'API key inválida'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar columnas existentes
        cursor.execute("PRAGMA table_info(pedidos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Agregar columnas si no existen
        columnas_a_agregar = [
            ('ticket_confirmado', 'INTEGER DEFAULT 0'),
            ('ticket_estado', 'VARCHAR(20) DEFAULT "pendiente"'),
            ('fecha_confirmacion', 'DATETIME')
        ]
        
        columnas_agregadas = []
        for columna, tipo in columnas_a_agregar:
            if columna not in columns:
                cursor.execute(f'ALTER TABLE pedidos ADD COLUMN {columna} {tipo}')
                columnas_agregadas.append(columna)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Base de datos actualizada exitosamente',
            'columnas_agregadas': columnas_agregadas,
            'columnas_existentes': columns
        })
        
    except Exception as e:
        return jsonify({'error': f'Error actualizando base de datos: {str(e)}'}), 500

@app.route("/api/pedido/confirmar/<numero_pedido>", methods=['POST'])
def confirmar_ticket(numero_pedido):
    """Endpoint para confirmar que un ticket fue creado exitosamente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        ticket_id = data.get('ticket_id')
        estado = data.get('estado', 'confirmado')
        
        # Actualizar pedido con confirmación
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pedidos 
            SET ticket_confirmado = 1,
                ticket_estado = ?,
                fecha_confirmacion = CURRENT_TIMESTAMP
            WHERE numero_pedido = ?
        """, (estado, numero_pedido))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Ticket {numero_pedido} confirmado exitosamente',
            'ticket_id': ticket_id,
            'estado': estado
        })
        
    except Exception as e:
        return jsonify({'error': f'Error confirmando ticket: {str(e)}'}), 500

@app.route("/contacto", methods=['GET', 'POST'])
def contacto():
    """
    RUTA DE CONTACTO - Página de contacto y formulario
    """
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        asunto = request.form.get('asunto')
        mensaje = request.form.get('mensaje')
        
        # Aquí podrías enviar el email o guardar en base de datos
        logger.info(f"Mensaje de contacto recibido de {nombre} ({email}): {asunto}")
        
        flash('¡Gracias por tu mensaje! Te responderemos pronto.', 'success')
        return redirect(url_for('contacto'))
    
    return render_template("contacto.html")

@app.route("/sobre-nosotros")
def sobre_nosotros():
    """
    RUTA SOBRE NOSOTROS - Página con información de la empresa
    """
    return render_template("sobre_nosotros.html")

# ==========================================
# SECCIÓN COMERCIANTES (RUTAS BÁSICAS)
# ==========================================

@app.route("/comerciantes")
def comerciantes_home():
    """
    Panel principal de Comerciantes con accesos rápidos.
    Usa los flujos existentes (carrito, checkout, pedidos) para asegurar funcionalidad.
    """
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    return render_template("comerciantes/dashboard.html", negocios=negocios, categorias=categorias)

@app.route("/comerciantes/pedidos")
def comerciantes_pedidos():
    """Atajo a los pedidos del usuario desde el panel de comerciantes."""
    return redirect(url_for('mis_pedidos'))

@app.route("/comerciantes/carrito")
def comerciantes_carrito():
    """Atajo al carrito normal desde el panel de comerciantes."""
    return redirect(url_for('carrito'))

@app.route("/comerciantes/checkout")
def comerciantes_checkout():
    """Atajo al checkout normal desde el panel de comerciantes."""
    return redirect(url_for('checkout'))

@app.route("/comerciantes/confirmacion/<numero_pedido>")
def comerciantes_confirmacion(numero_pedido):
    """Atajo a la confirmación de pedido normal desde el panel de comerciantes."""
    return redirect(url_for('confirmacion_pedido', numero_pedido=numero_pedido))

# ==========================================
# REGISTRO Y LOGIN DE COMERCIANTES
# ==========================================

@app.route("/comerciantes/registro", methods=['GET', 'POST'])
def registro_comerciante():
    """Registro específico para comerciantes"""
    if request.method == 'POST':
        # Datos personales
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        
        # Datos comerciales
        nombre_negocio = request.form.get('nombre_negocio')
        cuit = request.form.get('cuit')
        direccion_comercial = request.form.get('direccion_comercial')
        telefono_comercial = request.form.get('telefono_comercial')
        tipo_negocio = request.form.get('tipo_negocio')
        
        # Validaciones
        if not all([nombre, apellido, email, password, nombre_negocio]):
            flash('❌ Por favor completa todos los campos obligatorios', 'danger')
            return render_template("comerciantes/registro.html")
        
        # Crear usuario con rol comerciante
        resultado = database.crear_usuario(nombre, apellido, email, password, telefono, direccion, 'comerciante')
        
        if resultado['exito']:
            # Crear perfil de comerciante
            comerciante_resultado = database.crear_comerciante(
                resultado['usuario_id'], 
                nombre_negocio, 
                cuit, 
                direccion_comercial, 
                telefono_comercial, 
                tipo_negocio
            )
            
            if comerciante_resultado['exito']:
                flash(f'✅ ¡Comerciante registrado exitosamente! Bienvenido {nombre_negocio}, ya puedes iniciar sesión.', 'success')
                return redirect(url_for('login_comerciante'))
            else:
                flash(f'❌ Error al crear perfil comercial: {comerciante_resultado["mensaje"]}', 'danger')
        else:
            flash(f'❌ Error al crear usuario: {resultado["mensaje"]}', 'danger')
    
    return render_template("comerciantes/registro.html")

@app.route("/comerciantes/login", methods=['GET', 'POST'])
def login_comerciante():
    """Login específico para comerciantes"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('❌ Por favor ingresa email y contraseña', 'danger')
            return render_template("comerciantes/login.html")
        
        resultado = database.verificar_usuario(email, password)
        
        if resultado['exito']:
            usuario = resultado['usuario']
            
            # Verificar que sea comerciante
            if usuario.get('rol') != 'comerciante':
                flash('❌ Esta cuenta no está registrada como comerciante', 'danger')
                return render_template("comerciantes/login.html")
            
            # Obtener información del comerciante
            comerciante = database.obtener_comerciante_por_usuario(usuario['id'])
            
            if comerciante:
                session['usuario_id'] = usuario['id']
                session['usuario_nombre'] = usuario['nombre']
                session['usuario_email'] = usuario['email']
                session['usuario_rol'] = 'comerciante'
                session['comerciante_id'] = comerciante['id']
                session['nombre_negocio'] = comerciante['nombre_negocio']
                
                flash(f'✅ ¡Bienvenido, {comerciante["nombre_negocio"]}! Has iniciado sesión como comerciante', 'success')
                return redirect(url_for('comerciantes_home'))
            else:
                flash('❌ Error al cargar información del comerciante', 'danger')
        else:
            flash(f'❌ {resultado["mensaje"]}', 'danger')
    
    return render_template("comerciantes/login.html")

# ==========================================
# GESTIÓN DE PAQUETES DE COMERCIANTES
# ==========================================

@app.route("/comerciantes/paquetes")
def comerciantes_paquetes():
    """Gestión de paquetes de comerciantes"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    comerciante_id = session.get('comerciante_id')
    paquetes = database.obtener_paquetes_comerciante(comerciante_id)
    
    return render_template("comerciantes/paquetes.html", paquetes=paquetes)

@app.route("/comerciantes/paquetes/crear", methods=['GET', 'POST'])
def crear_paquete():
    """Crear nuevo paquete"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    if request.method == 'POST':
        nombre_paquete = request.form.get('nombre_paquete')
        descripcion = request.form.get('descripcion')
        frecuencia = request.form.get('frecuencia', 'mensual')
        
        if not nombre_paquete:
            flash('El nombre del paquete es obligatorio', 'danger')
            return render_template("comerciantes/crear_paquete.html")
        
        comerciante_id = session.get('comerciante_id')
        resultado = database.crear_paquete_comerciante(comerciante_id, nombre_paquete, descripcion, frecuencia)
        
        if resultado['exito']:
            flash(f'Paquete "{nombre_paquete}" creado exitosamente', 'success')
            return redirect(url_for('editar_paquete', paquete_id=resultado['paquete_id']))
        else:
            flash(f'Error al crear paquete: {resultado["mensaje"]}', 'danger')
    
    return render_template("comerciantes/crear_paquete.html")

@app.route("/comerciantes/paquetes/<int:paquete_id>/editar")
def editar_paquete(paquete_id):
    """Editar paquete existente"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    # Obtener datos completos
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    sucursales = datos.get('sucursales', {})
    
    # Obtener paquete
    comerciante_id = session.get('comerciante_id')
    paquetes = database.obtener_paquetes_comerciante(comerciante_id)
    paquete = next((p for p in paquetes if p['id'] == paquete_id), None)
    
    if not paquete:
        flash('Paquete no encontrado', 'danger')
        return redirect(url_for('comerciantes_paquetes'))
    
    return render_template("comerciantes/editar_paquete.html", 
                         paquete=paquete, 
                         negocios=negocios,
                         sucursales=sucursales)

@app.route("/comerciantes/paquetes/<int:paquete_id>/agregar_producto", methods=['POST'])
def agregar_producto_paquete(paquete_id):
    """Agregar producto a un paquete"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        return jsonify({'exito': False, 'mensaje': 'No autorizado'})
    
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if not producto_id or cantidad <= 0:
        return jsonify({'exito': False, 'mensaje': 'Datos inválidos'})
    
    resultado = database.agregar_producto_a_paquete(paquete_id, producto_id, cantidad)
    return jsonify(resultado)

@app.route("/api/productos_por_sucursal", methods=['POST'])
def api_productos_por_sucursal():
    """API para obtener productos de una sucursal específica"""
    if not usuario_logueado():
        return jsonify({'exito': False, 'mensaje': 'No autorizado'})
    
    data = request.get_json()
    negocio_id = data.get('negocio_id')
    sucursal_id = data.get('sucursal_id')
    
    if not negocio_id or not sucursal_id:
        return jsonify({'exito': False, 'mensaje': 'Datos incompletos'})
    
    productos = obtener_productos_por_sucursal(negocio_id, sucursal_id)
    
    return jsonify({
        'exito': True,
        'productos': productos
    })

@app.route("/comerciantes/paquetes/<int:paquete_id>/procesar", methods=['POST'])
def procesar_paquete(paquete_id):
    """Procesar pedido automático de un paquete"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    resultado = database.procesar_pedido_automatico_paquete(paquete_id)
    
    if resultado['exito']:
        flash(f'Pedido automático procesado: {resultado["numero_pedido"]}', 'success')
        return redirect(url_for('comerciantes_confirmacion', numero_pedido=resultado['numero_pedido']))
    else:
        flash(f'Error al procesar pedido: {resultado["mensaje"]}', 'danger')
        return redirect(url_for('comerciantes_paquetes'))

@app.route("/ticketera")
def ticketera():
    """
    RUTA PARA ACCEDER A LA TICKETERA
    Redirige a la aplicación de tickets
    """
    # En desarrollo usa localhost, en producción usa la URL de Render
    ticketera_url = os.environ.get('TICKETERA_URL', 'http://localhost:5001')
    return redirect(ticketera_url)

@app.route("/admin")
@admin_required
def admin():
    """
    RUTA PARA ACCEDER AL PANEL DE ADMINISTRACIÓN
    Redirige a la ticketera con credenciales de admin
    """
    # Usar variable global configurada
    return redirect(TICKETERA_URL)

# ==========================================
# FUNCIÓN DE INTEGRACIÓN CON BELGRANO TICKETS
# ==========================================

def enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas):
    """
    Enviar pedido automáticamente a la Ticketera vía API con conexión sólida
    Usa la versión mejorada para mayor confiabilidad
    
    PARÁMETROS:
    - numero_pedido: número único del pedido
    - usuario: datos del usuario que hizo el pedido
    - carrito_items: lista de productos en el carrito
    - total: monto total del pedido
    - metodo_pago: método de pago seleccionado
    - direccion: dirección de entrega
    - notas: notas adicionales del pedido
    
    RETORNA:
    - dict con datos del ticket creado si se envió exitosamente, None en caso contrario
    """
    # Usar la versión mejorada para mayor confiabilidad
    return enviar_pedido_a_ticketera_mejorado(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas)

def actualizar_pedido_con_ticket(numero_pedido, ticket_response):
    """
    Actualizar la base de datos de Ahorro con la información del ticket creado
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Actualizar pedido con información del ticket
        cursor.execute("""
            UPDATE pedidos 
            SET ticket_id = ?, 
                ticket_estado = ?, 
                ticket_fecha_creacion = ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE numero = ?
        """, (
            ticket_response.get('ticket_id'),
            ticket_response.get('estado', 'pendiente'),
            ticket_response.get('fecha_creacion'),
            numero_pedido
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Pedido {numero_pedido} actualizado con información del ticket")
        
    except Exception as e:
        logger.warning(f"⚠️ Error actualizando pedido con ticket: {e}")

def enviar_pedido_a_ticketera_mejorado(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas=None):
    """
    Enviar pedido a la Ticketera con conexión sólida y sin pérdida
    Versión mejorada con mejor manejo de errores y reintentos
    """
    try:
        # Obtener URL de la API desde variables de entorno
        api_url = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com')
        if not api_url.endswith('/api/tickets/recibir'):
            api_url = f"{api_url.rstrip('/')}/api/tickets/recibir"
        
        # Obtener datos del usuario con validación
        nombre_completo = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
        if not nombre_completo:
            nombre_completo = usuario.get('email', 'Cliente')
        
        # Obtener datos auxiliares para enriquecer información de productos
        negocios_dict = {}
        try:
            negocios_raw = obtener_negocios()
            if isinstance(negocios_raw, list):
                negocios_dict = {str(n.get('id', '')): n for n in negocios_raw}
            elif isinstance(negocios_raw, dict):
                negocios_dict = negocios_raw
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo negocios para ticket: {e}")
        
        sucursales_dict = {}
        try:
            sucursales_raw = obtener_sucursales()
            if isinstance(sucursales_raw, list):
                sucursales_dict = {str(s.get('id', '')): s for s in sucursales_raw}
            elif isinstance(sucursales_raw, dict):
                sucursales_dict = sucursales_raw
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo sucursales para ticket: {e}")
        
        categorias_dict = {}
        try:
            categorias_raw = obtener_categorias()
            if isinstance(categorias_raw, list):
                categorias_dict = {str(c.get('id', '')): c for c in categorias_raw}
            elif isinstance(categorias_raw, dict):
                categorias_dict = categorias_raw
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo categorías para ticket: {e}")
        
        # Preparar lista de productos con estructura completa para la Ticketera
        productos_lista = []
        logger.info(f"🔍 Procesando {len(carrito_items)} items del carrito para Ticketera...")
        
        for idx, item in enumerate(carrito_items, 1):
            try:
                producto = item.get('producto', {})
                if not producto:
                    logger.warning(f"⚠️ Item {idx} del carrito no tiene 'producto', saltando...")
                    continue
                
                # Validar que el item tenga cantidad y subtotal
                cantidad = int(item.get('cantidad', 0))
                subtotal = float(item.get('subtotal', 0))
                
                if cantidad <= 0:
                    logger.warning(f"⚠️ Item {idx} tiene cantidad inválida ({cantidad}), saltando...")
                    continue
                
                # Obtener información del negocio
                negocio_nombre = producto.get('negocio', 'Negocio no especificado')
                if producto.get('negocio_id'):
                    negocio_data = negocios_dict.get(str(producto['negocio_id']))
                    if negocio_data:
                        negocio_nombre = negocio_data.get('nombre', negocio_nombre)
                
                # Obtener información de la sucursal (usar la primera disponible)
                sucursal_nombre = "Sucursal no especificada"
                if producto.get('sucursales') and len(producto['sucursales']) > 0:
                    sucursal_id = producto['sucursales'][0]
                    sucursal_data = sucursales_dict.get(str(sucursal_id))
                    if sucursal_data:
                        sucursal_nombre = sucursal_data.get('nombre', sucursal_id)
                
                # Obtener información de la categoría
                categoria_nombre = producto.get('categoria', 'Sin categoría')
                if producto.get('categoria_id'):
                    categoria_data = categorias_dict.get(str(producto['categoria_id']))
                    if categoria_data:
                        categoria_nombre = categoria_data.get('nombre', categoria_nombre)
                elif producto.get('categoria'):
                    # Si categoria es un string, usarlo directamente
                    if isinstance(producto.get('categoria'), str):
                        categoria_nombre = producto.get('categoria')
                    else:
                        categoria_data = categorias_dict.get(str(producto['categoria']))
                        if categoria_data:
                            categoria_nombre = categoria_data.get('nombre', categoria_nombre)
                
                # Construir objeto producto para Ticketera
                producto_ticket = {
                    'id': str(producto.get('id', f'producto_{idx}')),
                    'nombre': producto.get('nombre', 'Producto sin nombre'),
                    'precio': float(producto.get('precio', 0)),
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'sucursal': sucursal_nombre,
                    'negocio': negocio_nombre,
                    'categoria': categoria_nombre,
                    'descripcion': producto.get('descripcion', producto.get('store', 'Sin descripción')),
                    'stock': int(producto.get('stock', 0)),
                    'destacado': bool(producto.get('destacado', False))
                }
                
                productos_lista.append(producto_ticket)
                logger.debug(f"   ✅ Producto {idx} procesado: {producto_ticket['nombre']} x{producto_ticket['cantidad']}")
                
            except Exception as e:
                logger.error(f"❌ Error procesando item {idx} del carrito: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"✅ {len(productos_lista)} productos procesados correctamente para Ticketera")
        
        # Preparar datos para enviar a la API con validación
        ticket_data = {
            "numero": numero_pedido,
            "cliente_nombre": nombre_completo,
            "cliente_direccion": direccion or "Dirección no especificada",
            "cliente_telefono": usuario.get('telefono', ''),
            "cliente_email": usuario['email'],
            "productos": productos_lista,
            "total": float(total),  # Asegurar que sea float
            "metodo_pago": metodo_pago,
            "indicaciones": notas or 'Sin indicaciones especiales',
            "estado": "pendiente",
            "prioridad": "normal",
            "tipo_cliente": "cliente",
            "fecha_creacion": datetime.now().isoformat(),
            "origen": "belgrano_ahorro"
        }
        
        # Validar datos antes de enviar
        if not ticket_data["cliente_nombre"] or not ticket_data["cliente_email"]:
            logger.error("❌ Datos de cliente incompletos")
            return None
        
        if not productos_lista:
            logger.error("❌ No hay productos en el carrito")
            return None
        
        # Log de datos que se van a enviar
        logger.info(f"📤 Enviando pedido a Ticketera:")
        logger.info(f"   URL: {api_url}")
        logger.info(f"   Pedido: {numero_pedido}")
        logger.info(f"   Cliente: {nombre_completo}")
        logger.info(f"   Total: ${total}")
        logger.info(f"   Productos: {len(productos_lista)} items")
        
        # Log detallado de cada producto que se envía
        for idx, producto in enumerate(productos_lista, 1):
            logger.info(f"   Producto {idx}: {producto.get('nombre', 'Sin nombre')} - Cantidad: {producto.get('cantidad', 0)} - Precio: ${producto.get('precio', 0)} - Subtotal: ${producto.get('subtotal', 0)}")
        
        # Log del payload completo (solo estructura, no datos sensibles)
        logger.debug(f"📋 Estructura del ticket_data:")
        logger.debug(f"   - numero: {ticket_data.get('numero')}")
        logger.debug(f"   - cliente_nombre: {ticket_data.get('cliente_nombre')}")
        logger.debug(f"   - cliente_email: {ticket_data.get('cliente_email')}")
        logger.debug(f"   - total: {ticket_data.get('total')}")
        logger.debug(f"   - productos (count): {len(ticket_data.get('productos', []))}")
        logger.debug(f"   - metodo_pago: {ticket_data.get('metodo_pago')}")
        logger.debug(f"   - origen: {ticket_data.get('origen')}")
        
        # Headers mejorados
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'User-Agent': 'BelgranoAhorro/1.0.0',
            'X-Request-ID': f"{numero_pedido}-{int(time.time())}",
            'X-Origin': 'belgrano_ahorro'
        }

        # Configuración de reintentos mejorada
        max_retries = 5
        backoff_seconds = [1, 2, 4, 8, 16]  # Backoff exponencial más agresivo
        last_response = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Intento {attempt + 1}/{max_retries} enviando a Ticketera...")
                
                # Verificar conectividad antes de enviar
                if attempt > 0:
                    try:
                        health_check = requests.get(f"{api_url.replace('/api/tickets', '/healthz')}", timeout=5)
                        if health_check.status_code != 200:
                            logger.warning(f"⚠️ Health check falló en intento {attempt + 1}")
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo verificar health check en intento {attempt + 1}: {e}")
                
                # Log del payload completo antes de enviar (solo en debug)
                import json as json_module
                logger.debug(f"📦 Payload completo a enviar a Ticketera:")
                logger.debug(json_module.dumps(ticket_data, indent=2, ensure_ascii=False))
                
                response = requests.post(
                    api_url,
                    json=ticket_data,
                    headers=headers,
                    timeout=20  # Timeout aumentado
                )
                last_response = response
                
                # Log de la respuesta recibida
                logger.info(f"📥 Respuesta de Ticketera: Status {response.status_code}")
                if response.status_code in (200, 201):
                    try:
                        response_data = response.json()
                        logger.info(f"   ✅ Ticket creado: {response_data.get('ticket_id', 'N/A')}")
                        logger.info(f"   ✅ Productos recibidos: {len(response_data.get('productos', []))} items")
                        # Log detallado de productos en la respuesta
                        productos_respuesta = response_data.get('productos', [])
                        if productos_respuesta:
                            logger.info(f"   📦 Productos en respuesta de Ticketera:")
                            for idx, prod in enumerate(productos_respuesta, 1):
                                logger.info(f"      {idx}. {prod.get('nombre', 'Sin nombre')} x{prod.get('cantidad', 0)}")
                        else:
                            logger.warning(f"   ⚠️ No se recibieron productos en la respuesta de Ticketera")
                    except Exception as e:
                        logger.warning(f"   ⚠️ No se pudo parsear respuesta JSON: {e}")
                        logger.warning(f"   ⚠️ Respuesta raw: {response.text[:200]}")
                
                if response.status_code in (200, 201):
                    logger.info(f"✅ Petición exitosa en intento {attempt + 1}")
                    break
                elif response.status_code == 401:
                    logger.error(f"❌ Error de autenticación (API Key inválida)")
                    return None
                elif response.status_code == 400:
                    logger.error(f"❌ Error en datos enviados: {response.text}")
                    return None
                else:
                    logger.warning(f"⚠️ Status {response.status_code} en intento {attempt + 1}")
                    logger.error(f"   Response: {response.text[:200]}...")
                    
            except requests.exceptions.Timeout:
                last_error = f"Timeout en intento {attempt + 1}"
                logger.warning(f"⏰ {last_error}")
            except requests.exceptions.ConnectionError:
                last_error = f"Error de conexión en intento {attempt + 1}"
                logger.warning(f"🔌 {last_error}")
            except requests.exceptions.RequestException as e:
                last_error = f"Error de request en intento {attempt + 1}: {str(e)}"
                logger.warning(f"🌐 {last_error}")
            except Exception as e:
                last_error = f"Error inesperado en intento {attempt + 1}: {str(e)}"
                logger.error(f"❌ {last_error}")
            
            # Backoff exponencial
            if attempt < max_retries - 1:
                wait_time = backoff_seconds[attempt]
                logger.info(f"⏳ Esperando {wait_time}s antes del siguiente intento...")
                time.sleep(wait_time)
        
        # Procesar resultado final
        if last_response is not None and last_response.status_code in (200, 201):
            try:
                ticket_response = last_response.json()
                logger.info(f"🎉 Pedido enviado exitosamente a Ticketera!")
                logger.error(f"   Ticket ID: {ticket_response.get('ticket_id', 'N/A')}")
                logger.error(f"   Número: {ticket_response.get('numero', 'N/A')}")
                logger.error(f"   Estado: {ticket_response.get('estado', 'N/A')}")
                logger.error(f"   Repartidor: {ticket_response.get('repartidor_asignado', 'N/A')}")
                
                # Actualizar base de datos de Ahorro con información del ticket
                actualizar_pedido_con_ticket(numero_pedido, ticket_response)
                
                # Log de éxito
                logger.info(f"✅ Comunicación completada: Pedido {numero_pedido} → Ticket {ticket_response.get('ticket_id')}")
                
                return ticket_response
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Error parseando respuesta JSON: {e}")
                logger.error(f"   Respuesta recibida: {last_response.text}")
                return None
        else:
            # Error final después de todos los reintentos
            status = last_response.status_code if last_response is not None else 'no_response'
            body = last_response.text if last_response is not None else 'no_body'
            error_msg = last_error if last_error else f"Status {status}"
            
            logger.error(f"💥 Error final enviando pedido a Ticketera después de {max_retries} intentos")
            logger.error(f"   Error: {error_msg}")
            if last_response:
                logger.error(f"   Status: {status}")
                logger.error(f"   Respuesta: {body[:500]}...")
            
            # Guardar pedido pendiente para reintento posterior
            guardar_pedido_pendiente(numero_pedido, ticket_data, error_msg)
            
            return None
            
    except Exception as e:
        logger.error(f"💥 Error crítico enviando pedido a Ticketera: {e}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return None

def guardar_pedido_pendiente(numero_pedido, ticket_data, error_msg):
    """
    Guardar pedido pendiente para reintento posterior
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_pendientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido VARCHAR(50) UNIQUE NOT NULL,
                datos_ticket TEXT NOT NULL,
                error_ultimo_intento TEXT,
                fecha_ultimo_intento DATETIME DEFAULT CURRENT_TIMESTAMP,
                intentos INTEGER DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT OR REPLACE INTO pedidos_pendientes 
            (numero_pedido, datos_ticket, error_ultimo_intento, fecha_ultimo_intento, intentos)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        """, (numero_pedido, json.dumps(ticket_data), error_msg))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Pedido {numero_pedido} guardado para reintento posterior")
        
    except Exception as e:
        logger.warning(f"⚠️ Error guardando pedido pendiente: {e}")

# ==========================================
# REGISTRAR API BLUEPRINT
# ==========================================

# Importar y registrar la API
try:
    from api_belgrano_ahorro import register_api_blueprint
    register_api_blueprint(app)
    logger.info("✅ API de Belgrano Ahorro registrada en /api/v1")
except ImportError as ie:
    logger.warning(f"⚠️ No se pudo importar register_api_blueprint: {ie}")
    logger.warning("⚠️ La aplicación continuará sin registrar la API (funcionalidad limitada)")
except Exception as e:
    logger.error(f"⚠️ Error registrando la API: {e}")
    import traceback
    logger.error(traceback.format_exc())
    logger.warning("⚠️ Continuando sin registrar la API (funcionalidad limitada)")
    # NO hacer raise - permitir que la app continúe
else:
    # Precarga no bloqueante de datos para evitar cold-start lentos
    try:
        from concurrent.futures import ThreadPoolExecutor
        _preload_executor = ThreadPoolExecutor(max_workers=2)
        def _precargar_datos():
            try:
                obtener_ofertas_activas()
            except Exception:
                pass
        _preload_executor.submit(_precargar_datos)
    except Exception as _e:
        logger.info("Precarga no disponible, continuando sin ella")

# ==========================================
# API ENDPOINTS PARA INTEGRACIÓN (LEGACY)
# ==========================================

@app.route('/api/tickets', methods=['POST'])
def api_crear_ticket():
    """Endpoint público para recibir tickets desde Belgrano Ahorro (LEGACY)"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        required_fields = ['cliente', 'productos', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Validar tipos de datos
        if not isinstance(data['cliente'], str):
            return jsonify({'error': 'cliente debe ser string'}), 400
        
        if not isinstance(data['productos'], list):
            return jsonify({'error': 'productos debe ser lista'}), 400
        
        if not isinstance(data['total'], (int, float)):
            return jsonify({'error': 'total debe ser número'}), 400
        
        # Generar número de pedido si no viene
        if 'numero_pedido' not in data:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = secrets.token_hex(3).upper()
            data['numero_pedido'] = f"TICK-{timestamp}-{random_suffix}"
        
        # Guardar ticket en la base de datos
        ticket_data = {
            'numero_pedido': data['numero_pedido'],
            'cliente': data['cliente'],
            'productos': json.dumps(data['productos']),
            'total': data['total'],
            'direccion': data.get('direccion', ''),
            'telefono': data.get('telefono', ''),
            'email': data.get('email', ''),
            'metodo_pago': data.get('metodo_pago', ''),
            'notas': data.get('notas', ''),
            'estado': 'pendiente',
            'prioridad': 'normal',
            'repartidor': 'Repartidor1'
        }
        
        # Usar la función de guardar ticket existente
        from app_tickets import guardar_ticket
        ticket_id = guardar_ticket(ticket_data)
        
        if ticket_id:
            logger.info(f"✅ Ticket recibido y guardado: {data['numero_pedido']}")
            logger.error(f"   Cliente: {data['cliente']}")
            logger.error(f"   Total: ${data['total']}")
            logger.error(f"   Productos: {len(data['productos'])} items")
            
            return jsonify({'msg': 'ticket registrado', 'ticket_id': ticket_id}), 201
        else:
            return jsonify({'error': 'Error guardando ticket'}), 500
            
    except Exception as e:
        logger.error(f"Error en API crear ticket: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/tickets', methods=['GET'])
def api_obtener_tickets():
    """Obtener todos los tickets (solo admin)"""
    try:
        from app_tickets import obtener_todos_los_tickets
        tickets = obtener_todos_los_tickets()
        return jsonify({'tickets': tickets}), 200
    except Exception as e:
        return jsonify({'error': 'Error obteniendo tickets'}), 500

@app.route('/health')
def health_check():
    """Health check para Render.com"""
    try:
        from app_tickets import contar_tickets
        total_tickets = contar_tickets()
        return jsonify({
            'status': 'healthy',
            'service': 'Belgrano Tickets',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'total_tickets': total_tickets,
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# FUNCIÓN GESTIÓN FLOTA CORREGIDA
# ==========================================

@app.route('/gestion_flota')
@flota_required
def gestion_flota_corregida():
    
    try:
        # Obtener todos los repartidores disponibles
        repartidores = ['Repartidor1', 'Repartidor2', 'Repartidor3', 'Repartidor4', 'Repartidor5']
        
        # Obtener tickets usando la función de base de datos
        from app_tickets import obtener_todos_los_tickets
        todos_tickets = obtener_todos_los_tickets()
        tickets_asignados = [t for t in todos_tickets if t.get('repartidor')]
        
        # Estadísticas por repartidor
        stats_repartidores = {}
        for rep in repartidores:
            tickets_rep = [t for t in todos_tickets if t.get('repartidor') == rep]
            stats_repartidores[rep] = {
                'total': len(tickets_rep),
                'pendientes': len([t for t in tickets_rep if t.get('estado') == 'pendiente']),
                'en_camino': len([t for t in tickets_rep if t.get('estado') in ['en-camino', 'en_camino']]),
                'entregados': len([t for t in tickets_rep if t.get('estado') in ['entregado', 'completado']])
            }
        
        return render_template('gestion_flota.html', 
                             repartidores=repartidores, 
                             tickets_asignados=tickets_asignados,
                             stats_repartidores=stats_repartidores)
    except Exception as e:
        logger.error(f"Error en gestion_flota: {e}")
        # Fallback con datos mínimos
        repartidores = ['Repartidor1', 'Repartidor2', 'Repartidor3', 'Repartidor4', 'Repartidor5']
        return render_template('gestion_flota.html', 
                             repartidores=repartidores, 
                             tickets_asignados=[],
                             stats_repartidores={})

# ==========================================
# MANEJADORES DE ERRORES
# ==========================================

@app.errorhandler(404)
def not_found(error):
    """
    MANEJADOR DE ERROR 404 - Página no encontrada
    Se ejecuta cuando alguien visita una URL que no existe
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """
    MANEJADOR DE ERROR 500 - Error interno del servidor
    Se ejecuta cuando hay un error en el servidor
    """
    return render_template('500.html'), 500

# ==========================================
# FUNCIONES DE AGREGACIÓN MEJORADAS
# ==========================================

def guardar_datos_json(datos):
    """
    Guarda datos en el archivo productos.json de forma segura
    """
    try:
        import json
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        # Limpiar cache después de guardar
        _limpiar_cache()
        return True
    except Exception as e:
        logger.error(f"Error guardando JSON: {e}")
        return False

def _guardar_negocio_en_db(negocio_data):
    """Guardar negocio en la base de datos PostgreSQL"""
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            # CORRECCIÓN: Convertir activo a boolean (no integer)
            # PostgreSQL requiere boolean, no integer (1/0)
            activo_value = negocio_data.get('activo', True)
            # Función helper para convertir a boolean
            if activo_value is None:
                activo = True
            elif isinstance(activo_value, bool):
                activo = activo_value
            elif isinstance(activo_value, int):
                activo = bool(activo_value)
            elif isinstance(activo_value, str):
                activo = activo_value.lower().strip() in ('true', '1', 'yes', 'on', 'si', 'sí')
            else:
                activo = True
            
            result = session.execute(text('''
                INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo)
                VALUES (:nombre, :descripcion, :direccion, :telefono, :email, :activo)
                RETURNING id
            '''), {
                'nombre': negocio_data.get('nombre', ''),
                'descripcion': negocio_data.get('descripcion', ''),
                'direccion': negocio_data.get('direccion', ''),
                'telefono': negocio_data.get('telefono', ''),
                'email': negocio_data.get('email', ''),
                'activo': activo  # Ahora es boolean (True/False), no integer
            })
            row = result.fetchone()
            negocio_id = row[0] if row else None
            session.commit()
            logger.info(f"[DB] ✅ Negocio guardado en PostgreSQL: ID {negocio_id}")
            return negocio_id
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando negocio en DB: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando negocio en DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def _guardar_producto_en_db(producto_data):
    """Guardar producto en la base de datos PostgreSQL"""
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            # CORRECCIÓN: Convertir activo y destacado a boolean (no integer)
            # PostgreSQL requiere boolean, no integer (1/0)
            def _to_bool(val, default):
                if val is None:
                    return default
                if isinstance(val, bool):
                    return val
                if isinstance(val, int):
                    return bool(val)
                if isinstance(val, str):
                    return val.lower().strip() in ('true', '1', 'yes', 'on', 'si', 'sí')
                return default
            
            activo = _to_bool(producto_data.get('activo', True), True)
            destacado = _to_bool(producto_data.get('destacado', False), False)
            store = producto_data.get('descripcion', producto_data.get('store', ''))
            negocio_id = producto_data.get('negocio_id', producto_data.get('negocio', 1))
            if isinstance(negocio_id, str):
                try:
                    negocio_id = int(negocio_id)
                except:
                    negocio_id = 1
            
            result = session.execute(text('''
                INSERT INTO productos (nombre, store, precio, original_price, categoria, imagen,
                                     stock, stock_minimo, negocio_id, activo, destacado)
                VALUES (:nombre, :store, :precio, :original_price, :categoria, :imagen,
                       :stock, :stock_minimo, :negocio_id, :activo, :destacado)
                RETURNING id
            '''), {
                'nombre': producto_data.get('nombre', ''),
                'store': store,
                'precio': float(producto_data.get('precio', 0)),
                'original_price': float(producto_data.get('original_price', producto_data.get('precio', 0))),
                'categoria': producto_data.get('categoria', ''),
                'imagen': producto_data.get('imagen', ''),
                'stock': int(producto_data.get('stock', 0)),
                'stock_minimo': int(producto_data.get('stock_minimo', 5)),
                'negocio_id': negocio_id,
                'activo': activo,
                'destacado': destacado
            })
            row = result.fetchone()
            producto_id = row[0] if row else None
            session.commit()
            logger.info(f"[DB] ✅ Producto guardado en PostgreSQL: ID {producto_id}")
            return producto_id
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando producto en DB: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando producto en DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def _guardar_sucursal_en_db(sucursal_data):
    """Guardar sucursal en la base de datos PostgreSQL"""
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            negocio_id = sucursal_data.get('negocio_id', sucursal_data.get('negocio', 1))
            if isinstance(negocio_id, str):
                try:
                    negocio_id = int(negocio_id)
                except:
                    negocio_id = 1
            
            # CORRECCIÓN: Convertir activo a boolean (no integer)
            # PostgreSQL requiere boolean, no integer (1/0)
            activo_value = sucursal_data.get('activo', True)
            if activo_value is None:
                activo = True
            elif isinstance(activo_value, bool):
                activo = activo_value
            elif isinstance(activo_value, int):
                activo = bool(activo_value)
            elif isinstance(activo_value, str):
                activo = activo_value.lower().strip() in ('true', '1', 'yes', 'on', 'si', 'sí')
            else:
                activo = True
            
            result = session.execute(text('''
                INSERT INTO sucursales (nombre, direccion, telefono, email, negocio_id, activo)
                VALUES (:nombre, :direccion, :telefono, :email, :negocio_id, :activo)
                RETURNING id
            '''), {
                'nombre': sucursal_data.get('nombre', ''),
                'direccion': sucursal_data.get('direccion', ''),
                'telefono': sucursal_data.get('telefono', ''),
                'email': sucursal_data.get('email', ''),
                'negocio_id': negocio_id,
                'activo': activo  # Ahora es boolean (True/False), no integer
            })
            row = result.fetchone()
            sucursal_id = row[0] if row else None
            session.commit()
            logger.info(f"[DB] ✅ Sucursal guardada en PostgreSQL: ID {sucursal_id}")
            return sucursal_id
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando sucursal en DB: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando sucursal en DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def _guardar_oferta_en_db(oferta_data):
    """Guardar oferta en la base de datos PostgreSQL"""
    try:
        from sqlalchemy import text
        session = get_db_connection()
        try:
            # CORRECCIÓN: Convertir activo/activa a boolean (no integer)
            # PostgreSQL requiere boolean, no integer (1/0)
            activa_value = oferta_data.get('activa', oferta_data.get('activo', True))
            if activa_value is None:
                activo = True
            elif isinstance(activa_value, bool):
                activo = activa_value
            elif isinstance(activa_value, int):
                activo = bool(activa_value)
            elif isinstance(activa_value, str):
                activo = activa_value.lower().strip() in ('true', '1', 'yes', 'on', 'si', 'sí')
            else:
                activo = True
            
            negocio_id = oferta_data.get('negocio_id', oferta_data.get('negocio', None))
            if isinstance(negocio_id, str):
                try:
                    negocio_id = int(negocio_id) if negocio_id else None
                except:
                    negocio_id = None
            
            nombre = oferta_data.get('titulo', oferta_data.get('nombre', ''))
            
            result = session.execute(text('''
                INSERT INTO ofertas (nombre, descripcion, descuento, fecha_inicio, fecha_fin, activo, negocio_id)
                VALUES (:nombre, :descripcion, :descuento, :fecha_inicio, :fecha_fin, :activo, :negocio_id)
                RETURNING id
            '''), {
                'nombre': nombre,
                'descripcion': oferta_data.get('descripcion', ''),
                'descuento': float(oferta_data.get('descuento', 0)),
                'fecha_inicio': oferta_data.get('fecha_inicio', ''),
                'fecha_fin': oferta_data.get('fecha_fin', ''),
                'activo': activo,  # Ahora es boolean (True/False), no integer
                'negocio_id': negocio_id
            })
            row = result.fetchone()
            oferta_id = row[0] if row else None
            session.commit()
            logger.info(f"[DB] ✅ Oferta guardada en PostgreSQL: ID {oferta_id}")
            return oferta_id
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando oferta en DB: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando oferta en DB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

@app.route('/admin/agregar_producto', methods=['POST'])
@admin_required
def agregar_producto_mejorado():
    """
    Agregar producto con manejo de errores mejorado
    """
    try:
        # Validar datos requeridos
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '').strip()
        categoria = request.form.get('categoria', '').strip()
        negocio = request.form.get('negocio', '').strip()
        
        if not all([nombre, precio, categoria, negocio]):
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('admin_panel'))
        
        try:
            precio_float = float(precio)
        except ValueError:
            flash('El precio debe ser un número válido', 'error')
            return redirect(url_for('admin_panel'))
        
        # Cargar datos actuales
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        # Crear nuevo producto
        nuevo_producto = {
            'id': str(uuid.uuid4()),
            'nombre': nombre,
            'precio': precio_float,
            'categoria': categoria,
            'negocio': negocio,
            'descripcion': request.form.get('descripcion', ''),
            'imagen': request.form.get('imagen', ''),
            'activo': True,
            'fecha_creacion': datetime.now().isoformat()
        }
        
        # Agregar a la lista
        if 'productos' not in datos:
            datos['productos'] = []
        datos['productos'].append(nuevo_producto)
        
        # Guardar
        if guardar_datos_json(datos):
            flash(f'Producto "{nombre}" agregado exitosamente', 'success')
            logger.info(f"Producto agregado: {nombre}")
        else:
            flash('Error al guardar el producto', 'error')
            
    except Exception as e:
        logger.error(f"Error agregando producto: {e}")
        flash('Error interno al agregar producto. Revisa los logs.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/agregar_sucursal', methods=['POST'])
@admin_required
def agregar_sucursal_mejorado():
    """
    Agregar sucursal con manejo de errores mejorado
    """
    try:
        # Validar datos requeridos
        nombre = request.form.get('nombre', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        if not all([nombre, direccion]):
            flash('Nombre y dirección son requeridos', 'error')
            return redirect(url_for('admin_panel'))
        
        # Cargar datos actuales
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        # Crear nueva sucursal
        nueva_sucursal = {
            'id': str(uuid.uuid4()),
            'nombre': nombre,
            'direccion': direccion,
            'telefono': telefono,
            'horario': request.form.get('horario', ''),
            'activo': True,
            'fecha_creacion': datetime.now().isoformat()
        }
        
        # Agregar a la lista
        if 'sucursales' not in datos:
            datos['sucursales'] = []
        datos['sucursales'].append(nueva_sucursal)
        
        # Guardar
        if guardar_datos_json(datos):
            flash(f'Sucursal "{nombre}" agregada exitosamente', 'success')
            logger.info(f"Sucursal agregada: {nombre}")
        else:
            flash('Error al guardar la sucursal', 'error')
            
    except Exception as e:
        logger.error(f"Error agregando sucursal: {e}")
        flash('Error interno al agregar sucursal. Revisa los logs.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/agregar_oferta', methods=['POST'])
@admin_required
def agregar_oferta_mejorado():
    """
    Agregar oferta con manejo de errores mejorado
    """
    try:
        # Validar datos requeridos
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        descuento = request.form.get('descuento', '').strip()
        
        if not all([titulo, descripcion, descuento]):
            flash('Título, descripción y descuento son requeridos', 'error')
            return redirect(url_for('admin_panel'))
        
        try:
            descuento_int = int(descuento)
            if descuento_int < 0 or descuento_int > 100:
                raise ValueError("Descuento debe estar entre 0 y 100")
        except ValueError:
            flash('El descuento debe ser un número entre 0 y 100', 'error')
            return redirect(url_for('admin_panel'))
        
        # Cargar datos actuales
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        # Crear nueva oferta
        nueva_oferta = {
            'id': str(uuid.uuid4()),
            'titulo': titulo,
            'descripcion': descripcion,
            'descuento': descuento_int,
            'imagen': request.form.get('imagen', ''),
            'fecha_inicio': request.form.get('fecha_inicio', ''),
            'fecha_fin': request.form.get('fecha_fin', ''),
            'activo': True,
            'fecha_creacion': datetime.now().isoformat()
        }
        
        # Agregar a la lista
        if 'ofertas' not in datos:
            datos['ofertas'] = []
        datos['ofertas'].append(nueva_oferta)
        
        # Guardar
        if guardar_datos_json(datos):
            flash(f'Oferta "{titulo}" agregada exitosamente', 'success')
            logger.info(f"Oferta agregada: {titulo}")
        else:
            flash('Error al guardar la oferta', 'error')
            
    except Exception as e:
        logger.error(f"Error agregando oferta: {e}")
        flash('Error interno al agregar oferta. Revisa los logs.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/agregar_negocio', methods=['POST'])
@admin_required
def agregar_negocio_mejorado():
    """
    Agregar negocio con manejo de errores mejorado
    """
    try:
        # Validar datos requeridos
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not all([nombre, descripcion]):
            flash('Nombre y descripción son requeridos', 'error')
            return redirect(url_for('admin_panel'))
        
        # Cargar datos actuales
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        # Crear nuevo negocio
        negocio_id = str(uuid.uuid4())
        nuevo_negocio = {
            'id': negocio_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'logo': request.form.get('logo', ''),
            'telefono': request.form.get('telefono', ''),
            'direccion': request.form.get('direccion', ''),
            'activo': True,
            'fecha_creacion': datetime.now().isoformat()
        }
        
        # Agregar al diccionario
        if 'negocios' not in datos:
            datos['negocios'] = {}
        datos['negocios'][negocio_id] = nuevo_negocio
        
        # Guardar
        if guardar_datos_json(datos):
            flash(f'Negocio "{nombre}" agregado exitosamente', 'success')
            logger.info(f"Negocio agregado: {nombre}")
        else:
            flash('Error al guardar el negocio', 'error')
            
    except Exception as e:
        logger.error(f"Error agregando negocio: {e}")
        flash('Error interno al agregar negocio. Revisa los logs.', 'error')
    
    return redirect(url_for('admin_panel'))

# ==========================================
# API AUTHENTICATION MIDDLEWARE
# ==========================================

def require_api_key(f):
    """Decorador para validar API key en endpoints /api/v1/*"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar API key en headers
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Validar contra la clave configurada
        if not api_key or api_key != BELGRANO_AHORRO_API_KEY:
            logger.warning(f"Acceso no autorizado a {request.path} desde {request.remote_addr}")
            return jsonify({
                'error': 'No autorizado',
                'message': 'API key inválida o faltante'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# FUNCIONES AUXILIARES PARA COMUNICACIÓN CON SERVICIOS EXTERNOS
# ==========================================

def _sync_to_external_services(endpoint, method='GET', data=None, item_id=None):
    """
    Sincronizar cambios con servicios externos (Ticketera y DevOps)
    Retorna True si la sincronización fue exitosa, False en caso contrario
    """
    external_services = []
    
    # Agregar Ticketera
    ticketera_url = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com').rstrip('/')
    if ticketera_url and not _is_self_host(ticketera_url):
        external_services.append({
            'name': 'Ticketera',
            'base_url': ticketera_url,
            'api_key': os.environ.get('TICKETERA_API_KEY', os.environ.get('BELGRANO_AHORRO_API_KEY', ''))
        })
    elif _is_self_host(ticketera_url):
        logger.debug("Ticketera URL apunta a esta instancia, se omite sincronización interna.")
    
    # Agregar DevOps solo si tiene una URL específica diferente a Belgrano Ahorro
    # DevOps normalmente está en la misma instancia que Belgrano Ahorro, así que no se sincroniza externamente
    devops_url = os.environ.get('DEVOPS_API_URL', '').strip().rstrip('/')
    if devops_url and not _is_self_host(devops_url):
        # Solo agregar DevOps si tiene una URL específica y diferente
        external_services.append({
            'name': 'DevOps',
            'base_url': devops_url,
            'api_key': os.environ.get('DEVOPS_API_KEY', os.environ.get('BELGRANO_AHORRO_API_KEY', ''))
        })
    else:
        logger.debug("DevOps está en la misma instancia que Belgrano Ahorro; no se realiza sincronización externa.")
    
    success_count = 0
    session = HTTP_SESSION
    for service in external_services:
        try:
            # Construir URL completa
            url = f"{service['base_url']}{endpoint}"
            if item_id:
                url = f"{service['base_url']}{endpoint.rstrip('/')}/{item_id}"
            
            # Headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {service['api_key']}",
                'X-API-Key': service['api_key'],
                'X-Origin': 'belgrano_ahorro'  # Siempre marcar origen como belgrano_ahorro
            }
            
            # Realizar petición con timeout corto
            timeout = HTTP_TIMEOUT_SECS
            response = session.request(method.upper(), url, headers=headers, json=data, timeout=timeout)
            
            if 200 <= response.status_code < 300:
                success_count += 1
                logger.info(f"✅ Sincronización exitosa con {service['name']}: {endpoint}")
            else:
                logger.warning(f"⚠️ Error sincronizando con {service['name']}: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Timeout sincronizando con {service['name']}: {endpoint}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error de conexión con {service['name']}: {str(e)}")
        except Exception as e:
            logger.warning(f"⚠️ Error inesperado sincronizando con {service['name']}: {str(e)}")
    
    return success_count > 0


def _get_from_external_service(endpoint, fallback_data_func):
    """
    Obtener datos de servicios externos con fallback a datos locales
    Retorna los datos obtenidos
    """
    # Intentar obtener de servicios externos
    services = [
        {
            'name': 'Belgrano Ahorro',
            'url': os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com'),
            'api_key': os.environ.get('BELGRANO_AHORRO_API_KEY', '')
        },
        {
            'name': 'Ticketera',
            'url': os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com'),
            'api_key': os.environ.get('TICKETERA_API_KEY', os.environ.get('BELGRANO_AHORRO_API_KEY', ''))
        }
    ]
    
    for service in services:
        if not service['url']:
            continue
        
        if _is_self_host(service['url']):
            logger.debug(f"Servicio {service['name']} apunta a esta instancia; se omite request HTTP.")
            continue
        
        try:
            url = f"{service['url'].rstrip('/')}{endpoint}"
            headers = {
                'Authorization': f"Bearer {service['api_key']}",
                'X-API-Key': service['api_key']
            }
            timeout = HTTP_TIMEOUT_SECS
            response = HTTP_SESSION.get(url, headers=headers, timeout=timeout)
            
            if 200 <= response.status_code < 300:
                data = response.json()
                # Normalizar formato de respuesta
                if isinstance(data, dict) and 'data' in data:
                    data = data['data']
                logger.info(f"✅ Datos obtenidos de {service['name']}: {endpoint}")
                return data
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Timeout obteniendo datos de {service['name']}: {endpoint}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error de conexión con {service['name']}: {str(e)}")
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo datos de {service['name']}: {str(e)}")
    
    # Fallback a datos locales
    logger.info(f"📦 Usando datos locales (fallback) para: {endpoint}")
    return fallback_data_func()

# ==========================================
# API ENDPOINTS PARA DEVOPS
# ==========================================

@app.route('/api/v1/negocios', methods=['GET'])
@require_api_key
def api_get_negocios():
    """API endpoint para obtener todos los negocios"""
    try:
        def fallback_negocios():
            datos = cargar_datos_completos()
            if not datos or 'negocios' not in datos:
                return []
            negocios = []
            for negocio_id, negocio_data in datos['negocios'].items():
                negocio_data['id'] = negocio_id
                negocios.append(negocio_data)
            return negocios
        
        negocios = _get_from_external_service('/api/v1/negocios', fallback_negocios)
        if not isinstance(negocios, list):
            negocios = []
        
        logger.info(f"✅ API: Negocios obtenidos exitosamente ({len(negocios)} items)")
        return jsonify(negocios), 200
    except Exception as e:
        logger.error(f"Error obteniendo negocios: {e}")
        return jsonify({'error': 'Error obteniendo negocios'}), 500

@app.route('/api/v1/negocios', methods=['POST'])
@require_api_key
def api_create_negocio():
    """API endpoint para crear un nuevo negocio"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nombre', 'descripcion', 'categoria']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        # Crear nuevo negocio
        negocio_id = str(uuid.uuid4())
        nuevo_negocio = {
            'id': negocio_id,
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'categoria': data['categoria'],
            'direccion': data.get('direccion', ''),
            'telefono': data.get('telefono', ''),
            'email': data.get('email', ''),
            'activo': data.get('activo', True),
            'fecha_creacion': datetime.now().isoformat(),
            'creado_desde': data.get('creado_desde', 'api')
        }
        
        # Agregar al diccionario
        if 'negocios' not in datos:
            datos['negocios'] = {}
        datos['negocios'][negocio_id] = nuevo_negocio
        
        # Guardar en base de datos PostgreSQL (persistencia permanente)
        db_id = _guardar_negocio_en_db(nuevo_negocio)
        if db_id:
            nuevo_negocio['db_id'] = db_id  # Agregar ID de DB al objeto
        
        # Guardar en JSON (backup/compatibilidad)
        if not guardar_datos_json(datos):
            logger.warning("⚠️ Error guardando en JSON, pero guardado en DB")
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/negocios', 'POST', nuevo_negocio)
        
        logger.info(f"✅ Negocio creado via API: {nuevo_negocio['nombre']} (DB ID: {db_id})")
        return jsonify(nuevo_negocio), 201
            
    except Exception as e:
        logger.error(f"Error creando negocio via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/negocios/<negocio_id>', methods=['PUT'])
@require_api_key
def api_update_negocio(negocio_id):
    """API endpoint para actualizar un negocio existente"""
    try:
        data = request.get_json()
        
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos or 'negocios' not in datos or negocio_id not in datos['negocios']:
            return jsonify({'error': 'Negocio no encontrado'}), 404
        
        # Actualizar datos
        negocio = datos['negocios'][negocio_id]
        for key, value in data.items():
            if key != 'id':  # No permitir cambiar el ID
                negocio[key] = value
        
        negocio['fecha_modificacion'] = datetime.now().isoformat()
        negocio['modificado_desde'] = data.get('modificado_desde', 'api')
        
        # Guardar localmente primero
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/negocios', 'PUT', negocio, negocio_id)
        
        logger.info(f"✅ Negocio actualizado via API: {negocio['nombre']}")
        return jsonify(negocio), 200
            
    except Exception as e:
        logger.error(f"Error actualizando negocio via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/negocios/<negocio_id>', methods=['DELETE'])
@require_api_key
def api_delete_negocio(negocio_id):
    """API endpoint para eliminar un negocio"""
    try:
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos or 'negocios' not in datos or negocio_id not in datos['negocios']:
            return jsonify({'error': 'Negocio no encontrado'}), 404
        
        # Eliminar negocio
        negocio_nombre = datos['negocios'][negocio_id]['nombre']
        del datos['negocios'][negocio_id]
        
        # Guardar localmente primero
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/negocios', 'DELETE', None, negocio_id)
        
        logger.info(f"✅ Negocio eliminado via API: {negocio_nombre}")
        return jsonify({'message': 'Negocio eliminado exitosamente'}), 200
            
    except Exception as e:
        logger.error(f"Error eliminando negocio via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/ofertas', methods=['GET'])
@require_api_key
def api_get_ofertas():
    """API endpoint para obtener todas las ofertas"""
    try:
        def fallback_ofertas():
            datos = cargar_datos_completos()
            if not datos or 'ofertas' not in datos:
                return []
            ofertas_data = datos['ofertas']
            if isinstance(ofertas_data, list):
                return ofertas_data
            elif isinstance(ofertas_data, dict):
                ofertas = []
                for oferta_id, oferta_data in ofertas_data.items():
                    oferta_data['id'] = oferta_id
                    ofertas.append(oferta_data)
                return ofertas
            return []
        
        ofertas = _get_from_external_service('/api/v1/ofertas', fallback_ofertas)
        if not isinstance(ofertas, list):
            ofertas = []
        
        logger.info(f"✅ API: Ofertas obtenidas exitosamente ({len(ofertas)} items)")
        return jsonify(ofertas), 200
    except Exception as e:
        logger.error(f"Error obteniendo ofertas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/categorias', methods=['GET'])
def api_get_categorias():
    """API endpoint para obtener todas las categorías"""
    try:
        datos = cargar_datos_completos()
        categorias = datos.get('categorias', {})
        
        # Convertir diccionario a lista
        categorias_lista = []
        for cat_id, cat_data in categorias.items():
            cat_data['id'] = cat_id
            categorias_lista.append(cat_data)
        
        return jsonify(categorias_lista), 200
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/sucursales', methods=['GET'])
@require_api_key
def api_get_sucursales():
    """API endpoint para obtener todas las sucursales"""
    try:
        def fallback_sucursales():
            datos = cargar_datos_completos()
            sucursales = datos.get('sucursales', {})
            sucursales_lista = []
            for suc_id, suc_data in sucursales.items():
                suc_data['id'] = suc_id
                sucursales_lista.append(suc_data)
            return sucursales_lista
        
        sucursales = _get_from_external_service('/api/v1/sucursales', fallback_sucursales)
        if not isinstance(sucursales, list):
            sucursales = []
        
        logger.info(f"✅ API: Sucursales obtenidas exitosamente ({len(sucursales)} items)")
        return jsonify(sucursales), 200
    except Exception as e:
        logger.error(f"Error obteniendo sucursales: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/sucursales', methods=['POST'])
@require_api_key
def api_create_sucursal():
    """API endpoint para crear una sucursal"""
    try:
        data = request.get_json()
        required_fields = ['nombre']
        for field in required_fields:
            if field not in data or data[field] in (None, ''):
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        sucursal_id = str(uuid.uuid4())
        nueva_sucursal = {
            'id': sucursal_id,
            'nombre': data['nombre'],
            'direccion': data.get('direccion', ''),
            'telefono': data.get('telefono', ''),
            'negocio_id': data.get('negocio_id', ''),
            'activo': bool(data.get('activo', True)),
            'fecha_creacion': datetime.now().isoformat(),
            'creado_desde': data.get('creado_desde', 'api')
        }
        if 'sucursales' not in datos:
            datos['sucursales'] = {}
        datos['sucursales'][sucursal_id] = nueva_sucursal
        
        # Guardar en base de datos PostgreSQL (persistencia permanente)
        db_id = _guardar_sucursal_en_db(nueva_sucursal)
        if db_id:
            nueva_sucursal['db_id'] = db_id  # Agregar ID de DB al objeto
        
        # Guardar en JSON (backup/compatibilidad)
        if not guardar_datos_json(datos):
            logger.warning("⚠️ Error guardando en JSON, pero guardado en DB")
        
        _sync_to_external_services('/api/v1/sucursales', 'POST', nueva_sucursal)
        logger.info(f"✅ Sucursal creada via API: {nueva_sucursal['nombre']} (DB ID: {db_id})")
        return jsonify(nueva_sucursal), 201
    except Exception as e:
        logger.error(f"Error creando sucursal via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/sucursales/<sucursal_id>', methods=['PUT'])
@require_api_key
def api_update_sucursal(sucursal_id):
    """API endpoint para actualizar una sucursal"""
    try:
        data = request.get_json()
        datos = cargar_datos_completos()
        if not datos or 'sucursales' not in datos or sucursal_id not in datos['sucursales']:
            return jsonify({'error': 'Sucursal no encontrada'}), 404
        sucursal = datos['sucursales'][sucursal_id]
        for key, value in data.items():
            if key != 'id':
                sucursal[key] = value
        sucursal['fecha_modificacion'] = datetime.now().isoformat()
        sucursal['modificado_desde'] = data.get('modificado_desde', 'api')
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        _sync_to_external_services('/api/v1/sucursales', 'PUT', sucursal, sucursal_id)
        logger.info(f"✅ Sucursal actualizada via API: {sucursal.get('nombre','')}")
        return jsonify(sucursal), 200
    except Exception as e:
        logger.error(f"Error actualizando sucursal via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/sucursales/<sucursal_id>', methods=['DELETE'])
@require_api_key
def api_delete_sucursal(sucursal_id):
    """API endpoint para eliminar una sucursal"""
    try:
        datos = cargar_datos_completos()
        if not datos or 'sucursales' not in datos or sucursal_id not in datos['sucursales']:
            return jsonify({'error': 'Sucursal no encontrada'}), 404
        sucursal_nombre = datos['sucursales'][sucursal_id].get('nombre', '')
        del datos['sucursales'][sucursal_id]
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        _sync_to_external_services('/api/v1/sucursales', 'DELETE', None, sucursal_id)
        logger.info(f"✅ Sucursal eliminada via API: {sucursal_nombre}")
        return jsonify({'message': 'Sucursal eliminada exitosamente'}), 200
    except Exception as e:
        logger.error(f"Error eliminando sucursal via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/pedidos', methods=['GET'])
def api_get_pedidos():
    """API endpoint para obtener pedidos del usuario"""
    try:
        # Por ahora devolver lista vacía hasta implementar autenticación
        return jsonify([]), 200
    except Exception as e:
        logger.error(f"Error obteniendo pedidos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/usuarios', methods=['GET'])
def api_get_usuarios():
    """API endpoint para obtener usuarios (solo admin)"""
    try:
        # Por ahora devolver lista vacía hasta implementar autenticación
        return jsonify([]), 200
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/test-ticketera', methods=['GET'])
def api_test_ticketera():
    """Endpoint de prueba para verificar conectividad con Ticketera"""
    try:
        import requests
        response = requests.get('http://localhost:5001/api/test', timeout=5)
        return jsonify({
            'status': 'success',
            'ticketera_status': response.status_code,
            'message': 'Conectividad verificada'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error conectando con Ticketera: {str(e)}'
        }), 500

@app.route('/api/v1/immediate-test', methods=['GET'])
def api_immediate_test():
    """Endpoint de prueba inmediato"""
    return "OK", 200

@app.route('/api/v1/ofertas', methods=['POST'])
@require_api_key
def api_create_oferta():
    """API endpoint para crear una nueva oferta"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['titulo', 'descripcion', 'descuento', 'fecha_inicio', 'fecha_fin']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        # Crear nueva oferta
        oferta_id = str(uuid.uuid4())
        nueva_oferta = {
            'id': oferta_id,
            'titulo': data['titulo'],
            'descripcion': data['descripcion'],
            'descuento': float(data['descuento']),
            'producto_nombre': data.get('producto_nombre', ''),  # Nombre del producto en texto libre
            'producto_id': data.get('producto_id', ''),
            'fecha_inicio': data['fecha_inicio'],
            'fecha_fin': data['fecha_fin'],
            'activa': data.get('activa', True),
            'fecha_creacion': datetime.now().isoformat(),
            'creado_desde': data.get('creado_desde', 'api')
        }
        
        # Agregar al diccionario
        if 'ofertas' not in datos:
            datos['ofertas'] = {}
        datos['ofertas'][oferta_id] = nueva_oferta
        
        # Guardar en base de datos PostgreSQL (persistencia permanente)
        db_id = _guardar_oferta_en_db(nueva_oferta)
        if db_id:
            nueva_oferta['db_id'] = db_id  # Agregar ID de DB al objeto
        
        # Guardar en JSON (backup/compatibilidad)
        if not guardar_datos_json(datos):
            logger.warning("⚠️ Error guardando en JSON, pero guardado en DB")
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/ofertas', 'POST', nueva_oferta)
        
        logger.info(f"✅ Oferta creada via API: {nueva_oferta['titulo']} (DB ID: {db_id})")
        return jsonify(nueva_oferta), 201
            
    except Exception as e:
        logger.error(f"Error creando oferta via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/ofertas/<oferta_id>', methods=['PUT'])
@require_api_key
def api_update_oferta(oferta_id):
    """API endpoint para actualizar una oferta existente"""
    try:
        data = request.get_json()
        
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos or 'ofertas' not in datos or oferta_id not in datos['ofertas']:
            return jsonify({'error': 'Oferta no encontrada'}), 404
        
        # Actualizar datos
        oferta = datos['ofertas'][oferta_id]
        for key, value in data.items():
            if key != 'id':  # No permitir cambiar el ID
                oferta[key] = value
        
        oferta['fecha_modificacion'] = datetime.now().isoformat()
        oferta['modificado_desde'] = data.get('modificado_desde', 'api')
        
        # Guardar localmente primero
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/ofertas', 'PUT', oferta, oferta_id)
        
        logger.info(f"✅ Oferta actualizada via API: {oferta['titulo']}")
        return jsonify(oferta), 200
            
    except Exception as e:
        logger.error(f"Error actualizando oferta via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/ofertas/<oferta_id>', methods=['DELETE'])
@require_api_key
def api_delete_oferta(oferta_id):
    """API endpoint para eliminar una oferta"""
    try:
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos or 'ofertas' not in datos or oferta_id not in datos['ofertas']:
            return jsonify({'error': 'Oferta no encontrada'}), 404
        
        # Eliminar oferta
        oferta_titulo = datos['ofertas'][oferta_id]['titulo']
        del datos['ofertas'][oferta_id]
        
        # Guardar localmente primero
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/ofertas', 'DELETE', None, oferta_id)
        
        logger.info(f"✅ Oferta eliminada via API: {oferta_titulo}")
        return jsonify({'message': 'Oferta eliminada exitosamente'}), 200
            
    except Exception as e:
        logger.error(f"Error eliminando oferta via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/productos', methods=['GET'])
@require_api_key
def api_get_productos():
    """API endpoint para obtener todos los productos"""
    try:
        def fallback_productos():
            datos = cargar_datos_completos()
            if not datos or 'productos' not in datos:
                return []
            return datos['productos']
        
        productos = _get_from_external_service('/api/v1/productos', fallback_productos)
        if not isinstance(productos, list):
            productos = []
        
        logger.info(f"✅ API: Productos obtenidos exitosamente ({len(productos)} items)")
        return jsonify(productos), 200
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/productos', methods=['POST'])
@require_api_key
def api_create_producto():
    """API endpoint para crear un nuevo producto"""
    try:
        data = request.get_json()
        required_fields = ['nombre', 'precio']
        for field in required_fields:
            if field not in data or data[field] in (None, ''):
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        nuevo_producto = {
            'id': str(uuid.uuid4()),
            'nombre': data['nombre'],
            'precio': float(data['precio']),
            'categoria': data.get('categoria', ''),
            'negocio': data.get('negocio', ''),
            'descripcion': data.get('descripcion', ''),
            'imagen': data.get('imagen', ''),
            'activo': bool(data.get('activo', True)),
            'fecha_creacion': datetime.now().isoformat(),
            'creado_desde': data.get('creado_desde', 'api')
        }
        if 'productos' not in datos:
            datos['productos'] = []
        datos['productos'].append(nuevo_producto)
        
        # Guardar en base de datos PostgreSQL (persistencia permanente)
        db_id = _guardar_producto_en_db(nuevo_producto)
        if db_id:
            nuevo_producto['db_id'] = db_id  # Agregar ID de DB al objeto
        
        # Guardar en JSON (backup/compatibilidad)
        if not guardar_datos_json(datos):
            logger.warning("⚠️ Error guardando en JSON, pero guardado en DB")
        
        _sync_to_external_services('/api/v1/productos', 'POST', nuevo_producto)
        logger.info(f"✅ Producto creado via API: {nuevo_producto['nombre']} (DB ID: {db_id})")
        return jsonify(nuevo_producto), 201
    except Exception as e:
        logger.error(f"Error creando producto via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/productos/<producto_id>', methods=['PUT'])
@require_api_key
def api_update_producto(producto_id):
    """API endpoint para actualizar un producto"""
    try:
        data = request.get_json()
        
        # Cargar datos existentes
        datos = cargar_datos_completos()
        if not datos or 'productos' not in datos:
            return jsonify({'error': 'Productos no encontrados'}), 404
        
        # Buscar producto por ID
        producto_encontrado = None
        for i, producto in enumerate(datos['productos']):
            if str(producto.get('id', '')) == str(producto_id):
                producto_encontrado = i
                break
        
        if producto_encontrado is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Actualizar datos del producto
        for key, value in data.items():
            if key != 'id':  # No permitir cambiar el ID
                datos['productos'][producto_encontrado][key] = value
        
        datos['productos'][producto_encontrado]['fecha_modificacion'] = datetime.now().isoformat()
        datos['productos'][producto_encontrado]['modificado_desde'] = data.get('modificado_desde', 'api')
        
        # Guardar localmente primero
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        # Intentar sincronizar con servicios externos
        _sync_to_external_services('/api/v1/productos', 'PUT', datos['productos'][producto_encontrado], producto_id)
        
        logger.info(f"✅ Producto actualizado via API: {datos['productos'][producto_encontrado]['nombre']}")
        return jsonify(datos['productos'][producto_encontrado]), 200
            
    except Exception as e:
        logger.error(f"Error actualizando producto via API: {e}")
        return jsonify({'error': 'Servicio DevOps temporalmente no disponible'}), 503

@app.route('/api/v1/productos/<producto_id>', methods=['DELETE'])
@require_api_key
def api_delete_producto(producto_id):
    """API endpoint para eliminar un producto"""
    try:
        datos = cargar_datos_completos()
        if not datos or 'productos' not in datos:
            return jsonify({'error': 'Productos no encontrados'}), 404
        indice = None
        for i, producto in enumerate(datos['productos']):
            if str(producto.get('id', '')) == str(producto_id):
                indice = i
                break
        if indice is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        producto_nombre = datos['productos'][indice].get('nombre', '')
        del datos['productos'][indice]
        if not guardar_datos_json(datos):
            return jsonify({'error': 'Error al guardar los cambios localmente'}), 500
        
        _sync_to_external_services('/api/v1/productos', 'DELETE', None, producto_id)
        logger.info(f"✅ Producto eliminado via API: {producto_nombre}")
        return jsonify({'message': 'Producto eliminado exitosamente'}), 200
    except Exception as e:
        logger.error(f"Error eliminando producto via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/precios', methods=['GET'])
@require_api_key
def api_get_precios():
    """API endpoint para obtener historial/estado de precios"""
    try:
        datos = cargar_datos_completos()
        precios = datos.get('precios', []) if datos else []
        return jsonify(precios), 200
    except Exception as e:
        logger.error(f"Error obteniendo precios: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/precios', methods=['POST'])
@require_api_key
def api_create_precio():
    """Crear registro de actualización de precio"""
    try:
        data = request.get_json()
        required_fields = ['producto_id', 'nuevo_precio']
        for field in required_fields:
            if field not in data or data[field] in (None, ''):
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}, 'precios': []}
        registro = {
            'id': str(uuid.uuid4()),
            'producto_id': data['producto_id'],
            'precio_anterior': data.get('precio_anterior'),
            'precio_actual': float(data['nuevo_precio']),
            'motivo': data.get('motivo', ''),
            'fecha_actualizacion': datetime.now().isoformat()
        }
        if 'precios' not in datos:
            datos['precios'] = []
        datos['precios'].append(registro)
        if guardar_datos_json(datos):
            logger.info(f"Precio creado via API: prod {registro['producto_id']}")
            return jsonify(registro), 201
        return jsonify({'error': 'Error al guardar el precio'}), 500
    except Exception as e:
        logger.error(f"Error creando precio via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/v1/precios/<producto_id>', methods=['PUT'])
@require_api_key
def api_update_precio(producto_id):
    """Actualizar precio actual de un producto (crea registro y, opcionalmente, actualiza producto)"""
    try:
        data = request.get_json()
        if 'nuevo_precio' not in data:
            return jsonify({'error': 'Campo requerido faltante: nuevo_precio'}), 400
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}, 'precios': []}
        precio_anterior = None
        if 'productos' in datos:
            for p in datos['productos']:
                if str(p.get('id', '')) == str(producto_id):
                    precio_anterior = p.get('precio')
                    p['precio'] = float(data['nuevo_precio'])
                    p['fecha_modificacion'] = datetime.now().isoformat()
                    break
        if 'precios' not in datos:
            datos['precios'] = []
        registro = {
            'id': str(uuid.uuid4()),
            'producto_id': producto_id,
            'precio_anterior': precio_anterior,
            'precio_actual': float(data['nuevo_precio']),
            'motivo': data.get('motivo', ''),
            'fecha_actualizacion': datetime.now().isoformat()
        }
        datos['precios'].append(registro)
        if guardar_datos_json(datos):
            logger.info(f"Precio actualizado via API: prod {producto_id}")
            return jsonify({'message': 'Precio actualizado', 'registro': registro}), 200
        return jsonify({'error': 'Error al guardar el precio'}), 500
    except Exception as e:
        logger.error(f"Error actualizando precio via API: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    """
    PUNTO DE ENTRADA - Solo se ejecuta si corremos este archivo directamente
    Inicia el servidor Flask en modo debug
    """
    logger.info("Iniciando aplicación Flask...")
    logger.info("🚀 Iniciando Belgrano Ahorro...")
    logger.info("📱 Abre tu navegador en: http://localhost:5000")
    logger.info("⏹️  Presiona Ctrl+C para detener")
    app.run(debug=True, host="0.0.0.0", port=5000)