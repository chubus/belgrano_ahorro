#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo para verificar que DevOps solo muestra datos reales de Belgrano Ahorro
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_devops_endpoints():
    """Probar todos los endpoints DevOps para verificar que no hay datos simulados"""
    
    print("=" * 80)
    print("🧪 TEST COMPLETO: DEVOPS - SOLO DATOS REALES")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # URLs base
    devops_base = "http://localhost:5000/devops"
    belgrano_base = "http://localhost:5000"
    
    # Headers para autenticación DevOps
    devops_headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Headers para API de Belgrano Ahorro
    api_headers = {
        'Content-Type': 'application/json',
        'X-API-Key': os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
    }
    
    results = {
        'devops_endpoints': {},
        'belgrano_endpoints': {},
        'comparison': {},
        'errors': []
    }
    
    # 1. Probar endpoints DevOps
    print("\n🔍 PROBANDO ENDPOINTS DEVOPS...")
    
    devops_endpoints = [
        '/negocios',
        '/productos', 
        '/ofertas',
        '/precios'
    ]
    
    for endpoint in devops_endpoints:
        try:
            url = f"{devops_base}{endpoint}"
            print(f"   Probando: {url}")
            
            response = requests.get(url, headers=devops_headers, timeout=10)
            
            if response.status_code == 200:
                # Verificar que no sea JSON crudo
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        if 'source' in data and data['source'] == 'simulated':
                            results['devops_endpoints'][endpoint] = {
                                'status': 'error',
                                'message': 'Datos simulados detectados',
                                'data': data
                            }
                        else:
                            results['devops_endpoints'][endpoint] = {
                                'status': 'success',
                                'message': 'Datos reales',
                                'data': data
                            }
                    except:
                        results['devops_endpoints'][endpoint] = {
                            'status': 'error',
                            'message': 'JSON inválido',
                            'data': response.text[:200]
                        }
                else:
                    # Es HTML, verificar que no contenga datos simulados
                    if 'simulated' in response.text.lower() or 'fallback' in response.text.lower():
                        results['devops_endpoints'][endpoint] = {
                            'status': 'error',
                            'message': 'Datos simulados en HTML',
                            'data': response.text[:200]
                        }
                    else:
                        results['devops_endpoints'][endpoint] = {
                            'status': 'success',
                            'message': 'HTML con datos reales',
                            'data': 'HTML response'
                        }
            else:
                results['devops_endpoints'][endpoint] = {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}',
                    'data': response.text[:200]
                }
                
        except Exception as e:
            results['devops_endpoints'][endpoint] = {
                'status': 'error',
                'message': f'Error de conexión: {str(e)}',
                'data': None
            }
            results['errors'].append(f"DevOps {endpoint}: {str(e)}")
    
    # 2. Probar endpoints Belgrano Ahorro
    print("\n🔍 PROBANDO ENDPOINTS BELGRANO AHORRO...")
    
    belgrano_endpoints = [
        '/api/v1/negocios',
        '/api/v1/productos',
        '/api/v1/ofertas',
        '/api/v1/precios'
    ]
    
    for endpoint in belgrano_endpoints:
        try:
            url = f"{belgrano_base}{endpoint}"
            print(f"   Probando: {url}")
            
            response = requests.get(url, headers=api_headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results['belgrano_endpoints'][endpoint] = {
                        'status': 'success',
                        'message': f'Datos obtenidos: {len(data) if isinstance(data, list) else "object"}',
                        'data': data
                    }
                except:
                    results['belgrano_endpoints'][endpoint] = {
                        'status': 'error',
                        'message': 'JSON inválido',
                        'data': response.text[:200]
                    }
            else:
                results['belgrano_endpoints'][endpoint] = {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}',
                    'data': response.text[:200]
                }
                
        except Exception as e:
            results['belgrano_endpoints'][endpoint] = {
                'status': 'error',
                'message': f'Error de conexión: {str(e)}',
                'data': None
            }
            results['errors'].append(f"Belgrano {endpoint}: {str(e)}")
    
    # 3. Comparar datos
    print("\n🔍 COMPARANDO DATOS...")
    
    for endpoint in devops_endpoints:
        devops_key = endpoint
        belgrano_key = f"/api/v1{endpoint}"
        
        if (devops_key in results['devops_endpoints'] and 
            belgrano_key in results['belgrano_endpoints']):
            
            devops_data = results['devops_endpoints'][devops_key]
            belgrano_data = results['belgrano_endpoints'][belgrano_key]
            
            if (devops_data['status'] == 'success' and 
                belgrano_data['status'] == 'success'):
                
                # Comparar cantidad de items
                devops_count = 0
                belgrano_count = 0
                
                if isinstance(devops_data['data'], list):
                    devops_count = len(devops_data['data'])
                elif isinstance(devops_data['data'], dict) and 'data' in devops_data['data']:
                    if isinstance(devops_data['data']['data'], list):
                        devops_count = len(devops_data['data']['data'])
                
                if isinstance(belgrano_data['data'], list):
                    belgrano_count = len(belgrano_data['data'])
                
                results['comparison'][endpoint] = {
                    'devops_count': devops_count,
                    'belgrano_count': belgrano_count,
                    'match': devops_count == belgrano_count,
                    'status': 'success' if devops_count == belgrano_count else 'warning'
                }
            else:
                results['comparison'][endpoint] = {
                    'status': 'error',
                    'message': 'No se pudieron obtener datos para comparar'
                }
    
    # 4. Generar reporte
    print("\n" + "=" * 80)
    print("📊 REPORTE FINAL")
    print("=" * 80)
    
    # Contar resultados
    devops_success = sum(1 for r in results['devops_endpoints'].values() if r['status'] == 'success')
    belgrano_success = sum(1 for r in results['belgrano_endpoints'].values() if r['status'] == 'success')
    comparison_success = sum(1 for r in results['comparison'].values() if r.get('status') == 'success')
    
    print(f"✅ Endpoints DevOps exitosos: {devops_success}/{len(devops_endpoints)}")
    print(f"✅ Endpoints Belgrano Ahorro exitosos: {belgrano_success}/{len(belgrano_endpoints)}")
    print(f"✅ Comparaciones exitosas: {comparison_success}/{len(devops_endpoints)}")
    
    if results['errors']:
        print(f"\n❌ Errores encontrados: {len(results['errors'])}")
        for error in results['errors']:
            print(f"   - {error}")
    
    # Verificar que no hay datos simulados
    simulated_found = False
    for endpoint, result in results['devops_endpoints'].items():
        if 'simulated' in str(result).lower() or 'fallback' in str(result).lower():
            simulated_found = True
            print(f"\n⚠️ DATOS SIMULADOS DETECTADOS EN: {endpoint}")
    
    if not simulated_found:
        print("\n✅ NO SE DETECTARON DATOS SIMULADOS")
    else:
        print("\n❌ SE DETECTARON DATOS SIMULADOS - REVISAR IMPLEMENTACIÓN")
    
    # Guardar reporte
    report_file = f"test_devops_real_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    return results

if __name__ == "__main__":
    test_devops_endpoints()

