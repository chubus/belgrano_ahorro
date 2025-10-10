#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final para verificar que DevOps solo muestra datos reales de Belgrano Ahorro
Sin datos simulados, fallback o falsos
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def test_devops_manager_no_fallback():
    """Verificar que el gestor DevOps no tenga datos de fallback"""
    print("🔍 VERIFICANDO GESTOR DEVOPS - SIN DATOS DE FALLBACK...")
    
    try:
        # Configurar variables de entorno
        os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
        os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        
        # Importar gestor
        from devops_belgrano_manager_unified import devops_manager_unified
        
        print(f"   ✅ Gestor importado correctamente")
        print(f"   ✅ Fallback mode: {devops_manager_unified.fallback_mode}")
        print(f"   ✅ URL configurada: {devops_manager_unified.belgrano_url}")
        
        # Verificar que no existe método de fallback
        if hasattr(devops_manager_unified, '_get_fallback_data'):
            print("   ❌ ERROR: Método _get_fallback_data() aún existe")
            return False
        else:
            print("   ✅ Método _get_fallback_data() eliminado correctamente")
        
        # Probar que retorna listas vacías si API no disponible
        print("   🔍 Probando que retorna listas vacías sin API...")
        
        # Simular modo fallback
        devops_manager_unified.fallback_mode = True
        
        negocios = devops_manager_unified.get_negocios()
        productos = devops_manager_unified.get_productos()
        ofertas = devops_manager_unified.get_ofertas()
        
        if len(negocios) == 0 and len(productos) == 0 and len(ofertas) == 0:
            print("   ✅ Retorna listas vacías correctamente (sin datos falsos)")
        else:
            print(f"   ❌ ERROR: Retorna datos falsos - Negocios: {len(negocios)}, Productos: {len(productos)}, Ofertas: {len(ofertas)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando gestor: {e}")
        return False

