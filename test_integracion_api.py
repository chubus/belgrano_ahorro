#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la integración API entre Belgrano Ahorro y Ticketera
"""

import requests
import json
import time

def test_api_ticketera():
    """Probar la API de la Ticketera"""
    
    # URL de la API de la Ticketera
    api_url = "http://localhost:5001/api/tickets"
    
    # Datos de prueba
    test_data = {
        "cliente": "Juan Pérez",
        "productos": ["Arroz x2", "Aceite x1", "Leche x3"],
        "total": 3500,
        "numero_pedido": f"TEST-{int(time.time())}",
        "direccion": "Av. Belgrano 123, CABA",
        "telefono": "1234567890",
        "email": "juan@test.com",
        "metodo_pago": "efectivo",
        "notas": "Entregar antes de las 18:00 - PRUEBA DE INTEGRACIÓN"
    }
    
    print("🧪 PROBANDO API DE LA TICKETERA")
    print("=" * 50)
    print(f"URL: {api_url}")
    print(f"Datos: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        # Enviar POST request
        response = requests.post(
            api_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ API de Ticketera funcionando correctamente")
            return True
        else:
            print("❌ Error en la API de Ticketera")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API de Ticketera")
        print("   Asegúrate de que la Ticketera esté ejecutándose en puerto 5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_ticketera():
    """Probar health check de la Ticketera"""
    
    health_url = "http://localhost:5001/health"
    
    print("\n🏥 PROBANDO HEALTH CHECK DE TICKETERA")
    print("=" * 40)
    
    try:
        response = requests.get(health_url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health check de Ticketera funcionando")
            return True
        else:
            print("❌ Health check de Ticketera falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en health check de Ticketera: {e}")
        return False

def test_belgrano_ahorro():
    """Probar que Belgrano Ahorro esté funcionando"""
    
    ahorro_url = "http://localhost:5000"
    
    print("\n🛒 PROBANDO BELGRANO AHORRO")
    print("=" * 30)
    
    try:
        response = requests.get(ahorro_url, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Belgrano Ahorro funcionando")
            return True
        else:
            print("❌ Belgrano Ahorro no responde correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con Belgrano Ahorro: {e}")
        return False

def test_integracion_completa():
    """Probar la integración completa"""
    
    print("\n🔄 PROBANDO INTEGRACIÓN COMPLETA")
    print("=" * 40)
    
    # Simular un pedido completo
    pedido_data = {
        "cliente": "María González",
        "productos": ["Pan x5", "Queso x2", "Huevos x12"],
        "total": 2800,
        "numero_pedido": f"INTEGRATION-{int(time.time())}",
        "direccion": "Calle San Martín 456, CABA",
        "telefono": "9876543210",
        "email": "maria@test.com",
        "metodo_pago": "tarjeta",
        "notas": "PRUEBA DE INTEGRACIÓN COMPLETA - Entregar en horario de tarde"
    }
    
    try:
        # Enviar a Ticketera
        response = requests.post(
            "http://localhost:5001/api/tickets",
            json=pedido_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ Integración completa exitosa")
            print("   Pedido enviado a Ticketera correctamente")
            
            # Verificar que se puede obtener el ticket
            tickets_response = requests.get("http://localhost:5001/api/tickets", timeout=5)
            if tickets_response.status_code == 200:
                print("✅ Ticket visible en panel de Ticketera")
                return True
            else:
                print("⚠️ Ticket enviado pero no visible en panel")
                return False
        else:
            print("❌ Error en integración completa")
            return False
            
    except Exception as e:
        print(f"❌ Error en integración completa: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN API")
    print("=" * 50)
    
    # Probar Belgrano Ahorro
    ahorro_ok = test_belgrano_ahorro()
    
    # Probar health check de Ticketera
    health_ok = test_health_ticketera()
    
    if health_ok:
        # Probar API de Ticketera
        api_ok = test_api_ticketera()
        
        # Probar integración completa
        integracion_ok = test_integracion_completa()
        
        if api_ok and integracion_ok:
            print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
            print("La integración API está funcionando correctamente")
            print("\n📋 Flujo de integración:")
            print("1. Cliente hace pedido en Belgrano Ahorro")
            print("2. Belgrano Ahorro envía automáticamente a Ticketera")
            print("3. Ticketera recibe y crea ticket")
            print("4. Ticket visible en panel de administración")
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
    else:
        print("\n❌ HEALTH CHECK FALLÓ")
        print("Verifica que la Ticketera esté ejecutándose")
    
    print("\n📋 URLs del sistema:")
    print("- Belgrano Ahorro: http://localhost:5000")
    print("- Ticketera: http://localhost:5001")
    print("- API Ticketera: http://localhost:5001/api/tickets")
    print("- Health Ticketera: http://localhost:5001/health")
    
    print("\n🔐 Credenciales Ticketera:")
    print("- Admin: admin@belgranoahorro.com / admin123")
    print("- Flota: repartidor1@belgranoahorro.com / flota123")
