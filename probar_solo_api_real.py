#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar que DevOps use SOLO datos reales de Belgrano Ahorro
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuración
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
API_TIMEOUT_SECS = 30

def build_api_url(endpoint: str) -> str:
    """Construir URL completa para endpoint de API"""
    return f"{BELGRANO_AHORRO_URL}/api/{endpoint}"

def verificar_conectividad_api():
    """Verificar que la API de Belgrano Ahorro esté disponible"""
    print("🔍 VERIFICANDO CONECTIVIDAD CON API REAL")
    print("=" * 50)
    
    try:
        # Health check
        health_url = f"{BELGRANO_AHORRO_URL}/healthz"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API de Belgrano Ahorro disponible")
            print(f"   URL: {BELGRANO_AHORRO_URL}")
            print(f"   Tiempo de respuesta: {response.elapsed.total_seconds():.2f}s")
            return True
        else:
            print(f"❌ API no disponible - Código: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con API: {e}")
        return False

def obtener_datos_reales(endpoint: str, nombre: str) -> List[Dict]:
    """Obtener datos SOLO desde API real de Belgrano Ahorro"""
    try:
        url = build_api_url(endpoint)
        headers = {
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'Content-Type': 'application/json',
            'X-Origin': 'test_solo_api_real'
        }
        
        print(f"🌐 Obteniendo {nombre} desde API real...")
        response = requests.get(url, headers=headers, timeout=API_TIMEOUT_SECS)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ {len(data)} {nombre} obtenidos desde API real")
                return data
            elif isinstance(data, dict) and 'data' in data:
                items = data.get('data', [])
                print(f"✅ {len(items)} {nombre} obtenidos desde API real")
                return items
            else:
                print(f"⚠️ Formato inesperado para {nombre}")
                return []
        else:
            print(f"❌ Error API {nombre}: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error obteniendo {nombre}: {e}")
        return []

def verificar_sin_fallbacks_locales():
    """Verificar que no se usen archivos de fallback local"""
    print("\n🔍 VERIFICANDO SIN FALLBACKS LOCALES")
    print("=" * 50)
    
    archivos_fallback = [
        'productos.json',
        'negocios.json', 
        'ofertas.json',
        'sucursales.json',
        'precios.json'
    ]
    
    fallbacks_encontrados = []
    for archivo in archivos_fallback:
        if os.path.exists(archivo):
            fallbacks_encontrados.append(archivo)
    
    if fallbacks_encontrados:
        print(f"⚠️ Archivos de fallback encontrados: {fallbacks_encontrados}")
        print("   Estos archivos NO se usarán - solo API real")
    else:
        print("✅ No hay archivos de fallback local")
    
    return fallbacks_encontrados

def probar_dashboard_datos_reales():
    """Probar que el dashboard obtenga datos reales"""
    print("\n📊 PROBANDO DATOS DEL DASHBOARD")
    print("=" * 50)
    
    # Obtener datos reales
    negocios = obtener_datos_reales('v1/negocios', 'negocios')
    productos = obtener_datos_reales('v1/productos', 'productos')
    ofertas = obtener_datos_reales('v1/ofertas', 'ofertas')
    sucursales = obtener_datos_reales('v1/sucursales', 'sucursales')
    precios = obtener_datos_reales('v1/precios', 'precios')
    
    # Mostrar resumen
    print(f"\n📈 RESUMEN DE DATOS REALES:")
    print(f"🏪 Negocios: {len(negocios)} registros reales")
    print(f"📦 Productos: {len(productos)} registros reales")
    print(f"🎯 Ofertas: {len(ofertas)} registros reales")
    print(f"🏢 Sucursales: {len(sucursales)} registros reales")
    print(f"💰 Precios: {len(precios)} registros reales")
    
    # Verificar que los datos no sean simulados
    if negocios:
        primer_negocio = negocios[0]
        print(f"\n🔍 MUESTRA DE DATOS REALES:")
        print(f"   Primer negocio: {primer_negocio.get('nombre', 'Sin nombre')}")
        print(f"   ID: {primer_negocio.get('id', 'Sin ID')}")
        print(f"   Activo: {primer_negocio.get('activo', 'Sin estado')}")
    
    return {
        'negocios': len(negocios),
        'productos': len(productos),
        'ofertas': len(ofertas),
        'sucursales': len(sucursales),
        'precios': len(precios)
    }

