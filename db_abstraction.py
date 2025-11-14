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
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    if not DATABASE_URL:
        raise ValueError("[DB] ERROR: DATABASE_URL no configurada. Configure DATABASE_URL en Render Dashboard.")

logger = logging.getLogger(__name__)

# SIEMPRE usar PostgreSQL - NO hay fallback
try:
    from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, DECIMAL, TEXT
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.pool import NullPool
    from sqlalchemy.dialects.postgresql import insert
    import urllib.parse
    
    # Parsear DATABASE_URL (Render puede venir con postgres:// que necesita convertirse)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Crear engine de SQLAlchemy
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Sin pool para evitar problemas de conexión
        echo=False,
        connect_args={"connect_timeout": 10}
    )
    
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()
    
    logger.info("[DB] ✅ Configurado para usar PostgreSQL (obligatorio)")
    USE_SQLALCHEMY = True
    USE_POSTGRESQL = True
except ImportError as e:
    logger.error(f"[DB] ❌ SQLAlchemy no disponible: {e}")
    raise
except Exception as e:
    logger.error(f"[DB] ❌ Error configurando PostgreSQL: {e}")
    raise

def get_db_connection():
    """
    Obtener conexión a la base de datos PostgreSQL
    Retorna una Session de SQLAlchemy que debe cerrarse con .close()
    
    SIEMPRE usa PostgreSQL - NO hay fallback a SQLite
    """
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
    Obtener el último ID insertado
    Compatible con SQLite y PostgreSQL
    """
    if USE_POSTGRESQL and USE_SQLALCHEMY:
        # En PostgreSQL, usar RETURNING o lastrowid del resultado
        if hasattr(cursor_or_result, 'lastrowid'):
            return cursor_or_result.lastrowid
        # Si no, necesitamos obtenerlo de otra forma
        return None
    else:
        # SQLite
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
    Adaptar query de SQLite a PostgreSQL si es necesario
    """
    if not USE_POSTGRESQL:
        return query
    
    # Reemplazos comunes
    replacements = {
        'INTEGER PRIMARY KEY AUTOINCREMENT': 'SERIAL PRIMARY KEY',
        'AUTOINCREMENT': '',  # PostgreSQL usa SERIAL
        'BOOLEAN': 'BOOLEAN',  # Mismo
        'TEXT': 'TEXT',  # Mismo
        'VARCHAR': 'VARCHAR',  # Mismo
        'DECIMAL': 'DECIMAL',  # Mismo
        'DATETIME': 'TIMESTAMP',  # PostgreSQL usa TIMESTAMP
        'CURRENT_TIMESTAMP': 'CURRENT_TIMESTAMP',  # Mismo
    }
    
    adapted = query
    for old, new in replacements.items():
        adapted = adapted.replace(old, new)
    
    return adapted

def execute_with_cursor(query: str, params: Optional[Union[tuple, dict]] = None):
    """
    Ejecutar query y retornar un objeto tipo cursor compatible
    Útil para código que espera cursor.execute(), cursor.fetchone(), etc.
    """
    if USE_POSTGRESQL and USE_SQLALCHEMY:
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
                
                # Intentar obtener lastrowid si es INSERT
                if 'INSERT' in query.upper():
                    # En PostgreSQL, usar RETURNING
                    if 'RETURNING' not in query.upper():
                        # No podemos obtener ID sin RETURNING, pero intentamos
                        pass
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
    else:
        import sqlite3
        db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor, conn

