#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Conectividad Completa DevOps ↔ Belgrano Ahorro
Verifica que DevOps pueda gestionar todos los datos de Belgrano Ahorro
"""

import os
import requests
import json
from datetime import datetime

def test_conectividad_completa():
    """Test completo de conectividad entre DevOps y Belgrano Ahorro"""
    
    print("=" * 60)
    print("🔗 TEST DE CONECTIVIDAD COMPLETA DEVOPS ↔ BELGRANO AHORRO")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configurar variables de entorno
    os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
    
    url = os.environ.get('BELGRANO_AHORRO_URL')
    api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
    
    print("📋 CONFIGURACIÓN:")
    print(f"   URL: {url}")
    print(f"   API Key: {api_key[:10]}...")
    print()
    
    # Headers para autenticación
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Endpoints a probar
    endpoints = [
        {
            'url': '/api/v1/negocios',
            'name': 'Negocios',
            'method': 'GET',
            'required': True
        },
        {
            'url': '/api/v1/productos',
            'name': 'Productos',
            'method': 'GET',
            'required': True
        },
        {
            'url': '/api/v1/sucursales',
            'name': 'Sucursales',
            'method': 'GET',
            'required': True
        },
        {
            'url': '/api/v1/ofertas',
            'name': 'Ofertas',
            'method': 'GET',
            'required': True
        },
        {
            'url': '/api/v1/categorias',
            'name': 'Categorías',
            'method': 'GET',
            'required': True
        }
    ]
    
    print("🧪 PROBANDO ENDPOINTS:")
    print("-" * 40)
    
    resultados = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{url}{endpoint["url"]}', headers=headers, timeout=15)
            status = response.status_code
            
            if status == 200:
                data = response.json()
                count = len(data) if isinstance(data, (list, dict)) else 0
                print(f"✅ {endpoint['name']}: {status} - {count} items")
                resultados[endpoint['name']] = {
                    'status': 'success',
                    'count': count,
                    'data': data
                }
            elif status == 401:
                print(f"❌ {endpoint['name']}: {status} - Error de autenticación")
                resultados[endpoint['name']] = {
                    'status': 'auth_error',
                    'error': 'API key inválida'
                }
            elif status == 500:
                print(f"❌ {endpoint['name']}: {status} - Error interno del servidor")
                resultados[endpoint['name']] = {
                    'status': 'server_error',
                    'error': 'Error interno'
                }
            else:
                print(f"⚠️ {endpoint['name']}: {status} - {response.text[:50]}")
                resultados[endpoint['name']] = {
                    'status': 'error',
                    'error': response.text[:100]
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint['name']}: Timeout")
            resultados[endpoint['name']] = {
                'status': 'timeout',
                'error': 'Timeout de conexión'
            }
        except requests.exceptions.ConnectionError:
            print(f"🔌 {endpoint['name']}: Error de conexión")
            resultados[endpoint['name']] = {
                'status': 'connection_error',
                'error': 'No se puede conectar'
            }
        except Exception as e:
            print(f"💥 {endpoint['name']}: Error inesperado - {e}")
            resultados[endpoint['name']] = {
                'status': 'unexpected_error',
                'error': str(e)
            }
    
    print()
    print("📊 RESUMEN DE RESULTADOS:")
    print("-" * 40)
    
    exitosos = 0
    errores_auth = 0
    errores_server = 0
    otros_errores = 0
    
    for name, resultado in resultados.items():
        if resultado['status'] == 'success':
            exitosos += 1
            print(f"✅ {name}: {resultado['count']} items")
        elif resultado['status'] == 'auth_error':
            errores_auth += 1
            print(f"🔐 {name}: Error de autenticación")
        elif resultado['status'] == 'server_error':
            errores_server += 1
            print(f"💥 {name}: Error del servidor")
        else:
            otros_errores += 1
            print(f"❌ {name}: {resultado['error']}")
    
    print()
    print("📈 ESTADÍSTICAS:")
    print(f"   ✅ Exitosos: {exitosos}")
    print(f"   🔐 Errores de autenticación: {errores_auth}")
    print(f"   💥 Errores del servidor: {errores_server}")
    print(f"   ❌ Otros errores: {otros_errores}")
    
    print()
    print("🎯 DIAGNÓSTICO:")
    if exitosos == len(endpoints):
        print("✅ CONECTIVIDAD PERFECTA - DevOps puede gestionar todos los datos")
    elif errores_auth > 0:
        print("🔐 PROBLEMA DE AUTENTICACIÓN - Verificar API key en servidor")
    elif errores_server > 0:
        print("💥 PROBLEMA DEL SERVIDOR - Verificar configuración del servidor")
    else:
        print("❌ PROBLEMAS DE CONECTIVIDAD - Verificar configuración general")
    
    return resultados

if __name__ == "__main__":
    test_conectividad_completa()
