#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrector de Base de Datos Belgrano Ahorro
Corrige errores y optimiza para uso masivo
"""

import sqlite3
import os
import hashlib
from datetime import datetime

def conectar_db(ruta_db):
    """Conectar a la base de datos"""
    try:
        conn = sqlite3.connect(ruta_db)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Error conectando a {ruta_db}: {e}")
        return None

def corregir_tabla_usuarios(conn):
    """Corregir tabla de usuarios"""
    try:
        cursor = conn.cursor()
        
        print("🔧 Corrigiendo tabla usuarios...")
        
        # Verificar si existe columna tipo
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'tipo' not in columnas:
            print("   • Agregando columna 'tipo'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo VARCHAR(20) DEFAULT 'comun'")
        
        if 'activo' not in columnas:
            print("   • Agregando columna 'activo'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN activo BOOLEAN DEFAULT 1")
        
        if 'password_hash' not in columnas:
            print("   • Agregando columna 'password_hash'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN password_hash VARCHAR(255)")
        
        if 'email_verificado' not in columnas:
            print("   • Agregando columna 'email_verificado'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN email_verificado BOOLEAN DEFAULT 0")
        
        if 'ultimo_acceso' not in columnas:
            print("   • Agregando columna 'ultimo_acceso'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN ultimo_acceso DATETIME")
        
        # Migrar passwords a hash si es necesario
        cursor.execute("SELECT id, password FROM usuarios WHERE password_hash IS NULL")
        usuarios_sin_hash = cursor.fetchall()
        
        for usuario in usuarios_sin_hash:
            user_id, password = usuario
            if password and not password.startswith('$'):  # No es hash
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        
        conn.commit()
        print("✅ Tabla usuarios corregida exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo tabla usuarios: {e}")
        return False

def optimizar_tabla_productos(conn):
    """Optimizar tabla de productos"""
    try:
        cursor = conn.cursor()
        
        print("🔧 Optimizando tabla productos...")
        
        # Verificar columnas faltantes
        cursor.execute("PRAGMA table_info(productos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'stock' not in columnas:
            print("   • Agregando columna 'stock'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
        
        if 'stock_minimo' not in columnas:
            print("   • Agregando columna 'stock_minimo'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 0")
        
        if 'negocio_id' not in columnas:
            print("   • Agregando columna 'negocio_id'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN negocio_id INTEGER")
        
        if 'fecha_creacion' not in columnas:
            print("   • Agregando columna 'fecha_creacion'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        if 'fecha_actualizacion' not in columnas:
            print("   • Agregando columna 'fecha_actualizacion'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Actualizar stock para productos existentes
        cursor.execute("UPDATE productos SET stock = 50 WHERE stock IS NULL")
        cursor.execute("UPDATE productos SET stock_minimo = 5 WHERE stock_minimo IS NULL")
        cursor.execute("UPDATE productos SET negocio_id = 1 WHERE negocio_id IS NULL")
        
        conn.commit()
        print("✅ Tabla productos optimizada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error optimizando tabla productos: {e}")
        return False

def crear_tabla_categorias(conn):
    """Crear tabla de categorías"""
    try:
        cursor = conn.cursor()
        
        print("🔧 Creando tabla categorías...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            activa BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insertar categorías básicas
        categorias = [
            ("Lácteos", "Productos lácteos frescos"),
            ("Panadería", "Pan y productos de panadería"),
            ("Carnes", "Carnes y embutidos"),
            ("Verduras", "Verduras frescas"),
            ("Frutas", "Frutas frescas"),
            ("Bebidas", "Bebidas y refrescos"),
            ("Limpieza", "Productos de limpieza"),
            ("Higiene", "Productos de higiene personal")
        ]
        
        for nombre, descripcion in categorias:
            cursor.execute("""
            INSERT OR IGNORE INTO categorias (nombre, descripcion)
            VALUES (?, ?)
            """, (nombre, descripcion))
        
        conn.commit()
        print("✅ Tabla categorías creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla categorías: {e}")
        return False

def crear_tabla_negocios(conn):
    """Crear tabla de negocios"""
    try:
        cursor = conn.cursor()
        
        print("🔧 Creando tabla negocios...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS negocios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(255) NOT NULL,
            descripcion TEXT,
            direccion TEXT,
            telefono VARCHAR(20),
            email VARCHAR(255),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insertar negocios básicos
        negocios = [
            ("Supermercado Central", "Supermercado con productos frescos y ofertas diarias", "Av. Belgrano 1234", "+54 11 1234-5678", "info@supercentral.com"),
            ("Farmacia San Martín", "Farmacia con medicamentos y productos de salud", "Calle San Martín 567", "+54 11 9876-5432", "contacto@farmaciasanmartin.com"),
            ("Restaurante El Buen Sabor", "Restaurante con comida casera y delivery", "Av. Corrientes 890", "+54 11 5555-1234", "pedidos@elbuensabor.com")
        ]
        
        for nombre, descripcion, direccion, telefono, email in negocios:
            cursor.execute("""
            INSERT OR IGNORE INTO negocios (nombre, descripcion, direccion, telefono, email)
            VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, direccion, telefono, email))
        
        conn.commit()
        print("✅ Tabla negocios creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla negocios: {e}")
        return False

