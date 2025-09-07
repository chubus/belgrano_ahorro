#!/usr/bin/env python3
"""
Script de prueba para verificar la sincronización entre DevOps y Belgrano Ahorro
"""

import requests
import json
import os
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = 'https://belgranoahorro-hp30.onrender.com/api/'
BELGRANO_AHORRO_API_KEY = 'belgrano_ahorro_api_key_2025'
API_TIMEOUT_SECS = 8

def test_api_connection():
    """Probar conexión con la API de Belgrano Ahorro"""
    print("🔍 Probando conexión con Belgrano Ahorro...")
    
    try:
        response = requests.get(
            f"{BELGRANO_AHORRO_URL}v1/productos",
            headers={'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}'},
            timeout=API_TIMEOUT_SECS
        )
        
        if response.status_code == 200:
            print("✅ Conexión exitosa con Belgrano Ahorro")
            productos = response.json()
            print(f"📊 Productos encontrados: {len(productos)}")
            return True
        else:
            print(f"❌ Error en conexión: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_negocios_endpoints():
    """Probar endpoints de negocios"""
    print("\n🏪 Probando endpoints de negocios...")
    
    # Test GET negocios
    try:
        response = requests.get(
            f"{BELGRANO_AHORRO_URL}v1/negocios",
            headers={'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}'},
            timeout=API_TIMEOUT_SECS
        )
        
        if response.status_code == 200:
            print("✅ GET /v1/negocios - OK")
            negocios = response.json()
            print(f"📊 Negocios encontrados: {len(negocios)}")
        else:
            print(f"⚠️ GET /v1/negocios - {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en GET negocios: {e}")

def test_productos_endpoints():
    """Probar endpoints de productos"""
    print("\n📦 Probando endpoints de productos...")
    
    # Test GET productos
    try:
        response = requests.get(
            f"{BELGRANO_AHORRO_URL}v1/productos",
            headers={'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}'},
            timeout=API_TIMEOUT_SECS
        )
        
        if response.status_code == 200:
            print("✅ GET /v1/productos - OK")
            productos = response.json()
            print(f"📊 Productos encontrados: {len(productos)}")
        else:
            print(f"⚠️ GET /v1/productos - {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en GET productos: {e}")

def test_ofertas_endpoints():
    """Probar endpoints de ofertas"""
    print("\n🎯 Probando endpoints de ofertas...")
    
    # Test GET ofertas
    try:
        response = requests.get(
            f"{BELGRANO_AHORRO_URL}v1/ofertas",
            headers={'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}'},
            timeout=API_TIMEOUT_SECS
        )
        
        if response.status_code == 200:
            print("✅ GET /v1/ofertas - OK")
            ofertas = response.json()
            print(f"📊 Ofertas encontradas: {len(ofertas)}")
        else:
            print(f"⚠️ GET /v1/ofertas - {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en GET ofertas: {e}")

def test_sucursales_endpoints():
    """Probar endpoints de sucursales"""
    print("\n🏢 Probando endpoints de sucursales...")
    
    # Test GET sucursales
    try:
        response = requests.get(
            f"{BELGRANO_AHORRO_URL}v1/sucursales",
            headers={'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}'},
            timeout=API_TIMEOUT_SECS
        )
        
        if response.status_code == 200:
            print("✅ GET /v1/sucursales - OK")
            sucursales = response.json()
            print(f"📊 Sucursales encontradas: {len(sucursales)}")
        else:
            print(f"⚠️ GET /v1/sucursales - {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en GET sucursales: {e}")

def test_notificaciones():
    """Probar endpoint de notificaciones"""
    print("\n📢 Probando endpoint de notificaciones...")
    
    # Test POST notificaciones
    try:
        payload = {
            'tipo_cambio': 'test_sincronizacion',
            'datos': {'test': True},
            'timestamp': datetime.utcnow().isoformat(),
            'origen': 'devops_test'
        }
        
        response = requests.post(
            f"{BELGRANO_AHORRO_URL}v1/notificaciones/cambios",
            headers={'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}'},
            json=payload,
            timeout=API_TIMEOUT_SECS
        )
        
        if response.status_code == 200:
            print("✅ POST /v1/notificaciones/cambios - OK")
        else:
            print(f"⚠️ POST /v1/notificaciones/cambios - {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en POST notificaciones: {e}")

def test_fallback_local():
    """Probar fallback local"""
    print("\n💾 Probando fallback local...")
    
    if os.path.exists('productos.json'):
        try:
            with open('productos.json', 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            print("✅ Archivo productos.json encontrado")
            print(f"📊 Productos locales: {len(datos.get('productos', []))}")
            print(f"📊 Negocios locales: {len(datos.get('negocios', {}))}")
            print(f"📊 Sucursales locales: {len(datos.get('sucursales', {}))}")
            print(f"📊 Ofertas locales: {len(datos.get('ofertas', {}))}")
            
        except Exception as e:
            print(f"❌ Error leyendo productos.json: {e}")
    else:
        print("⚠️ Archivo productos.json no encontrado")

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de sincronización DevOps - Belgrano Ahorro")
    print("=" * 60)
    
    # Probar conexión
    if test_api_connection():
        # Probar endpoints específicos
        test_negocios_endpoints()
        test_productos_endpoints()
        test_ofertas_endpoints()
        test_sucursales_endpoints()
        test_notificaciones()
    
    # Probar fallback local
    test_fallback_local()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("\n📋 Resumen:")
    print("- Si ves ✅, el endpoint funciona correctamente")
    print("- Si ves ⚠️, el endpoint existe pero puede tener problemas")
    print("- Si ves ❌, hay un error que necesita atención")

if __name__ == "__main__":
    main()
