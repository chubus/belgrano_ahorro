#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST PERFIL SIMPLE - BELGRANO AHORRO
====================================

Script simple para testear específicamente el perfil
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_perfil_simple():
    """Test simple del perfil"""
    print("🔍 Testeando perfil...")
    
    try:
        # Test 1: Intentar acceder al perfil sin login
        print("\n1. Acceso al perfil sin login")
        response = requests.get(f"{BASE_URL}/perfil", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Correcto: Redirige a login")
        else:
            print("   ❌ Error: No redirige correctamente")
        
        # Test 2: Login
        print("\n2. Login")
        login_data = {
            "email": "test@test.com",
            "password": "123456"
        }
        session = requests.Session()
        response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"   Status: {response.status_code}")
        
        # Test 3: Acceso al perfil con login
        print("\n3. Acceso al perfil con login")
        response = session.get(f"{BASE_URL}/perfil")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Perfil accesible correctamente")
            # Verificar que el contenido sea correcto
            if "Mi Perfil" in response.text:
                print("   ✅ Contenido del perfil correcto")
            else:
                print("   ❌ Contenido del perfil incorrecto")
        else:
            print("   ❌ Error accediendo al perfil")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_base_datos():
    """Test de la base de datos"""
    print("\n🗄️ Testeando base de datos...")
    
    try:
        import db as database
        
        # Verificar que se pueda obtener un usuario
        usuario = database.obtener_usuario_por_id(1)
        if usuario:
            print("✅ Usuario obtenido de la base de datos")
            print(f"   ID: {usuario.get('id')}")
            print(f"   Nombre: {usuario.get('nombre')}")
            print(f"   Fecha registro: {usuario.get('fecha_registro')}")
        else:
            print("❌ No se pudo obtener usuario de la base de datos")
            
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")

def main():
    """Función principal"""
    print("🧪 TEST PERFIL SIMPLE - BELGRANO AHORRO")
    print("=" * 40)
    
    test_base_datos()
    test_perfil_simple()
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    main() 