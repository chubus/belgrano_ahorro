#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIMPIAR BASE DE DATOS - BELGRANO AHORRO
=======================================

Script para limpiar la base de datos y crear un usuario de prueba limpio
"""

import sqlite3
import db as database

print("🧹 Limpiando base de datos...")

try:
    conn = sqlite3.connect('belgrano_ahorro.db')
    cursor = conn.cursor()
    
    # Eliminar todos los usuarios existentes
    cursor.execute("DELETE FROM usuarios")
    print("✅ Usuarios eliminados")
    
    # Resetear el autoincrement
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='usuarios'")
    print("✅ Secuencia reseteada")
    
    conn.commit()
    conn.close()
    
    # Crear un usuario de prueba limpio
    print("\n👤 Creando usuario de prueba...")
    resultado = database.crear_usuario(
        nombre="Usuario",
        apellido="Prueba", 
        email="test@test.com",
        password="123456",
        telefono="123456789",
        direccion="Dirección de prueba"
    )
    
    if resultado:
        print("✅ Usuario de prueba creado correctamente")
        
        # Verificar que se puede obtener
        usuario = database.obtener_usuario_por_id(1)
        if usuario:
            print("✅ Usuario obtenido correctamente:")
            print(f"   ID: {usuario.get('id')}")
            print(f"   Nombre: {usuario.get('nombre')}")
            print(f"   Email: {usuario.get('email')}")
            print(f"   Fecha registro: {usuario.get('fecha_registro')}")
        else:
            print("❌ No se pudo obtener el usuario")
    else:
        print("❌ Error creando usuario de prueba")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Limpieza completada") 