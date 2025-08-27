#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests

# Configuración para pruebas
TICKETS_URL = os.environ.get('TICKETS_URL', 'http://127.0.0.1:5001')
API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

# URLs de producción para testing
if os.environ.get('RENDER_ENVIRONMENT') == 'production':
    TICKETS_URL = os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
    API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

payload = {
    "numero": "T-PRUEBA-APIKEY-01",
    "cliente_nombre": "Cliente Test",
    "cliente_direccion": "Av 123",
    "cliente_telefono": "123456",
    "cliente_email": "test@example.com",
    "productos": ["Prod1"],
    "total": 100
}

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

def test_api_connection():
    """Probar conexión con la API de Tickets"""
    url = f"{TICKETS_URL}/api/tickets"
    print(f"🔗 Probando conexión a: {url}")
    print(f"🔑 API Key: {API_KEY[:10]}...")
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"📊 Status: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                result = resp.json()
                print("✅ Respuesta exitosa:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return True
            except Exception as e:
                print(f"⚠️ Error parseando JSON: {e}")
                print(f"📄 Respuesta: {resp.text}")
                return False
        else:
            print(f"❌ Error HTTP {resp.status_code}")
            print(f"📄 Respuesta: {resp.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar a {url}")
        print("   Verifica que el servidor esté ejecutándose")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout al conectar con {url}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de Comunicación API - Belgrano Tickets")
    print("=" * 50)
    success = test_api_connection()
    
    if success:
        print("\n✅ Test completado exitosamente")
    else:
        print("\n❌ Test falló")
        exit(1)