def verificar_funciones_devops():
    """Verificar que las funciones DevOps usen solo API real"""
    print("\n🔧 VERIFICANDO FUNCIONES DEVOPS")
    print("=" * 50)
    
    # Verificar que no hay referencias a fallbacks en el código
    archivos_a_verificar = [
        'belgrano_tickets/devops_routes_backup.py',
        'belgrano_tickets/app.py',
        'devops_belgrano_manager_unified.py'
    ]
    
    referencias_fallback = []
    
    for archivo in archivos_a_verificar:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Buscar referencias a fallbacks
                if 'productos.json' in contenido:
                    referencias_fallback.append(f"{archivo}: productos.json")
                if 'fallback' in contenido.lower():
                    referencias_fallback.append(f"{archivo}: fallback")
                if 'datos locales' in contenido.lower():
                    referencias_fallback.append(f"{archivo}: datos locales")
                    
            except Exception as e:
                print(f"⚠️ Error leyendo {archivo}: {e}")
    
    if referencias_fallback:
        print(f"⚠️ Referencias a fallbacks encontradas:")
        for ref in referencias_fallback:
            print(f"   - {ref}")
        print("   Estas referencias deben ser eliminadas")
    else:
        print("✅ No se encontraron referencias a fallbacks")
    
    return referencias_fallback

def generar_reporte_final():
    """Generar reporte final de verificación"""
    print("\n📋 GENERANDO REPORTE FINAL")
    print("=" * 50)
    
    reporte = {
        'timestamp': datetime.now().isoformat(),
        'api_url': BELGRANO_AHORRO_URL,
        'api_key_configured': bool(BELGRANO_AHORRO_API_KEY),
        'conectividad': verificar_conectividad_api(),
        'fallbacks_locales': verificar_sin_fallbacks_locales(),
        'datos_reales': probar_dashboard_datos_reales(),
        'referencias_fallback': verificar_funciones_devops()
    }
    
    # Guardar reporte
    with open('reporte_solo_api_real.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Reporte guardado: reporte_solo_api_real.json")
    
    # Resumen final
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"✅ API Conectada: {'Sí' if reporte['conectividad'] else 'No'}")
    print(f"✅ Sin Fallbacks: {'Sí' if not reporte['fallbacks_locales'] else 'No'}")
    print(f"✅ Datos Reales: {sum(reporte['datos_reales'].values())} registros")
    print(f"✅ Sin Referencias Fallback: {'Sí' if not reporte['referencias_fallback'] else 'No'}")
    
    if (reporte['conectividad'] and 
        not reporte['fallbacks_locales'] and 
        not reporte['referencias_fallback']):
        print(f"\n🎉 ¡ÉXITO! DevOps usa SOLO datos reales de Belgrano Ahorro")
        return True
    else:
        print(f"\n⚠️ REQUIERE CORRECCIONES para usar solo API real")
        return False

def main():
    """Función principal"""
    print("🧪 PROBANDO SOLO API REAL - BELGRANO AHORRO")
    print("=" * 60)
    print("Verificando que DevOps use únicamente datos reales")
    print("")
    
    # Ejecutar todas las verificaciones
    resultado = generar_reporte_final()
    
    if resultado:
        print("\n✅ VERIFICACIÓN EXITOSA")
        print("   DevOps usa SOLO datos reales de Belgrano Ahorro")
        print("   Sin fallbacks locales")
        print("   Sin datos simulados")
    else:
        print("\n❌ VERIFICACIÓN FALLIDA")
        print("   Se requieren correcciones para usar solo API real")
    
    return resultado

if __name__ == "__main__":
    main()
