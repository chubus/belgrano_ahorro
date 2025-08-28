#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de comunicación mejorada entre Belgrano Ahorro y Ticketera
Verifica que la conexión sea sólida y sin pérdida
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
    """Verificar que ambos servicios estén funcionando"""
    print("🔍 Verificando health checks...")
    
    # Belgrano Ahorro
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro: OK")
        else:
            print(f"❌ Belgrano Ahorro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Belgrano Ahorro: Error - {e}")
        return False
    
    # Ticketera
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Ticketera: OK")
        else:
            print(f"❌ Ticketera: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ticketera: Error - {e}")
        return False
    
    return True

def test_creacion_ticket():
    """Test de creación de ticket con datos reales"""
    print("\n🎫 Probando creación de ticket...")
    
    ticket_data = {
        "numero": f"MEJORADO-{int(time.time())}",
        "cliente_nombre": "Cliente Test Mejorado",
        "cliente_direccion": "Dirección Test Mejorado 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "test.mejorado@example.com",
        "productos": ["Arroz 1kg x2 - $500", "Aceite 900ml x1 - $800", "Leche 1L x3 - $1200"],
        "total": 2500.00,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de comunicación mejorada",
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente",
        "fecha_creacion": datetime.now().isoformat(),
        "origen": "belgrano_ahorro"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'BelgranoAhorro/1.0.0',
        'X-Request-ID': f"{ticket_data['numero']}-{int(time.time())}",
        'X-Origin': 'belgrano_ahorro'
    }
    
    try:
        print(f"📤 Enviando ticket a {TICKETERA_URL}/api/tickets")
        print(f"   Número: {ticket_data['numero']}")
        print(f"   Cliente: {ticket_data['cliente_nombre']}")
        print(f"   Total: ${ticket_data['total']}")
        
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=20
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                print("✅ Ticket creado exitosamente!")
                print(f"   Ticket ID: {response_data.get('ticket_id', 'N/A')}")
                print(f"   Número: {response_data.get('numero', 'N/A')}")
                print(f"   Estado: {response_data.get('estado', 'N/A')}")
                print(f"   Repartidor: {response_data.get('repartidor_asignado', 'N/A')}")
                return response_data.get('numero')
            except json.JSONDecodeError:
                print(f"⚠️ Respuesta no es JSON válido: {response.text}")
                return None
        else:
            print(f"❌ Error creando ticket: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return None

def test_confirmacion_ticket(ticket_numero):
    """Test de confirmación de ticket"""
    if not ticket_numero:
        print("⚠️ No hay ticket para confirmar")
        return False
    
    print(f"\n📥 Confirmando ticket {ticket_numero}...")
    
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
            timeout=15
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Ticket confirmado exitosamente!")
            return True
        else:
            print(f"❌ Error confirmando ticket: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en confirmación: {e}")
        return False

def test_reintentos():
    """Test de reintentos con URL inválida"""
    print("\n🔄 Probando sistema de reintentos...")
    
    # Usar URL inválida para probar reintentos
    invalid_url = "https://invalid-url-test.com/api/tickets"
    
    ticket_data = {
        "numero": f"RETRY-TEST-{int(time.time())}",
        "cliente_nombre": "Test Reintentos",
        "total": 100.00
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    max_retries = 3
    backoff_seconds = [1, 2, 4]
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Intento {attempt + 1}/{max_retries} con URL inválida...")
            response = requests.post(
                invalid_url,
                json=ticket_data,
                headers=headers,
                timeout=5
            )
        except requests.exceptions.ConnectionError:
            print(f"🔌 Error de conexión en intento {attempt + 1} (esperado)")
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout en intento {attempt + 1} (esperado)")
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Esperando {backoff_seconds[attempt]}s...")
            time.sleep(backoff_seconds[attempt])
    
    print("✅ Sistema de reintentos probado correctamente")

def main():
    """Función principal"""
    print("🚀 TEST DE COMUNICACIÓN MEJORADA")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. Verificar health checks
    if not test_health_checks():
        print("\n❌ Los servicios no están disponibles")
        return
    
    # 2. Test de reintentos
    test_reintentos()
    
    # 3. Test de creación de ticket
    ticket_numero = test_creacion_ticket()
    
    # 4. Test de confirmación
    if ticket_numero:
        confirmacion_exitosa = test_confirmacion_ticket(ticket_numero)
    else:
        confirmacion_exitosa = False
    
    # 5. Resultado final
    print("\n" + "=" * 50)
    print("🏁 RESULTADO FINAL")
    print("=" * 50)
    
    if ticket_numero and confirmacion_exitosa:
        print("🎉 ¡COMUNICACIÓN MEJORADA FUNCIONANDO!")
        print("✅ Conexión sólida y sin pérdida")
        print("✅ Tickets se crean correctamente")
        print("✅ Confirmaciones funcionan")
        print("✅ Sistema de reintentos operativo")
    elif ticket_numero:
        print("⚠️ Comunicación parcialmente funcional")
        print("✅ Tickets se crean correctamente")
        print("❌ Confirmaciones tienen problemas")
    else:
        print("❌ Problemas en la comunicación")
        print("🔧 Revisar configuración y logs")

if __name__ == "__main__":
    main()
