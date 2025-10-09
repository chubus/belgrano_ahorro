#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la integración API entre Belgrano Ahorro y Tickets
"""

import requests
import json
import time

def test_api_tickets():
    """Probar la API de tickets"""
    
    # URL de la API (cambiar según el deploy)
    api_url = "http://localhost:5001/api/tickets"
    
    # Datos de prueba
    test_data = {
        "cliente": "Juan Pérez",
        "productos": ["Arroz", "Aceite", "Leche"],
        "total": 3500,
        "numero_pedido": f"TEST-{int(time.time())}",
        "direccion": "Av. Belgrano 123, CABA",
        "telefono": "1234567890",
        "email": "juan@test.com",
        "metodo_pago": "efectivo",
        "notas": "Entregar antes de las 18:00 - PRUEBA"
    }
    
    print("🧪 PROBANDO API DE TICKETS")
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
            print("✅ API funcionando correctamente")
            return True
        else:
            print("❌ Error en la API")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API")
        print("   Asegúrate de que la aplicación esté ejecutándose en puerto 5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_check():
    """Probar health check"""
    
    health_url = "http://localhost:5001/health"
    
    print("\n🏥 PROBANDO HEALTH CHECK")
    print("=" * 30)
    
    try:
        response = requests.get(health_url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health check funcionando")
            return True
        else:
            print("❌ Health check falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_get_tickets():
    """Probar obtener tickets"""
    
    tickets_url = "http://localhost:5001/api/tickets"
    
    print("\n📋 PROBANDO OBTENER TICKETS")
    print("=" * 30)
    
    try:
        response = requests.get(tickets_url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Obtener tickets funcionando")
            return True
        else:
            print("❌ Obtener tickets falló")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo tickets: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE LA API")
    print("=" * 50)
    
    # Probar health check
    health_ok = test_health_check()
    
    if health_ok:
        # Probar API de tickets
        api_ok = test_api_tickets()
        
        # Probar obtener tickets
        get_ok = test_get_tickets()
        
        if api_ok and get_ok:
            print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
            print("La API está lista para recibir tickets desde Belgrano Ahorro")
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
    else:
        print("\n❌ HEALTH CHECK FALLÓ")
        print("Verifica que la aplicación esté ejecutándose")
    
    print("\n📋 Para ver los tickets:")
    print("1. Ve a http://localhost:5001")
    print("2. Login con: admin@belgranoahorro.com / admin123")
    print("3. Ve a /tickets para ver el panel")
    
    print("\n🔗 URLs de prueba:")
    print("- Health: http://localhost:5001/health")
    print("- API: http://localhost:5001/api/tickets")
    print("- Panel: http://localhost:5001/tickets")
