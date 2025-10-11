#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico del error 500 en /carrito de Belgrano Ahorro
"""

import os
import sys
import json
import traceback
from datetime import datetime

def test_carga_productos():
    """Probar carga de productos.json"""
    print("🔍 PROBANDO CARGA DE PRODUCTOS.JSON...")
    
    try:
        with open("productos.json", "r", encoding="utf-8") as f:
            productos = json.load(f)
        
        print(f"   ✅ Archivo productos.json cargado correctamente")
        print(f"   📊 Estructura: {list(productos.keys())}")
        
        if 'productos' in productos:
            print(f"   📊 Productos encontrados: {len(productos['productos'])}")
            
            # Verificar estructura de productos
            if len(productos['productos']) > 0:
                primer_producto = productos['productos'][0]
                print(f"   📊 Primer producto: {primer_producto.get('nombre', 'Sin nombre')}")
                print(f"   📊 Campos del producto: {list(primer_producto.keys())}")
                
                # Verificar campos requeridos
                campos_requeridos = ['id', 'nombre', 'precio']
                campos_faltantes = [campo for campo in campos_requeridos if campo not in primer_producto]
                
                if campos_faltantes:
                    print(f"   ❌ Campos faltantes en productos: {campos_faltantes}")
                    return False
                else:
                    print(f"   ✅ Todos los campos requeridos están presentes")
            else:
                print(f"   ⚠️ ADVERTENCIA: Lista de productos vacía")
        else:
            print(f"   ❌ ERROR: No se encontró la clave 'productos' en el JSON")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"   ❌ ERROR: Archivo productos.json no encontrado")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ ERROR: JSON inválido en productos.json: {e}")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: Error cargando productos.json: {e}")
        return False

def test_funcion_obtener_producto():
    """Probar función obtener_producto_por_id"""
    print("\n🔍 PROBANDO FUNCIÓN OBTENER_PRODUCTO_POR_ID...")
    
    try:
        # Simular la carga de productos como en app_unificado.py
        with open("productos.json", "r", encoding="utf-8") as f:
            productos = json.load(f)
        
        def obtener_producto_por_id(producto_id):
            """Busca un producto por su ID en la lista de productos"""
            for producto in productos['productos']:
                if str(producto['id']) == str(producto_id):
                    return producto
            return None
        
        # Probar con diferentes IDs
        test_ids = [1, 2, 999, "1", "999"]
        
        for test_id in test_ids:
            producto = obtener_producto_por_id(test_id)
            if producto:
                print(f"   ✅ ID {test_id}: {producto.get('nombre', 'Sin nombre')} - ${producto.get('precio', 0)}")
            else:
                print(f"   ⚠️ ID {test_id}: No encontrado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error en función obtener_producto_por_id: {e}")
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return False

def test_simulacion_carrito():
    """Simular la lógica del carrito"""
    print("\n🔍 SIMULANDO LÓGICA DEL CARRITO...")
    
    try:
        # Simular sesión de carrito
        carrito_session = {
            '1': 2,  # Producto ID 1, cantidad 2
            '2': 1,  # Producto ID 2, cantidad 1
            '999': 3  # Producto ID 999 (no existe)
        }
        
        # Cargar productos
        with open("productos.json", "r", encoding="utf-8") as f:
            productos = json.load(f)
        
        def obtener_producto_por_id(producto_id):
            for producto in productos['productos']:
                if str(producto['id']) == str(producto_id):
                    return producto
            return None
        
        # Simular lógica del carrito
        carrito_items = []
        total = 0
        
        for producto_id, cantidad in carrito_session.items():
            print(f"   🔍 Procesando producto ID {producto_id}, cantidad {cantidad}")
            
            producto = obtener_producto_por_id(producto_id)
            if producto:
                subtotal = producto['precio'] * cantidad
                carrito_items.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                })
                total += subtotal
                print(f"   ✅ Producto encontrado: {producto['nombre']} - Subtotal: ${subtotal}")
            else:
                print(f"   ⚠️ Producto ID {producto_id} no encontrado")
        
        print(f"   📊 Total del carrito: ${total}")
        print(f"   📊 Items en carrito: {len(carrito_items)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error simulando carrito: {e}")
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return False

def test_template_carrito():
    """Verificar que el template carrito.html existe y es válido"""
    print("\n🔍 VERIFICANDO TEMPLATE CARRITO.HTML...")
    
    try:
        if not os.path.exists("templates/carrito.html"):
            print(f"   ❌ ERROR: Template carrito.html no encontrado")
            return False
        
        with open("templates/carrito.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"   ✅ Template carrito.html encontrado")
        print(f"   📊 Tamaño del archivo: {len(content)} caracteres")
        
        # Verificar elementos clave del template
        elementos_requeridos = [
            'carrito_items',
            'total',
            'item.producto',
            'item.cantidad',
            'item.subtotal'
        ]
        
        elementos_faltantes = []
        for elemento in elementos_requeridos:
            if elemento not in content:
                elementos_faltantes.append(elemento)
        
        if elementos_faltantes:
            print(f"   ❌ ERROR: Elementos faltantes en template: {elementos_faltantes}")
            return False
        else:
            print(f"   ✅ Todos los elementos requeridos están en el template")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error verificando template: {e}")
        return False

def test_imports_app_unificado():
    """Verificar imports necesarios en app_unificado.py"""
    print("\n🔍 VERIFICANDO IMPORTS EN APP_UNIFICADO.PY...")
    
    try:
        with open("app_unificado.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        imports_requeridos = [
            'from flask import',
            'import json',
            'import logging',
            'session',
            'render_template'
        ]
        
        imports_faltantes = []
        for import_req in imports_requeridos:
            if import_req not in content:
                imports_faltantes.append(import_req)
        
        if imports_faltantes:
            print(f"   ❌ ERROR: Imports faltantes: {imports_faltantes}")
            return False
        else:
            print(f"   ✅ Todos los imports requeridos están presentes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error verificando imports: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DEL ERROR 500 EN /CARRITO")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Carga de productos.json", test_carga_productos),
        ("Función obtener_producto_por_id", test_funcion_obtener_producto),
        ("Simulación de carrito", test_simulacion_carrito),
        ("Template carrito.html", test_template_carrito),
        ("Imports en app_unificado.py", test_imports_app_unificado)
    ]
    
    resultados = {}
    
    for nombre, test_func in tests:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        try:
            resultado = test_func()
            resultados[nombre] = resultado
            if resultado:
                print(f"✅ {nombre}: OK")
            else:
                print(f"❌ {nombre}: FALLÓ")
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
            resultados[nombre] = False
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 80)
    
    tests_pasados = sum(1 for resultado in resultados.values() if resultado)
    total_tests = len(resultados)
    
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    for nombre, resultado in resultados.items():
        status = "✅ OK" if resultado else "❌ FALLÓ"
        print(f"   {status}: {nombre}")
    
    if tests_pasados == total_tests:
        print("\n🎉 TODOS LOS TESTS PASARON - /CARRITO DEBERÍA FUNCIONAR")
        print("💡 Si aún hay error 500, revisar logs del servidor Flask")
    else:
        print(f"\n⚠️ {total_tests - tests_pasados} TESTS FALLARON - ESTOS SON LOS PROBLEMAS")
    
    # Guardar reporte
    reporte = {
        'timestamp': datetime.now().isoformat(),
        'tests_pasados': tests_pasados,
        'total_tests': total_tests,
        'resultados': resultados,
        'status': 'success' if tests_pasados == total_tests else 'error'
    }
    
    reporte_file = f"diagnostico_carrito_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_file, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {reporte_file}")
    
    return tests_pasados == total_tests

if __name__ == "__main__":
    main()
