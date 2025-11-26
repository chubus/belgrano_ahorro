#!/usr/bin/env python3
"""
Migración automática: Asegurar columnas image_url en todas las tablas
Se ejecuta automáticamente al iniciar la aplicación
"""
import os
import logging

logger = logging.getLogger(__name__)

def ensure_image_columns():
    """Asegurar que las columnas de imagen existen en todas las tablas"""
    try:
        # Detectar tipo de base de datos
        db_url = os.environ.get('DATABASE_URL', '')
        
        if not db_url or 'sqlite' in db_url.lower():
            logger.info("📁 Base de datos SQLite detectada - verificando columnas de imagen")
            ensure_image_columns_sqlite()
        elif 'postgres' in db_url.lower():
            logger.info("🐘 Base de datos PostgreSQL detectada - verificando columnas de imagen")
            ensure_image_columns_postgres()
        else:
            logger.warning(f"⚠️ Tipo de base de datos desconocido: {db_url[:50]}...")
            
    except Exception as e:
        logger.error(f"❌ Error en migración automática de columnas: {e}")
        # No fallar el inicio de la aplicación por esto
        logger.warning("⚠️ La aplicación continuará pero las funciones de imagen pueden fallar")

def ensure_image_columns_sqlite():
    """Asegurar columnas de imagen en SQLite"""
    import sqlite3
    
    # Buscar base de datos SQLite
    db_paths = [
        os.environ.get('TICKETS_DB_PATH', 'belgrano_tickets.db'),
        'belgrano_ahorro.db',
        './belgrano_ahorro.db',
        '../belgrano_ahorro.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Tablas a verificar
                tables = ['negocios', 'sucursales', 'productos']
                
                for table in tables:
                    # Verificar si la tabla existe
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if not cursor.fetchone():
                        continue
                    
                    # Obtener columnas existentes
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # Agregar image_url si no existe
                    if 'image_url' not in columns:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN image_url TEXT")
                        logger.info(f"✅ Agregada columna 'image_url' a tabla '{table}' en {db_path}")
                    
                    # Agregar imagen si no existe (para compatibilidad)
                    if 'imagen' not in columns:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN imagen TEXT")
                        logger.info(f"✅ Agregada columna 'imagen' a tabla '{table}' en {db_path}")
                
                conn.commit()
                conn.close()
                logger.info(f"✅ Migración SQLite completada para {db_path}")
                
            except Exception as e:
                logger.error(f"❌ Error migrando {db_path}: {e}")

def ensure_image_columns_postgres():
    """Asegurar columnas de imagen en PostgreSQL"""
    try:
        import psycopg2
        from urllib.parse import urlparse
    except ImportError:
        logger.error("❌ psycopg2 no está instalado - no se puede migrar PostgreSQL")
        return
    
    db_url = os.environ.get('DATABASE_URL', '')
    
    # Convertir URL si es necesario
    if db_url.startswith('postgresql+psycopg2://'):
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql://', 1)
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Tablas a verificar
        tables = ['negocios', 'sucursales', 'productos']
        
        for table in tables:
            # Verificar si image_url existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name=%s AND column_name='image_url'
                )
            """, (table,))
            
            if not cursor.fetchone()[0]:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN image_url TEXT")
                logger.info(f"✅ Agregada columna 'image_url' a tabla '{table}'")
            
            # Verificar si imagen existe (para compatibilidad)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name=%s AND column_name='imagen'
                )
            """, (table,))
            
            if not cursor.fetchone()[0]:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN imagen TEXT")
                logger.info(f"✅ Agregada columna 'imagen' a tabla '{table}'")
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✅ Migración PostgreSQL completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error migrando PostgreSQL: {e}")
        raise

if __name__ == '__main__':
    # Configurar logging básico para ejecución standalone
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    ensure_image_columns()
