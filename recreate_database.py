#!/usr/bin/env python3
"""
Script para recrear la base de datos con la estructura correcta
"""

import os
import sqlite3

def recreate_database():
    """Recrear la base de datos con la estructura correcta"""
    
    db_path = 'belgrano_tickets.db'
    
    # Hacer backup de la base de datos actual
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        os.rename(db_path, backup_path)
        print(f"📦 Backup creado: {backup_path}")
    
    try:
        # Crear nueva base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla usuarios
        cursor.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL,
                role VARCHAR(20) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla ticket con la estructura correcta
        cursor.execute('''
            CREATE TABLE ticket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero VARCHAR(50) UNIQUE NOT NULL,
                cliente_nombre VARCHAR(120) NOT NULL,
                cliente_direccion VARCHAR(200) NOT NULL,
                cliente_telefono VARCHAR(50) NOT NULL,
                cliente_email VARCHAR(120) NOT NULL,
                productos TEXT NOT NULL,
                total FLOAT NOT NULL DEFAULT 0.0,
                estado VARCHAR(20) DEFAULT 'pendiente',
                prioridad VARCHAR(20) DEFAULT 'normal',
                indicaciones TEXT,
                asignado_a INTEGER,
                repartidor_nombre VARCHAR(50),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_asignacion DATETIME,
                fecha_entrega DATETIME,
                notas_repartidor TEXT,
                FOREIGN KEY (asignado_a) REFERENCES user (id)
            )
        ''')
        
        # Crear tabla configuracion
        cursor.execute('''
            CREATE TABLE configuracion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave VARCHAR(100) UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                descripcion TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar usuarios por defecto
        cursor.execute('''
            INSERT INTO user (username, email, password, role, nombre, activo)
            VALUES 
                ('admin', 'admin@belgrano.com', 'pbkdf2:sha256:600000$admin123$hash', 'admin', 'Administrador', 1),
                ('flota1', 'flota1@belgrano.com', 'pbkdf2:sha256:600000$flota123$hash', 'flota', 'Repartidor 1', 1),
                ('flota2', 'flota2@belgrano.com', 'pbkdf2:sha256:600000$flota123$hash', 'flota', 'Repartidor 2', 1)
        ''')
        
        # Insertar algunos tickets de ejemplo
        cursor.execute('''
            INSERT INTO ticket (numero, cliente_nombre, cliente_direccion, cliente_telefono, cliente_email, productos, total, estado, prioridad)
            VALUES 
                ('T001', 'Juan Pérez', 'Av. Corrientes 1234', '1234567890', 'juan@email.com', '{"productos": [{"nombre": "Leche", "precio": 500}]}', 500.0, 'pendiente', 'normal'),
                ('T002', 'María García', 'Av. Santa Fe 5678', '0987654321', 'maria@email.com', '{"productos": [{"nombre": "Pan", "precio": 300}]}', 300.0, 'en_proceso', 'alta')
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos recreada con estructura correcta")
        print("✅ Usuarios por defecto creados")
        print("✅ Tickets de ejemplo creados")
        
    except Exception as e:
        print(f"❌ Error recreando base de datos: {e}")
        # Restaurar backup si hay error
        if os.path.exists(f"{db_path}.backup"):
            os.rename(f"{db_path}.backup", db_path)
            print("🔄 Backup restaurado")

if __name__ == "__main__":
    recreate_database()

