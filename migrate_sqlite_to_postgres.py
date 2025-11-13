#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración de SQLite a PostgreSQL
Migra todos los datos de belgrano_ahorro.db a PostgreSQL
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_sqlite_to_postgres():
    """
    Migrar datos de SQLite a PostgreSQL
    """
    # Verificar que DATABASE_URL está configurada
    database_url = os.getenv('DATABASE_URL', '')
    if not database_url or not (database_url.startswith('postgresql://') or database_url.startswith('postgres://')):
        logger.error("❌ DATABASE_URL no configurada o no es PostgreSQL")
        logger.error("   Configura DATABASE_URL con la URL de PostgreSQL antes de migrar")
        return False
    
    # Verificar que el archivo SQLite existe
    sqlite_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
    if not os.path.exists(sqlite_path):
        logger.error(f"❌ Archivo SQLite no encontrado: {sqlite_path}")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        from psycopg2.extras import execute_values
        import psycopg2
        
        # Parsear DATABASE_URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Conectar a PostgreSQL
        logger.info("🔗 Conectando a PostgreSQL...")
        pg_engine = create_engine(database_url)
        pg_conn = pg_engine.raw_connection()
        pg_cursor = pg_conn.cursor()
        
        # Conectar a SQLite
        logger.info(f"🔗 Conectando a SQLite: {sqlite_path}")
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Lista de tablas a migrar (en orden de dependencias)
        tables = [
            'usuarios',
            'negocios',
            'categorias',
            'productos',
            'sucursales',
            'ofertas',
            'pedidos',
            'pedido_items',
            'carrito',
            'tickets',
            'comerciantes',
            'paquetes_comerciantes',
            'paquete_items'
        ]
        
        total_migrated = 0
        
        for table in tables:
            try:
                # Verificar que la tabla existe en SQLite
                sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not sqlite_cursor.fetchone():
                    logger.info(f"⏭️  Tabla {table} no existe en SQLite, saltando...")
                    continue
                
                # Obtener datos de SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    logger.info(f"ℹ️  Tabla {table} está vacía, saltando...")
                    continue
                
                # Obtener nombres de columnas
                column_names = [description[0] for description in sqlite_cursor.description]
                
                # Convertir filas a tuplas
                data_tuples = [tuple(row) for row in rows]
                
                # Crear query de inserción
                columns_str = ', '.join(column_names)
                placeholders = ', '.join(['%s'] * len(column_names))
                insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                
                # Insertar en PostgreSQL
                logger.info(f"📦 Migrando {len(rows)} registros de {table}...")
                execute_values(
                    pg_cursor,
                    insert_query,
                    data_tuples,
                    template=None,
                    page_size=100
                )
                
                total_migrated += len(rows)
                logger.info(f"✅ {table}: {len(rows)} registros migrados")
                
            except Exception as e:
                logger.error(f"❌ Error migrando tabla {table}: {e}")
                # Continuar con las demás tablas
                continue
        
        # Commit cambios
        pg_conn.commit()
        
        # Cerrar conexiones
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()
        
        logger.info(f"✅ Migración completada: {total_migrated} registros migrados en total")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        logger.error("   Asegúrate de tener instalado: psycopg2-binary y sqlalchemy")
        return False
    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def verify_migration():
    """
    Verificar que la migración fue exitosa
    """
    database_url = os.getenv('DATABASE_URL', '')
    if not database_url:
        logger.error("❌ DATABASE_URL no configurada")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Contar registros en cada tabla
            tables = ['usuarios', 'negocios', 'categorias', 'productos', 'sucursales', 'ofertas', 'pedidos']
            
            logger.info("📊 Verificando migración...")
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"   {table}: {count} registros")
                except Exception as e:
                    logger.warning(f"   {table}: Error al contar ({e})")
        
        logger.info("✅ Verificación completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando migración: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrar datos de SQLite a PostgreSQL')
    parser.add_argument('--verify', action='store_true', help='Solo verificar migración (no migrar)')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    else:
        logger.info("🚀 Iniciando migración SQLite → PostgreSQL")
        logger.info("=" * 60)
        
        success = migrate_sqlite_to_postgres()
        
        if success:
            logger.info("=" * 60)
            logger.info("✅ Migración completada exitosamente")
            logger.info("")
            logger.info("📋 Verificar migración con:")
            logger.info("   python migrate_sqlite_to_postgres.py --verify")
        else:
            logger.error("=" * 60)
            logger.error("❌ Migración falló")
            sys.exit(1)

