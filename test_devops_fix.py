#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar las correcciones de DevOps
"""

import requests
import json
from datetime import datetime

def test_devops_endpoints():
    """Probar endpoints de DevOps"""
    base_url = "http://localhost:5002/devops"
    
    print("🔧 Probando correcciones de DevOps...")
    print("=" * 50)
    
    # Test 1: Login
    print("1. Probando login...")
    try:
        login_data = {
            'username': 'devops',
            'password': 'DevOps2025!Secure'
        }
        
        session = requests.Session()
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # Test 2: Negocios
    print("\n2. Probando /devops/negocios...")
    try:
        response = session.get(f"{base_url}/negocios")
        
        if response.status_code == 200:
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ Negocios devuelve HTML correctamente")
            else:
                print(f"❌ Negocios devuelve: {response.headers.get('content-type')}")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en negocios: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en negocios: {e}")
    
    # Test 3: Precios
    print("\n3. Probando /devops/precios...")
    try:
        response = session.get(f"{base_url}/precios")
        
        if response.status_code == 200:
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ Precios devuelve HTML correctamente")
            else:
                print(f"❌ Precios devuelve: {response.headers.get('content-type')}")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en precios: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en precios: {e}")
    
    # Test 4: Productos
    print("\n4. Probando /devops/productos...")
    try:
        response = session.get(f"{base_url}/productos")
        
        if response.status_code == 200:
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ Productos devuelve HTML correctamente")
            else:
                print(f"❌ Productos devuelve: {response.headers.get('content-type')}")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en productos: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en productos: {e}")
    
    # Test 5: Sucursales
    print("\n5. Probando /devops/sucursales...")
    try:
        response = session.get(f"{base_url}/sucursales")
        
        if response.status_code == 200:
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ Sucursales devuelve HTML correctamente")
            else:
                print(f"❌ Sucursales devuelve: {response.headers.get('content-type')}")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en sucursales: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en sucursales: {e}")
    
    # Test 6: Ofertas
    print("\n6. Probando /devops/ofertas...")
    try:
        response = session.get(f"{base_url}/ofertas")
        
        if response.status_code == 200:
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ Ofertas devuelve HTML correctamente")
            else:
                print(f"❌ Ofertas devuelve: {response.headers.get('content-type')}")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en ofertas: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en ofertas: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Pruebas completadas")
    
    return True

if __name__ == "__main__":
    test_devops_endpoints()
