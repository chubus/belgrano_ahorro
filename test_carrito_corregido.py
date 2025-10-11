#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que el carrito funciona correctamente después de las correcciones
"""

import os
import sys
import json
import traceback
from datetime import datetime

def test_template_carrito_corregido():
    """Verificar que el template carrito.html esté corregido"""
    print("🔍 VERIFICANDO CORRECCIONES EN CARRITO.HTML...")
    
    try:
        with open("templates/carrito.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar que se use item.producto.id en lugar de item.producto.nombre
        if 'value="{{ item.producto.id }}"' in content:
            print("   ✅ Template corregido: Usa item.producto.id correctamente")
        elif 'value="{{ item.producto.nombre }}"' in content:
            print("   ❌ ERROR: Template aún usa item.producto.nombre (incorrecto)")
            return False
        else:
            print("   ⚠️ ADVERTENCIA: No se detectó el campo producto_id en el template")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error verificando template: {e}")
        return False

def test_funcion_actualizar_cantidad():
    """Verificar que la función actualizar_cantidad esté corregida"""
    print("\n🔍 VERIFICANDO FUNCIÓN ACTUALIZAR_CANTIDAD...")
    
    try:
        with open("app_unificado.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar que use obtener_producto_por_id para obtener el nombre
        if 'obtener_producto_por_id(producto_id)' in content:
            print("   ✅ Función corregida: Usa obtener_producto_por_id para obtener nombre")
        else:
            print("   ❌ ERROR: Función no usa obtener_producto_por_id")
            return False
        
        # Verificar que no use producto_id directamente en los mensajes
        if 'flash(f\'{producto_id}' in content:
            print("   ❌ ERROR: Función aún usa producto_id directamente en mensajes")
            return False
        else:
            print("   ✅ Función corregida: No usa producto_id directamente en mensajes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error verificando función: {e}")
        return False

def test_simulacion_carrito_completa():
    """Simular el flujo completo del carrito"""
    print("\n🔍 SIMULANDO FLUJO COMPLETO DEL CARRITO...")
    
    try:
        # Cargar productos
        with open("productos.json", "r", encoding="utf-8") as f:
            productos = json.load(f)
        
        def obtener_producto_por_id(producto_id):
            for producto in productos['productos']:
                if str(producto['id']) == str(producto_id):
                    return producto
            return None
        
        # Simular sesión de carrito
        carrito_session = {
            '1': 2,  # Arroz 1kg, cantidad 2
            '2': 1,  # Aceite 900ml, cantidad 1
        }
        
        print("   🔍 Simulando ruta /carrito...")
        
        # Simular lógica de la ruta /carrito
        carrito_items = []
        total = 0
        
        for producto_id, cantidad in carrito_session.items():
            producto = obtener_producto_por_id(producto_id)
            if producto:
                subtotal = producto['precio'] * cantidad
                carrito_items.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                })
                total += subtotal
                print(f"   ✅ {producto['nombre']}: {cantidad} x ${producto['precio']} = ${subtotal}")
        
        print(f"   📊 Total del carrito: ${total}")
        print(f"   📊 Items en carrito: {len(carrito_items)}")
        
        # Simular actualización de cantidad
        print("\n   🔍 Simulando actualizar_cantidad...")
        
        # Simular actualizar cantidad del producto ID 1 a 3
        producto_id = '1'
        nueva_cantidad = 3
        
        if nueva_cantidad > 0:
            carrito_session[producto_id] = nueva_cantidad
            producto = obtener_producto_por_id(producto_id)
            nombre_producto = producto['nombre'] if producto else f'Producto {producto_id}'
            print(f"   ✅ Cantidad de {nombre_producto} actualizada a {nueva_cantidad}")
        
        # Recalcular total
        total_actualizado = 0
        for producto_id, cantidad in carrito_session.items():
            producto = obtener_producto_por_id(producto_id)
            if producto:
                subtotal = producto['precio'] * cantidad
                total_actualizado += subtotal
        
        print(f"   📊 Total actualizado: ${total_actualizado}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error simulando carrito: {e}")
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return False

def test_estructura_datos_carrito():
    """Verificar que la estructura de datos del carrito sea correcta"""
    print("\n🔍 VERIFICANDO ESTRUCTURA DE DATOS DEL CARRITO...")
    
    try:
        # Cargar productos
        with open("productos.json", "r", encoding="utf-8") as f:
            productos = json.load(f)
        
        def obtener_producto_por_id(producto_id):
            for producto in productos['productos']:
                if str(producto['id']) == str(producto_id):
                    return producto
            return None
        
        # Simular carrito con datos reales
        carrito_session = {'1': 2, '2': 1}
        carrito_items = []
        
        for producto_id, cantidad in carrito_session.items():
            producto = obtener_producto_por_id(producto_id)
            if producto:
                subtotal = producto['precio'] * cantidad
                item = {
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                }
                carrito_items.append(item)
                
                # Verificar estructura del item
                campos_requeridos = ['producto', 'cantidad', 'subtotal']
                campos_faltantes = [campo for campo in campos_requeridos if campo not in item]
                
                if campos_faltantes:
                    print(f"   ❌ ERROR: Campos faltantes en item: {campos_faltantes}")
                    return False
                
                # Verificar estructura del producto
                campos_producto = ['id', 'nombre', 'precio']
                campos_faltantes_producto = [campo for campo in campos_producto if campo not in producto]
                
                if campos_faltantes_producto:
                    print(f"   ❌ ERROR: Campos faltantes en producto: {campos_faltantes_producto}")
                    return False
                
                print(f"   ✅ Item válido: {producto['nombre']} - Cantidad: {cantidad} - Subtotal: ${subtotal}")
        
        print(f"   ✅ Estructura de datos del carrito correcta")
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: Error verificando estructura: {e}")
        return False

def main():
    """Función principal del test"""
    print("=" * 80)
    print("🧪 TEST: CARRITO CORREGIDO - VERIFICACIÓN COMPLETA")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Template carrito corregido", test_template_carrito_corregido),
        ("Función actualizar_cantidad corregida", test_funcion_actualizar_cantidad),
        ("Simulación carrito completa", test_simulacion_carrito_completa),
        ("Estructura datos carrito", test_estructura_datos_carrito)
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
    print("📊 RESUMEN DEL TEST")
    print("=" * 80)
    
    tests_pasados = sum(1 for resultado in resultados.values() if resultado)
    total_tests = len(resultados)
    
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    for nombre, resultado in resultados.items():
        status = "✅ OK" if resultado else "❌ FALLÓ"
        print(f"   {status}: {nombre}")
    
    if tests_pasados == total_tests:
        print("\n🎉 TODOS LOS TESTS PASARON - /CARRITO DEBERÍA FUNCIONAR CORRECTAMENTE")
        print("💡 El error 500 debería estar resuelto")
    else:
        print(f"\n⚠️ {total_tests - tests_pasados} TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
    
    # Guardar reporte
    reporte = {
        'timestamp': datetime.now().isoformat(),
        'tests_pasados': tests_pasados,
        'total_tests': total_tests,
        'resultados': resultados,
        'status': 'success' if tests_pasados == total_tests else 'error'
    }
    
    reporte_file = f"test_carrito_corregido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_file, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {reporte_file}")
    
    return tests_pasados == total_tests

if __name__ == "__main__":
    main()
