#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos
"""

import sqlite3
import os

def check_database():
    """Verificar la estructura de la base de datos"""
    
    db_path = 'belgrano_tickets.db'
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Tablas encontradas: {[table[0] for table in tables]}")
        
        # Verificar estructura de ticket
        if ('ticket',) in tables:
            cursor.execute('PRAGMA table_info(ticket)')
            columns = cursor.fetchall()
            print(f"\n📊 Columnas de ticket:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        # Verificar si existe la columna numero
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='ticket'")
        table_sql = cursor.fetchone()
        if table_sql:
            print(f"\n📝 SQL de tabla ticket:")
            print(table_sql[0])
        
        conn.close()
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

if __name__ == "__main__":
    check_database()

