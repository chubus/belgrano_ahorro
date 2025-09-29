#!/usr/bin/env python3
"""
Script para verificar la configuración de la base de datos
"""

import os
import sqlite3

def check_database_config():
    """Verificar configuración de la base de datos"""
    
    print("🔧 Verificando configuración de base de datos...")
    
    # Verificar archivo de base de datos
    db_path = 'belgrano_tickets.db'
    if os.path.exists(db_path):
        print(f"✅ Archivo de base de datos encontrado: {db_path}")
        print(f"📏 Tamaño: {os.path.getsize(db_path)} bytes")
    else:
        print(f"❌ Archivo de base de datos no encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Tablas encontradas: {[table[0] for table in tables]}")
        
        # Verificar estructura de ticket
        if ('ticket',) in tables:
            cursor.execute('PRAGMA table_info(ticket)')
            columns = cursor.fetchall()
            print(f"✅ Columnas de ticket:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Verificar si existe la columna numero
            column_names = [col[1] for col in columns]
            if 'numero' in column_names:
                print("✅ Columna 'numero' encontrada")
            else:
                print("❌ Columna 'numero' NO encontrada")
            
            # Verificar si existe la columna total
            if 'total' in column_names:
                print("✅ Columna 'total' encontrada")
            else:
                print("❌ Columna 'total' NO encontrada")
        
        # Verificar datos
        cursor.execute("SELECT COUNT(*) FROM ticket")
        count = cursor.fetchone()[0]
        print(f"✅ Tickets en base de datos: {count}")
        
        # Verificar datos específicos
        cursor.execute("SELECT id, numero, cliente_nombre, total FROM ticket LIMIT 3")
        rows = cursor.fetchall()
        print(f"✅ Primeros 3 tickets:")
        for row in rows:
            print(f"  - ID: {row[0]}, Número: {row[1]}, Cliente: {row[2]}, Total: {row[3]}")
        
        conn.close()
        print("✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

if __name__ == "__main__":
    check_database_config()