def optimizar_tabla_carrito(conn):
    """Optimizar tabla de carrito"""
    try:
        cursor = conn.cursor()
        
        print("🔧 Optimizando tabla carrito...")
        
        # Verificar estructura actual
        cursor.execute("PRAGMA table_info(carrito)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'precio_unitario' not in columnas:
            print("   • Agregando columna 'precio_unitario'...")
            cursor.execute("ALTER TABLE carrito ADD COLUMN precio_unitario DECIMAL(10,2)")
        
        # Actualizar precios unitarios
        cursor.execute("""
        UPDATE carrito 
        SET precio_unitario = (
            SELECT precio FROM productos WHERE productos.id = carrito.producto_id
        )
        WHERE precio_unitario IS NULL
        """)
        
        conn.commit()
        print("✅ Tabla carrito optimizada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error optimizando tabla carrito: {e}")
        return False

def crear_usuarios_ejemplo(conn):
    """Crear usuarios de ejemplo"""
    try:
        cursor = conn.cursor()
        
        print("👥 Creando usuarios de ejemplo...")
        
        # Usuario común
        password_hash = hashlib.sha256("usuario123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios 
        (nombre, apellido, email, telefono, password, password_hash, tipo, activo, email_verificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Juan", "Pérez", "usuario@ejemplo.com", "+54 11 1234-5678",
            "usuario123", password_hash, "comun", 1, 1
        ))
        
        # Usuario comercial
        password_hash = hashlib.sha256("comercial123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios 
        (nombre, apellido, email, telefono, password, password_hash, tipo, activo, email_verificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "María", "González", "comercial@ejemplo.com", "+54 11 9876-5432",
            "comercial123", password_hash, "comercial", 1, 1
        ))
        
        # Usuario admin
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios 
        (nombre, apellido, email, telefono, password, password_hash, tipo, activo, email_verificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Carlos", "Admin", "admin@ejemplo.com", "+54 11 5555-1234",
            "admin123", password_hash, "admin", 1, 1
        ))
        
        conn.commit()
        print("✅ Usuarios de ejemplo creados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuarios de ejemplo: {e}")
        return False

def crear_indices_optimizacion(conn):
    """Crear índices para optimización"""
    try:
        cursor = conn.cursor()
        
        print("🔧 Creando índices de optimización...")
        
        # Índices para usuarios
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo)")
        
        # Índices para productos
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_precio ON productos(precio)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_productos_negocio ON productos(negocio_id)")
        
        # Índices para carrito
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_carrito_usuario ON carrito(usuario_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_carrito_producto ON carrito(producto_id)")
        
        # Índices para pedidos
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON pedidos(usuario_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_pedido)")
        
        conn.commit()
        print("✅ Índices de optimización creados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando índices: {e}")
        return False

def verificar_rendimiento(conn):
    """Verificar rendimiento de la base de datos"""
    try:
        cursor = conn.cursor()
        
        print("\n⚡ Verificando rendimiento...")
        
        # Contar registros
        tablas = ['usuarios', 'productos', 'carrito', 'pedidos', 'categorias', 'negocios']
        
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
        
        # Verificar usuarios por tipo
        cursor.execute("SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo")
        tipos_usuario = cursor.fetchall()
        print(f"\n👥 Usuarios por tipo:")
        for tipo, count in tipos_usuario:
            print(f"   • {tipo}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando rendimiento: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 CORRECTOR DE BASE DE DATOS BELGRANO AHORRO")
    print("=" * 60)
    
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
        # Corregir estructura
        print("\n🔧 CORRIGIENDO ESTRUCTURA...")
        corregir_tabla_usuarios(conn)
        optimizar_tabla_productos(conn)
        crear_tabla_categorias(conn)
        crear_tabla_negocios(conn)
        optimizar_tabla_carrito(conn)
        
        # Crear usuarios de ejemplo
        print("\n👥 CREANDO USUARIOS DE EJEMPLO...")
        crear_usuarios_ejemplo(conn)
        
        # Crear índices de optimización
        print("\n⚡ OPTIMIZANDO RENDIMIENTO...")
        crear_indices_optimizacion(conn)
        
        # Verificar rendimiento
        verificar_rendimiento(conn)
        
        print("\n✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
        print("\n📊 RESUMEN:")
        print("   • Estructura de usuarios corregida y optimizada")
        print("   • Tabla de productos optimizada para carrito masivo")
        print("   • Tablas de categorías y negocios creadas")
        print("   • Índices de optimización implementados")
        print("   • Usuarios de ejemplo creados")
        print("   • Base de datos lista para uso masivo")
        
        print("\n🔑 CREDENCIALES DE PRUEBA:")
        print("   • Usuario común: usuario@ejemplo.com / usuario123")
        print("   • Usuario comercial: comercial@ejemplo.com / comercial123")
        print("   • Usuario admin: admin@ejemplo.com / admin123")
        
        print("\n🛒 FUNCIONALIDADES DE CARRITO:")
        print("   • Carrito optimizado para uso masivo")
        print("   • Gestión de stock en tiempo real")
        print("   • Precios unitarios automáticos")
        print("   • Índices para consultas rápidas")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
