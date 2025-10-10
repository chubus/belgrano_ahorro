#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo de conectividad entre DevOps y Belgrano Ahorro
Verifica autenticación, endpoints y datos reales
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def test_belgrano_ahorro_api():
    """Probar API de Belgrano Ahorro directamente"""
    print("🔍 PROBANDO API DE BELGRANO AHORRO...")
    
    base_url = "http://localhost:5000"
    api_key = "belgrano_ahorro_api_key_2025"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    endpoints = [
        '/api/v1/negocios',
        '/api/v1/productos', 
        '/api/v1/ofertas',
        '/api/v1/precios',
        '/api/v1/sucursales'
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"   Probando: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    'status': 'success',
                    'data': data,
                    'count': len(data) if isinstance(data, list) else 'object'
                }
                print(f"   ✅ {endpoint}: {len(data) if isinstance(data, list) else 'OK'}")
            else:
                results[endpoint] = {
                    'status': 'error',
                    'code': response.status_code,
                    'message': response.text[:200]
                }
                print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            results[endpoint] = {
                'status': 'error',
                'message': str(e)
            }
            print(f"   ❌ {endpoint}: {e}")
    
    return results

def test_devops_manager():
    """Probar gestor DevOps directamente"""
    print("\n🔍 PROBANDO GESTOR DEVOPS...")
    
    try:
        # Configurar variables de entorno
        os.environ['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
        os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        
        # Importar gestor
        from devops_belgrano_manager_unified import devops_manager_unified
        
        print(f"   ✅ Gestor importado correctamente")
        print(f"   ✅ Fallback mode: {devops_manager_unified.fallback_mode}")
        print(f"   ✅ URL configurada: {devops_manager_unified.belgrano_url}")
        
        # Probar conectividad
        print("   🔍 Probando conectividad...")
        connectivity = devops_manager_unified.test_connectivity()
        
        print(f"   📊 Estado general: {connectivity['overall_status']}")
        print(f"   📊 Mensaje: {connectivity['message']}")
        
        for endpoint, result in connectivity['endpoints'].items():
            status = result['status']
            message = result['message']
            print(f"   {'✅' if status == 'success' else '❌'} {endpoint}: {message}")
        
        return connectivity
        
    except Exception as e:
        print(f"   ❌ Error importando gestor: {e}")
        return {'overall_status': 'error', 'message': str(e)}

def test_devops_endpoints():
    """Probar endpoints DevOps"""
    print("\n🔍 PROBANDO ENDPOINTS DEVOPS...")
    
    base_url = "http://localhost:5000"
    
    endpoints = [
        '/devops/negocios',
        '/devops/productos',
        '/devops/ofertas', 
        '/devops/precios'
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"   Probando: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    print(f"   ❌ {endpoint}: Devuelve JSON crudo")
                    results[endpoint] = {'status': 'error', 'message': 'JSON crudo detectado'}
                else:
                    print(f"   ✅ {endpoint}: Devuelve HTML correctamente")
                    results[endpoint] = {'status': 'success', 'message': 'HTML correcto'}
            else:
                print(f"   ⚠️ {endpoint}: HTTP {response.status_code}")
                results[endpoint] = {'status': 'warning', 'code': response.status_code}
                
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
            results[endpoint] = {'status': 'error', 'message': str(e)}
    
    return results

def test_crud_operations():
    """Probar operaciones CRUD"""
    print("\n🔍 PROBANDO OPERACIONES CRUD...")
    
    try:
        from devops_belgrano_manager_unified import devops_manager_unified
        
        # Test GET
        print("   📖 Probando GET negocios...")
        negocios = devops_manager_unified.get_negocios()
        print(f"   ✅ Negocios obtenidos: {len(negocios)}")
        
        # Test GET productos
        print("   📖 Probando GET productos...")
        productos = devops_manager_unified.get_productos()
        print(f"   ✅ Productos obtenidos: {len(productos)}")
        
        # Test GET ofertas
        print("   📖 Probando GET ofertas...")
        ofertas = devops_manager_unified.get_ofertas()
        print(f"   ✅ Ofertas obtenidas: {len(ofertas)}")
        
        return {
            'negocios': len(negocios),
            'productos': len(productos),
            'ofertas': len(ofertas)
        }
        
    except Exception as e:
        print(f"   ❌ Error en operaciones CRUD: {e}")
        return {'error': str(e)}

def main():
    """Función principal"""
    print("=" * 80)
    print("🧪 TEST COMPLETO DE CONECTIVIDAD DEVOPS - BELGRANO AHORRO")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar variables de entorno
    os.environ['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
    
    # 1. Probar API de Belgrano Ahorro
    belgrano_results = test_belgrano_ahorro_api()
    
    # 2. Probar gestor DevOps
    devops_manager_results = test_devops_manager()
    
    # 3. Probar endpoints DevOps
    devops_endpoints_results = test_devops_endpoints()
    
    # 4. Probar operaciones CRUD
    crud_results = test_crud_operations()
    
    # Generar reporte final
    print("\n" + "=" * 80)
    print("📊 REPORTE FINAL")
    print("=" * 80)
    
    # Contar resultados
    belgrano_success = sum(1 for r in belgrano_results.values() if r.get('status') == 'success')
    devops_success = sum(1 for r in devops_endpoints_results.values() if r.get('status') == 'success')
    
    print(f"✅ API Belgrano Ahorro: {belgrano_success}/{len(belgrano_results)} endpoints funcionando")
    print(f"✅ Endpoints DevOps: {devops_success}/{len(devops_endpoints_results)} funcionando")
    print(f"✅ Gestor DevOps: {devops_manager_results.get('overall_status', 'unknown')}")
    
    if 'error' not in crud_results:
        print(f"✅ CRUD Operations: {crud_results}")
    else:
        print(f"❌ CRUD Operations: {crud_results['error']}")
    
    # Verificar que no hay JSON crudo
    json_crudo = any('JSON crudo' in str(r) for r in devops_endpoints_results.values())
    if json_crudo:
        print("\n❌ SE DETECTÓ JSON CRUDO EN ENDPOINTS DEVOPS")
    else:
        print("\n✅ NO SE DETECTÓ JSON CRUDO - ENDPOINTS CORRECTOS")
    
    # Guardar reporte
    report = {
        'timestamp': datetime.now().isoformat(),
        'belgrano_api': belgrano_results,
        'devops_manager': devops_manager_results,
        'devops_endpoints': devops_endpoints_results,
        'crud_operations': crud_results
    }
    
    report_file = f"test_conectividad_completa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
