#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chequeo de servicios DevOps activos
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def verificar_servicios():
    """Verificar que todos los servicios estan activos"""
    print("VERIFICANDO SERVICIOS DEVOPS ACTIVOS")
    print("=" * 50)
    
    servicios = {
        'Belgrano Ahorro': 'http://localhost:5000/',
        'Ticketera': 'http://localhost:5001/',
        'DevOps': 'http://localhost:5002/devops/',
        'API Gateway': 'http://localhost:5003/gateway/health',
        'Sistema Sync': 'http://localhost:5004/sync/status'
    }
    
    servicios_activos = {}
    
    for nombre, url in servicios.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302]:
                print(f"OK {nombre} - Activo ({response.status_code})")
                servicios_activos[nombre] = True
            else:
                print(f"WARNING {nombre} - Respuesta {response.status_code}")
                servicios_activos[nombre] = False
        except requests.exceptions.ConnectionError:
            print(f"ERROR {nombre} - No se puede conectar")
            servicios_activos[nombre] = False
        except Exception as e:
            print(f"ERROR {nombre} - {e}")
            servicios_activos[nombre] = False
    
    return servicios_activos

def verificar_endpoints_devops():
    """Verificar endpoints DevOps"""
    print("\nVERIFICANDO ENDPOINTS DEVOPS")
    print("=" * 50)
    
    devops_url = 'http://localhost:5002'
    endpoints = [
        '/devops/login',
        '/devops/',
        '/devops/health',
        '/devops/negocios',
        '/devops/productos',
        '/devops/ofertas',
        '/devops/sucursales',
        '/devops/precios'
    ]
    
    endpoints_ok = []
    
    for endpoint in endpoints:
        try:
            url = f"{devops_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 302, 401]:
                print(f"OK {endpoint}")
                endpoints_ok.append(endpoint)
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return len(endpoints_ok)

def verificar_conectividad_belgrano():
    """Verificar conectividad con Belgrano Ahorro"""
    print("\nVERIFICANDO CONECTIVIDAD BELGRANO AHORRO")
    print("=" * 50)
    
    belgrano_url = 'http://localhost:5000'
    endpoints = [
        '/',
        '/api/negocios',
        '/api/productos',
        '/api/ofertas',
        '/api/sucursales',
        '/api/precios'
    ]
    
    conectividad_ok = []
    
    for endpoint in endpoints:
        try:
            url = f"{belgrano_url}{endpoint}"
            headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code in [200, 401]:
                print(f"OK {endpoint}")
                conectividad_ok.append(endpoint)
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return len(conectividad_ok)

def verificar_api_gateway():
    """Verificar API Gateway"""
    print("\nVERIFICANDO API GATEWAY")
    print("=" * 50)
    
    gateway_url = 'http://localhost:5003'
    endpoints = [
        '/gateway/health',
        '/gateway/negocios',
        '/gateway/productos',
        '/gateway/ofertas',
        '/gateway/sucursales'
    ]
    
    gateway_ok = []
    
    for endpoint in endpoints:
        try:
            url = f"{gateway_url}{endpoint}"
            headers = {'Authorization': 'Bearer devops_api_key_2025'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code in [200, 401]:
                print(f"OK {endpoint}")
                gateway_ok.append(endpoint)
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return len(gateway_ok)

def verificar_sistema_sync():
    """Verificar sistema de sincronizacion"""
    print("\nVERIFICANDO SISTEMA DE SINCRONIZACION")
    print("=" * 50)
    
    sync_url = 'http://localhost:5004'
    endpoints = [
        '/sync/status',
        '/sync/force',
        '/sync/differences'
    ]
    
    sync_ok = []
    
    for endpoint in endpoints:
        try:
            url = f"{sync_url}{endpoint}"
            if endpoint == '/sync/force':
                response = requests.post(url, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 401]:
                print(f"OK {endpoint}")
                sync_ok.append(endpoint)
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    return len(sync_ok)

def generar_reporte_final():
    """Generar reporte final"""
    print("\nGENERANDO REPORTE FINAL")
    print("=" * 50)
    
    # Ejecutar todas las verificaciones
    servicios = verificar_servicios()
    endpoints_devops = verificar_endpoints_devops()
    conectividad_belgrano = verificar_conectividad_belgrano()
    api_gateway = verificar_api_gateway()
    sistema_sync = verificar_sistema_sync()
    
    # Calcular metricas
    servicios_activos = sum(1 for v in servicios.values() if v)
    total_servicios = len(servicios)
    
    reporte = {
        'timestamp': datetime.now().isoformat(),
        'servicios': servicios,
        'endpoints_devops': endpoints_devops,
        'conectividad_belgrano': conectividad_belgrano,
        'api_gateway': api_gateway,
        'sistema_sync': sistema_sync,
        'metricas': {
            'servicios_activos': servicios_activos,
            'total_servicios': total_servicios,
            'porcentaje_servicios': round((servicios_activos / total_servicios) * 100, 2),
            'endpoints_devops_ok': endpoints_devops,
            'conectividad_belgrano_ok': conectividad_belgrano,
            'api_gateway_ok': api_gateway,
            'sistema_sync_ok': sistema_sync
        }
    }
    
    # Guardar reporte
    with open('reporte_servicios_activos.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\nServicios activos: {servicios_activos}/{total_servicios}")
    print(f"Endpoints DevOps OK: {endpoints_devops}")
    print(f"Conectividad Belgrano OK: {conectividad_belgrano}")
    print(f"API Gateway OK: {api_gateway}")
    print(f"Sistema Sync OK: {sistema_sync}")
    
    if servicios_activos >= 4:
        print("\nSISTEMA DEVOPS FUNCIONAL")
        print("Listo para deploy")
        return True
    else:
        print("\nSISTEMA DEVOPS REQUIERE CORRECCIONES")
        print("Algunos servicios no estan activos")
        return False

def main():
    """Funcion principal"""
    print("CHEQUEO COMPLETO DE SERVICIOS DEVOPS")
    print("=" * 60)
    print("Verificacion exhaustiva antes del deploy")
    print("")
    
    return generar_reporte_final()

if __name__ == "__main__":
    main()
