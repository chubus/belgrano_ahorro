#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la comunicación entre Belgrano Ahorro y Belgrano Tickets
"""

import requests
import json
import time
from datetime import datetime

# Configuración
AHORRO_URL = "http://localhost:5000"
TICKETS_URL = "http://localhost:5001"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_ahorro_api():
    """Probar API de Belgrano Ahorro"""
    print("🔍 Probando API de Belgrano Ahorro...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    # 1. Health check
    try:
        response = requests.get(f"{AHORRO_URL}/api/v1/health", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Health check de Ahorro: OK")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Service: {health_data.get('service')}")
        else:
            print(f"❌ Health check de Ahorro: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error en health check de Ahorro: {e}")
    
    # 2. Obtener productos
    try:
        response = requests.get(f"{AHORRO_URL}/api/v1/productos", headers=headers, timeout=10)
        if response.status_code == 200:
            productos_data = response.json()
            print(f"✅ Productos de Ahorro: {productos_data.get('total', 0)} productos")
        else:
            print(f"❌ Productos de Ahorro: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo productos de Ahorro: {e}")
    
    # 3. Obtener estadísticas
    try:
        response = requests.get(f"{AHORRO_URL}/api/v1/stats", headers=headers, timeout=10)
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas de Ahorro: {stats_data.get('stats', {}).get('total_pedidos', 0)} pedidos")
        else:
            print(f"❌ Estadísticas de Ahorro: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de Ahorro: {e}")

def test_tickets_api():
    """Probar API de Belgrano Tickets"""
    print("\n🎫 Probando API de Belgrano Tickets...")
    
    # 1. Health check
    try:
        response = requests.get(f"{TICKETS_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check de Tickets: OK")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Service: {health_data.get('service')}")
            print(f"   Ahorro API: {health_data.get('ahorro_api', 'unknown')}")
        else:
            print(f"❌ Health check de Tickets: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error en health check de Tickets: {e}")
    
    # 2. Obtener tickets
    try:
        response = requests.get(f"{TICKETS_URL}/api/tickets", timeout=10)
        if response.status_code == 200:
            tickets_data = response.json()
            print(f"✅ Tickets: {len(tickets_data.get('tickets', []))} tickets")
        else:
            print(f"❌ Tickets: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo tickets: {e}")

def test_comunicacion_bidireccional():
    """Probar comunicación bidireccional entre plataformas"""
    print("\n🔄 Probando comunicación bidireccional...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    # 1. Crear ticket de prueba en Tickets
    test_ticket = {
        "numero": "TEST-API-001",
        "cliente_nombre": "Cliente Test API",
        "cliente_direccion": "Dirección Test API",
        "cliente_telefono": "123456789",
        "cliente_email": "test-api@belgranoahorro.com",
        "productos": ["Producto Test API x1"],
        "total": 100.0,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de comunicación bidireccional"
    }
    
    try:
        response = requests.post(f"{TICKETS_URL}/api/tickets", json=test_ticket, timeout=10)
        if response.status_code == 201:
            print("✅ Ticket de prueba creado en Tickets")
            ticket_response = response.json()
            ticket_id = ticket_response.get('ticket_id')
            
            # 2. Sincronizar tickets hacia Ahorro
            sync_data = {
                "tickets": [{
                    "numero_pedido": test_ticket["numero"],
                    "ticket_id": ticket_id,
                    "estado": "pendiente",
                    "repartidor": "Test Repartidor",
                    "fecha_creacion": datetime.now().isoformat(),
                    "fecha_actualizacion": datetime.now().isoformat(),
                    "datos_completos": test_ticket
                }]
            }
            
            response = requests.post(f"{AHORRO_URL}/api/v1/sync/tickets", json=sync_data, headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ Tickets sincronizados hacia Ahorro")
            else:
                print(f"❌ Error sincronizando tickets: {response.status_code}")
                
        else:
            print(f"❌ Error creando ticket de prueba: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en comunicación bidireccional: {e}")

def test_endpoints_ahorro_desde_tickets():
    """Probar endpoints de Ahorro desde Tickets"""
    print("\n🌐 Probando endpoints de Ahorro desde Tickets...")
    
    # 1. Obtener productos desde Tickets
    try:
        response = requests.get(f"{TICKETS_URL}/api/ahorro/productos", timeout=10)
        if response.status_code == 200:
            productos_data = response.json()
            print(f"✅ Productos obtenidos desde Tickets: {len(productos_data.get('productos', []))} productos")
        else:
            print(f"❌ Error obteniendo productos desde Tickets: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en endpoint de productos desde Tickets: {e}")
    
    # 2. Probar conexión con Ahorro
    try:
        response = requests.get(f"{TICKETS_URL}/api/ahorro/test", timeout=10)
        if response.status_code == 200:
            test_data = response.json()
            print("✅ Test de conexión con Ahorro desde Tickets: OK")
            print(f"   Health check: {test_data.get('health_check', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Error en test de conexión: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en test de conexión desde Tickets: {e}")

def generar_reporte():
    """Generar reporte de la prueba"""
    reporte = {
        'fecha_prueba': datetime.now().isoformat(),
        'configuracion': {
            'ahorro_url': AHORRO_URL,
            'tickets_url': TICKETS_URL,
            'api_key': API_KEY
        },
        'resultados': {
            'ahorro_api': 'tested',
            'tickets_api': 'tested',
            'comunicacion_bidireccional': 'tested',
            'endpoints_ahorro_desde_tickets': 'tested'
        }
    }
    
    with open('reporte_prueba_comunicacion.json', 'w') as f:
        json.dump(reporte, f, indent=2)
    
    print(f"\n📄 Reporte guardado en: reporte_prueba_comunicacion.json")

def main():
    """Función principal"""
    print("🚀 PRUEBA DE COMUNICACIÓN ENTRE BELGRANO AHORRO Y TICKETS")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Ahorro URL: {AHORRO_URL}")
    print(f"🎫 Tickets URL: {TICKETS_URL}")
    print()
    
    # Ejecutar pruebas
    test_ahorro_api()
    test_tickets_api()
    test_comunicacion_bidireccional()
    test_endpoints_ahorro_desde_tickets()
    
    # Generar reporte
    generar_reporte()
    
    print("\n🏁 Prueba completada")
    print("=" * 30)

if __name__ == "__main__":
    main()
