#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capa de abstracción de base de datos
Soporta SQLite (desarrollo) y PostgreSQL (producción)
"""

import os
import logging
from typing import Optional, Any, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Detectar qué tipo de base de datos usar
DATABASE_URL = os.getenv('DATABASE_URL', '')

# Si DATABASE_URL está configurada y es PostgreSQL, usar SQLAlchemy
USE_POSTGRESQL = (
    DATABASE_URL and 
    (DATABASE_URL.startswith('postgresql://') or DATABASE_URL.startswith('postgres://'))
)

if USE_POSTGRESQL:
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
        
        logger.info("✅ Configurado para usar PostgreSQL")
        USE_SQLALCHEMY = True
    except ImportError as e:
        logger.warning(f"⚠️ SQLAlchemy no disponible ({e}), usando SQLite")
        USE_SQLALCHEMY = False
        USE_POSTGRESQL = False
        engine = None
        SessionLocal = None
        Base = None
else:
    USE_SQLALCHEMY = False
    engine = None
    SessionLocal = None
    Base = None
    logger.info("ℹ️ Usando SQLite (desarrollo)")

def get_db_connection():
    """
    Obtener conexión a la base de datos
    Retorna conexión compatible (SQLite o SQLAlchemy Session)
    
    NOTA: Para PostgreSQL retorna una Session que debe cerrarse con .close()
    Para SQLite retorna una Connection que debe cerrarse con .close()
    """
    if USE_POSTGRESQL and USE_SQLALCHEMY:
        # Retornar sesión de SQLAlchemy
        return SessionLocal()
    else:
        # Retornar conexión SQLite tradicional
        import sqlite3
        db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

@contextmanager
def get_db():
    """
    Context manager para obtener conexión a la base de datos
    Se cierra automáticamente al salir del bloque
    
    Uso:
        with get_db() as conn:
            # usar conn
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        if USE_POSTGRESQL and USE_SQLALCHEMY:
            conn.close()  # Session de SQLAlchemy
        else:
            conn.close()  # Connection de SQLite

def execute_query(query: str, params: Optional[Union[tuple, dict]] = None, fetch: bool = False):
    """
    Ejecutar query de forma compatible con SQLite y PostgreSQL
    
    Args:
        query: SQL query (puede usar ? para SQLite o :param para ambos)
        params: Tupla o diccionario de parámetros
        fetch: Si True, retorna resultados (fetchall)
    
    Returns:
        Si fetch=True: Lista de resultados
        Si fetch=False: Cursor o resultado de ejecución
    """
    # Normalizar query para compatibilidad
    # SQLite usa ? pero PostgreSQL prefiere :param, SQLAlchemy maneja ambos
    if USE_POSTGRESQL and USE_SQLALCHEMY:
        session = SessionLocal()
        try:
            if params:
                if isinstance(params, dict):
                    result = session.execute(text(query), params)
                else:
                    # Convertir tupla a dict si es necesario
                    result = session.execute(text(query), params)
            else:
                result = session.execute(text(query))
            
            if fetch:
                rows = result.fetchall()
                # Convertir a formato similar a sqlite3.Row
                return [dict(row._mapping) for row in rows] if rows else []
            else:
                session.commit()
                return result
        except Exception as e:
            session.rollback()
            logger.error(f"Error ejecutando query: {e}")
            raise
        finally:
            session.close()
    else:
        import sqlite3
        db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                rows = cursor.fetchall()
                return [dict(row) for row in rows] if rows else []
            else:
                conn.commit()
                return cursor
        except Exception as e:
            conn.rollback()
            logger.error(f"Error ejecutando query: {e}")
            raise
        finally:
            conn.close()

def execute_many(query: str, params_list: list):
    """
    Ejecutar query múltiples veces (executemany)
    Compatible con SQLite y PostgreSQL
    """
    if USE_POSTGRESQL and USE_SQLALCHEMY:
        session = SessionLocal()
        try:
            stmt = text(query)
            for params in params_list:
                if isinstance(params, dict):
                    session.execute(stmt, params)
                else:
                    session.execute(stmt, params)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error ejecutando executemany: {e}")
            raise
        finally:
            session.close()
    else:
        import sqlite3
        db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error ejecutando executemany: {e}")
            raise
        finally:
            conn.close()

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
    Crear tablas si no existen (compatible con SQLite y PostgreSQL)
    """
    if USE_POSTGRESQL and USE_SQLALCHEMY:
        # Crear tablas usando SQLAlchemy
        # Por ahora, usar las funciones de db.py pero adaptadas
        logger.info("⚠️ ensure_tables() con PostgreSQL requiere definición de modelos SQLAlchemy")
        logger.info("   Por ahora, las tablas se crearán automáticamente al usar la API")
    else:
        # Usar función tradicional de db.py
        try:
            import db as database
            database.inicializar_base_datos()
            logger.info("✅ Tablas verificadas/creadas en SQLite")
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")

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

