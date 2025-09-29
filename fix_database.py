#!/usr/bin/env python3
"""
Script para corregir la base de datos de Ticketera
"""

import sqlite3
import os

def fix_database():
    """Corregir la estructura de la base de datos"""
    
    db_path = 'belgrano_tickets.db'
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existe la tabla tickets
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
        if cursor.fetchone():
            print("📋 Tabla 'tickets' encontrada, renombrando a 'ticket'")
            
            # Renombrar tabla de tickets a ticket
            cursor.execute("ALTER TABLE tickets RENAME TO ticket")
            print("✅ Tabla renombrada de 'tickets' a 'ticket'")
        
        # Verificar estructura de ticket
        cursor.execute('PRAGMA table_info(ticket)')
        columns = cursor.fetchall()
        print(f"\n📊 Columnas de ticket:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar si existe la columna numero
        column_names = [col[1] for col in columns]
        if 'numero' not in column_names:
            print("❌ Columna 'numero' no encontrada")
            print("🔧 Agregando columna 'numero'")
            cursor.execute("ALTER TABLE ticket ADD COLUMN numero VARCHAR(50)")
            cursor.execute("UPDATE ticket SET numero = 'T' || id WHERE numero IS NULL")
            print("✅ Columna 'numero' agregada")
        
        conn.commit()
        conn.close()
        print("\n✅ Base de datos corregida")
        
    except Exception as e:
        print(f"❌ Error corrigiendo base de datos: {e}")

if __name__ == "__main__":
    fix_database()

