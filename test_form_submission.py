#!/usr/bin/env python3
"""
Script de prueba específico para formularios
"""

import requests
import time

# Configuración
BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_registro_completo():
    """Probar el registro completo paso a paso"""
    print("🧪 Probando registro completo...")
    
    # 1. Obtener la página de registro
    print("1. Obteniendo página de registro...")
    response = session.get(f"{BASE_URL}/register")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Error al obtener página de registro")
        return
    
    # 2. Enviar formulario de registro
    print("2. Enviando formulario de registro...")
    datos_registro = {
        'nombre': 'Usuario',
        'apellido': 'Prueba',
        'email': 'prueba2@test.com',
        'password': 'password123',
        'confirmar_password': 'password123',
        'telefono': '123456789',
        'direccion': 'Dirección de prueba'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(f"{BASE_URL}/register", data=datos_registro, headers=headers, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'No redirect')}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    
    if response.status_code == 302:
        print("✅ Registro exitoso (redirección)")
        # Seguir la redirección
        redirect_url = response.headers.get('Location')
        if redirect_url:
            print(f"3. Siguiendo redirección a: {redirect_url}")
            response = session.get(f"{BASE_URL}{redirect_url}")
            print(f"   Status final: {response.status_code}")
    else:
        print("❌ Registro no exitoso")
        print(f"   Contenido: {response.text[:200]}...")

def test_login_completo():
    """Probar el login completo paso a paso"""
    print("\n🧪 Probando login completo...")
    
    # 1. Obtener la página de login
    print("1. Obteniendo página de login...")
    response = session.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Error al obtener página de login")
        return
    
    # 2. Enviar formulario de login
    print("2. Enviando formulario de login...")
    datos_login = {
        'email': 'prueba2@test.com',
        'password': 'password123'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(f"{BASE_URL}/login", data=datos_login, headers=headers, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'No redirect')}")
    
    if response.status_code == 302:
        print("✅ Login exitoso (redirección)")
        # Seguir la redirección
        redirect_url = response.headers.get('Location')
        if redirect_url:
            print(f"3. Siguiendo redirección a: {redirect_url}")
            response = session.get(f"{BASE_URL}{redirect_url}")
            print(f"   Status final: {response.status_code}")
    else:
        print("❌ Login no exitoso")
        print(f"   Contenido: {response.text[:200]}...")

def test_recuperar_password_completo():
    """Probar la recuperación de contraseña completa"""
    print("\n🧪 Probando recuperación de contraseña...")
    
    # 1. Obtener la página de recuperación
    print("1. Obteniendo página de recuperación...")
    response = session.get(f"{BASE_URL}/recuperar-password")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Error al obtener página de recuperación")
        return
    
    # 2. Enviar formulario de recuperación
    print("2. Enviando formulario de recuperación...")
    datos_recuperacion = {
        'email': 'prueba2@test.com'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(f"{BASE_URL}/recuperar-password", data=datos_recuperacion, headers=headers, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'No redirect')}")
    
    if response.status_code == 200:
        print("✅ Recuperación completada")
    else:
        print("❌ Error en recuperación")
        print(f"   Contenido: {response.text[:200]}...")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas específicas de formularios...")
    
    # Probar registro completo
    test_registro_completo()
    
    # Esperar un momento
    time.sleep(1)
    
    # Probar login completo
    test_login_completo()
    
    # Esperar un momento
    time.sleep(1)
    
    # Probar recuperación de contraseña
    test_recuperar_password_completo()
    
    print("\n✅ Pruebas completadas") 