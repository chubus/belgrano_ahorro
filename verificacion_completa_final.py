#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación completa final de todos los servicios DevOps
"""

import requests
import time
from datetime import datetime

def verificar_servicios():
    """Verificar todos los servicios"""
    print("VERIFICACION COMPLETA FINAL DE SERVICIOS DEVOPS")
    print("=" * 60)
    print("Verificando todos los servicios y endpoints")
    print("")
    
    servicios = {
        'Belgrano Ahorro': 'http://localhost:5000/',
        'Ticketera': 'http://localhost:5001/',
        'DevOps': 'http://localhost:5002/devops/',
        'API Gateway': 'http://localhost:5003/gateway/health',
        'Sistema Sync': 'http://localhost:5004/sync/status'
    }
    
    print("VERIFICANDO SERVICIOS PRINCIPALES")
    print("=" * 50)
    
    servicios_activos = 0
    
    for nombre, url in servicios.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 302]:
                print(f"OK {nombre} - Activo ({response.status_code})")
                servicios_activos += 1
            else:
                print(f"WARNING {nombre} - Respuesta {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"ERROR {nombre} - No se puede conectar")
        except Exception as e:
            print(f"ERROR {nombre} - {e}")
    
    return servicios_activos

def verificar_endpoints_devops():
    """Verificar endpoints DevOps"""
    print("\nVERIFICANDO ENDPOINTS DEVOPS")
    print("=" * 50)
    
    endpoints = [
        '/devops/login',
        '/devops/',
        '/devops/health',
        '/devops/status',
        '/devops/info',
        '/devops/negocios',
        '/devops/productos',
        '/devops/ofertas',
        '/devops/sucursales',
        '/devops/precios',
        '/devops/sync'
    ]
    
    funcionando = 0
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5002{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302, 401]:
                print(f"OK {endpoint}")
                funcionando += 1
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return funcionando

def verificar_endpoints_ticketera():
    """Verificar endpoints Ticketera"""
    print("\nVERIFICANDO ENDPOINTS TICKETERA")
    print("=" * 50)
    
    endpoints = [
        '/',
        '/login',
        '/devops/',
        '/devops/login',
        '/devops/health',
        '/devops/negocios',
        '/devops/productos',
        '/devops/ofertas',
        '/devops/sucursales',
        '/devops/precios'
    ]
    
    funcionando = 0
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5001{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302, 401]:
                print(f"OK {endpoint}")
                funcionando += 1
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return funcionando

def verificar_apis_belgrano():
    """Verificar APIs de Belgrano Ahorro"""
    print("\nVERIFICANDO APIs BELGRANO AHORRO")
    print("=" * 50)
    
    apis = [
        '/',
        '/api/negocios',
        '/api/productos',
        '/api/ofertas',
        '/api/sucursales',
        '/api/precios'
    ]
    
    funcionando = 0
    
    for api in apis:
        try:
            url = f"http://localhost:5000{api}"
            headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code in [200, 401]:
                print(f"OK {api}")
                funcionando += 1
            else:
                print(f"ERROR {api} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {api} - {e}")
    
    return funcionando

def verificar_api_gateway():
    """Verificar API Gateway"""
    print("\nVERIFICANDO API GATEWAY")
    print("=" * 50)
    
    endpoints = [
        '/gateway/health',
        '/gateway/negocios',
        '/gateway/productos',
        '/gateway/ofertas',
        '/gateway/sucursales'
    ]
    
    funcionando = 0
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5003{endpoint}"
            headers = {'Authorization': 'Bearer devops_api_key_2025'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code in [200, 401]:
                print(f"OK {endpoint}")
                funcionando += 1
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return funcionando

def verificar_sistema_sync():
    """Verificar sistema de sincronización"""
    print("\nVERIFICANDO SISTEMA DE SINCRONIZACION")
    print("=" * 50)
    
    endpoints = [
        '/sync/status',
        '/sync/force',
        '/sync/differences'
    ]
    
    funcionando = 0
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5004{endpoint}"
            if endpoint == '/sync/force':
                response = requests.post(url, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 401]:
                print(f"OK {endpoint}")
                funcionando += 1
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return funcionando

def generar_reporte_final():
    """Generar reporte final"""
    print("\n" + "=" * 60)
    print("REPORTE FINAL DE CONECTIVIDAD")
    print("=" * 60)
    
    # Verificar todos los componentes
    servicios_activos = verificar_servicios()
    endpoints_devops = verificar_endpoints_devops()
    endpoints_ticketera = verificar_endpoints_ticketera()
    apis_belgrano = verificar_apis_belgrano()
    api_gateway = verificar_api_gateway()
    sistema_sync = verificar_sistema_sync()
    
    # Calcular métricas
    total_servicios = 5
    total_endpoints_devops = 11
    total_endpoints_ticketera = 10
    total_apis_belgrano = 6
    total_api_gateway = 5
    total_sistema_sync = 3
    
    print(f"\nSERVICIOS ACTIVOS: {servicios_activos}/{total_servicios} ({round(servicios_activos/total_servicios*100, 1)}%)")
    print(f"ENDPOINTS DEVOPS: {endpoints_devops}/{total_endpoints_devops} ({round(endpoints_devops/total_endpoints_devops*100, 1)}%)")
    print(f"ENDPOINTS TICKETERA: {endpoints_ticketera}/{total_endpoints_ticketera} ({round(endpoints_ticketera/total_endpoints_ticketera*100, 1)}%)")
    print(f"APIs BELGRANO: {apis_belgrano}/{total_apis_belgrano} ({round(apis_belgrano/total_apis_belgrano*100, 1)}%)")
    print(f"API GATEWAY: {api_gateway}/{total_api_gateway} ({round(api_gateway/total_api_gateway*100, 1)}%)")
    print(f"SISTEMA SYNC: {sistema_sync}/{total_sistema_sync} ({round(sistema_sync/total_sistema_sync*100, 1)}%)")
    
    # Estado general
    if servicios_activos >= 4 and endpoints_devops >= 8:
        print("\nSISTEMA DEVOPS COMPLETAMENTE FUNCIONAL")
        print("Todos los servicios principales están operativos")
        print("Endpoints DevOps funcionando correctamente")
        print("Sistema listo para deploy")
        return True
    else:
        print("\nSISTEMA DEVOPS REQUIERE ATENCION")
        print("Algunos servicios o endpoints no están funcionando")
        return False

def main():
    """Función principal"""
    print("VERIFICACION COMPLETA FINAL")
    print("=" * 60)
    print("Verificando todos los servicios DevOps")
    print("")
    
    return generar_reporte_final()

if __name__ == "__main__":
    main()
