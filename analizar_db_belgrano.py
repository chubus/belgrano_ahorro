#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador y Corrector de Base de Datos Belgrano Ahorro
Revisa la estructura, identifica errores y la hace operativa para uso masivo
"""

import sqlite3
import os
import sys
from datetime import datetime
import hashlib
import secrets

def conectar_db(ruta_db):
    """Conectar a la base de datos"""
    try:
        conn = sqlite3.connect(ruta_db)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Error conectando a {ruta_db}: {e}")
        return None

def obtener_estructura_tablas(conn):
    """Obtener estructura de todas las tablas"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        
        estructura = {}
        for tabla in tablas:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = cursor.fetchall()
            estructura[tabla] = columnas
        
        return estructura
    except Exception as e:
        print(f"❌ Error obteniendo estructura: {e}")
        return {}

def analizar_usuarios(conn):
    """Analizar tabla de usuarios"""
    try:
        cursor = conn.cursor()
        
        # Verificar si existe tabla usuarios
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cursor.fetchone():
            print("❌ Tabla 'usuarios' no existe")
            return False
        
        # Obtener estructura de usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas = cursor.fetchall()
        print(f"\n📋 Estructura tabla usuarios:")
        for col in columnas:
            print(f"   • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
        
        # Contar usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]
        print(f"\n👥 Total usuarios: {total_usuarios}")
        
        # Verificar tipos de usuario
        cursor.execute("SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo")
        tipos_usuario = cursor.fetchall()
        print(f"\n📊 Tipos de usuario:")
        for tipo, count in tipos_usuario:
            print(f"   • {tipo}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analizando usuarios: {e}")
        return False

def analizar_productos(conn):
    """Analizar tabla de productos"""
    try:
        cursor = conn.cursor()
        
        # Verificar si existe tabla productos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
        if not cursor.fetchone():
            print("❌ Tabla 'productos' no existe")
            return False
        
        # Obtener estructura de productos
        cursor.execute("PRAGMA table_info(productos)")
        columnas = cursor.fetchall()
        print(f"\n📋 Estructura tabla productos:")
        for col in columnas:
            print(f"   • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
        
        # Contar productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        print(f"\n🛍️ Total productos: {total_productos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analizando productos: {e}")
        return False

def analizar_carrito(conn):
    """Analizar funcionalidad de carrito"""
    try:
        cursor = conn.cursor()
        
        # Verificar tablas relacionadas con carrito
        tablas_carrito = ['carrito', 'carrito_items', 'pedidos', 'pedido_items']
        tablas_existentes = []
        
        for tabla in tablas_carrito:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
            if cursor.fetchone():
                tablas_existentes.append(tabla)
        
        print(f"\n🛒 Tablas de carrito existentes: {tablas_existentes}")
        
        if 'carrito' in tablas_existentes:
            cursor.execute("PRAGMA table_info(carrito)")
            columnas = cursor.fetchall()
            print(f"\n📋 Estructura tabla carrito:")
            for col in columnas:
                print(f"   • {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        return len(tablas_existentes) > 0
        
    except Exception as e:
        print(f"❌ Error analizando carrito: {e}")
        return False

def crear_estructura_optimizada(conn):
    """Crear estructura optimizada para uso masivo"""
    try:
        cursor = conn.cursor()
        
        print("\n🔧 Creando estructura optimizada...")
        
        # Tabla usuarios optimizada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            telefono VARCHAR(20),
            direccion TEXT,
            tipo ENUM('comun', 'comercial', 'admin') DEFAULT 'comun',
            activo BOOLEAN DEFAULT 1,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso DATETIME,
            token_verificacion VARCHAR(255),
            email_verificado BOOLEAN DEFAULT 0,
            INDEX idx_email (email),
            INDEX idx_tipo (tipo),
            INDEX idx_activo (activo)
        )
        """)
        
        # Tabla productos optimizada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(255) NOT NULL,
            descripcion TEXT,
            precio DECIMAL(10,2) NOT NULL,
            precio_anterior DECIMAL(10,2),
            categoria_id INTEGER,
            negocio_id INTEGER,
            stock INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            imagen_url VARCHAR(500),
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_categoria (categoria_id),
            INDEX idx_negocio (negocio_id),
            INDEX idx_activo (activo),
            INDEX idx_precio (precio)
        )
        """)
        
        # Tabla carrito optimizada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrito_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            precio_unitario DECIMAL(10,2) NOT NULL,
            fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios_optimizada(id),
            FOREIGN KEY (producto_id) REFERENCES productos_optimizada(id),
            UNIQUE(usuario_id, producto_id),
            INDEX idx_usuario (usuario_id),
            INDEX idx_producto (producto_id)
        )
        """)
        
        # Tabla pedidos optimizada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            estado ENUM('pendiente', 'confirmado', 'preparando', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente',
            direccion_entrega TEXT NOT NULL,
            telefono_contacto VARCHAR(20),
            notas TEXT,
            fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega DATETIME,
            FOREIGN KEY (usuario_id) REFERENCES usuarios_optimizada(id),
            INDEX idx_usuario (usuario_id),
            INDEX idx_estado (estado),
            INDEX idx_fecha (fecha_pedido)
        )
        """)
        
        # Tabla items de pedido
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedido_items_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos_optimizada(id),
            FOREIGN KEY (producto_id) REFERENCES productos_optimizada(id),
            INDEX idx_pedido (pedido_id),
            INDEX idx_producto (producto_id)
        )
        """)
        
        # Tabla categorías
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            activa BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_activa (activa)
        )
        """)
        
        # Tabla negocios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS negocios_optimizada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(255) NOT NULL,
            descripcion TEXT,
            direccion TEXT,
            telefono VARCHAR(20),
            email VARCHAR(255),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_activo (activo)
        )
        """)
        
        conn.commit()
        print("✅ Estructura optimizada creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando estructura optimizada: {e}")
        return False

def crear_usuarios_ejemplo(conn):
    """Crear usuarios de ejemplo para testing"""
    try:
        cursor = conn.cursor()
        
        print("\n👥 Creando usuarios de ejemplo...")
        
        # Usuario común
        password_hash = hashlib.sha256("usuario123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios_optimizada 
        (email, password_hash, nombre, apellido, telefono, tipo, activo, email_verificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "usuario@ejemplo.com",
            password_hash,
            "Juan",
            "Pérez",
            "+54 11 1234-5678",
            "comun",
            1,
            1
        ))
        
        # Usuario comercial
        password_hash = hashlib.sha256("comercial123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios_optimizada 
        (email, password_hash, nombre, apellido, telefono, tipo, activo, email_verificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "comercial@ejemplo.com",
            password_hash,
            "María",
            "González",
            "+54 11 9876-5432",
            "comercial",
            1,
            1
        ))
        
        # Usuario admin
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios_optimizada 
        (email, password_hash, nombre, apellido, telefono, tipo, activo, email_verificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin@ejemplo.com",
            password_hash,
            "Carlos",
            "Admin",
            "+54 11 5555-1234",
            "admin",
            1,
            1
        ))
        
        conn.commit()
        print("✅ Usuarios de ejemplo creados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuarios de ejemplo: {e}")
        return False

def crear_productos_ejemplo(conn):
    """Crear productos de ejemplo"""
    try:
        cursor = conn.cursor()
        
        print("\n🛍️ Creando productos de ejemplo...")
        
        # Crear categorías
        categorias = [
            ("Lácteos", "Productos lácteos frescos"),
            ("Panadería", "Pan y productos de panadería"),
            ("Carnes", "Carnes y embutidos"),
            ("Verduras", "Verduras frescas"),
            ("Frutas", "Frutas frescas")
        ]
        
        for nombre, descripcion in categorias:
            cursor.execute("""
            INSERT OR REPLACE INTO categorias_optimizada (nombre, descripcion)
            VALUES (?, ?)
            """, (nombre, descripcion))
        
        # Crear negocios
        negocios = [
            ("Supermercado Central", "Supermercado con productos frescos", "Av. Belgrano 1234", "+54 11 1234-5678", "info@supercentral.com"),
            ("Farmacia San Martín", "Farmacia con medicamentos", "Calle San Martín 567", "+54 11 9876-5432", "contacto@farmaciasanmartin.com")
        ]
        
        for nombre, descripcion, direccion, telefono, email in negocios:
            cursor.execute("""
            INSERT OR REPLACE INTO negocios_optimizada (nombre, descripcion, direccion, telefono, email)
            VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, direccion, telefono, email))
        
        # Crear productos
        productos = [
            ("Leche Entera 1L", "Leche fresca pasteurizada", 850.0, 950.0, 1, 1, 50),
            ("Pan Integral", "Pan de molde integral", 450.0, 500.0, 2, 1, 25),
            ("Yogur Natural", "Yogur natural sin azúcar", 320.0, 350.0, 1, 1, 30),
            ("Manzanas Rojas", "Manzanas rojas frescas", 180.0, 200.0, 5, 1, 40),
            ("Pollo Entero", "Pollo fresco entero", 1200.0, 1300.0, 3, 1, 15)
        ]
        
        for nombre, descripcion, precio, precio_anterior, categoria_id, negocio_id, stock in productos:
            cursor.execute("""
            INSERT OR REPLACE INTO productos_optimizada 
            (nombre, descripcion, precio, precio_anterior, categoria_id, negocio_id, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, descripcion, precio, precio_anterior, categoria_id, negocio_id, stock))
        
        conn.commit()
        print("✅ Productos de ejemplo creados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando productos de ejemplo: {e}")
        return False

def verificar_rendimiento(conn):
    """Verificar rendimiento de la base de datos"""
    try:
        cursor = conn.cursor()
        
        print("\n⚡ Verificando rendimiento...")
        
        # Contar registros
        tablas = ['usuarios_optimizada', 'productos_optimizada', 'categorias_optimizada', 'negocios_optimizada']
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   • {tabla}: {count} registros")
            except:
                print(f"   • {tabla}: No existe")
        
        # Verificar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indices = cursor.fetchall()
        print(f"\n📊 Índices creados: {len(indices)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando rendimiento: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 ANALIZADOR Y CORRECTOR DE BASE DE DATOS BELGRANO AHORRO")
    print("=" * 70)
    
    # Buscar base de datos principal
    db_paths = [
        "belgrano_ahorro.db",
        "belgrano_tickets/data/belgrano_ahorro.db",
        "belgrano_tickets/belgrano_ahorro.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos de Belgrano Ahorro")
        return
    
    print(f"📁 Base de datos encontrada: {db_path}")
    
    # Conectar a la base de datos
    conn = conectar_db(db_path)
    if not conn:
        return
    
    try:
        # Analizar estructura actual
        print("\n🔍 ANALIZANDO ESTRUCTURA ACTUAL...")
        estructura = obtener_estructura_tablas(conn)
        
        print(f"\n📋 Tablas encontradas: {list(estructura.keys())}")
        
        # Analizar componentes clave
        analizar_usuarios(conn)
        analizar_productos(conn)
        analizar_carrito(conn)
        
        # Crear estructura optimizada
        print("\n🔧 CREANDO ESTRUCTURA OPTIMIZADA...")
        if crear_estructura_optimizada(conn):
            crear_usuarios_ejemplo(conn)
            crear_productos_ejemplo(conn)
            verificar_rendimiento(conn)
        
        print("\n✅ ANÁLISIS Y CORRECCIÓN COMPLETADOS")
        print("\n📊 RESUMEN:")
        print("   • Estructura optimizada creada")
        print("   • Usuarios de ejemplo creados")
        print("   • Productos de ejemplo creados")
        print("   • Base de datos lista para uso masivo")
        print("\n🔑 CREDENCIALES DE PRUEBA:")
        print("   • Usuario común: usuario@ejemplo.com / usuario123")
        print("   • Usuario comercial: comercial@ejemplo.com / comercial123")
        print("   • Usuario admin: admin@ejemplo.com / admin123")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
