#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG PERFIL - BELGRANO AHORRO
==============================

Script para debuggear el problema con el perfil
"""

import sqlite3
import db as database

print("🔍 Debug del perfil...")

# Verificar si la base de datos existe
try:
    conn = sqlite3.connect('belgrano_ahorro.db')
    cursor = conn.cursor()
    
    # Verificar estructura de la tabla usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    columnas = cursor.fetchall()
    print("📋 Estructura de la tabla usuarios:")
    for col in columnas:
        print(f"   {col[1]} ({col[2]})")
    
    # Verificar si hay usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]
    print(f"👥 Total de usuarios: {count}")
    
    if count > 0:
        # Obtener el primer usuario
        cursor.execute("SELECT * FROM usuarios LIMIT 1")
        usuario_raw = cursor.fetchone()
        print("📄 Usuario raw:")
        for i, valor in enumerate(usuario_raw):
            print(f"   [{i}]: {valor}")
        
        # Probar la función obtener_usuario_por_id
        usuario_id = usuario_raw[0]
        print(f"\n🔍 Probando obtener_usuario_por_id con ID {usuario_id}...")
        
        usuario = database.obtener_usuario_por_id(usuario_id)
        if usuario:
            print("✅ Usuario obtenido:")
            for campo, valor in usuario.items():
                print(f"   {campo}: {valor}")
        else:
            print("❌ No se pudo obtener el usuario")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Debug completado") 