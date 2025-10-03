#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple del endpoint de ofertas
"""

import requests
import json

def test_ofertas_simple():
    """Test simple del endpoint de ofertas"""
    
    print("TEST SIMPLE DEL ENDPOINT DE OFERTAS")
    print("=" * 50)
    
    # Probar endpoint local
    base_url = "http://localhost:5000"
    api_key = "belgrano_ahorro_api_key_2025"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("\n1. Probando endpoint local...")
    try:
        response = requests.get(f"{base_url}/api/v1/ofertas", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   [OK] Endpoint funcionando")
            print(f"   Total ofertas: {data.get('total', 0)}")
            return True
        else:
            print(f"   [ERROR] Codigo: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   [ERROR] No se puede conectar - aplicacion no iniciada")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    test_ofertas_simple()
