#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rápido del endpoint /api/tickets después de la corrección
"""

import requests
import json
import time

TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_endpoint():
    """Test rápido del endpoint"""
    print("🚀 Test rápido del endpoint /api/tickets")
    
    ticket_data = {
        "numero": f"QUICK-TEST-{int(time.time())}",
        "cliente_nombre": "Test Rápido",
        "cliente_direccion": "Test Dirección",
        "cliente_telefono": "123456789",
        "cliente_email": "test@test.com",
        "productos": ["Producto Test x1"],
        "total": 100.50,
        "metodo_pago": "efectivo",
        "indicaciones": "Test rápido",
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'BelgranoAhorro/1.0.0'
    }
    
    try:
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in (200, 201):
            print("✅ Endpoint funcionando correctamente!")
            return True
        else:
            print("❌ Endpoint aún tiene problemas")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_endpoint()
