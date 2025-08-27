#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar comunicación entre servicios en producción
"""

import os
import json
import requests
import time
from datetime import datetime

# URLs de producción
AHORRO_URL = "https://belgranoahorro.onrender.com"
TICKETS_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_health_endpoints():
    """Probar endpoints de health check"""
    print("🔍 Probando endpoints de health check")
    print("=" * 50)
    
    # Probar Ahorro
    try:
        print(f"📡 Probando {AHORRO_URL}/healthz")
        ahorro_health = requests.get(f"{AHORRO_URL}/healthz", timeout=10)
        print(f"✅ Ahorro: {ahorro_health.status_code}")
        if ahorro_health.status_code == 200:
            print(f"   Respuesta: {json.dumps(ahorro_health.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Ahorro: Error - {e}")
    
    # Probar Tickets
    try:
        print(f"📡 Probando {TICKETS_URL}/healthz")
        tickets_health = requests.get(f"{TICKETS_URL}/healthz", timeout=10)
        print(f"✅ Tickets: {tickets_health.status_code}")
        if tickets_health.status_code == 200:
            print(f"   Respuesta: {json.dumps(tickets_health.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Tickets: Error - {e}")

def test_ticket_creation():
    """Probar creación de ticket"""
    print("\n🎫 Probando creación de ticket")
    print("=" * 50)
    
    # Datos de prueba
    ticket_data = {
        "numero": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "cliente_nombre": "Cliente Test Producción",
        "cliente_direccion": "Av. Test 123, CABA",
        "cliente_telefono": "1234567890",
        "cliente_email": "test@produccion.com",
        "productos": ["Producto Test 1", "Producto Test 2"],
        "total": 150.0,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de producción",
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
        print(f"📤 Enviando ticket a {TICKETS_URL}/api/tickets")
        print(f"📦 Datos: {json.dumps(ticket_data, indent=2)}")
        
        response = requests.post(
            f"{TICKETS_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code in (200, 201):
            result = response.json()
            print("✅ Ticket creado exitosamente:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ Error creando ticket: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error enviando ticket: {e}")
        return None

def test_confirmation_endpoint(ticket_response):
    """Probar endpoint de confirmación"""
    if not ticket_response:
        return
    
    print("\n✅ Probando endpoint de confirmación")
    print("=" * 50)
    
    numero_pedido = ticket_response.get('numero')
    confirmation_data = {
        'ticket_id': ticket_response.get('ticket_id'),
        'estado': 'confirmado'
    }
    
    try:
        print(f"📤 Confirmando ticket en {AHORRO_URL}/api/pedido/confirmar/{numero_pedido}")
        
        response = requests.post(
            f"{AHORRO_URL}/api/pedido/confirmar/{numero_pedido}",
            json=confirmation_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Ticket confirmado exitosamente:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error confirmando ticket: {response.text}")
            
    except Exception as e:
        print(f"❌ Error confirmando ticket: {e}")

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 PRUEBAS DE PRODUCCIÓN")
    print("Belgrano Ahorro ↔ Belgrano Tickets")
    print("=" * 60)
    
    # Paso 1: Health checks
    test_health_endpoints()
    
    # Paso 2: Crear ticket
    ticket_response = test_ticket_creation()
    
    # Paso 3: Confirmar ticket
    if ticket_response:
        test_confirmation_endpoint(ticket_response)
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()
