#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos desde cero
"""

import os
import sqlite3
from datetime import datetime

def inicializar_base_datos():
    """Inicializar la base de datos desde cero"""
    print("🗄️ Inicializando base de datos...")
    
    # Eliminar archivo de base de datos si existe
    if os.path.exists('belgrano_ahorro.db'):
        os.remove('belgrano_ahorro.db')
        print("✅ Base de datos anterior eliminada")
    
    try:
        # Crear nueva base de datos
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Tabla usuarios
        cursor.execute('''
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(50) NOT NULL,
                apellido VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefono VARCHAR(20),
                direccion TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                password VARCHAR(100) NOT NULL,
                rol VARCHAR(20) DEFAULT 'cliente'
            )
        ''')
        print("✅ Tabla usuarios creada")
        
        # Tabla productos
        cursor.execute('''
            CREATE TABLE productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                store VARCHAR(50) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                original_price DECIMAL(10,2),
                discount INTEGER,
                new BOOLEAN DEFAULT 0,
                imagen VARCHAR(255),
                categoria VARCHAR(50),
                destacado BOOLEAN DEFAULT 0,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        print("✅ Tabla productos creada")
        
        # Tabla carrito
        cursor.execute('''
            CREATE TABLE carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        print("✅ Tabla carrito creada")
        
        # Tabla pedidos
        cursor.execute('''
            CREATE TABLE pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                numero_pedido VARCHAR(50) UNIQUE NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10,2) NOT NULL,
                estado VARCHAR(20) DEFAULT 'pendiente',
                metodo_pago VARCHAR(50),
                direccion_entrega TEXT,
                notas TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        print("✅ Tabla pedidos creada")
        
        # Tabla items de pedidos
        cursor.execute('''
            CREATE TABLE pedido_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        print("✅ Tabla pedido_items creada")
        
        # Tabla tokens de recuperación
        cursor.execute('''
            CREATE TABLE tokens_recuperacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token VARCHAR(100) UNIQUE NOT NULL,
                expiracion DATETIME NOT NULL,
                usado BOOLEAN DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        print("✅ Tabla tokens_recuperacion creada")
        
        conn.commit()
        conn.close()
        
        print("🎉 Base de datos inicializada correctamente")
        print("📊 Tablas creadas:")
        print("   - usuarios")
        print("   - productos") 
        print("   - carrito")
        print("   - pedidos")
        print("   - pedido_items")
        print("   - tokens_recuperacion")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        return False

def probar_funciones_db():
    """Probar que las funciones de la base de datos funcionan"""
    print("\n🧪 Probando funciones de base de datos...")
    
    try:
        import db
        
        # Probar crear usuario
        resultado = db.crear_usuario(
            nombre="Test",
            apellido="Usuario",
            email="test@test.com",
            password="test123",
            telefono="123456789",
            direccion="Dirección de prueba"
        )
        
        if resultado['exito']:
            print("✅ Función crear_usuario funciona")
            
            # Probar verificar usuario
            resultado_login = db.verificar_usuario("test@test.com", "test123")
            if resultado_login['exito']:
                print("✅ Función verificar_usuario funciona")
            else:
                print("❌ Función verificar_usuario falló")
            
            # Limpiar usuario de prueba
            conn = sqlite3.connect('belgrano_ahorro.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE email = ?", ("test@test.com",))
            conn.commit()
            conn.close()
            print("✅ Usuario de prueba eliminado")
            
        else:
            print(f"❌ Función crear_usuario falló: {resultado['mensaje']}")
            
    except Exception as e:
        print(f"❌ Error probando funciones: {e}")

if __name__ == "__main__":
    print("🚀 Inicializando sistema de base de datos...")
    
    # Inicializar base de datos
    if inicializar_base_datos():
        # Probar funciones
        probar_funciones_db()
        print("\n✅ Sistema listo para usar")
    else:
        print("\n❌ Error en la inicialización") 