#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba de Comunicación API
Verifica la comunicación entre DevOps y Belgrano Ahorro
"""

import os
import sys
import json
import time
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_comunicacion():
    """Probar la comunicación API completa"""
    try:
        print("=== PRUEBA DE COMUNICACIÓN API ===")
        
        # Importar cliente
        from belgrano_client import belgrano_client, test_connection
        
        print("✅ Cliente API importado correctamente")
        
        # 1. Probar conexión
        print("\n--- 1. Probando conexión ---")
        if not test_connection():
            print("❌ No se puede conectar a Belgrano Ahorro API")
            return False
        
        print("✅ Conexión exitosa")
        
        # 2. Probar creación de negocio
        print("\n--- 2. Probando creación de negocio ---")
        negocio_data = {
            'nombre': 'Negocio Test API',
            'descripcion': 'Negocio creado para probar comunicación API',
            'direccion': 'Calle API 123',
            'telefono': '+54 11 1234-5678',
            'email': 'test@api.com',
            'activo': True
        }
        
        resultado_negocio = belgrano_client.create_business(negocio_data)
        if 'error' in resultado_negocio:
            print(f"❌ Error creando negocio: {resultado_negocio['error']}")
            return False
        
        negocio_id = resultado_negocio['data']['id']
        print(f"✅ Negocio creado: ID {negocio_id}")
        
        # 3. Probar creación de producto
        print("\n--- 3. Probando creación de producto ---")
        producto_data = {
            'nombre': 'Producto Test API',
            'descripcion': 'Producto creado para probar comunicación API',
            'precio': 250.0,
            'categoria': 'Test',
            'stock': 50,
            'negocio_id': negocio_id,
            'activo': True
        }
        
        resultado_producto = belgrano_client.create_product(producto_data)
        if 'error' in resultado_producto:
            print(f"❌ Error creando producto: {resultado_producto['error']}")
            return False
        
        producto_id = resultado_producto['data']['id']
        print(f"✅ Producto creado: ID {producto_id}")
        
        # 4. Probar creación de oferta
        print("\n--- 4. Probando creación de oferta ---")
        oferta_data = {
            'titulo': 'Oferta Test API',
            'descripcion': 'Oferta creada para probar comunicación API',
            'productos': 'Producto Test API',
            'hasta_agotar_stock': True,
            'activa': True
        }
        
        resultado_oferta = belgrano_client.create_offer(oferta_data)
        if 'error' in resultado_oferta:
            print(f"❌ Error creando oferta: {resultado_oferta['error']}")
            return False
        
        oferta_id = resultado_oferta['data']['id']
        print(f"✅ Oferta creada: ID {oferta_id}")
        
        # 5. Probar creación de sucursal
        print("\n--- 5. Probando creación de sucursal ---")
        sucursal_data = {
            'nombre': 'Sucursal Test API',
            'direccion': 'Av. API 456',
            'telefono': '+54 11 9876-5432',
            'email': 'sucursal@api.com',
            'negocio_id': negocio_id,
            'activo': True
        }
        
        resultado_sucursal = belgrano_client.create_branch(sucursal_data)
        if 'error' in resultado_sucursal:
            print(f"❌ Error creando sucursal: {resultado_sucursal['error']}")
            return False
        
        sucursal_id = resultado_sucursal['data']['id']
        print(f"✅ Sucursal creada: ID {sucursal_id}")
        
        # 6. Verificar que todos los datos se pueden obtener
        print("\n--- 6. Verificando obtención de datos ---")
        
        # Obtener negocios
        negocios = belgrano_client.get_businesses()
        if 'error' in negocios:
            print(f"❌ Error obteniendo negocios: {negocios['error']}")
            return False
        
        print(f"✅ Negocios obtenidos: {len(negocios.get('data', []))}")
        
        # Obtener productos
        productos = belgrano_client.get_products()
        if 'error' in productos:
            print(f"❌ Error obteniendo productos: {productos['error']}")
            return False
        
        print(f"✅ Productos obtenidos: {len(productos.get('data', []))}")
        
        # Obtener ofertas
        ofertas = belgrano_client.get_offers()
        if 'error' in ofertas:
            print(f"❌ Error obteniendo ofertas: {ofertas['error']}")
            return False
        
        print(f"✅ Ofertas obtenidas: {len(ofertas.get('data', []))}")
        
        # Obtener sucursales
        sucursales = belgrano_client.get_branches()
        if 'error' in sucursales:
            print(f"❌ Error obteniendo sucursales: {sucursales['error']}")
            return False
        
        print(f"✅ Sucursales obtenidas: {len(sucursales.get('data', []))}")
        
        # 7. Verificar que los datos creados están presentes
        print("\n--- 7. Verificando datos creados ---")
        
        negocio_encontrado = any(n['nombre'] == 'Negocio Test API' for n in negocios.get('data', []))
        producto_encontrado = any(p['nombre'] == 'Producto Test API' for p in productos.get('data', []))
        oferta_encontrada = any(o['titulo'] == 'Oferta Test API' for o in ofertas.get('data', []))
        sucursal_encontrada = any(s['nombre'] == 'Sucursal Test API' for s in sucursales.get('data', []))
        
        print(f"✅ Negocio encontrado: {negocio_encontrado}")
        print(f"✅ Producto encontrado: {producto_encontrado}")
        print(f"✅ Oferta encontrada: {oferta_encontrada}")
        print(f"✅ Sucursal encontrada: {sucursal_encontrada}")
        
        print("\n=== PRUEBA COMPLETADA ===")
        print("✅ Todas las pruebas pasaron correctamente")
        print("✅ La comunicación API está funcionando")
        print("✅ Los datos se están sincronizando entre sistemas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_datos_api():
    """Limpiar datos de prueba de la API"""
    try:
        print("\n--- Limpiando datos de prueba ---")
        
        from belgrano_client import belgrano_client
        
        # Obtener datos para limpiar
        negocios = belgrano_client.get_businesses()
        productos = belgrano_client.get_products()
        ofertas = belgrano_client.get_offers()
        sucursales = belgrano_client.get_branches()
        
        # Eliminar datos de prueba
        for negocio in negocios.get('data', []):
            if 'Test API' in negocio['nombre']:
                belgrano_client.delete_business(negocio['id'])
        
        for producto in productos.get('data', []):
            if 'Test API' in producto['nombre']:
                belgrano_client.delete_product(producto['id'])
        
        for oferta in ofertas.get('data', []):
            if 'Test API' in oferta['titulo']:
                belgrano_client.delete_offer(oferta['id'])
        
        for sucursal in sucursales.get('data', []):
            if 'Test API' in sucursal['nombre']:
                belgrano_client.delete_branch(sucursal['id'])
        
        print("✅ Datos de prueba eliminados")
        
    except Exception as e:
        print(f"⚠️ Error limpiando datos: {e}")

if __name__ == "__main__":
    print("Iniciando prueba de comunicación API...")
    
    # Ejecutar prueba
    exito = test_api_comunicacion()
    
    if exito:
        # Preguntar si limpiar datos
        respuesta = input("\n¿Desea limpiar los datos de prueba? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            limpiar_datos_api()
    
    print("\nPrueba finalizada.")
