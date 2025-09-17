#!/usr/bin/env python3
"""
Script de inicialización específico para Ticketera en deploy
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def inicializar_ticketera_deploy():
    """Inicializar base de datos de ticketera para deploy"""
    print("Inicializando Ticketera para deploy...")
    
    try:
        # Crear base de datos
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        
        # Tabla usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(50),
                telefono VARCHAR(20),
                rol VARCHAR(20) DEFAULT 'cliente',
                activo BOOLEAN DEFAULT 1,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla tickets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido VARCHAR(50) UNIQUE NOT NULL,
                cliente VARCHAR(100) NOT NULL,
                productos TEXT NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                direccion TEXT,
                telefono VARCHAR(20),
                email VARCHAR(100),
                metodo_pago VARCHAR(50),
                notas TEXT,
                estado VARCHAR(20) DEFAULT 'pendiente',
                prioridad VARCHAR(20) DEFAULT 'normal',
                repartidor VARCHAR(50),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verificar si ya existen usuarios
        cursor.execute('SELECT COUNT(*) FROM usuarios')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Crear usuario admin
            admin_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@belgranoahorro.com', admin_password, 'Administrador', 'admin', True))
            
            # Crear usuarios flota
            flota_usuarios = [
                ('repartidor1', 'repartidor1@belgranoahorro.com', 'Repartidor 1'),
                ('repartidor2', 'repartidor2@belgranoahorro.com', 'Repartidor 2'),
                ('repartidor3', 'repartidor3@belgranoahorro.com', 'Repartidor 3'),
                ('repartidor4', 'repartidor4@belgranoahorro.com', 'Repartidor 4'),
                ('repartidor5', 'repartidor5@belgranoahorro.com', 'Repartidor 5')
            ]
            
            for username, email, nombre in flota_usuarios:
                flota_password = generate_password_hash('flota123')
                cursor.execute('''
                    INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, flota_password, nombre, 'flota', True))
            
            print("Usuarios del sistema inicializados")
        else:
            print(f"Ya existen {count} usuarios en el sistema")
        
        conn.commit()
        conn.close()
        
        print("Base de datos de Ticketera inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"Error inicializando Ticketera: {e}")
        return False

if __name__ == "__main__":
    inicializar_ticketera_deploy()
