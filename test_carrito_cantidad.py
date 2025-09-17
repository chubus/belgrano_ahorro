#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad del carrito con cantidad
"""

import requests
import json

def test_carrito_cantidad():
    """Probar la funcionalidad del carrito con diferentes cantidades"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Probando funcionalidad del carrito con cantidad...")
    
    # Test 1: Agregar producto con cantidad 1
    print("\n📦 Test 1: Agregar producto con cantidad 1")
    data = {
        'producto_id': '1',
        'cantidad': 1
    }
    
    try:
        response = requests.post(f"{base_url}/agregar_al_carrito", data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Producto agregado: {result.get('mensaje', '')}")
            print(f"   Cantidad en carrito: {result.get('carrito_count', 0)}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 2: Agregar producto con cantidad 3
    print("\n📦 Test 2: Agregar producto con cantidad 3")
    data = {
        'producto_id': '2',
        'cantidad': 3
    }
    
    try:
        response = requests.post(f"{base_url}/agregar_al_carrito", data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Producto agregado: {result.get('mensaje', '')}")
            print(f"   Cantidad en carrito: {result.get('carrito_count', 0)}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Agregar producto con cantidad 5
    print("\n📦 Test 3: Agregar producto con cantidad 5")
    data = {
        'producto_id': '3',
        'cantidad': 5
    }
    
    try:
        response = requests.post(f"{base_url}/agregar_al_carrito", data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Producto agregado: {result.get('mensaje', '')}")
            print(f"   Cantidad en carrito: {result.get('carrito_count', 0)}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 4: Verificar carrito
    print("\n🛒 Test 4: Verificar contenido del carrito")
    try:
        response = requests.get(f"{base_url}/carrito")
        if response.status_code == 200:
            print("✅ Carrito accesible")
        else:
            print(f"❌ Error al acceder al carrito: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_verificar_servicio():
    """Verificar que el servicio esté funcionando"""
    print("\n🔍 Verificando servicio...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro está funcionando")
            return True
        else:
            print(f"⚠️ Belgrano Ahorro responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar con Belgrano Ahorro: {e}")
        print("   Asegúrate de que esté ejecutándose en http://localhost:5000")
        return False

if __name__ == "__main__":
    print("🎯 PRUEBA DE FUNCIONALIDAD DEL CARRITO CON CANTIDAD")
    print("=" * 60)
    
    if test_verificar_servicio():
        test_carrito_cantidad()
    
    print("\n🎯 Pruebas completadas")
