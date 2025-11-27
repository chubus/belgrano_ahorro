#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicialización centralizada de la base de datos PostgreSQL
Crea todas las tablas necesarias si no existen
NO se ejecuta al importar - solo cuando se llama explícitamente
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from urllib.parse import urlparse

# Logger con prefijo [DB]
logger = logging.getLogger(__name__)

# Variable global para evitar múltiples inicializaciones
_db_initialized = False
_engine = None

def _validate_database_url():
    """
    Validar que DATABASE_URL esté correctamente configurada
    Retorna (is_valid, error_message)
    """
    try:
        from config import DATABASE_URL
    except ImportError:
        import os
        DATABASE_URL = os.getenv('DATABASE_URL', '') or os.getenv('POSTGRES_URL', '')
        if not DATABASE_URL:
            return False, "[DB] ERROR: DATABASE_URL no configurada. Configure DATABASE_URL o POSTGRES_URL en Render Dashboard."
    
    if not DATABASE_URL:
        return False, "[DB] ERROR: DATABASE_URL está vacía. Configure DATABASE_URL en Render Dashboard."
    
    # Validar formato de URL
    try:
        parsed = urlparse(DATABASE_URL)
        if not parsed.hostname:
            return False, "[DB] ERROR: DATABASE_URL no tiene un hostname válido"
        
        # Verificar que el hostname sea completo (no solo un fragmento)
        if parsed.hostname.startswith('dpg-') and '.' not in parsed.hostname:
            return False, f"[DB] ERROR: Hostname incompleto: '{parsed.hostname}'. La URL debe incluir el dominio completo. Ejemplo correcto: dpg-xxx.frankfurt-postgres.render.com"
        
        return True, None
    except Exception as e:
        return False, f"[DB] ERROR validando DATABASE_URL: {e}"

