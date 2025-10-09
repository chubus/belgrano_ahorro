#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que NO aparezcan JSON crudos en DevOps
"""

import requests
import json
from datetime import datetime

def test_no_json_crudo():
    """Probar que no aparezcan JSON crudos"""
    base_url = "http://localhost:5002/devops"
    
    print("🔧 Verificando que NO aparezcan JSON crudos...")
    print("=" * 60)
    
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
    
    # Test 2: Verificar que negocios NO devuelva JSON
    print("\n2. Verificando /devops/negocios...")
    try:
        response = session.get(f"{base_url}/negocios")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar que NO sea JSON
        if 'application/json' in response.headers.get('content-type', ''):
            print("❌ ERROR: Negocios devuelve JSON!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        # Verificar que NO contenga JSON crudo
        if '"status":"error"' in response.text or '"message":"Error interno del servidor DevOps"' in response.text:
            print("❌ ERROR: Negocios contiene JSON crudo!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Negocios devuelve HTML correctamente")
        else:
            print(f"⚠️ Negocios devuelve: {response.headers.get('content-type')}")
            
    except Exception as e:
        print(f"❌ Error en negocios: {e}")
        return False
    
    # Test 3: Verificar que precios NO devuelva JSON
    print("\n3. Verificando /devops/precios...")
    try:
        response = session.get(f"{base_url}/precios")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar que NO sea JSON
        if 'application/json' in response.headers.get('content-type', ''):
            print("❌ ERROR: Precios devuelve JSON!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        # Verificar que NO contenga JSON crudo
        if '"status":"error"' in response.text or '"message":"Error interno del servidor DevOps"' in response.text:
            print("❌ ERROR: Precios contiene JSON crudo!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Precios devuelve HTML correctamente")
        else:
            print(f"⚠️ Precios devuelve: {response.headers.get('content-type')}")
            
    except Exception as e:
        print(f"❌ Error en precios: {e}")
        return False
    
    # Test 4: Verificar que productos NO devuelva JSON
    print("\n4. Verificando /devops/productos...")
    try:
        response = session.get(f"{base_url}/productos")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar que NO sea JSON
        if 'application/json' in response.headers.get('content-type', ''):
            print("❌ ERROR: Productos devuelve JSON!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        # Verificar que NO contenga JSON crudo
        if '"status":"error"' in response.text or '"message":"Error interno del servidor DevOps"' in response.text:
            print("❌ ERROR: Productos contiene JSON crudo!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Productos devuelve HTML correctamente")
        else:
            print(f"⚠️ Productos devuelve: {response.headers.get('content-type')}")
            
    except Exception as e:
        print(f"❌ Error en productos: {e}")
        return False
    
    # Test 5: Verificar que sucursales NO devuelva JSON
    print("\n5. Verificando /devops/sucursales...")
    try:
        response = session.get(f"{base_url}/sucursales")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar que NO sea JSON
        if 'application/json' in response.headers.get('content-type', ''):
            print("❌ ERROR: Sucursales devuelve JSON!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        # Verificar que NO contenga JSON crudo
        if '"status":"error"' in response.text or '"message":"Error interno del servidor DevOps"' in response.text:
            print("❌ ERROR: Sucursales contiene JSON crudo!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Sucursales devuelve HTML correctamente")
        else:
            print(f"⚠️ Sucursales devuelve: {response.headers.get('content-type')}")
            
    except Exception as e:
        print(f"❌ Error en sucursales: {e}")
        return False
    
    # Test 6: Verificar que ofertas NO devuelva JSON
    print("\n6. Verificando /devops/ofertas...")
    try:
        response = session.get(f"{base_url}/ofertas")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar que NO sea JSON
        if 'application/json' in response.headers.get('content-type', ''):
            print("❌ ERROR: Ofertas devuelve JSON!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        # Verificar que NO contenga JSON crudo
        if '"status":"error"' in response.text or '"message":"Error interno del servidor DevOps"' in response.text:
            print("❌ ERROR: Ofertas contiene JSON crudo!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Ofertas devuelve HTML correctamente")
        else:
            print(f"⚠️ Ofertas devuelve: {response.headers.get('content-type')}")
            
    except Exception as e:
        print(f"❌ Error en ofertas: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Verificación completada - NO se encontraron JSON crudos")
    print("✅ Todas las rutas devuelven HTML correctamente")
    
    return True

if __name__ == "__main__":
    test_no_json_crudo()
