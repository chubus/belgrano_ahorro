#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicialización centralizada de la base de datos PostgreSQL
Crea todas las tablas necesarias si no existen
"""

import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import NullPool
from config import DATABASE_URL

# Logger con prefijo [DB]
logger = logging.getLogger(__name__)

def init_db():
    """
    Inicializar base de datos PostgreSQL
    Crea todas las tablas necesarias si no existen
    """
    logger.info("[DB] Iniciando inicialización de base de datos...")
    
    try:
        # Crear engine de SQLAlchemy
        engine = create_engine(
            DATABASE_URL,
            poolclass=NullPool,
            echo=False,
            connect_args={"connect_timeout": 10}
        )
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("[DB] ✅ Conexión a PostgreSQL establecida")
        
        # Crear tablas si no existen
        with engine.connect() as conn:
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
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
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
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre TEXT,
                    apellido TEXT,
                    telefono TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            logger.info("[DB] ✅ Tabla 'usuarios' verificada/creada")
            
            # Tabla pedidos (si no existe)
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    numero_pedido TEXT UNIQUE NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    metodo_pago TEXT,
                    direccion_entrega TEXT,
                    notas TEXT,
                    estado TEXT DEFAULT 'pendiente',
                    ticket_id INTEGER,
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
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            '''))
            logger.info("[DB] ✅ Tabla 'items_pedido' verificada/creada")
            
            conn.commit()
        
        logger.info("[DB] ✅ Todas las tablas verificadas/creadas correctamente")
        return engine
        
    except Exception as e:
        logger.error(f"[DB] ❌ Error inicializando base de datos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

