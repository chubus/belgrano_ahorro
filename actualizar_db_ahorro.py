#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la base de datos de Belgrano Ahorro
Agrega las columnas necesarias para el sistema de tickets
"""

import sqlite3
import os
from datetime import datetime

def actualizar_base_datos_ahorro():
    """Actualizar la base de datos para agregar columnas de tickets"""
    try:
        print("🔧 Actualizando base de datos de Belgrano Ahorro...")
        
        # Conectar a la base de datos
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(pedidos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Columnas actuales en tabla pedidos: {columns}")
        
        # Agregar columnas si no existen
        columnas_a_agregar = [
            ('ticket_confirmado', 'INTEGER DEFAULT 0'),
            ('ticket_estado', 'VARCHAR(20) DEFAULT "pendiente"'),
            ('fecha_confirmacion', 'DATETIME')
        ]
        
        for columna, tipo in columnas_a_agregar:
            if columna not in columns:
                print(f"📝 Agregando columna '{columna}' a la tabla pedidos...")
                try:
                    cursor.execute(f'ALTER TABLE pedidos ADD COLUMN {columna} {tipo}')
                    print(f"✅ Columna '{columna}' agregada exitosamente")
                except Exception as e:
                    print(f"⚠️ Error agregando columna '{columna}': {e}")
            else:
                print(f"✅ La columna '{columna}' ya existe")
        
        # Verificar columnas después de la actualización
        cursor.execute("PRAGMA table_info(pedidos)")
        columns_actualizadas = [col[1] for col in cursor.fetchall()]
        print(f"📊 Columnas después de actualización: {columns_actualizadas}")
        
        # Contar pedidos existentes
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]
        print(f"📊 Total de pedidos en BD: {total_pedidos}")
        
        conn.commit()
        conn.close()
        
        print("🎉 Base de datos de Belgrano Ahorro actualizada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = actualizar_base_datos_ahorro()
    if success:
        print("✅ Actualización completada")
    else:
        print("💥 Error en la actualización")