def init_db():
    """
    Inicializar base de datos PostgreSQL
    Crea todas las tablas necesarias si no existen
    
    Esta función NO se ejecuta al importar el módulo.
    Debe ser llamada explícitamente después de que las variables de entorno estén cargadas.
    """
    global _db_initialized, _engine
    
    if _db_initialized:
        logger.info("[DB] ℹ️ Base de datos ya fue inicializada (omitiendo reinicialización)")
        return _engine
    
    logger.info("[DB] Iniciando inicialización de base de datos...")
    
    # Validar DATABASE_URL antes de intentar conectar
    is_valid, error_msg = _validate_database_url()
    if not is_valid:
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        from config import DATABASE_URL
    except ImportError:
        import os
        DATABASE_URL = os.getenv('DATABASE_URL', '') or os.getenv('POSTGRES_URL', '')
        if not DATABASE_URL:
            raise ValueError("[DB] ERROR: DATABASE_URL no configurada. Configure DATABASE_URL o POSTGRES_URL en Render Dashboard.")
    
    # Convertir postgres:// a postgresql:// si es necesario
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Asegurar que la URL tenga sslmode=require para Render
    if 'sslmode' not in DATABASE_URL:
        separator = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
    
    try:
        # Crear engine de SQLAlchemy con pool_pre_ping
        _engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,  # Verificar conexiones antes de usarlas
            connect_args={"connect_timeout": 10}
        )
        
        # Probar conexión con timeout
        logger.info("[DB] Intentando conectar a PostgreSQL...")
        with _engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("[DB] ✅ Conectado a PostgreSQL correctamente")
        
        # Crear tablas si no existen
        with _engine.connect() as conn:
            # Tabla negocios
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS negocios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    logo TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Agregar columna 'logo' si la tabla ya existe pero no tiene el campo
            try:
                conn.execute(text('''
                    ALTER TABLE negocios ADD COLUMN IF NOT EXISTS logo TEXT
                '''))
                logger.info("[DB] ✅ Columna 'logo' verificada/agregada a tabla 'negocios'")
            except Exception as e:
                logger.warning(f"[DB] ⚠️ No se pudo agregar columna 'logo': {e}")

            logger.info("[DB] ✅ Tabla 'negocios' verificada/creada")
            
            # Tabla categorías
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT,
                    activa BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            logger.info("[DB] ✅ Tabla 'categorias' verificada/creada")
            
            # Tabla productos
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    store TEXT,
                    precio DECIMAL(10,2) NOT NULL,
                    original_price DECIMAL(10,2),
                    categoria TEXT,
                    imagen TEXT,
                    stock INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 5,
                    negocio_id INTEGER DEFAULT 1,
                    activo BOOLEAN DEFAULT TRUE,
                    destacado BOOLEAN DEFAULT FALSE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'productos' verificada/creada")
            
            # Tabla sucursales
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS sucursales (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    negocio_id INTEGER NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'sucursales' verificada/creada")
            
            # Tabla ofertas
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS ofertas (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    descuento DECIMAL(10,2) NOT NULL,
                    fecha_inicio TIMESTAMP,
                    fecha_fin TIMESTAMP,
                    producto_id INTEGER,
                    negocio_id INTEGER,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos(id),
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'ofertas' verificada/creada")
            
            # Tabla usuarios (si no existe)
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre VARCHAR(255),
                    apellido VARCHAR(255),
                    telefono VARCHAR(20),
                    rol VARCHAR(50) DEFAULT 'cliente',
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Agregar columna 'rol' si la tabla ya existe pero no tiene el campo
            try:
                conn.execute(text('''
                    ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR(50) DEFAULT 'cliente'
                '''))
            except Exception:
                # La columna ya existe o no se puede agregar, continuar
                pass
            logger.info("[DB] ✅ Tabla 'usuarios' verificada/creada")
            
            # Tabla pedidos (si no existe)
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    numero_pedido VARCHAR(255) UNIQUE NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    metodo_pago VARCHAR(50),
                    direccion_entrega TEXT,
                    notas TEXT,
                    estado VARCHAR(50) DEFAULT 'pendiente',
                    ticketera_id VARCHAR(255),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'pedidos' verificada/creada")
            
            # Tabla items_pedido (si no existe)
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS items_pedido (
                    id SERIAL PRIMARY KEY,
                    pedido_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario DECIMAL(10,2) NOT NULL,
                    subtotal DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'items_pedido' verificada/creada")

            # Tabla tokens_recuperacion (si no existe)
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS tokens_recuperacion (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    expiracion TIMESTAMP NOT NULL,
                    usado BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'tokens_recuperacion' verificada/creada")
            
            conn.commit()
        
        logger.info("[DB] ✅ Todas las tablas verificadas/creadas correctamente")
        
        # Cargar datos iniciales si la DB está vacía
        try:
            from load_initial_data import load_initial_data
            load_initial_data()
        except ImportError:
            logger.warning("[DB] ⚠️ No se pudo importar load_initial_data")
        except Exception as e:
            logger.warning(f"[DB] ⚠️ Error cargando datos iniciales: {e}")
        
        _db_initialized = True
        return _engine
        
    except OperationalError as e:
        error_msg = str(e)
        if "could not translate host name" in error_msg or "Name or service not known" in error_msg:
            logger.error("[DB] ❌ ERROR: No se puede resolver el hostname de la base de datos")
            logger.error(f"[DB]    Error: {error_msg}")
            logger.error("[DB]    Verifique que DATABASE_URL tenga el formato correcto:")
            logger.error("[DB]    postgresql://user:password@hostname:port/database?sslmode=require")
            logger.error("[DB]    El hostname debe ser completo (ej: dpg-xxx.frankfurt-postgres.render.com)")
            raise ValueError("[DB] ERROR: Hostname de base de datos no resuelto. Verifique DATABASE_URL en Render Dashboard.")
        else:
            logger.error(f"[DB] ❌ Error de conexión a PostgreSQL: {e}")
            raise
    except Exception as e:
        logger.error(f"[DB] ❌ Error inicializando base de datos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

# NO ejecutar init_db() al importar el módulo
# Solo se ejecuta cuando se llama explícitamente
