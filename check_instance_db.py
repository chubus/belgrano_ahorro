#!/usr/bin/env python3
"""
Script para verificar la base de datos en instance/
"""

import os
import sqlite3

def check_instance_database():
    """Verificar la base de datos en instance/"""
    
    print("🔧 Verificando base de datos en instance/...")
    
    # Verificar si existe el directorio instance
    instance_dir = 'instance'
    if os.path.exists(instance_dir):
        print(f"✅ Directorio instance encontrado: {instance_dir}")
        
        # Verificar archivos en instance
        files = os.listdir(instance_dir)
        print(f"✅ Archivos en instance: {files}")
        
        # Verificar si existe belgrano_tickets.db en instance
        db_path = os.path.join(instance_dir, 'belgrano_tickets.db')
        if os.path.exists(db_path):
            print(f"✅ Archivo de base de datos encontrado: {db_path}")
            print(f"📏 Tamaño: {os.path.getsize(db_path)} bytes")
            
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
                
                conn.close()
                print("✅ Verificación completada")
                
            except Exception as e:
                print(f"❌ Error verificando base de datos: {e}")
        else:
            print(f"❌ Archivo de base de datos no encontrado: {db_path}")
    else:
        print(f"❌ Directorio instance no encontrado: {instance_dir}")

if __name__ == "__main__":
    check_instance_database()

