#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del endpoint de ofertas corregido
"""

import requests
import json
import sys
import os

def test_ofertas_local():
    """Probar el endpoint de ofertas localmente"""
    
    # Configuración local
    base_url = "http://localhost:5000"
    api_key = "belgrano_ahorro_api_key_2025"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("=" * 60)
    print("TEST DEL ENDPOINT DE OFERTAS CORREGIDO")
    print("=" * 60)
    
    # Test 1: GET /api/v1/ofertas
    print("\n1. Probando GET /api/v1/ofertas")
    try:
        response = requests.get(f"{base_url}/api/v1/ofertas", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Respuesta exitosa")
            print(f"   Total ofertas: {data.get('total', 0)}")
            if data.get('data'):
                print("   Primeras ofertas:")
                for oferta in data['data'][:3]:
                    print(f"     - ID: {oferta.get('id')}, Título: {oferta.get('titulo')}")
        else:
            print(f"   [ERROR] Código: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   [ERROR] No se puede conectar al servicio local")
        print("   Asegúrate de que la aplicación esté ejecutándose en puerto 5000")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Test 2: GET /api/offers (endpoint alternativo)
    print("\n2. Probando GET /api/offers")
    try:
        response = requests.get(f"{base_url}/api/offers", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Respuesta exitosa")
            print(f"   Total ofertas: {data.get('total', 0)}")
        else:
            print(f"   [ERROR] Código: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   [ERROR] No se puede conectar al servicio local")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Test 3: Verificar base de datos directamente
    print("\n3. Verificando base de datos directamente")
    try:
        import sqlite3
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ofertas")
        count = cursor.fetchone()[0]
        print(f"   [OK] Ofertas en BD: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, titulo, descuento_porcentaje, activa FROM ofertas LIMIT 3")
            rows = cursor.fetchall()
            print("   Primeras ofertas en BD:")
            for row in rows:
                print(f"     - ID: {row[0]}, Título: {row[1]}, Descuento: {row[2]}%, Activa: {row[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"   [ERROR] Error verificando BD: {e}")

if __name__ == "__main__":
    test_ofertas_local()
