#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el endpoint /api/tickets de la Ticketera funciona correctamente
"""

import requests
import json
import time
from datetime import datetime

# Configuración
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_health_check():
    """Probar health check de la Ticketera"""
    print("🔍 Probando health check de Ticketera...")
    
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health check OK: {response.text}")
            return True
        else:
            print(f"❌ Health check falló: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_api_tickets_endpoint():
    """Probar el endpoint /api/tickets"""
    print("\n🎫 Probando endpoint /api/tickets...")
    
    # Datos de prueba
    ticket_data = {
        "numero": f"TEST-{int(time.time())}",
        "cliente_nombre": "Cliente de Prueba",
        "cliente_direccion": "Dirección de Prueba 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "test@example.com",
        "productos": ["Arroz 1kg x2", "Aceite 900ml x1", "Leche 1L x3"],
        "total": 2500.50,
        "metodo_pago": "efectivo",
        "indicaciones": "Prueba de endpoint /api/tickets",
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

def test_api_tickets_recibir_endpoint():
    """Probar el endpoint alternativo /api/tickets/recibir"""
    print("\n🎫 Probando endpoint alternativo /api/tickets/recibir...")
    
    # Datos de prueba
    ticket_data = {
        "numero": f"TEST-RECIBIR-{int(time.time())}",
        "cliente_nombre": "Cliente de Prueba Recibir",
        "cliente_direccion": "Dirección de Prueba Recibir 456",
        "cliente_telefono": "9876543210",
        "cliente_email": "test.recibir@example.com",
        "productos": ["Fideos 500g x1", "Azúcar 1kg x2"],
        "total": 1800.00,
        "metodo_pago": "tarjeta",
        "indicaciones": "Prueba de endpoint /api/tickets/recibir",
        "estado": "pendiente",
        "prioridad": "alta",
        "tipo_cliente": "comerciante"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'BelgranoAhorro/1.0.0'
    }
    
    try:
        print(f"📤 Enviando datos a {TICKETERA_URL}/api/tickets/recibir")
        print(f"   Datos: {json.dumps(ticket_data, indent=2)}")
        
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets/recibir",
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
                print(f"✅ Ticket recibido exitosamente:")
                print(f"   Ticket ID: {response_data.get('ticket_id', 'N/A')}")
                print(f"   Número: {response_data.get('numero', 'N/A')}")
                print(f"   Estado: {response_data.get('estado', 'N/A')}")
                print(f"   Repartidor: {response_data.get('repartidor_asignado', 'N/A')}")
                return response_data.get('numero')
            except json.JSONDecodeError:
                print(f"⚠️ Respuesta no es JSON válido: {response.text}")
                return None
        else:
            print(f"❌ Error recibiendo ticket: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return None

def test_invalid_api_key():
    """Probar con API key inválida"""
    print("\n🔑 Probando con API key inválida...")
    
    ticket_data = {
        "numero": f"TEST-INVALID-{int(time.time())}",
        "cliente_nombre": "Cliente Test",
        "total": 100
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'invalid_key',
        'User-Agent': 'BelgranoAhorro/1.0.0'
    }
    
    try:
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ API key inválida rechazada correctamente")
            return True
        else:
            print(f"❌ API key inválida no fue rechazada: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando API key inválida: {e}")
        return False

def test_missing_data():
    """Probar con datos faltantes"""
    print("\n📝 Probando con datos faltantes...")
    
    # Datos incompletos
    ticket_data = {
        "numero": f"TEST-MISSING-{int(time.time())}"
        # Falta cliente_nombre y total
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
        
        if response.status_code == 400:
            print("✅ Datos faltantes rechazados correctamente")
            return True
        else:
            print(f"❌ Datos faltantes no fueron rechazados: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando datos faltantes: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del endpoint /api/tickets de Ticketera")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎫 Ticketera URL: {TICKETERA_URL}")
    print("=" * 60)
    
    # 1. Probar health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("❌ Health check falló - la aplicación no está disponible")
        return
    
    # 2. Probar endpoint principal /api/tickets
    ticket_numero_1 = test_api_tickets_endpoint()
    
    # 3. Probar endpoint alternativo /api/tickets/recibir
    ticket_numero_2 = test_api_tickets_recibir_endpoint()
    
    # 4. Probar validaciones de seguridad
    security_test_1 = test_invalid_api_key()
    security_test_2 = test_missing_data()
    
    print("\n" + "=" * 60)
    print("🏁 Resumen de Pruebas")
    print("=" * 60)
    
    print(f"✅ Health Check: {'OK' if health_ok else 'FAIL'}")
    print(f"✅ Endpoint /api/tickets: {'OK' if ticket_numero_1 else 'FAIL'}")
    print(f"✅ Endpoint /api/tickets/recibir: {'OK' if ticket_numero_2 else 'FAIL'}")
    print(f"✅ Validación API Key: {'OK' if security_test_1 else 'FAIL'}")
    print(f"✅ Validación Datos: {'OK' if security_test_2 else 'FAIL'}")
    
    if ticket_numero_1 or ticket_numero_2:
        print("\n🎉 El endpoint /api/tickets está funcionando correctamente!")
        print("✅ La Ticketera puede recibir tickets desde Belgrano Ahorro")
    else:
        print("\n❌ Hay problemas con el endpoint /api/tickets")
        print("🔧 Revisar logs y configuración de la Ticketera")

if __name__ == "__main__":
    main()
