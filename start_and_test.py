#!/usr/bin/env python3
"""
Script para iniciar la aplicación y hacer pruebas automáticas
"""

import subprocess
import time
import requests
import sys

def start_app():
    """Iniciar la aplicación Flask"""
    print("🚀 Iniciando aplicación Flask...")
    
    try:
        # Iniciar la aplicación en segundo plano
        process = subprocess.Popen([sys.executable, "app.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar a que la aplicación se inicie
        time.sleep(3)
        
        print("✅ Aplicación iniciada")
        return process
        
    except Exception as e:
        print(f"❌ Error al iniciar aplicación: {e}")
        return None

def test_endpoints():
    """Probar endpoints de la aplicación"""
    print("\n🧪 Probando endpoints...")
    
    endpoints = [
        ("/", "Página principal"),
        ("/register", "Página de registro"),
        ("/login", "Página de login"),
        ("/recuperar-password", "Página de recuperación")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} - OK")
            else:
                print(f"❌ {description} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {description} - Error: {e}")

def test_registro_web():
    """Probar registro desde la web"""
    print("\n🧪 Probando registro web...")
    
    try:
        # Datos de prueba
        datos = {
            'nombre': 'Usuario',
            'apellido': 'Web',
            'email': 'web@test.com',
            'password': 'password123',
            'confirmar_password': 'password123',
            'telefono': '123456789',
            'direccion': 'Dirección web'
        }
        
        response = requests.post("http://localhost:5000/register", data=datos, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"URL final: {response.url}")
        
        if response.status_code in [200, 302]:
            print("✅ Registro web exitoso")
        else:
            print("❌ Error en registro web")
            
    except Exception as e:
        print(f"❌ Error en prueba web: {e}")

def main():
    """Función principal"""
    print("🎯 Iniciando aplicación y pruebas...")
    
    # Iniciar aplicación
    process = start_app()
    
    if process is None:
        print("❌ No se pudo iniciar la aplicación")
        return
    
    try:
        # Esperar un momento
        time.sleep(2)
        
        # Probar endpoints
        test_endpoints()
        
        # Probar registro web
        test_registro_web()
        
        print("\n✅ Pruebas completadas")
        
    finally:
        # Detener la aplicación
        print("\n🛑 Deteniendo aplicación...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main() 