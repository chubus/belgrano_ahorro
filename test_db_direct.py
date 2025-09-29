#!/usr/bin/env python3
"""
Script para probar la base de datos directamente
"""

import sqlite3

def test_database_direct():
    """Probar la base de datos directamente"""
    
    try:
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        
        # Probar consulta simple
        cursor.execute("SELECT COUNT(*) FROM ticket")
        count = cursor.fetchone()[0]
        print(f"✅ Tickets en DB: {count}")
        
        # Probar consulta con columnas específicas
        cursor.execute("SELECT id, numero, cliente_nombre, total FROM ticket LIMIT 5")
        rows = cursor.fetchall()
        print(f"✅ Primeros 5 tickets:")
        for row in rows:
            print(f"  - ID: {row[0]}, Número: {row[1]}, Cliente: {row[2]}, Total: {row[3]}")
        
        # Probar consulta con filtros
        cursor.execute("SELECT COUNT(*) FROM ticket WHERE estado = 'pendiente'")
        pendientes = cursor.fetchone()[0]
        print(f"✅ Tickets pendientes: {pendientes}")
        
        conn.close()
        print("✅ Base de datos funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

if __name__ == "__main__":
    test_database_direct()

