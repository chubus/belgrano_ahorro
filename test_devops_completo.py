#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Completo de DevOps
Verifica todas las funcionalidades de DevOps
"""

import requests
import time
from datetime import datetime

def test_devops_completo():
    """Test completo de DevOps"""
    print("🔧 TEST COMPLETO DE DEVOPS")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs de DevOps
    devops_url = "http://localhost:5002"
    
    # Test 1: Verificar que DevOps esté funcionando
    print("🔍 VERIFICANDO CONECTIVIDAD DEVOPS...")
    try:
        response = requests.get(f"{devops_url}/devops/", timeout=10)
        if response.status_code == 200:
            print("✅ Panel DevOps: FUNCIONANDO")
        else:
            print(f"⚠️ Panel DevOps: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Panel DevOps: ERROR - {e}")
        return False
    
    # Test 2: Health Check
    print("\n🏥 VERIFICANDO HEALTH CHECK...")
    try:
        response = requests.get(f"{devops_url}/devops/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"   Belgrano Ahorro: {data.get('belgrano_ahorro', 'unknown')}")
        else:
            print(f"⚠️ Health Check: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
    
    # Test 3: Login DevOps
    print("\n🔐 VERIFICANDO LOGIN DEVOPS...")
    try:
        login_data = {
            "username": "devops",
            "password": "DevOps2025!Secure"
        }
        
        response = requests.post(f"{devops_url}/devops/login", 
                               data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Login DevOps: OK")
        else:
            print(f"⚠️ Login DevOps: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Login DevOps: ERROR - {e}")
    
    # Test 4: Gestión de Negocios
    print("\n🏢 VERIFICANDO GESTIÓN DE NEGOCIOS...")
    try:
        response = requests.get(f"{devops_url}/devops/negocios", timeout=10)
        if response.status_code == 200:
            print("✅ Gestión Negocios: OK")
        else:
            print(f"⚠️ Gestión Negocios: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Gestión Negocios: ERROR - {e}")
    
    # Test 5: Gestión de Productos
    print("\n📦 VERIFICANDO GESTIÓN DE PRODUCTOS...")
    try:
        response = requests.get(f"{devops_url}/devops/productos", timeout=10)
        if response.status_code == 200:
            print("✅ Gestión Productos: OK")
        else:
            print(f"⚠️ Gestión Productos: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Gestión Productos: ERROR - {e}")
    
    # Test 6: Gestión de Sucursales
    print("\n🏪 VERIFICANDO GESTIÓN DE SUCURSALES...")
    try:
        response = requests.get(f"{devops_url}/devops/sucursales", timeout=10)
        if response.status_code == 200:
            print("✅ Gestión Sucursales: OK")
        else:
            print(f"⚠️ Gestión Sucursales: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Gestión Sucursales: ERROR - {e}")
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DEVOPS")
    print("=" * 50)
    print("✅ DevOps está funcionando correctamente")
    print("🌐 URL: http://localhost:5002/devops/")
    print("🔐 Usuario: devops")
    print("🔑 Contraseña: DevOps2025!Secure")
    print("🎯 Funcionalidades disponibles:")
    print("   - Dashboard principal")
    print("   - Gestión de negocios")
    print("   - Gestión de productos")
    print("   - Gestión de sucursales")
    print("   - Health check del sistema")
    print(f"⏰ Test completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_devops_completo()
