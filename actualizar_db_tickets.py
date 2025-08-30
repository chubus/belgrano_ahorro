#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la base de datos de tickets con los nuevos campos
"""

import sqlite3
import json
from datetime import datetime

def actualizar_base_datos_tickets():
    """Actualizar la base de datos de tickets con los nuevos campos"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        print("🔄 Actualizando base de datos de tickets...")
        
        # Verificar si la tabla tickets existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
        if not cursor.fetchone():
            print("❌ La tabla 'tickets' no existe. Creando tabla completa...")
            
            # Crear tabla tickets completa
            cursor.execute('''
                CREATE TABLE tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero VARCHAR(50) UNIQUE NOT NULL,
                    cliente_nombre VARCHAR(100) NOT NULL,
                    cliente_direccion TEXT,
                    cliente_telefono VARCHAR(20),
                    cliente_email VARCHAR(100),
                    productos TEXT NOT NULL,
                    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    estado VARCHAR(20) DEFAULT 'pendiente',
                    estado_envio VARCHAR(20) DEFAULT 'pendiente',
                    prioridad VARCHAR(20) DEFAULT 'normal',
                    indicaciones TEXT,
                    repartidor VARCHAR(50),
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_envio DATETIME,
                    fecha_entrega DATETIME
                )
            ''')
            print("✅ Tabla tickets creada con todos los campos")
        else:
            print("✅ Tabla tickets existe, verificando campos...")
            
            # Verificar y agregar campos faltantes
            campos_requeridos = [
                ('total', 'DECIMAL(10,2) DEFAULT 0.00'),
                ('estado_envio', 'VARCHAR(20) DEFAULT "pendiente"'),
                ('fecha_envio', 'DATETIME'),
                ('fecha_entrega', 'DATETIME')
            ]
            
            for campo, tipo in campos_requeridos:
                try:
                    cursor.execute(f'ALTER TABLE tickets ADD COLUMN {campo} {tipo}')
                    print(f"✅ Campo '{campo}' agregado")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ Campo '{campo}' ya existe")
                    else:
                        print(f"⚠️ Error agregando campo '{campo}': {e}")
        
        # Crear tabla de registro de tickets
        print("🔄 Creando tabla de registro de tickets...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                numero VARCHAR(50) NOT NULL,
                cliente_nombre VARCHAR(100) NOT NULL,
                cliente_direccion TEXT,
                cliente_telefono VARCHAR(20),
                cliente_email VARCHAR(100),
                productos TEXT NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                estado_final VARCHAR(20) NOT NULL,
                estado_envio_final VARCHAR(20) NOT NULL,
                prioridad VARCHAR(20),
                indicaciones TEXT,
                repartidor VARCHAR(50),
                fecha_creacion DATETIME,
                fecha_envio DATETIME,
                fecha_entrega DATETIME,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        ''')
        print("✅ Tabla registro_tickets creada/verificada")
        
        # Actualizar tickets existentes con total calculado
        print("🔄 Actualizando totales de tickets existentes...")
        cursor.execute('SELECT id, productos FROM tickets WHERE total = 0 OR total IS NULL')
        tickets_sin_total = cursor.fetchall()
        
        for ticket_id, productos_json in tickets_sin_total:
            try:
                productos = json.loads(productos_json) if productos_json else []
                total = 0.0
                
                for producto in productos:
                    cantidad = producto.get('cantidad', 1)
                    precio = producto.get('precio', 0)
                    total += cantidad * precio
                
                cursor.execute('UPDATE tickets SET total = ? WHERE id = ?', (total, ticket_id))
                print(f"✅ Ticket {ticket_id}: Total actualizado a ${total:.2f}")
                
            except Exception as e:
                print(f"⚠️ Error actualizando ticket {ticket_id}: {e}")
        
        # Actualizar estado_envio para tickets existentes
        print("🔄 Actualizando estados de envío...")
        cursor.execute('''
            UPDATE tickets 
            SET estado_envio = CASE 
                WHEN estado = 'entregado' THEN 'entregado'
                WHEN estado = 'en-camino' THEN 'en-envio'
                WHEN estado = 'en-preparacion' THEN 'en-preparacion'
                ELSE 'pendiente'
            END
            WHERE estado_envio IS NULL OR estado_envio = 'pendiente'
        ''')
        
        conn.commit()
        print("✅ Estados de envío actualizados")
        
        # Mostrar estadísticas finales
        cursor.execute('SELECT COUNT(*) FROM tickets')
        total_tickets = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM registro_tickets')
        total_registro = cursor.fetchone()[0]
        
        print("\n📊 Estadísticas finales:")
        print(f"   • Tickets activos: {total_tickets}")
        print(f"   • Tickets en registro: {total_registro}")
        
        conn.close()
        print("\n✅ Actualización de base de datos completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando actualización de base de datos de tickets...")
    print("=" * 50)
    
    if actualizar_base_datos_tickets():
        print("\n🎉 ¡Actualización completada exitosamente!")
        print("📱 El sistema de tickets está listo para usar con las nuevas funcionalidades:")
        print("   • Estados de envío: pendiente, en-preparacion, en-envio, entregado")
        print("   • Totales calculados automáticamente")
        print("   • Registro de tickets (historial)")
        print("   • Asignación de repartidores y prioridades")
    else:
        print("\n❌ Error en la actualización. Revisa los logs anteriores.")
