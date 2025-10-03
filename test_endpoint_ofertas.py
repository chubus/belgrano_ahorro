#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para el endpoint de ofertas
"""

import requests
import json
import sys

def test_endpoint_ofertas():
    """Probar el endpoint de ofertas con diferentes métodos"""
    
    base_url = "https://belgranoahorro-hp30.onrender.com"
    api_key = "belgrano_ahorro_api_key_2025"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("=" * 60)
    print("INVESTIGACIÓN DEL ENDPOINT DE OFERTAS")
    print("=" * 60)
    
    # Test 1: GET /api/v1/ofertas
    print("\n1. Probando GET /api/v1/ofertas")
    try:
        response = requests.get(f"{base_url}/api/v1/ofertas", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   Error Response: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: GET /api/offers (endpoint alternativo)
    print("\n2. Probando GET /api/offers")
    try:
        response = requests.get(f"{base_url}/api/offers", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   Error Response: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Verificar estructura de la base de datos
    print("\n3. Verificando estructura de base de datos")
    try:
        import sqlite3
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Verificar si existe la tabla ofertas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ofertas'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("   [OK] Tabla 'ofertas' existe")
            
            # Verificar estructura de la tabla
            cursor.execute("PRAGMA table_info(ofertas)")
            columns = cursor.fetchall()
            print("   Columnas de la tabla ofertas:")
            for col in columns:
                print(f"     - {col[1]} ({col[2]})")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM ofertas")
            count = cursor.fetchone()[0]
            print(f"   Registros en ofertas: {count}")
            
            # Mostrar algunos registros
            if count > 0:
                cursor.execute("SELECT id, titulo, activa FROM ofertas LIMIT 3")
                rows = cursor.fetchall()
                print("   Primeros registros:")
                for row in rows:
                    print(f"     - ID: {row[0]}, Título: {row[1]}, Activa: {row[2]}")
        else:
            print("   [ERROR] Tabla 'ofertas' no existe")
            
        conn.close()
        
    except Exception as e:
        print(f"   Error verificando BD: {e}")
    
    # Test 4: Probar endpoint de salud
    print("\n4. Probando endpoint de salud")
    try:
        response = requests.get(f"{base_url}/healthz", timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] Servicio respondiendo")
        else:
            print(f"   [ERROR] Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_endpoint_ofertas()
