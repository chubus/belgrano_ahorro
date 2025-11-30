#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cargar solo datos mínimos necesarios en PostgreSQL
Los datos reales se obtienen desde las APIs de Belgrano Ahorro, Ticketera y DevOps
"""

import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def load_initial_data():
    """
    Cargar solo datos mínimos necesarios (usuario admin)
    Los datos reales (negocios, productos, ofertas, categorías, sucursales)
    se obtienen desde las APIs de Belgrano Ahorro, Ticketera y DevOps
    """
    logger.info("[DB] Verificando si se necesita crear usuario administrador...")
    
    try:
        # Obtener engine desde init_db o db_abstraction
        try:
            from init_db import _engine as engine
            if engine is None:
                # Intentar obtener desde db_abstraction
                from db_abstraction import engine as engine_alt
                engine = engine_alt
        except (ImportError, AttributeError):
            # Fallback: obtener desde db_abstraction directamente
            try:
                from db_abstraction import engine
            except ImportError:
                logger.warning("[DB] ⚠️ No se pudo importar engine. Saltando carga de datos iniciales.")
                return
        
        if engine is None:
            logger.warning("[DB] ⚠️ Engine no está inicializado. Saltando carga de datos iniciales.")
            return
        
        with engine.connect() as conn:
            # 🔒 PREVENCIÓN DE DEADLOCKS: Usar Advisory Lock de PostgreSQL
            # Esto evita que múltiples workers intenten inicializar datos simultáneamente
            # El ID 8675309 es arbitrario pero fijo para esta tarea
            try:
                lock_acquired = conn.execute(text("SELECT pg_try_advisory_lock(8675309)")).scalar()
                if not lock_acquired:
                    logger.info("[DB] ⏳ Otro proceso ya está inicializando datos (Lock ocupado). Saltando...")
                    return
                
                logger.info("[DB] 🔒 Lock de inicialización adquirido. Verificando datos...")

                # Verificar si ya existe un usuario admin
                result = conn.execute(text('''
                    SELECT COUNT(*) FROM usuarios WHERE email = 'admin@belgrano.com'
                '''))
                admin_exists = result.scalar() > 0
                
                if not admin_exists:
                    logger.info("[DB] Creando usuario administrador mínimo...")
                    
                    # Crear usuario administrador
                    from db import hash_password
                    hashed_password = hash_password('admin123')
                    conn.execute(text('''
                        INSERT INTO usuarios (email, password_hash, nombre, apellido, rol, activo)
                        VALUES ('admin@belgrano.com', :password_hash, 'Admin', 'Belgrano', 'admin', TRUE)
                        ON CONFLICT (email) DO NOTHING
                    '''), {'password_hash': hashed_password})
                    
                    conn.commit()
                    logger.info("[DB] ✅ Usuario admin creado (email: admin@belgrano.com, password: admin123)")
                    logger.info("[DB] ℹ️ Los datos reales se obtendrán desde las APIs:")
                    logger.info("[DB]    - Belgrano Ahorro: https://belgranoahorro-aliq.onrender.com")
                    logger.info("[DB]    - Ticketera: https://ticketerabelgrano.onrender.com")
                    logger.info("[DB]    - DevOps: Gestión de datos desde dashboard")
                else:
                    logger.info("[DB] ℹ️ Usuario admin ya existe")
                
                # Verificar estado de la base de datos
                result = conn.execute(text('SELECT COUNT(*) FROM negocios'))
                count_negocios = result.scalar()
                
                result = conn.execute(text('SELECT COUNT(*) FROM productos'))
                count_productos = result.scalar()
                
                result = conn.execute(text('SELECT COUNT(*) FROM ofertas'))
                count_ofertas = result.scalar()
                
                result = conn.execute(text('SELECT COUNT(*) FROM categorias'))
                count_categorias = result.scalar()
                
                if count_negocios == 0 and count_productos == 0:
                    logger.info("[DB] ℹ️ Base de datos vacía - Los datos se cargarán desde:")
                    logger.info("[DB]    1. DevOps Dashboard: Crear negocios, productos, ofertas")
                    logger.info("[DB]    2. APIs de Belgrano Ahorro y Ticketera")
                    logger.info("[DB]    3. Sincronización automática entre servicios")
                else:
                    logger.info(f"[DB] ℹ️ Base de datos tiene datos: {count_negocios} negocios, {count_productos} productos, {count_ofertas} ofertas, {count_categorias} categorías")

            finally:
                # Liberar el lock siempre, incluso si hay error
                conn.execute(text("SELECT pg_advisory_unlock(8675309)"))
                logger.info("[DB] 🔓 Lock de inicialización liberado")
                
    except Exception as e:
        logger.error(f"[DB] ❌ Error cargando datos iniciales: {e}")
        import traceback
        logger.error(traceback.format_exc())

