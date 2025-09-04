#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba para Sistema de Sincronización DevOps
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
API_KEY = "belgrano_ahorro_api_key_2025"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    "X-Origin": "devops"
}

def test_endpoint(endpoint, method="GET", data=None):
    """Probar endpoint específico"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        
        success = response.status_code in [200, 201]
        result = response.json() if success else response.text
        
        print(f"{'✅' if success else '❌'} {method} {endpoint}: {response.status_code}")
        if success and data:
            print(f"   📊 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return success, result
        
    except Exception as e:
        print(f"❌ Error en {method} {endpoint}: {e}")
        return False, str(e)

def main():
    """Ejecutar pruebas principales"""
    print("🚀 PRUEBAS DEL SISTEMA DEVOPS")
    print(f"📍 URL: {BASE_URL}")
    print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    
    # Pruebas básicas
    test_endpoint("/devops/health")
    test_endpoint("/devops/sync/status")
    test_endpoint("/devops/info")
    
    # Pruebas de datos
    test_endpoint("/devops/negocios")
    test_endpoint("/devops/sucursales")
    test_endpoint("/devops/ofertas")
    
    # Prueba de sincronización
    test_endpoint("/devops/sync/force", "POST")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main()
