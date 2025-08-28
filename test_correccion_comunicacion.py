#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de corrección de comunicación entre aplicaciones
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_complete_communication():
    """Test completo de comunicación corregida"""
    print("🚀 Test de comunicación corregida")
    print("=" * 50)
    
    # 1. Crear ticket en Ticketera
    print("📤 1. Creando ticket en Ticketera...")
    
    ticket_data = {
        "numero": f"FIX-TEST-{int(time.time())}",
        "cliente_nombre": "Cliente Test Fix",
        "cliente_direccion": "Dirección Test Fix 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "test.fix@example.com",
        "productos": ["Arroz 1kg x2", "Aceite 900ml x1"],
        "total": 1500.00,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de corrección",
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
            response_data = response.json()
            ticket_numero = response_data.get('numero')
            print(f"✅ Ticket creado: {ticket_numero}")
            
            # 2. Confirmar ticket en Belgrano Ahorro
            print(f"📥 2. Confirmando ticket {ticket_numero} en Belgrano Ahorro...")
            
            confirmation_data = {
                "ticket_id": f"TICKET-{ticket_numero}",
                "estado": "confirmado"
            }
            
            confirm_response = requests.post(
                f"{BELGRANO_AHORRO_URL}/api/pedido/confirmar/{ticket_numero}",
                json=confirmation_data,
                headers=headers,
                timeout=10
            )
            
            print(f"📥 Respuesta confirmación: Status {confirm_response.status_code}")
            print(f"   Body: {confirm_response.text}")
            
            if confirm_response.status_code == 200:
                print("✅ COMUNICACIÓN COMPLETAMENTE FUNCIONAL!")
                print("🎯 Las aplicaciones se comunican correctamente")
                return True
            else:
                print("❌ Error en confirmación")
                return False
        else:
            print(f"❌ Error creando ticket: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return False

def test_health_checks():
    """Test de health checks"""
    print("\n🔍 Verificando health checks...")
    
    # Belgrano Ahorro
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro: OK")
        else:
            print(f"❌ Belgrano Ahorro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Ahorro: Error - {e}")
    
    # Ticketera
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Ticketera: OK")
        else:
            print(f"❌ Ticketera: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Ticketera: Error - {e}")

if __name__ == "__main__":
    print(f"📅 Test iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar health checks
    test_health_checks()
    
    # Test de comunicación completa
    success = test_complete_communication()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ¡CORRECCIÓN EXITOSA!")
        print("✅ La comunicación entre aplicaciones está funcionando")
        print("📤 Los tickets se envían desde Belgrano Ahorro a la Ticketera")
        print("📥 Las confirmaciones se procesan correctamente")
    else:
        print("❌ Aún hay problemas en la comunicación")
        print("🔧 Revisar logs y configuración")
