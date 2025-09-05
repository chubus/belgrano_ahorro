#!/usr/bin/env python3
"""
🔍 DEBUG ESPECÍFICO PARA ERROR 500 EN OFERTAS
=============================================

Script para diagnosticar específicamente el error 500 en la página de ofertas.
"""

import requests
import json
from datetime import datetime

def test_ofertas_debug():
    print("🔍 DIAGNÓSTICO ESPECÍFICO - ERROR 500 EN OFERTAS")
    print("=" * 60)
    
    devops_url = "https://ticketerabelgrano.onrender.com"
    session = requests.Session()
    
    # 1. Autenticar
    print("\n1. 🔐 AUTENTICANDO EN DEVOPS")
    try:
        response = session.post(
            f"{devops_url}/devops/login",
            data={"username": "devops", "password": "devops2025"},
            timeout=10,
            allow_redirects=False
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Autenticación exitosa")
        else:
            print("   ❌ Error en autenticación")
            return
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return
    
    # 2. Probar dashboard (debería funcionar)
    print("\n2. 📊 PROBANDO DASHBOARD")
    try:
        response = session.get(f"{devops_url}/devops/dashboard", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Dashboard funciona correctamente")
        else:
            print("   ❌ Dashboard con problemas")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # 3. Probar productos (debería funcionar)
    print("\n3. 📦 PROBANDO PRODUCTOS")
    try:
        response = session.get(f"{devops_url}/devops/productos", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Productos funciona correctamente")
        else:
            print("   ❌ Productos con problemas")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # 4. Probar negocios (debería funcionar)
    print("\n4. 🏢 PROBANDO NEGOCIOS")
    try:
        response = session.get(f"{devops_url}/devops/negocios", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Negocios funciona correctamente")
        else:
            print("   ❌ Negocios con problemas")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # 5. Probar sucursales (debería funcionar)
    print("\n5. 🏪 PROBANDO SUCURSALES")
    try:
        response = session.get(f"{devops_url}/devops/sucursales", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Sucursales funciona correctamente")
        else:
            print("   ❌ Sucursales con problemas")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # 6. Probar ofertas (PROBLEMA)
    print("\n6. 🏷️ PROBANDO OFERTAS (PROBLEMA)")
    try:
        response = session.get(f"{devops_url}/devops/ofertas", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Ofertas funciona correctamente")
        elif response.status_code == 500:
            print("   ❌ Error 500 en ofertas")
            print(f"   📝 Response headers: {dict(response.headers)}")
            print(f"   📝 Response content (first 500 chars): {response.text[:500]}")
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # 7. Probar precios
    print("\n7. 💰 PROBANDO PRECIOS")
    try:
        response = session.get(f"{devops_url}/devops/precios", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Precios funciona correctamente")
        else:
            print("   ❌ Precios con problemas")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    test_ofertas_debug()
