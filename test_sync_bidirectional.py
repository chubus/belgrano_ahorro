#!/usr/bin/env python3
# =================================================================
# SCRIPT DE PRUEBA PARA SINCRONIZACIÓN BIDIRECCIONAL
# BELGRANO AHORRO ↔ BELGRANO TICKETERA
# =================================================================

import os
import sys
import requests
import json
from datetime import datetime

# Configuración de URLs
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"

# API Keys
BELGRANO_AHORRO_API_KEY = "belgrano_ahorro_api_key_2025"
TICKETERA_API_KEY = "ticketera_api_key_2025"

def test_health_check():
    """Probar health check de ambas plataformas"""
    print("🏥 Verificando salud de las plataformas...")
    
    # Test Belgrano Ahorro
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print(f"✅ Belgrano Ahorro: HEALTHY (Status: {response.status_code})")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️ Belgrano Ahorro: UNHEALTHY (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Belgrano Ahorro: ERROR - {e}")
    
    # Test Ticketera
    try:
        response = requests.get(f"{TICKETERA_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Ticketera: HEALTHY (Status: {response.status_code})")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️ Ticketera: UNHEALTHY (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Ticketera: ERROR - {e}")

def test_api_connection():
    """Probar conexión API entre plataformas"""
    print("\n🔗 Probando conexión API entre plataformas...")
    
    # Test desde Ahorro hacia Ticketera
    print("   📤 Ahorro → Ticketera:")
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0'
        }
        
        # Test simple de conexión
        response = requests.get(f"{TICKETERA_URL}/api/tickets", headers=headers, timeout=10)
        if response.status_code in [200, 401, 403]:  # Cualquier respuesta válida
            print(f"     ✅ Conexión exitosa (Status: {response.status_code})")
        else:
            print(f"     ⚠️ Conexión parcial (Status: {response.status_code})")
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")
    
    # Test desde Ticketera hacia Ahorro
    print("   📥 Ticketera → Ahorro:")
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': TICKETERA_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0'
        }
        
        # Test simple de conexión
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/v1/productos", headers=headers, timeout=10)
        if response.status_code in [200, 401, 403]:  # Cualquier respuesta válida
            print(f"     ✅ Conexión exitosa (Status: {response.status_code})")
        else:
            print(f"     ⚠️ Conexión parcial (Status: {response.status_code})")
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")

def test_sync_endpoints():
    """Probar endpoints de sincronización"""
    print("\n🔄 Probando endpoints de sincronización...")
    
    # Test endpoint de sincronización en Ahorro
    print("   📤 Endpoint sincronización Ahorro:")
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': TICKETERA_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0'
        }
        
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/sync/status", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"     ✅ Endpoint funcionando (Status: {response.status_code})")
            print(f"     Response: {response.json()}")
        else:
            print(f"     ⚠️ Endpoint con problemas (Status: {response.status_code})")
    except Exception as e:
        print(f"     ❌ Error en endpoint: {e}")
    
    # Test endpoint de sincronización en Ticketera
    print("   📥 Endpoint sincronización Ticketera:")
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0'
        }
        
        response = requests.get(f"{TICKETERA_URL}/api/sync/status", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"     ✅ Endpoint funcionando (Status: {response.status_code})")
            print(f"     Response: {response.json()}")
        else:
            print(f"     ⚠️ Endpoint con problemas (Status: {response.status_code})")
    except Exception as e:
        print(f"     ❌ Error en endpoint: {e}")

def test_product_sync():
    """Probar sincronización de productos"""
    print("\n📦 Probando sincronización de productos...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': TICKETERA_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0'
        }
        
        # Simular datos de productos para sincronización
        test_productos = [
            {
                'id': 'test_prod_001',
                'nombre': 'Producto de Prueba',
                'precio': 99.99,
                'categoria': 'test',
                'negocio': 'test_negocio',
                'stock': 10,
                'activo': True
            }
        ]
        
        sync_data = {
            'productos': test_productos,
            'origen': 'ticketera',
            'fecha_sync': datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{BELGRANO_AHORRO_URL}/api/v1/productos/sync",
            json=sync_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print(f"     ✅ Sincronización exitosa (Status: {response.status_code})")
            print(f"     Response: {response.json()}")
        else:
            print(f"     ⚠️ Sincronización con problemas (Status: {response.status_code})")
            print(f"     Response: {response.text}")
            
    except Exception as e:
        print(f"     ❌ Error en sincronización: {e}")

def test_ticket_sync():
    """Probar sincronización de tickets"""
    print("\n🎫 Probando sincronización de tickets...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0'
        }
        
        # Simular datos de ticket para sincronización
        test_ticket = {
            'numero': 'TEST-TICKET-001',
            'cliente_nombre': 'Cliente de Prueba',
            'cliente_email': 'test@example.com',
            'cliente_direccion': 'Dirección de Prueba',
            'cliente_telefono': '123456789',
            'productos': [
                {
                    'id': 'prod_001',
                    'nombre': 'Producto Test',
                    'precio': 50.00,
                    'cantidad': 2
                }
            ],
            'total': 100.00,
            'metodo_pago': 'efectivo',
            'indicaciones': 'Test de sincronización',
            'estado': 'pendiente',
            'origen': 'ahorro'
        }
        
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets/sync",
            json=test_ticket,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print(f"     ✅ Sincronización exitosa (Status: {response.status_code})")
            print(f"     Response: {response.json()}")
        else:
            print(f"     ⚠️ Sincronización con problemas (Status: {response.status_code})")
            print(f"     Response: {response.text}")
            
    except Exception as e:
        print(f"     ❌ Error en sincronización: {e}")

def main():
    """Función principal de pruebas"""
    print("🔗 PRUEBAS DE SINCRONIZACIÓN BIDIRECCIONAL")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Belgrano Ahorro: {BELGRANO_AHORRO_URL}")
    print(f"🎫 Ticketera: {TICKETERA_URL}")
    print()
    
    # Ejecutar pruebas
    test_health_check()
    test_api_connection()
    test_sync_endpoints()
    test_product_sync()
    test_ticket_sync()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
    print("📊 Revisa los resultados arriba para verificar la conectividad")

if __name__ == "__main__":
    main()
