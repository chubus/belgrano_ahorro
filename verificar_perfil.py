#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACIÓN DE PERFIL - BELGRANO AHORRO
========================================

Script simple para verificar que el perfil funcione correctamente
"""

import db as database

print("🔍 Verificando función obtener_usuario_por_id...")

# Crear un usuario de prueba
resultado = database.crear_usuario(
    nombre="Test",
    apellido="Usuario", 
    email="test@test.com",
    password="123456",
    telefono="123456789",
    direccion="Dirección de prueba"
)

if resultado:
    print("✅ Usuario creado correctamente")
    
    # Obtener el usuario
    usuario = database.obtener_usuario_por_id(1)
    
    if usuario:
        print("✅ Usuario obtenido correctamente")
        print(f"   ID: {usuario.get('id')}")
        print(f"   Nombre: {usuario.get('nombre')}")
        print(f"   Email: {usuario.get('email')}")
        print(f"   Fecha registro: {usuario.get('fecha_registro')}")
        
        # Verificar que fecha_registro esté presente
        if 'fecha_registro' in usuario:
            print("✅ Campo fecha_registro está presente")
            if usuario['fecha_registro']:
                print(f"   Valor: {usuario['fecha_registro']}")
            else:
                print("   Valor: None (se mostrará 'Fecha no disponible')")
        else:
            print("❌ Campo fecha_registro NO está presente")
    else:
        print("❌ No se pudo obtener el usuario")
else:
    print("❌ Error creando usuario")

print("\n✅ Verificación completada") 