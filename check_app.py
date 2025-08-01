#!/usr/bin/env python3
"""
Script para verificar el estado de la aplicación
"""

import requests
import time

def check_app():
    """Verificar si la aplicación está ejecutándose"""
    print("🔍 Verificando estado de la aplicación...")
    
    try:
        # Intentar conectar a la aplicación
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ Aplicación ejecutándose - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación")
        print("   La aplicación no está ejecutándose en http://localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar a la aplicación")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_simple_endpoints():
    """Probar endpoints simples"""
    print("\n🧪 Probando endpoints simples...")
    
    endpoints = [
        "/",
        "/login",
        "/register",
        "/recuperar-password"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Verificando aplicación Flask...")
    
    if check_app():
        test_simple_endpoints()
    else:
        print("\n💡 Para iniciar la aplicación, ejecuta:")
        print("   python start_app.py")
        print("   o")
        print("   python app.py") 