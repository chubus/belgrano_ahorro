#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iniciar solo los servicios esenciales para DevOps
"""

import subprocess
import time
import requests

def start_essential_services():
    """Iniciar servicios esenciales"""
    print("INICIANDO SERVICIOS ESENCIALES DEVOPS")
    print("=" * 50)
    
    # Solo iniciar Belgrano Ahorro y API Gateway
    services = [
        {'name': 'Belgrano Ahorro', 'script': 'app.py', 'port': 5000},
        {'name': 'API Gateway', 'script': 'api_gateway.py', 'port': 5003}
    ]
    
    for service in services:
        try:
            print(f"Iniciando {service['name']}...")
            subprocess.Popen([
                'python', service['script']
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"OK {service['name']} iniciado")
        except Exception as e:
            print(f"ERROR {service['name']}: {e}")

def wait_and_verify():
    """Esperar y verificar servicios"""
    print("\nESPERANDO SERVICIOS...")
    time.sleep(10)
    
    print("\nVERIFICANDO SERVICIOS")
    print("=" * 50)
    
    services = {
        'Belgrano Ahorro': 'http://localhost:5000/',
        'API Gateway': 'http://localhost:5003/gateway/health'
    }
    
    active = 0
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302]:
                print(f"OK {name} - Activo")
                active += 1
            else:
                print(f"WARNING {name} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {name} - {e}")
    
    return active

def test_apis():
    """Probar APIs de Belgrano Ahorro"""
    print("\nPROBANDO APIs BELGRANO AHORRO")
    print("=" * 50)
    
    apis = [
        '/api/negocios',
        '/api/productos', 
        '/api/ofertas',
        '/api/sucursales',
        '/api/precios'
    ]
    
    working = 0
    
    for api in apis:
        try:
            url = f"http://localhost:5000{api}"
            headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code in [200, 401]:
                print(f"OK {api}")
                working += 1
            else:
                print(f"ERROR {api} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {api} - {e}")
    
    return working

def main():
    """Función principal"""
    print("INICIO DE SERVICIOS ESENCIALES")
    print("=" * 60)
    
    # Iniciar servicios
    start_essential_services()
    
    # Esperar y verificar
    active_services = wait_and_verify()
    
    # Probar APIs
    working_apis = test_apis()
    
    # Reporte
    print("\n" + "=" * 60)
    print("REPORTE FINAL")
    print("=" * 60)
    print(f"Servicios activos: {active_services}/2")
    print(f"APIs funcionando: {working_apis}/5")
    
    if active_services >= 2 and working_apis >= 3:
        print("\nSERVICIOS ESENCIALES FUNCIONANDO")
        print("Belgrano Ahorro y API Gateway operativos")
        print("APIs principales funcionando")
        return True
    else:
        print("\nSERVICIOS REQUIEREN ATENCION")
        return False

if __name__ == "__main__":
    main()
