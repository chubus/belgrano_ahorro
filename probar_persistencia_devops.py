#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la persistencia de DevOps
"""

import os
import sys
from datetime import datetime

def probar_persistencia():
    """Probar la funcionalidad de persistencia DevOps"""
    print("🔧 PROBANDO PERSISTENCIA DEVOPS")
    print("=" * 50)
    
    try:
        from devops_persistence import get_devops_db
        db = get_devops_db()
        print("✅ Conexión a base de datos establecida")
        
        # Probar creación de negocio
        print("\n📝 Probando creación de negocio...")
        negocio_data = {
            'nombre': 'Negocio de Prueba DevOps',
            'descripcion': 'Negocio creado desde DevOps para prueba',
            'direccion': 'Calle de Prueba 123',
            'telefono': '+54 11 1234-5678',
            'email': 'prueba@devops.com',
            'activo': True
        }
        
        nuevo_negocio = db.crear_negocio(negocio_data)
        print(f"✅ Negocio creado: ID {nuevo_negocio['id']} - {nuevo_negocio['nombre']}")
        
        # Probar creación de producto
        print("\n📦 Probando creación de producto...")
        producto_data = {
            'nombre': 'Producto de Prueba DevOps',
            'descripcion': 'Producto creado desde DevOps para prueba',
            'precio': 1500.50,
            'categoria': 'Pruebas',
            'stock': 100,
            'stock_minimo': 10,
            'negocio_id': nuevo_negocio['id'],
            'activo': True
        }
        
        nuevo_producto = db.crear_producto(producto_data)
        print(f"✅ Producto creado: ID {nuevo_producto['id']} - {nuevo_producto['nombre']}")
        
        # Probar creación de oferta
        print("\n🏷️ Probando creación de oferta...")
        oferta_data = {
            'titulo': 'Oferta de Prueba DevOps',
            'descripcion': 'Oferta creada desde DevOps para prueba',
            'productos': ['Producto de Prueba DevOps', 'Otro Producto'],
            'hasta_agotar_stock': True,
            'activa': True
        }
        
        nueva_oferta = db.crear_oferta(oferta_data)
        print(f"✅ Oferta creada: ID {nueva_oferta['id']} - {nueva_oferta['titulo']}")
        
        # Probar obtención de datos
        print("\n📊 Probando obtención de datos...")
        negocios = db.obtener_negocios()
        productos = db.obtener_productos()
        ofertas = db.obtener_ofertas()
        
        print(f"✅ Negocios encontrados: {len(negocios)}")
        print(f"✅ Productos encontrados: {len(productos)}")
        print(f"✅ Ofertas encontradas: {len(ofertas)}")
        
        # Probar sincronización
        print("\n🔄 Probando sincronización...")
        sync_data = db.sincronizar_con_belgrano_ahorro()
        print(f"✅ Sincronización: {sync_data}")
        
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("✅ La persistencia DevOps está funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_datos_prueba():
    """Limpiar datos de prueba creados"""
    try:
        from devops_persistence import get_devops_db
        db = get_devops_db()
        
        # Eliminar datos de prueba
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ofertas WHERE titulo LIKE '%Prueba DevOps%'")
            cursor.execute("DELETE FROM productos WHERE nombre LIKE '%Prueba DevOps%'")
            cursor.execute("DELETE FROM negocios WHERE nombre LIKE '%Prueba DevOps%'")
            conn.commit()
        
        print("🧹 Datos de prueba eliminados")
        
    except Exception as e:
        print(f"⚠️ Error limpiando datos: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE PERSISTENCIA DEVOPS")
    print("=" * 60)
    
    # Verificar que existe la base de datos
    db_paths = [
        'belgrano_ahorro.db',
        '../belgrano_ahorro.db',
        '../../belgrano_ahorro.db'
    ]
    
    db_found = False
    for path in db_paths:
        if os.path.exists(path):
            print(f"✅ Base de datos encontrada en: {path}")
            db_found = True
            break
    
    if not db_found:
        print("❌ No se encontró la base de datos belgrano_ahorro.db")
        print("📁 Rutas buscadas:")
        for path in db_paths:
            print(f"   - {path}")
        sys.exit(1)
    
    # Ejecutar pruebas
    if probar_persistencia():
        print("\n🧹 Limpiando datos de prueba...")
        limpiar_datos_prueba()
        print("\n✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
    else:
        print("\n❌ PRUEBAS FALLARON")
        sys.exit(1)
