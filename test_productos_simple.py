#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple de productos con información completa
"""

import requests
import json
import time

# Configuración
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_productos_completos():
    """Test simple de productos con información completa"""
    
    ticket_data = {
        "numero": f"TEST-PROD-{int(time.time())}",
        "cliente_nombre": "Cliente Test Productos",
        "cliente_direccion": "Dirección Test",
        "cliente_telefono": "1234567890",
        "cliente_email": "test@example.com",
        "productos": [
            {
                "id": 1,
                "nombre": "Arroz 1kg",
                "precio": 950.0,
                "cantidad": 2,
                "subtotal": 1900.0,
                "sucursal": "Sucursal Centro",
                "negocio": "Belgrano Ahorro",
                "categoria": "Granos y Cereales",
                "descripcion": "Arroz de grano largo",
                "stock": 50,
                "destacado": True
            },
            {
                "id": 2,
                "nombre": "Aceite 900ml",
                "precio": 1800.0,
                "cantidad": 1,
                "subtotal": 1800.0,
                "sucursal": "Sucursal Sur",
                "negocio": "Belgrano Ahorro",
                "categoria": "Condimentos",
                "descripcion": "Aceite de girasol",
                "stock": 45,
                "destacado": True
            }
        ],
        "total": 3700.0,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de productos completos",
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente",
        "fecha_creacion": "2025-08-28T23:10:00",
        "origen": "belgrano_ahorro"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    try:
        print("📤 Enviando productos con información completa...")
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in (200, 201):
            data = response.json()
            print("✅ Éxito!")
            print(f"Ticket ID: {data.get('ticket_id')}")
            print(f"Número: {data.get('numero')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_productos_completos()
