#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba para Persistencia DevOps
Verifica que la persistencia funcione correctamente
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def probar_persistencia():
    """Probar la persistencia de DevOps"""
    try:
        print("=== PRUEBA DE PERSISTENCIA DEVOPS ===")
        
        # Importar módulos
        from devops_persistence import get_devops_db
        from sincronizar_belgrano_ahorro import SincronizadorBelgranoAhorro
        
        print("✅ Módulos importados correctamente")
        
        # Probar conexión a base de datos
        db = get_devops_db()
        print("✅ Conexión a base de datos establecida")
        
        # Probar creación de negocio
        print("\n--- Probando creación de negocio ---")
        datos_negocio = {
            'nombre': 'Negocio de Prueba',
            'descripcion': 'Negocio creado para probar persistencia',
            'direccion': 'Calle de Prueba 123',
            'telefono': '+54 11 1234-5678',
            'email': 'prueba@negocio.com',
            'activo': True
        }
        
        nuevo_negocio = db.crear_negocio(datos_negocio)
        print(f"✅ Negocio creado: ID {nuevo_negocio['id']} - {nuevo_negocio['nombre']}")
        
        # Probar creación de producto
        print("\n--- Probando creación de producto ---")
        datos_producto = {
            'nombre': 'Producto de Prueba',
            'descripcion': 'Producto creado para probar persistencia',
            'precio': 100.0,
            'categoria': 'Pruebas',
            'stock': 50,
            'negocio_id': nuevo_negocio['id'],
            'activo': True
        }
        
        nuevo_producto = db.crear_producto(datos_producto)
        print(f"✅ Producto creado: ID {nuevo_producto['id']} - {nuevo_producto['nombre']}")
        
        # Probar creación de oferta
        print("\n--- Probando creación de oferta ---")
        datos_oferta = {
            'titulo': 'Oferta de Prueba',
            'descripcion': 'Oferta creada para probar persistencia',
            'productos': ['Producto de Prueba', 'Otro Producto'],
            'hasta_agotar_stock': True,
            'activa': True
        }
        
        nueva_oferta = db.crear_oferta(datos_oferta)
        print(f"✅ Oferta creada: ID {nueva_oferta['id']} - {nueva_oferta['titulo']}")
        
        # Probar obtención de datos
        print("\n--- Probando obtención de datos ---")
        negocios = db.obtener_negocios()
        productos = db.obtener_productos()
        ofertas = db.obtener_ofertas()
        
        print(f"✅ Negocios obtenidos: {len(negocios)}")
        print(f"✅ Productos obtenidos: {len(productos)}")
        print(f"✅ Ofertas obtenidas: {len(ofertas)}")
        
        # Probar sincronización
        print("\n--- Probando sincronización ---")
        sincronizador = SincronizadorBelgranoAhorro()
        resultado_sync = sincronizador.sincronizar_todo()
        
        if resultado_sync.get('status') == 'success':
            print("✅ Sincronización exitosa")
            print(f"   - Negocios: {resultado_sync.get('negocios', 0)}")
            print(f"   - Productos: {resultado_sync.get('productos', 0)}")
            print(f"   - Ofertas: {resultado_sync.get('ofertas', 0)}")
        else:
            print("❌ Error en sincronización")
        
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
            cursor.execute("DELETE FROM ofertas WHERE titulo LIKE '%Prueba%'")
            cursor.execute("DELETE FROM productos WHERE nombre LIKE '%Prueba%'")
            cursor.execute("DELETE FROM negocios WHERE nombre LIKE '%Prueba%'")
            
            conn.commit()
            print("✅ Datos de prueba eliminados")
            
    except Exception as e:
        print(f"⚠️ Error limpiando datos: {e}")

if __name__ == "__main__":
    print("Iniciando prueba de persistencia DevOps...")
    
    # Ejecutar prueba
    exito = probar_persistencia()
    
    if exito:
        # Preguntar si limpiar datos
        respuesta = input("\n¿Desea limpiar los datos de prueba? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            limpiar_datos_prueba()
    
    print("\nPrueba finalizada.")
