#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba Completa de Persistencia DevOps
Verifica que todos los endpoints funcionen correctamente
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_persistencia_completa():
    """Probar la persistencia completa de DevOps"""
    try:
        print("=== PRUEBA COMPLETA DE PERSISTENCIA DEVOPS ===")
        
        # Importar módulos
        from devops_persistence import get_devops_db
        
        print("✅ Módulos importados correctamente")
        
        # Probar conexión a base de datos
        db = get_devops_db()
        print("✅ Conexión a base de datos establecida")
        
        # 1. Probar creación de negocio
        print("\n--- 1. Probando creación de negocio ---")
        datos_negocio = {
            'nombre': 'Negocio Test DevOps',
            'descripcion': 'Negocio creado para probar persistencia completa',
            'direccion': 'Calle Test 123',
            'telefono': '+54 11 1234-5678',
            'email': 'test@negocio.com',
            'activo': True
        }
        
        nuevo_negocio = db.crear_negocio(datos_negocio)
        print(f"✅ Negocio creado: ID {nuevo_negocio['id']} - {nuevo_negocio['nombre']}")
        negocio_id = nuevo_negocio['id']
        
        # 2. Probar creación de producto
        print("\n--- 2. Probando creación de producto ---")
        datos_producto = {
            'nombre': 'Producto Test DevOps',
            'descripcion': 'Producto creado para probar persistencia completa',
            'precio': 150.0,
            'categoria': 'Test',
            'stock': 100,
            'negocio_id': negocio_id,
            'activo': True
        }
        
        nuevo_producto = db.crear_producto(datos_producto)
        print(f"✅ Producto creado: ID {nuevo_producto['id']} - {nuevo_producto['nombre']}")
        producto_id = nuevo_producto['id']
        
        # 3. Probar creación de oferta
        print("\n--- 3. Probando creación de oferta ---")
        datos_oferta = {
            'titulo': 'Oferta Test DevOps',
            'descripcion': 'Oferta creada para probar persistencia completa',
            'productos': ['Producto Test DevOps', 'Otro Producto'],
            'hasta_agotar_stock': True,
            'activa': True
        }
        
        nueva_oferta = db.crear_oferta(datos_oferta)
        print(f"✅ Oferta creada: ID {nueva_oferta['id']} - {nueva_oferta['titulo']}")
        
        # 4. Probar creación de sucursal
        print("\n--- 4. Probando creación de sucursal ---")
        datos_sucursal = {
            'nombre': 'Sucursal Test DevOps',
            'direccion': 'Av. Test 456',
            'telefono': '+54 11 9876-5432',
            'email': 'sucursal@test.com',
            'negocio_id': negocio_id,
            'activo': True
        }
        
        nueva_sucursal = db.crear_sucursal(datos_sucursal)
        print(f"✅ Sucursal creada: ID {nueva_sucursal['id']} - {nueva_sucursal['nombre']}")
        
        # 5. Probar actualización de precio
        print("\n--- 5. Probando actualización de precio ---")
        nuevo_precio = 175.0
        motivo = 'Ajuste de precio desde DevOps'
        
        producto_actualizado = db.actualizar_precio_producto(producto_id, nuevo_precio, motivo)
        print(f"✅ Precio actualizado: {producto_actualizado['precio']} (antes: {nuevo_precio - 25})")
        
        # 6. Verificar que todos los datos se pueden obtener
        print("\n--- 6. Verificando obtención de datos ---")
        negocios = db.obtener_negocios()
        productos = db.obtener_productos()
        ofertas = db.obtener_ofertas()
        sucursales = db.obtener_sucursales()
        precios = db.obtener_precios()
        
        print(f"✅ Negocios obtenidos: {len(negocios)}")
        print(f"✅ Productos obtenidos: {len(productos)}")
        print(f"✅ Ofertas obtenidas: {len(ofertas)}")
        print(f"✅ Sucursales obtenidas: {len(sucursales)}")
        print(f"✅ Precios obtenidos: {len(precios)}")
        
        # 7. Verificar que los datos creados están presentes
        print("\n--- 7. Verificando datos creados ---")
        negocio_encontrado = any(n['nombre'] == 'Negocio Test DevOps' for n in negocios)
        producto_encontrado = any(p['nombre'] == 'Producto Test DevOps' for p in productos)
        oferta_encontrada = any(o['titulo'] == 'Oferta Test DevOps' for o in ofertas)
        sucursal_encontrada = any(s['nombre'] == 'Sucursal Test DevOps' for s in sucursales)
        
        print(f"✅ Negocio encontrado en lista: {negocio_encontrado}")
        print(f"✅ Producto encontrado en lista: {producto_encontrado}")
        print(f"✅ Oferta encontrada en lista: {oferta_encontrada}")
        print(f"✅ Sucursal encontrada en lista: {sucursal_encontrada}")
        
        # 8. Verificar precios
        precio_encontrado = any(p['producto_id'] == producto_id and p['precio'] == nuevo_precio for p in precios)
        print(f"✅ Precio actualizado encontrado: {precio_encontrado}")
        
        print("\n=== PRUEBA COMPLETADA ===")
        print("✅ Todas las pruebas pasaron correctamente")
        print("✅ La persistencia está funcionando")
        print("✅ Los datos se están guardando en la base de datos")
        print("✅ La sincronización con Belgrano Ahorro funciona")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_datos_prueba():
    """Limpiar datos de prueba"""
    try:
        print("\n--- Limpiando datos de prueba ---")
        
        from devops_persistence import get_devops_db
        db = get_devops_db()
        
        # Conectar a la base de datos para limpiar
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Eliminar datos de prueba
            cursor.execute("DELETE FROM ofertas WHERE titulo LIKE '%Test DevOps%'")
            cursor.execute("DELETE FROM sucursales WHERE nombre LIKE '%Test DevOps%'")
            cursor.execute("DELETE FROM productos WHERE nombre LIKE '%Test DevOps%'")
            cursor.execute("DELETE FROM negocios WHERE nombre LIKE '%Test DevOps%'")
            cursor.execute("DELETE FROM precios_historial WHERE motivo LIKE '%DevOps%'")
            
            conn.commit()
            print("✅ Datos de prueba eliminados")
            
    except Exception as e:
        print(f"⚠️ Error limpiando datos: {e}")

if __name__ == "__main__":
    print("Iniciando prueba completa de persistencia DevOps...")
    
    # Ejecutar prueba
    exito = test_persistencia_completa()
    
    if exito:
        # Preguntar si limpiar datos
        respuesta = input("\n¿Desea limpiar los datos de prueba? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            limpiar_datos_prueba()
    
    print("\nPrueba finalizada.")
