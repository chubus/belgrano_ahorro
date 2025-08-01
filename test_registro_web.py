#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el registro de usuarios desde la web
"""

import requests
import time
import random
import string
from datetime import datetime

def generar_datos_prueba():
    """Generar datos únicos para la prueba"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
    
    return {
        'nombre': 'Usuario',
        'apellido': 'Prueba',
        'email': f'test_{timestamp}_{random_str}@test.com',
        'password': 'TestPassword123!',
        'confirmar_password': 'TestPassword123!',
        'telefono': '1234567890',
        'direccion': 'Dirección de prueba 123',
        'terminos': 'aceptado'
    }

def test_registro_web():
    """Probar registro de usuarios desde la web"""
    print("🌐 Probando registro de usuarios desde la web...")
    
    # URL base
    base_url = "http://localhost:5000"
    
    try:
        # 1. Verificar que la aplicación está corriendo
        print("1️⃣ Verificando que la aplicación está corriendo...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicación Flask está corriendo")
        else:
            print(f"❌ Aplicación no responde correctamente: {response.status_code}")
            return False
        
        # 2. Obtener página de registro
        print("\n2️⃣ Obteniendo página de registro...")
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ Página de registro accesible")
        else:
            print(f"❌ Error accediendo a página de registro: {response.status_code}")
            return False
        
        # 3. Probar registro de usuario
        print("\n3️⃣ Probando registro de usuario...")
        datos = generar_datos_prueba()
        print(f"📧 Email de prueba: {datos['email']}")
        
        response = requests.post(f"{base_url}/register", data=datos, timeout=10)
        
        if response.status_code == 200:
            print("✅ Formulario de registro enviado correctamente")
            
            # Verificar si hay mensaje de éxito en la respuesta
            if "Usuario creado exitosamente" in response.text or "registrado" in response.text.lower():
                print("✅ Usuario registrado exitosamente")
            else:
                print("⚠️ Registro enviado pero verificar respuesta")
                print(f"📄 Contenido de respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error en registro: {response.status_code}")
            print(f"📄 Contenido de respuesta: {response.text[:200]}...")
            return False
        
        # 4. Probar login con el usuario creado
        print("\n4️⃣ Probando login con usuario creado...")
        login_data = {
            'email': datos['email'],
            'password': datos['password']
        }
        
        response = requests.post(f"{base_url}/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Formulario de login enviado correctamente")
            
            # Verificar si el login fue exitoso
            if "bienvenido" in response.text.lower() or "inicio" in response.text.lower():
                print("✅ Login exitoso")
            else:
                print("⚠️ Login enviado pero verificar respuesta")
        else:
            print(f"❌ Error en login: {response.status_code}")
        
        print("\n🎉 Pruebas de registro web completadas")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación Flask")
        print("💡 Asegúrate de que la aplicación esté corriendo en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error en pruebas web: {e}")
        return False

def test_paginas_principales():
    """Probar que las páginas principales funcionan"""
    print("\n🌐 Probando páginas principales...")
    
    base_url = "http://localhost:5000"
    paginas = [
        ("/", "Página principal"),
        ("/login", "Página de login"),
        ("/register", "Página de registro"),
        ("/carrito", "Página de carrito"),
        ("/contacto", "Página de contacto")
    ]
    
    for ruta, nombre in paginas:
        try:
            response = requests.get(f"{base_url}{ruta}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {nombre}: OK")
            else:
                print(f"❌ {nombre}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {nombre}: Error de conexión")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de registro web...")
    print("💡 Asegúrate de que la aplicación Flask esté corriendo")
    print("💡 Comando: python app.py")
    print()
    
    # Esperar un momento para que la aplicación se inicie
    print("⏳ Esperando 3 segundos para que la aplicación se inicie...")
    time.sleep(3)
    
    # Probar páginas principales
    test_paginas_principales()
    
    # Probar registro web
    test_registro_web()
    
    print("\n✅ Pruebas completadas")
    print("💡 Para probar manualmente:")
    print("   http://localhost:5000/register")
    print("   http://localhost:5000/login") 