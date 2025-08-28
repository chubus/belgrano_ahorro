#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo de comunicación entre Belgrano Ahorro y Ticketera
"""

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

def test_ticketera_endpoints():
    """Probar todos los endpoints de la Ticketera"""
    print("\n🎫 Probando endpoints de Ticketera...")
    
    # Test endpoint principal
    try:
        response = requests.get(f"{TICKETERA_URL}/", timeout=10)
        print(f"✅ Ticketera Home: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Ticketera Home: Error - {e}")
    
    # Test endpoint de login
    try:
        response = requests.get(f"{TICKETERA_URL}/login", timeout=10)
        print(f"✅ Ticketera Login: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Ticketera Login: Error - {e}")

def test_api_tickets_endpoint():
    """Probar el endpoint /api/tickets con datos reales"""
    print("\n🎫 Probando endpoint /api/tickets...")
    
    ticket_data = {
        "numero": f"DIAG-{int(time.time())}",
        "cliente_nombre": "Cliente Diagnóstico",
        "cliente_direccion": "Dirección Diagnóstico 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "diagnostico@test.com",
        "productos": ["Arroz 1kg x2", "Aceite 900ml x1", "Leche 1L x3"],
        "total": 2500.50,
        "metodo_pago": "efectivo",
        "indicaciones": "Prueba de diagnóstico completo",
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
        print(f"📤 Enviando datos a {TICKETERA_URL}/api/tickets")
        print(f"   Datos: {json.dumps(ticket_data, indent=2)}")
        
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        print(f"📥 Respuesta recibida:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.text}")
        
        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                print(f"✅ Ticket creado exitosamente:")
                print(f"   Ticket ID: {response_data.get('ticket_id', 'N/A')}")
                print(f"   Número: {response_data.get('numero', 'N/A')}")
                print(f"   Estado: {response_data.get('estado', 'N/A')}")
                print(f"   Repartidor: {response_data.get('repartidor_asignado', 'N/A')}")
                return response_data.get('numero')
            except json.JSONDecodeError:
                print(f"⚠️ Respuesta no es JSON válido: {response.text}")
                return None
        else:
            print(f"❌ Error creando ticket: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return None

def test_belgrano_ahorro_endpoints():
    """Probar endpoints de Belgrano Ahorro"""
    print("\n🛒 Probando endpoints de Belgrano Ahorro...")
    
    # Test home
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/", timeout=10)
        print(f"✅ Belgrano Ahorro Home: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Ahorro Home: Error - {e}")
    
    # Test endpoint de confirmación
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/pedido/confirmar/TEST-001", timeout=10)
        print(f"✅ Endpoint confirmación: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Endpoint confirmación: Error - {e}")

def test_complete_flow():
    """Probar flujo completo de comunicación"""
    print("\n🔄 Probando flujo completo de comunicación...")
    
    # 1. Crear ticket en Ticketera
    ticket_numero = test_api_tickets_endpoint()
    
    if not ticket_numero:
        print("❌ No se pudo crear ticket - flujo interrumpido")
        return False
    
    # 2. Confirmar ticket en Belgrano Ahorro
    print(f"\n✅ Confirmando ticket {ticket_numero} en Belgrano Ahorro...")
    
    confirmation_data = {
        "ticket_id": f"TICKET-{ticket_numero}",
        "estado": "confirmado"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    try:
        response = requests.post(
            f"{BELGRANO_AHORRO_URL}/api/pedido/confirmar/{ticket_numero}",
            json=confirmation_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📥 Respuesta confirmación:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Flujo completo exitoso!")
            return True
        else:
            print("❌ Error en confirmación")
            return False
            
    except Exception as e:
        print(f"❌ Error en confirmación: {e}")
        return False

def test_network_connectivity():
    """Probar conectividad de red"""
    print("\n🌐 Probando conectividad de red...")
    
    # Test DNS resolution
    try:
        import socket
        socket.gethostbyname("ticketerabelgrano.onrender.com")
        print("✅ DNS Ticketera: OK")
    except Exception as e:
        print(f"❌ DNS Ticketera: Error - {e}")
    
    try:
        socket.gethostbyname("belgranoahorro-hp30.onrender.com")
        print("✅ DNS Belgrano Ahorro: OK")
    except Exception as e:
        print(f"❌ DNS Belgrano Ahorro: Error - {e}")

def test_api_key_validation():
    """Probar validación de API key"""
    print("\n🔑 Probando validación de API key...")
    
    # Test con API key válida
    headers_valid = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'BelgranoAhorro/1.0.0'
    }
    
    # Test con API key inválida
    headers_invalid = {
        'Content-Type': 'application/json',
        'X-API-Key': 'invalid_key',
        'User-Agent': 'BelgranoAhorro/1.0.0'
    }
    
    ticket_data = {
        "numero": f"TEST-API-{int(time.time())}",
        "cliente_nombre": "Test API",
        "total": 100
    }
    
    # Test API key válida
    try:
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers_valid,
            timeout=10
        )
        if response.status_code != 401:
            print("✅ API key válida: Aceptada correctamente")
        else:
            print("❌ API key válida: Rechazada incorrectamente")
    except Exception as e:
        print(f"❌ Error probando API key válida: {e}")
    
    # Test API key inválida
    try:
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers_invalid,
            timeout=10
        )
        if response.status_code == 401:
            print("✅ API key inválida: Rechazada correctamente")
        else:
            print(f"❌ API key inválida: Aceptada incorrectamente (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error probando API key inválida: {e}")

def main():
    """Función principal de diagnóstico"""
    print("🚀 Diagnóstico completo de comunicación entre aplicaciones")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Belgrano Ahorro: {BELGRANO_AHORRO_URL}")
    print(f"🎫 Ticketera: {TICKETERA_URL}")
    print("=" * 70)
    
    # 1. Probar conectividad de red
    test_network_connectivity()
    
    # 2. Probar health checks
    test_health_checks()
    
    # 3. Probar endpoints básicos
    test_belgrano_ahorro_endpoints()
    test_ticketera_endpoints()
    
    # 4. Probar validación de API key
    test_api_key_validation()
    
    # 5. Probar endpoint de tickets
    ticket_numero = test_api_tickets_endpoint()
    
    # 6. Probar flujo completo
    if ticket_numero:
        flow_success = test_complete_flow()
    else:
        flow_success = False
    
    print("\n" + "=" * 70)
    print("🏁 Resumen del Diagnóstico")
    print("=" * 70)
    
    if ticket_numero and flow_success:
        print("✅ COMUNICACIÓN FUNCIONANDO CORRECTAMENTE")
        print("🎯 Las aplicaciones pueden comunicarse sin problemas")
        print("📤 Los tickets se envían desde Belgrano Ahorro a la Ticketera")
        print("📥 Las confirmaciones se procesan correctamente")
    else:
        print("❌ HAY PROBLEMAS EN LA COMUNICACIÓN")
        print("🔧 Revisar configuración y logs de ambas aplicaciones")
        print("📋 Verificar variables de entorno y URLs")
        print("🔑 Confirmar que las API keys son correctas")

if __name__ == "__main__":
    main()
