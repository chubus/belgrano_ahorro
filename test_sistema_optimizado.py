#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Optimizado del Sistema DevOps-Belgrano Ahorro
Verifica todas las correcciones implementadas
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = "http://localhost:5000"
TICKETERA_URL = "http://localhost:5001"
DEVOPS_URL = "http://localhost:5002"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_conectividad():
    """Test de conectividad básica"""
    print("🔍 VERIFICANDO CONECTIVIDAD...")
    
    servicios = {
        "Belgrano Ahorro": BELGRANO_AHORRO_URL,
        "Ticketera": TICKETERA_URL,
        "DevOps": f"{DEVOPS_URL}/devops/"
    }
    
    resultados = {}
    
    for nombre, url in servicios.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {nombre}: FUNCIONANDO")
                resultados[nombre] = True
            else:
                print(f"⚠️ {nombre}: Status {response.status_code}")
                resultados[nombre] = False
        except requests.exceptions.Timeout:
            print(f"⏰ {nombre}: TIMEOUT")
            resultados[nombre] = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {nombre}: NO CONECTADO")
            resultados[nombre] = False
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
            resultados[nombre] = False
    
    return resultados

def test_apis_belgrano():
    """Test de APIs de Belgrano Ahorro"""
    print("\n🛒 TESTEANDO APIs DE BELGRANO AHORRO...")
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test GET endpoints
    endpoints = ['negocios', 'productos', 'ofertas', 'sucursales', 'health']
    
    for endpoint in endpoints:
        try:
            url = f"{BELGRANO_AHORRO_URL}/api/{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ GET /api/{endpoint}: OK")
            else:
                print(f"⚠️ GET /api/{endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ GET /api/{endpoint}: ERROR - {e}")

def test_creacion_datos():
    """Test de creación de datos con validación mejorada"""
    print("\n📝 TESTEANDO CREACIÓN DE DATOS...")
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test crear negocio
    try:
        negocio_data = {
            "nombre": "Test Negocio Optimizado",
            "descripcion": "Negocio de prueba con validación mejorada",
            "direccion": "Calle Test 123",
            "telefono": "123456789",
            "email": "test@negocio.com",
            "activo": True
        }
        
        response = requests.post(f"{BELGRANO_AHORRO_URL}/api/negocios", 
                               headers=headers, json=negocio_data, timeout=10)
        
        if response.status_code == 201:
            print("✅ Crear negocio: OK")
            negocio_id = response.json().get('data', {}).get('id')
        else:
            print(f"⚠️ Crear negocio: Status {response.status_code}")
            negocio_id = None
    except Exception as e:
        print(f"❌ Crear negocio: ERROR - {e}")
        negocio_id = None
    
    # Test crear producto (sin descripcion)
    try:
        producto_data = {
            "nombre": "Producto Test Optimizado",
            "precio": 99.99,
            "categoria": "Test",
            "stock": 10,
            "negocio_id": negocio_id,
            "activo": True
        }
        
        response = requests.post(f"{BELGRANO_AHORRO_URL}/api/productos", 
                               headers=headers, json=producto_data, timeout=10)
        
        if response.status_code == 201:
            print("✅ Crear producto: OK")
        else:
            print(f"⚠️ Crear producto: Status {response.status_code}")
            if response.content:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Crear producto: ERROR - {e}")
    
    # Test crear sucursal (sin negocio_id)
    try:
        sucursal_data = {
            "nombre": "Sucursal Test Optimizada",
            "direccion": "Calle Sucursal 456",
            "telefono": "987654321",
            "email": "sucursal@test.com",
            "activo": True
        }
        
        response = requests.post(f"{BELGRANO_AHORRO_URL}/api/sucursales", 
                               headers=headers, json=sucursal_data, timeout=10)
        
        if response.status_code == 201:
            print("✅ Crear sucursal: OK")
        else:
            print(f"⚠️ Crear sucursal: Status {response.status_code}")
            if response.content:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Crear sucursal: ERROR - {e}")

def test_validacion_datos():
    """Test de validación de datos"""
    print("\n🔍 TESTEANDO VALIDACIÓN DE DATOS...")
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test validación de precio negativo
    try:
        producto_invalido = {
            "nombre": "Producto Precio Negativo",
            "precio": -10.0,
            "categoria": "Test"
        }
        
        response = requests.post(f"{BELGRANO_AHORRO_URL}/api/productos", 
                               headers=headers, json=producto_invalido, timeout=10)
        
        if response.status_code == 400:
            print("✅ Validación precio negativo: OK")
        else:
            print(f"⚠️ Validación precio negativo: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Validación precio negativo: ERROR - {e}")
    
    # Test validación de email inválido
    try:
        sucursal_invalida = {
            "nombre": "Sucursal Email Inválido",
            "email": "email-invalido"
        }
        
        response = requests.post(f"{BELGRANO_AHORRO_URL}/api/sucursales", 
                               headers=headers, json=sucursal_invalida, timeout=10)
        
        if response.status_code == 400:
            print("✅ Validación email inválido: OK")
        else:
            print(f"⚠️ Validación email inválido: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Validación email inválido: ERROR - {e}")

def test_devops_optimizado():
    """Test de DevOps con configuración optimizada"""
    print("\n🔧 TESTEANDO DEVOPS OPTIMIZADO...")
    
    # Test login DevOps
    try:
        login_data = {
            "username": "devops",
            "password": "DevOps2025!Secure"
        }
        
        response = requests.post(f"{DEVOPS_URL}/devops/login", 
                               data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Login DevOps: OK")
        else:
            print(f"⚠️ Login DevOps: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Login DevOps: ERROR - {e}")
    
    # Test panel DevOps
    try:
        response = requests.get(f"{DEVOPS_URL}/devops/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Panel DevOps: OK")
        else:
            print(f"⚠️ Panel DevOps: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Panel DevOps: ERROR - {e}")

def main():
    """Función principal"""
    print("🚀 TEST OPTIMIZADO DEL SISTEMA DEVOPS-BELGRANO AHORRO")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar tests
    resultados_conectividad = test_conectividad()
    test_apis_belgrano()
    test_creacion_datos()
    test_validacion_datos()
    test_devops_optimizado()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    servicios_funcionando = sum(1 for status in resultados_conectividad.values() if status)
    total_servicios = len(resultados_conectividad)
    
    print(f"🔗 Conectividad: {servicios_funcionando}/{total_servicios} servicios funcionando")
    
    if servicios_funcionando == total_servicios:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
    elif servicios_funcionando > 0:
        print("⚠️ Sistema parcialmente funcional")
    else:
        print("❌ Sistema no funcional")
    
    print(f"⏰ Test completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
