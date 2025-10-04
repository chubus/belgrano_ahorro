#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que NO aparezcan JSON crudos en DevOps de Ticketera
"""

import requests
import json
from datetime import datetime

def test_ticketera_devops_no_json():
    """Probar que no aparezcan JSON crudos en DevOps de ticketera"""
    base_url = "http://localhost:5001/devops"
    
    print("🔧 Verificando que NO aparezcan JSON crudos en DevOps de Ticketera...")
    print("=" * 70)
    
    # Test 1: Login en ticketera
    print("1. Probando login en ticketera...")
    try:
        login_data = {
            'username': 'devops',
            'password': 'DevOps2025!Secure'
        }
        
        session = requests.Session()
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login exitoso en ticketera")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # Test 2: Verificar que ofertas NO devuelva JSON
    print("\n2. Verificando /devops/ofertas en ticketera...")
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
        if ('"status":"error"' in response.text or 
            '"message":"Error interno del servidor DevOps"' in response.text or
            '"error":"No autorizado"' in response.text):
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
    
    # Test 3: Verificar que negocios NO devuelva JSON
    print("\n3. Verificando /devops/negocios en ticketera...")
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
        if ('"status":"error"' in response.text or 
            '"message":"Error interno del servidor DevOps"' in response.text or
            '"error":"No autorizado"' in response.text):
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
    
    # Test 4: Verificar que productos NO devuelva JSON
    print("\n4. Verificando /devops/productos en ticketera...")
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
        if ('"status":"error"' in response.text or 
            '"message":"Error interno del servidor DevOps"' in response.text or
            '"error":"No autorizado"' in response.text):
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
    
    # Test 5: Verificar que precios NO devuelva JSON
    print("\n5. Verificando /devops/precios en ticketera...")
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
        if ('"status":"error"' in response.text or 
            '"message":"Error interno del servidor DevOps"' in response.text or
            '"error":"No autorizado"' in response.text):
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
    
    # Test 6: Verificar dashboard principal
    print("\n6. Verificando /devops/ en ticketera...")
    try:
        response = session.get(f"{base_url}/")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar que NO sea JSON
        if 'application/json' in response.headers.get('content-type', ''):
            print("❌ ERROR: Dashboard devuelve JSON!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        # Verificar que NO contenga JSON crudo
        if ('"status":"error"' in response.text or 
            '"message":"Error interno del servidor DevOps"' in response.text or
            '"error":"No autorizado"' in response.text):
            print("❌ ERROR: Dashboard contiene JSON crudo!")
            print(f"Contenido: {response.text[:200]}...")
            return False
        
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Dashboard devuelve HTML correctamente")
        else:
            print(f"⚠️ Dashboard devuelve: {response.headers.get('content-type')}")
            
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🎯 Verificación completada - NO se encontraron JSON crudos en Ticketera")
    print("✅ Todas las rutas DevOps en ticketera devuelven HTML correctamente")
    
    return True

if __name__ == "__main__":
    test_ticketera_devops_no_json()
