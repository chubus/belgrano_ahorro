#!/usr/bin/env python3
"""
Script simple para probar el registro de usuarios
"""

import requests
import time

def test_registro_simple():
    """Probar registro de usuarios de forma simple"""
    print("🧪 Probando registro simple...")
    
    # Datos de prueba
    datos = {
        'nombre': 'Usuario',
        'apellido': 'Test',
        'email': 'test@test.com',
        'password': 'password123',
        'confirmar_password': 'password123',
        'telefono': '123456789',
        'direccion': 'Dirección test',
        'terminos': 'aceptado'
    }
    
    try:
        # 1. Verificar que la aplicación esté ejecutándose
        print("1. Verificando aplicación...")
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ La aplicación no está ejecutándose")
            return
        
        # 2. Obtener página de registro
        print("\n2. Obteniendo página de registro...")
        response = requests.get("http://localhost:5000/register", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Error al obtener página de registro")
            return
        
        # 3. Enviar formulario de registro
        print("\n3. Enviando formulario de registro...")
        response = requests.post("http://localhost:5000/register", data=datos, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if response.status_code == 302:
            print("✅ Registro exitoso (redirección)")
            # Seguir la redirección
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print(f"   Redirigiendo a: {redirect_url}")
                response = requests.get(f"http://localhost:5000{redirect_url}", timeout=5)
                print(f"   Status final: {response.status_code}")
        elif response.status_code == 200:
            print("⚠️ Registro completado pero sin redirección")
            # Verificar si hay mensajes de error en el contenido
            if "error" in response.text.lower() or "error" in response.text.lower():
                print("❌ Hay errores en la página")
            else:
                print("✅ Registro parece exitoso")
        else:
            print(f"❌ Error en registro: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_login_simple():
    """Probar login de usuarios de forma simple"""
    print("\n🧪 Probando login simple...")
    
    # Datos de login
    datos = {
        'email': 'test@test.com',
        'password': 'password123'
    }
    
    try:
        # Enviar formulario de login
        response = requests.post("http://localhost:5000/login", data=datos, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if response.status_code == 302:
            print("✅ Login exitoso (redirección)")
        elif response.status_code == 200:
            print("⚠️ Login completado pero sin redirección")
        else:
            print(f"❌ Error en login: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas simples de registro...")
    
    # Probar registro
    test_registro_simple()
    
    # Esperar un momento
    time.sleep(2)
    
    # Probar login
    test_login_simple()
    
    print("\n✅ Pruebas completadas") 