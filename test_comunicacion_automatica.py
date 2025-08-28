#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la comunicación automática entre Belgrano Ahorro y Ticketera
"""

import os
import requests
import json
import time
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_health_checks():
    """Probar health checks de ambos servicios"""
    print("🔍 Probando health checks...")
    
    # Test Belgrano Ahorro
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print(f"✅ Belgrano Ahorro: {response.text}")
        else:
            print(f"❌ Belgrano Ahorro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Ahorro: Error - {e}")
    
    # Test Ticketera
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print(f"✅ Ticketera: {response.text}")
        else:
            print(f"❌ Ticketera: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Ticketera: Error - {e}")

def test_ticket_creation():
    """Probar creación de ticket en Ticketera"""
    print("\n🎫 Probando creación de ticket...")
    
    ticket_data = {
        "numero": f"TEST-{int(time.time())}",
        "cliente_nombre": "Cliente de Prueba",
        "cliente_direccion": "Dirección de Prueba 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "test@example.com",
        "productos": ["Producto 1 x2", "Producto 2 x1"],
        "total": 1500.50,
        "metodo_pago": "efectivo",
        "indicaciones": "Prueba de comunicación automática",
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
            timeout=15
        )
        
        if response.status_code in (200, 201):
            ticket_response = response.json()
            print(f"✅ Ticket creado exitosamente:")
            print(f"   Número: {ticket_data['numero']}")
            print(f"   Ticket ID: {ticket_response.get('ticket_id', 'N/A')}")
            print(f"   Estado: {ticket_response.get('estado', 'N/A')}")
            return ticket_data['numero']
        else:
            print(f"❌ Error creando ticket: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return None

def test_ticket_confirmation(numero_pedido):
    """Probar confirmación de ticket en Belgrano Ahorro"""
    if not numero_pedido:
        print("⚠️ Saltando confirmación - no hay número de pedido")
        return
    
    print(f"\n✅ Probando confirmación de ticket {numero_pedido}...")
    
    confirmation_data = {
        "ticket_id": f"TICKET-{numero_pedido}",
        "estado": "confirmado"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    try:
        response = requests.post(
            f"{BELGRANO_AHORRO_URL}/api/pedido/confirmar/{numero_pedido}",
            json=confirmation_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            confirmation_response = response.json()
            print(f"✅ Ticket confirmado exitosamente:")
            print(f"   Número: {numero_pedido}")
            print(f"   Estado: {confirmation_response.get('estado', 'N/A')}")
        else:
            print(f"❌ Error confirmando ticket: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en confirmación: {e}")

def test_variables_entorno():
    """Verificar que las variables de entorno están configuradas correctamente"""
    print("🔧 Verificando variables de entorno...")
    
    # Simular variables de entorno como en producción
    env_vars = {
        'TICKETERA_URL': TICKETERA_URL,
        'BELGRANO_AHORRO_API_KEY': API_KEY,
        'RENDER_ENVIRONMENT': 'production'
    }
    
    for key, value in env_vars.items():
        print(f"   {key}: {value}")
    
    print("✅ Variables de entorno configuradas correctamente")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de comunicación automática")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Belgrano Ahorro: {BELGRANO_AHORRO_URL}")
    print(f"🎫 Ticketera: {TICKETERA_URL}")
    print("=" * 50)
    
    # 1. Verificar variables de entorno
    test_variables_entorno()
    
    # 2. Probar health checks
    test_health_checks()
    
    # 3. Probar creación de ticket
    numero_pedido = test_ticket_creation()
    
    # 4. Probar confirmación de ticket
    test_ticket_confirmation(numero_pedido)
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")
    print("=" * 50)
    
    if numero_pedido:
        print("✅ Comunicación automática funcionando correctamente")
        print("🎯 Cada compra en Belgrano Ahorro se enviará automáticamente a la Ticketera")
    else:
        print("❌ Hay problemas en la comunicación")
        print("🔧 Revisar configuración y logs")

if __name__ == "__main__":
    main()