def test_devops_routes_no_simulated():
    """Verificar que las rutas DevOps no tengan datos simulados"""
    print("\n🔍 VERIFICANDO RUTAS DEVOPS - SIN DATOS SIMULADOS...")
    
    try:
        # Leer archivo devops_routes.py
        with open('devops_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que no contenga datos simulados
        simulated_keywords = [
            'simulated',
            'fallback_data',
            '_get_fallback_data',
            'source.*simulated',
            'datos.*simulados',
            'fake.*data',
            'mock.*data'
        ]
        
        for keyword in simulated_keywords:
            if keyword in content.lower():
                print(f"   ❌ ERROR: Encontrado '{keyword}' en devops_routes.py")
                return False
        
        print("   ✅ devops_routes.py no contiene datos simulados")
        
        # Verificar que solo use datos reales de API
        if 'devops_manager.get_' in content and 'devops_manager.create_' in content:
            print("   ✅ Usa solo métodos del gestor DevOps (datos reales)")
        else:
            print("   ⚠️ ADVERTENCIA: No se detectaron llamadas al gestor DevOps")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando rutas: {e}")
        return False

def test_archivos_obsoletos_eliminados():
    """Verificar que archivos obsoletos con datos simulados fueron eliminados"""
    print("\n🔍 VERIFICANDO ARCHIVOS OBSOLETOS ELIMINADOS...")
    
    archivos_obsoletos = [
        'devops_routes_clean.py',
        'devops_belgrano_manager_enhanced.py',
        'simulador_conectividad.py'
    ]
    
    eliminados = 0
    for archivo in archivos_obsoletos:
        if not os.path.exists(archivo):
            print(f"   ✅ {archivo} eliminado correctamente")
            eliminados += 1
        else:
            print(f"   ❌ ERROR: {archivo} aún existe")
    
    if eliminados == len(archivos_obsoletos):
        print(f"   ✅ Todos los archivos obsoletos eliminados ({eliminados}/{len(archivos_obsoletos)})")
        return True
    else:
        print(f"   ❌ Solo {eliminados}/{len(archivos_obsoletos)} archivos eliminados")
        return False

def test_conectividad_real():
    """Probar conectividad real con Belgrano Ahorro"""
    print("\n🔍 PROBANDO CONECTIVIDAD REAL CON BELGRANO AHORRO...")
    
    try:
        # Configurar variables de entorno
        os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
        os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        
        from devops_belgrano_manager_unified import devops_manager_unified
        
        # Probar conectividad
        connectivity = devops_manager_unified.test_connectivity()
        
        print(f"   📊 Estado general: {connectivity['overall_status']}")
        print(f"   📊 Mensaje: {connectivity['message']}")
        
        # Verificar endpoints
        endpoints_ok = 0
        for endpoint, result in connectivity['endpoints'].items():
            status = result['status']
            message = result['message']
            if status == 'success':
                print(f"   ✅ {endpoint}: {message}")
                endpoints_ok += 1
            else:
                print(f"   ⚠️ {endpoint}: {message}")
        
        print(f"   📊 Endpoints funcionando: {endpoints_ok}/{len(connectivity['endpoints'])}")
        
        return connectivity['overall_status'] in ['success', 'partial']
        
    except Exception as e:
        print(f"   ❌ Error probando conectividad: {e}")
        return False

def test_datos_reales_vs_simulados():
    """Comparar datos reales vs simulados"""
    print("\n🔍 COMPARANDO DATOS REALES VS SIMULADOS...")
    
    try:
        # Configurar variables de entorno
        os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
        os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        
        from devops_belgrano_manager_unified import devops_manager_unified
        
        # Obtener datos reales
        print("   📖 Obteniendo datos reales de API...")
        negocios_reales = devops_manager_unified.get_negocios()
        productos_reales = devops_manager_unified.get_productos()
        ofertas_reales = devops_manager_unified.get_ofertas()
        
        print(f"   📊 Negocios reales: {len(negocios_reales)}")
        print(f"   📊 Productos reales: {len(productos_reales)}")
        print(f"   📊 Ofertas reales: {len(ofertas_reales)}")
        
        # Verificar que no sean datos simulados conocidos
        datos_simulados_conocidos = [
            {'nombre': 'Supermercado Central'},
            {'nombre': 'Farmacia San Martín'},
            {'nombre': 'Leche Entera 1L'},
            {'nombre': 'Pan Integral'},
            {'titulo': 'Oferta Especial 50%'}
        ]
        
        datos_simulados_encontrados = 0
        
        for negocio in negocios_reales:
            if any(simulado['nombre'] == negocio.get('nombre') for simulado in datos_simulados_conocidos):
                datos_simulados_encontrados += 1
                print(f"   ❌ DATO SIMULADO DETECTADO: {negocio.get('nombre')}")
        
        for producto in productos_reales:
            if any(simulado['nombre'] == producto.get('nombre') for simulado in datos_simulados_conocidos):
                datos_simulados_encontrados += 1
                print(f"   ❌ DATO SIMULADO DETECTADO: {producto.get('nombre')}")
        
        for oferta in ofertas_reales:
            if any(simulado['titulo'] == oferta.get('titulo') for simulado in datos_simulados_conocidos):
                datos_simulados_encontrados += 1
                print(f"   ❌ DATO SIMULADO DETECTADO: {oferta.get('titulo')}")
        
        if datos_simulados_encontrados == 0:
            print("   ✅ No se detectaron datos simulados conocidos")
            return True
        else:
            print(f"   ❌ Se detectaron {datos_simulados_encontrados} datos simulados")
            return False
        
    except Exception as e:
        print(f"   ❌ Error comparando datos: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("🧪 TEST FINAL: DEVOPS - SOLO DATOS REALES DE BELGRANO AHORRO")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar variables de entorno
    os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
    
    tests = [
        ("Gestor DevOps sin fallback", test_devops_manager_no_fallback),
        ("Rutas DevOps sin simulados", test_devops_routes_no_simulated),
        ("Archivos obsoletos eliminados", test_archivos_obsoletos_eliminados),
        ("Conectividad real", test_conectividad_real),
        ("Datos reales vs simulados", test_datos_reales_vs_simulados)
    ]
    
    resultados = {}
    
    for nombre, test_func in tests:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        try:
            resultado = test_func()
            resultados[nombre] = resultado
            if resultado:
                print(f"✅ {nombre}: PASÓ")
            else:
                print(f"❌ {nombre}: FALLÓ")
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
            resultados[nombre] = False
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    
    tests_pasados = sum(1 for resultado in resultados.values() if resultado)
    total_tests = len(resultados)
    
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    for nombre, resultado in resultados.items():
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"   {status}: {nombre}")
    
    if tests_pasados == total_tests:
        print("\n🎉 TODOS LOS TESTS PASARON - DEVOPS SOLO MUESTRA DATOS REALES")
    else:
        print(f"\n⚠️ {total_tests - tests_pasados} TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
    
    # Guardar reporte
    reporte = {
        'timestamp': datetime.now().isoformat(),
        'tests_pasados': tests_pasados,
        'total_tests': total_tests,
        'resultados': resultados,
        'status': 'success' if tests_pasados == total_tests else 'partial'
    }
    
    reporte_file = f"test_devops_datos_reales_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_file, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {reporte_file}")
    
    return tests_pasados == total_tests

if __name__ == "__main__":
    main()
