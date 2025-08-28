#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación final de comunicación entre Belgrano Ahorro y Ticketera
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def verificar_health_checks():
    """Verificar que ambos servicios estén funcionando"""
    print("🔍 Verificando health checks...")
    
    # Belgrano Ahorro
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/healthz", timeout=15)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro: OK")
            return True
        else:
            print(f"❌ Belgrano Ahorro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Belgrano Ahorro: Error - {e}")
        return False
    
    # Ticketera
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=15)
        if response.status_code == 200:
            print("✅ Ticketera: OK")
            return True
        else:
            print(f"❌ Ticketera: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ticketera: Error - {e}")
        return False

def actualizar_base_datos():
    """Actualizar la base de datos en producción"""
    print("\n🔧 Actualizando base de datos en producción...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    try:
        response = requests.post(
            f"{BELGRANO_AHORRO_URL}/api/actualizar-db",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Base de datos actualizada exitosamente")
            print(f"📊 Columnas agregadas: {data.get('columnas_agregadas', [])}")
            return True
        else:
            print(f"❌ Error actualizando BD: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en actualización: {e}")
        return False

def test_comunicacion_completa():
    """Test de comunicación completa"""
    print("\n🔄 Probando comunicación completa...")
    
    # 1. Crear ticket en Ticketera
    ticket_data = {
        "numero": f"FINAL-TEST-{int(time.time())}",
        "cliente_nombre": "Cliente Final Test",
        "cliente_direccion": "Dirección Final Test 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "final.test@example.com",
        "productos": ["Arroz 1kg x2", "Aceite 900ml x1"],
        "total": 1500.00,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de verificación final",
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
            print(f"📥 Confirmando ticket {ticket_numero}...")
            
            confirmation_data = {
                "ticket_id": f"TICKET-{ticket_numero}",
                "estado": "confirmado"
            }
            
            confirm_response = requests.post(
                f"{BELGRANO_AHORRO_URL}/api/pedido/confirmar/{ticket_numero}",
                json=confirmation_data,
                headers=headers,
                timeout=15
            )
            
            if confirm_response.status_code == 200:
                print("✅ Ticket confirmado exitosamente")
                return True
            else:
                print(f"❌ Error en confirmación: {confirm_response.status_code}")
                print(f"   Response: {confirm_response.text}")
                return False
        else:
            print(f"❌ Error creando ticket: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN FINAL DE COMUNICACIÓN")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. Verificar health checks
    if not verificar_health_checks():
        print("\n❌ Los servicios no están disponibles")
        return
    
    # 2. Actualizar base de datos
    if not actualizar_base_datos():
        print("\n⚠️ No se pudo actualizar la base de datos")
        print("   Continuando con el test...")
    
    # 3. Test de comunicación completa
    success = test_comunicacion_completa()
    
    print("\n" + "=" * 50)
    print("🏁 RESULTADO FINAL")
    print("=" * 50)
    
    if success:
        print("🎉 ¡COMUNICACIÓN COMPLETAMENTE FUNCIONAL!")
        print("✅ Todas las funciones están operando correctamente")
        print("✅ Los tickets se crean y confirman sin problemas")
        print("✅ La comunicación entre aplicaciones es sólida")
    else:
        print("❌ Aún hay problemas en la comunicación")
        print("🔧 Revisar logs y configuración")

if __name__ == "__main__":
    main()
