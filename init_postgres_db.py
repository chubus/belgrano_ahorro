#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar base de datos PostgreSQL
Crea todas las tablas necesarias en PostgreSQL
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_postgres_database():
    """
    Inicializar base de datos PostgreSQL creando todas las tablas
    """
    database_url = os.getenv('DATABASE_URL', '')
    
    if not database_url or not (database_url.startswith('postgresql://') or database_url.startswith('postgres://')):
        logger.error("❌ DATABASE_URL no configurada o no es PostgreSQL")
        logger.error("   Configura DATABASE_URL antes de inicializar")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        
        # Parsear DATABASE_URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Conectar a PostgreSQL
        logger.info("🔗 Conectando a PostgreSQL...")
        engine = create_engine(database_url)
        
        # Leer script SQL
        sql_file = 'create_postgres_tables.sql'
        if not os.path.exists(sql_file):
            logger.error(f"❌ Archivo SQL no encontrado: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Ejecutar script
        logger.info("📦 Creando tablas en PostgreSQL...")
        with engine.connect() as conn:
            # Dividir script en statements individuales
            statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        logger.debug(f"✅ Ejecutado: {statement[:50]}...")
                    except Exception as e:
                        # Ignorar errores de "ya existe" pero loguear otros
                        if 'already exists' not in str(e).lower() and 'duplicate' not in str(e).lower():
                            logger.warning(f"⚠️  Error ejecutando statement: {e}")
            
            conn.commit()
        
        logger.info("✅ Base de datos PostgreSQL inicializada correctamente")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        logger.error("   Asegúrate de tener instalado: sqlalchemy y psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    logger.info("🚀 Inicializando base de datos PostgreSQL")
    logger.info("=" * 60)
    
    success = init_postgres_database()
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Inicialización completada exitosamente")
    else:
        logger.error("=" * 60)
        logger.error("❌ Inicialización falló")
        sys.exit(1)

