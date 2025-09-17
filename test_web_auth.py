#!/usr/bin/env python3
"""
Script de prueba para testear la autenticación web
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_registro():
    """Probar el registro de usuarios"""
    print("🧪 Probando registro de usuarios...")
    
    # Datos de prueba
    datos_registro = {
        'nombre': 'Usuario',
        'apellido': 'Prueba',
        'email': 'prueba@test.com',
        'password': 'password123',
        'confirmar_password': 'password123',
        'telefono': '123456789',
        'direccion': 'Dirección de prueba'
    }
    
    try:
        # Hacer POST al endpoint de registro
        response = session.post(f"{BASE_URL}/register", data=datos_registro)
        
        print(f"Status Code: {response.status_code}")
        print(f"URL final: {response.url}")
        print(f"Contenido: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Registro completado (código 200)")
        elif response.status_code == 302:
            print("✅ Registro exitoso (redirección)")
        else:
            print(f"❌ Error en registro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

def test_login():
    """Probar el login de usuarios"""
    print("\n🧪 Probando login de usuarios...")
    
    # Datos de login
    datos_login = {
        'email': 'prueba@test.com',
        'password': 'password123'
    }
    
    try:
        # Hacer POST al endpoint de login
        response = session.post(f"{BASE_URL}/login", data=datos_login)
        
        print(f"Status Code: {response.status_code}")
        print(f"URL final: {response.url}")
        print(f"Contenido: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Login completado (código 200)")
        elif response.status_code == 302:
            print("✅ Login exitoso (redirección)")
        else:
            print(f"❌ Error en login: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

def test_recuperar_password():
    """Probar la recuperación de contraseña"""
    print("\n🧪 Probando recuperación de contraseña...")
    
    # Datos de recuperación
    datos_recuperacion = {
        'email': 'prueba@test.com'
    }
    
    try:
        # Hacer POST al endpoint de recuperación
        response = session.post(f"{BASE_URL}/recuperar-password", data=datos_recuperacion)
        
        print(f"Status Code: {response.status_code}")
        print(f"URL final: {response.url}")
        print(f"Contenido: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Recuperación completada (código 200)")
        else:
            print(f"❌ Error en recuperación: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

def test_pagina_principal():
    """Probar acceso a la página principal"""
    print("\n🧪 Probando acceso a página principal...")
    
    try:
        response = session.get(f"{BASE_URL}/")
        
        print(f"Status Code: {response.status_code}")
        print(f"URL final: {response.url}")
        
        if response.status_code == 200:
            print("✅ Página principal accesible")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de autenticación web...")
    
    # Probar página principal primero
    test_pagina_principal()
    
    # Probar registro
    test_registro()
    
    # Probar login
    test_login()
    
    # Probar recuperación de contraseña
    test_recuperar_password()
    
    print("\n✅ Pruebas completadas") 