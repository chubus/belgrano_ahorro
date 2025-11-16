#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capa de abstracción de base de datos
USA SIEMPRE PostgreSQL - NO hay fallback a SQLite
"""

import logging
from typing import Optional, Any, Union
from contextlib import contextmanager

# Importar configuración centralizada
try:
    from config import DATABASE_URL
except ImportError:
    import os
    DATABASE_URL = os.getenv('DATABASE_URL', '') or os.getenv('POSTGRES_URL', '')
    if not DATABASE_URL:
        # No hacer raise aquí - permitir que la app inicie sin DB (lazy initialization)
        DATABASE_URL = None
        logger.warning("[DB] ⚠️ DATABASE_URL no configurada. La conexión se intentará más tarde.")

logger = logging.getLogger(__name__)

# Variables globales para lazy initialization
engine = None
SessionLocal = None
Base = None
USE_SQLALCHEMY = False
USE_POSTGRESQL = False

def _validate_and_setup_database():
    """
    Validar DATABASE_URL y configurar el engine de PostgreSQL
    Solo se ejecuta cuando se necesita la conexión (lazy initialization)
    """
    global engine, SessionLocal, Base, USE_SQLALCHEMY, USE_POSTGRESQL, DATABASE_URL
    
    if engine is not None:
        return  # Ya está configurado
    
    # Obtener DATABASE_URL si no está disponible
    if not DATABASE_URL:
        try:
            from config import DATABASE_URL as config_db_url
            DATABASE_URL = config_db_url
        except ImportError:
            import os
            DATABASE_URL = os.getenv('DATABASE_URL', '') or os.getenv('POSTGRES_URL', '')
    
    if not DATABASE_URL:
        error_msg = "[DB] ERROR: DATABASE_URL no configurada. Configure DATABASE_URL o POSTGRES_URL en Render Dashboard."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Validar formato de la URL
    from urllib.parse import urlparse
    try:
        parsed = urlparse(DATABASE_URL)
        if not parsed.hostname:
            raise ValueError("[DB] ERROR: DATABASE_URL no tiene un hostname válido")
        
        # Verificar que el hostname sea completo
        if parsed.hostname.startswith('dpg-') and '.' not in parsed.hostname:
            raise ValueError(f"[DB] ERROR: Hostname incompleto: '{parsed.hostname}'. La URL debe incluir el dominio completo. Ejemplo correcto: dpg-xxx.frankfurt-postgres.render.com")
    except Exception as e:
        logger.error(f"[DB] ERROR validando DATABASE_URL: {e}")
        raise
    
    # SIEMPRE usar PostgreSQL - NO hay fallback
    try:
        from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, DECIMAL, TEXT
        from sqlalchemy.orm import sessionmaker, declarative_base
        from sqlalchemy.pool import NullPool
        from sqlalchemy.dialects.postgresql import insert
        from sqlalchemy.exc import OperationalError
        import urllib.parse
        
        # Parsear DATABASE_URL (Render puede venir con postgres:// que necesita convertirse)
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Asegurar que la URL tenga sslmode=require para Render
        if 'sslmode' not in DATABASE_URL:
            separator = '&' if '?' in DATABASE_URL else '?'
            DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
        
        # Crear engine de SQLAlchemy con pool_pre_ping para mantener conexiones vivas
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,  # Verificar conexiones antes de usarlas
            connect_args={"connect_timeout": 10}
        )
        
        SessionLocal = sessionmaker(bind=engine)
        Base = declarative_base()
        
        # Probar conexión con manejo de errores mejorado
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("[DB] ✅ Conectado a PostgreSQL correctamente")
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
                raise
        
        USE_SQLALCHEMY = True
        USE_POSTGRESQL = True
    except ImportError as e:
        logger.error(f"[DB] ❌ SQLAlchemy no disponible: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"[DB] ❌ Error configurando PostgreSQL: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def get_db_connection():
    """
    Obtener conexión a la base de datos PostgreSQL
    Retorna una Session de SQLAlchemy que debe cerrarse con .close()
    
    SIEMPRE usa PostgreSQL - NO hay fallback a SQLite
    Lazy initialization: configura el engine solo cuando se necesita
    """
    # Lazy initialization: configurar el engine solo cuando se necesita
    if engine is None:
        _validate_and_setup_database()
    
    if not USE_POSTGRESQL or not USE_SQLALCHEMY:
        raise RuntimeError("[DB] ERROR: PostgreSQL no está configurado correctamente")
    
    # Retornar sesión de SQLAlchemy
    return SessionLocal()

@contextmanager
def get_db():
    """
    Context manager para obtener conexión a la base de datos PostgreSQL
    Se cierra automáticamente al salir del bloque
    
    Uso:
        with get_db() as session:
            # usar session
    """
    session = get_db_connection()
    try:
        yield session
    finally:
        session.close()  # Session de SQLAlchemy

def execute_query(query: str, params: Optional[Union[tuple, dict]] = None, fetch: bool = False):
    """
    Ejecutar query en PostgreSQL
    
    Args:
        query: SQL query (puede usar ? o :param)
        params: Tupla o diccionario de parámetros
        fetch: Si True, retorna resultados (fetchall)
    
    Returns:
        Si fetch=True: Lista de resultados
        Si fetch=False: Resultado de ejecución
    """
    session = SessionLocal()
    try:
        # Convertir ? a :param si es necesario
        if params and isinstance(params, tuple) and '?' in query:
            adapted_query = query
            param_dict = {}
            for i, param in enumerate(params):
                param_name = f'param{i}'
                adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                param_dict[param_name] = param
            query = adapted_query
            params = param_dict
        
        if params:
            result = session.execute(text(query), params)
        else:
            result = session.execute(text(query))
        
        if fetch:
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows] if rows else []
        else:
            session.commit()
            return result
    except Exception as e:
        session.rollback()
        logger.error(f"[DB] Error ejecutando query: {e}")
        raise
    finally:
        session.close()

def execute_many(query: str, params_list: list):
    """
    Ejecutar query múltiples veces en PostgreSQL
    """
    session = SessionLocal()
    try:
        stmt = text(query)
        for params in params_list:
            if isinstance(params, dict):
                session.execute(stmt, params)
            else:
                # Convertir tupla a dict si es necesario
                if isinstance(params, tuple) and '?' in query:
                    adapted_query = query
                    param_dict = {}
                    for i, param in enumerate(params):
                        param_name = f'param{i}'
                        adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                        param_dict[param_name] = param
                    session.execute(text(adapted_query), param_dict)
                else:
                    session.execute(stmt, params)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"[DB] Error ejecutando executemany: {e}")
        raise
    finally:
        session.close()

def get_lastrowid(cursor_or_result):
    """
    Obtener el último ID insertado de PostgreSQL
    Requiere que la query use RETURNING id
    """
    if hasattr(cursor_or_result, 'lastrowid'):
        return cursor_or_result.lastrowid
    return None

def ensure_tables():
    """
    Crear tablas si no existen en PostgreSQL
    DEPRECATED: Usar init_db() de init_db.py en su lugar
    """
    logger.warning("[DB] ensure_tables() está deprecado. Use init_db() de init_db.py")
    try:
        from init_db import init_db
        init_db()
    except ImportError:
        logger.error("[DB] No se pudo importar init_db. Las tablas deben crearse manualmente.")

# Función helper para adaptar queries SQLite a PostgreSQL
def adapt_query(query: str) -> str:
    """
    Adaptar query de SQLite a PostgreSQL
    """
    # Reemplazos comunes
    replacements = {
        'INTEGER PRIMARY KEY AUTOINCREMENT': 'SERIAL PRIMARY KEY',
        'AUTOINCREMENT': '',  # PostgreSQL usa SERIAL
        'DATETIME': 'TIMESTAMP',  # PostgreSQL usa TIMESTAMP
    }
    
    adapted = query
    for old, new in replacements.items():
        adapted = adapted.replace(old, new)
    
    return adapted

def execute_with_cursor(query: str, params: Optional[Union[tuple, dict]] = None):
    """
    Ejecutar query y retornar un objeto tipo cursor compatible
    Útil para código que espera cursor.execute(), cursor.fetchone(), etc.
    SIEMPRE usa PostgreSQL
    """
    from sqlalchemy import text
    
    class PostgresCursor:
        """Wrapper para simular cursor de SQLite con PostgreSQL"""
        def __init__(self, session, result=None):
            self.session = session
            self.result = result
            self._lastrowid = None
            self._rows = []
        
        def execute(self, query, params=None):
            # Adaptar query si es necesario
            if '?' in query and params:
                # Convertir ? a :param para PostgreSQL
                adapted_query = query
                param_dict = {}
                if isinstance(params, tuple):
                    for i, param in enumerate(params):
                        param_name = f'param{i}'
                        adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                        param_dict[param_name] = param
                    params = param_dict
            
            stmt = text(query if not isinstance(params, dict) else adapted_query)
            self.result = self.session.execute(stmt, params or {})
            
            # Intentar obtener lastrowid si es INSERT con RETURNING
            if 'INSERT' in query.upper() and 'RETURNING' in query.upper():
                row = self.result.fetchone()
                if row:
                    self._lastrowid = row[0] if hasattr(row, '__getitem__') else getattr(row, 'id', None)
            return self
        
        def fetchone(self):
            if self.result:
                row = self.result.fetchone()
                if row:
                    # Convertir a dict similar a sqlite3.Row
                    return type('Row', (), dict(row._mapping))()
            return None
        
        def fetchall(self):
            if self.result:
                rows = self.result.fetchall()
                # Convertir a lista de objetos Row
                return [type('Row', (), dict(row._mapping))() for row in rows]
            return []
        
        @property
        def lastrowid(self):
            return self._lastrowid
        
        def close(self):
            pass  # La sesión se cierra externamente
    
    session = SessionLocal()
    cursor = PostgresCursor(session)
    cursor.execute(query, params)
    return cursor, session

