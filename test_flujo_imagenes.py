#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el flujo de creación con IMÁGENES
Prueba la creación de negocio y producto con image_url para validar Auto-Healing
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = os.getenv('BELGRANO_AHORRO_URL', 'http://localhost:10000') # Default local para prueba rápida si corre
# Si estamos en entorno de desarrollo, intentar usar la URL de producción o localhost
if not os.getenv('BELGRANO_AHORRO_URL'):
    print("⚠️  BELGRANO_AHORRO_URL no definida. Usando default.")

BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_create_negocio_con_imagen():
    """Probar creación de negocio con imagen"""
    print_section("1. CREAR NEGOCIO CON IMAGEN")
    
    url = f"{BELGRANO_AHORRO_URL}/api/v1/negocios" # Usar v1 explícitamente
    headers = {
        'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
        'Content-Type': 'application/json',
        'X-API-Key': BELGRANO_AHORRO_API_KEY
    }
    
    # URL de imagen de prueba
    test_image_url = "https://via.placeholder.com/800x600.png?text=Negocio+Test"
    
    data = {
        'nombre': f'Negocio Imagen {datetime.now().strftime("%H%M%S")}',
        'descripcion': 'Negocio con imagen para probar Auto-Healing',
        'direccion': 'Av. Prueba 123',
        'telefono': '555-1234',
        'email': 'imagen@test.com',
        'activo': True,
        'image_url': test_image_url # Campo crítico
    }
    
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in (200, 201):
            result = response.json()
            # Adaptar según estructura de respuesta (data o directo)
            negocio_id = result.get('data', {}).get('id') if 'data' in result else result.get('id')
            
            if not negocio_id and 'id' in result:
                 negocio_id = result['id']
                 
            print(f"✅ Negocio creado exitosamente con ID: {negocio_id}")
            return negocio_id
        else:
            print(f"❌ Error creando negocio: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def test_create_producto_con_imagen(negocio_id):
    """Probar creación de producto con imagen"""
    print_section("2. CREAR PRODUCTO CON IMAGEN")
    
    if not negocio_id:
        print("❌ No se puede crear producto sin negocio_id")
        return None
    
    url = f"{BELGRANO_AHORRO_URL}/api/v1/productos"
    headers = {
        'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
        'Content-Type': 'application/json',
        'X-API-Key': BELGRANO_AHORRO_API_KEY
    }
    
    test_image_url = "https://via.placeholder.com/400x400.png?text=Producto+Test"
    
    data = {
        'nombre': f'Producto Imagen {datetime.now().strftime("%H%M%S")}',
        'store': 'Descripción del producto con imagen',
        'precio': 250.50,
        'negocio_id': negocio_id,
        'categoria': 'Pruebas',
        'stock': 50,
        'activo': True,
        'image_url': test_image_url, # Campo crítico
        'imagen': 'producto_test.jpg' # Campo legacy
    }
    
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in (200, 201):
            result = response.json()
            producto_id = result.get('data', {}).get('id') if 'data' in result else result.get('id')
            
            if not producto_id and 'id' in result:
                 producto_id = result['id']

            print(f"✅ Producto creado exitosamente con ID: {producto_id}")
            return producto_id
        else:
            print(f"❌ Error creando producto: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("  PRUEBA DE AUTO-HEALING DE IMÁGENES")
    print("="*60)
    
    # Ejecutar pruebas
    negocio_id = test_create_negocio_con_imagen()
    producto_id = test_create_producto_con_imagen(negocio_id) if negocio_id else None
    
    print_section("RESUMEN")
    if negocio_id and producto_id:
        print("✅ PRUEBA EXITOSA: Auto-Healing funcionó correctamente.")
        print("   Se crearon negocio y producto con image_url sin errores 500.")
    else:
        print("❌ PRUEBA FALLIDA: Hubo errores en la creación.")
        sys.exit(1)

if __name__ == '__main__':
    main()
