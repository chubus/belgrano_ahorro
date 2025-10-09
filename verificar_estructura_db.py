#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estructura de la base de datos
"""

import sqlite3

def verificar_estructura():
    """Verificar estructura de las tablas"""
    print("VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Verificar estructura de productos
        print("\nESTRUCTURA TABLA PRODUCTOS:")
        cursor.execute('PRAGMA table_info(productos)')
        for row in cursor.fetchall():
            print(f"  {row}")
        
        # Verificar estructura de sucursales
        print("\nESTRUCTURA TABLA SUCURSALES:")
        cursor.execute('PRAGMA table_info(sucursales)')
        for row in cursor.fetchall():
            print(f"  {row}")
        
        # Verificar datos de productos
        print("\nDATOS PRODUCTOS (primeros 3):")
        cursor.execute('SELECT * FROM productos LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row}")
        
        # Verificar datos de sucursales
        print("\nDATOS SUCURSALES (primeros 3):")
        cursor.execute('SELECT * FROM sucursales LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_estructura()

