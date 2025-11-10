#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el flujo DevOps -> Belgrano Ahorro
Prueba la creación de negocio, producto y oferta desde DevOps
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta

# Configuración
BELGRANO_AHORRO_URL = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_create_negocio():
    """Probar creación de negocio"""
    print_section("1. CREAR NEGOCIO")
    
    url = f"{BELGRANO_AHORRO_URL}/api/negocios"
    headers = {
        'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
        'Content-Type': 'application/json',
        'X-API-Key': BELGRANO_AHORRO_API_KEY
    }
    
    data = {
        'nombre': f'Negocio Test DevOps {datetime.now().strftime("%H%M%S")}',
        'descripcion': 'Negocio creado desde DevOps para prueba',
        'direccion': 'Calle Test 123',
        'telefono': '123456789',
        'email': 'test@devops.com',
        'activo': True
    }
    
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            negocio_id = result.get('data', {}).get('id')
            print(f"✅ Negocio creado exitosamente con ID: {negocio_id}")
            return negocio_id
        else:
            print(f"❌ Error creando negocio: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def test_create_producto(negocio_id):
    """Probar creación de producto"""
    print_section("2. CREAR PRODUCTO")
    
    if not negocio_id:
        print("❌ No se puede crear producto sin negocio_id")
        return None
    
    url = f"{BELGRANO_AHORRO_URL}/api/productos"
    headers = {
        'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
        'Content-Type': 'application/json',
        'X-API-Key': BELGRANO_AHORRO_API_KEY
    }
    
    data = {
        'nombre': f'Producto Test DevOps {datetime.now().strftime("%H%M%S")}',
        'descripcion': 'Producto creado desde DevOps para prueba',
        'precio': 199.99,
        'negocio_id': negocio_id,
        'categoria': 'Test',
        'stock': 10,
        'activo': True
    }
    
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            producto_id = result.get('data', {}).get('id')
            print(f"✅ Producto creado exitosamente con ID: {producto_id}")
            return producto_id
        else:
            print(f"❌ Error creando producto: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def test_create_oferta(producto_id, negocio_id):
    """Probar creación de oferta"""
    print_section("3. CREAR OFERTA")
    
    if not producto_id:
        print("❌ No se puede crear oferta sin producto_id")
        return None
    
    url = f"{BELGRANO_AHORRO_URL}/api/ofertas"
    headers = {
        'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
        'Content-Type': 'application/json',
        'X-API-Key': BELGRANO_AHORRO_API_KEY
    }
    
    fecha_inicio = datetime.now().strftime('%Y-%m-%d')
    fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    data = {
        'titulo': f'Oferta Test DevOps {datetime.now().strftime("%H%M%S")}',
        'descripcion': 'Oferta creada desde DevOps para prueba',
        'descuento': 15.0,
        'producto_id': producto_id,
        'negocio_id': negocio_id,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'activa': True
    }
    
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            oferta_id = result.get('data', {}).get('id')
            print(f"✅ Oferta creada exitosamente con ID: {oferta_id}")
            return oferta_id
        else:
            print(f"❌ Error creando oferta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None

def test_list_items():
    """Probar listado de items"""
    print_section("4. VERIFICAR ITEMS CREADOS")
    
    headers = {
        'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
        'X-API-Key': BELGRANO_AHORRO_API_KEY
    }
    
    # Listar negocios
    print("\n📋 Negocios:")
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/negocios", headers=headers, timeout=15)
        if response.status_code == 200:
            negocios = response.json().get('data', [])
            print(f"   Total: {len(negocios)} negocios")
            for negocio in negocios[-3:]:  # Mostrar últimos 3
                print(f"   - ID: {negocio.get('id')}, Nombre: {negocio.get('nombre')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Listar productos
    print("\n📦 Productos:")
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/productos", headers=headers, timeout=15)
        if response.status_code == 200:
            productos = response.json().get('data', [])
            print(f"   Total: {len(productos)} productos")
            for producto in productos[-3:]:  # Mostrar últimos 3
                print(f"   - ID: {producto.get('id')}, Nombre: {producto.get('nombre')}, Precio: ${producto.get('precio')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Listar ofertas
    print("\n🎯 Ofertas:")
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/ofertas", headers=headers, timeout=15)
        if response.status_code == 200:
            ofertas = response.json().get('data', [])
            print(f"   Total: {len(ofertas)} ofertas")
            for oferta in ofertas[-3:]:  # Mostrar últimos 3
                print(f"   - ID: {oferta.get('id')}, Nombre: {oferta.get('nombre')}, Descuento: {oferta.get('descuento')}%")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

def main():
    print("\n" + "="*60)
    print("  PRUEBA DE FLUJO DEVOPS -> BELGRANO AHORRO")
    print("="*60)
    print(f"URL: {BELGRANO_AHORRO_URL}")
    print(f"API Key: {BELGRANO_AHORRO_API_KEY[:10]}...")
    
    # Ejecutar pruebas
    negocio_id = test_create_negocio()
    producto_id = test_create_producto(negocio_id) if negocio_id else None
    oferta_id = test_create_oferta(producto_id, negocio_id) if producto_id else None
    
    # Verificar items creados
    test_list_items()
    
    # Resumen
    print_section("RESUMEN")
    if negocio_id and producto_id and oferta_id:
        print("✅ TODAS LAS PRUEBAS EXITOSAS")
        print(f"   - Negocio ID: {negocio_id}")
        print(f"   - Producto ID: {producto_id}")
        print(f"   - Oferta ID: {oferta_id}")
        print("\n✅ El flujo DevOps -> Belgrano Ahorro funciona correctamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print(f"   - Negocio: {'✅' if negocio_id else '❌'}")
        print(f"   - Producto: {'✅' if producto_id else '❌'}")
        print(f"   - Oferta: {'✅' if oferta_id else '❌'}")
        sys.exit(1)

if __name__ == '__main__':
    main()

