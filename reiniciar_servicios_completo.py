#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reiniciar todos los servicios DevOps y verificar funcionamiento
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime

def kill_existing_processes():
    """Terminar procesos existentes en los puertos"""
    print("TERMINANDO PROCESOS EXISTENTES")
    print("=" * 50)
    
    ports = [5000, 5001, 5002, 5003, 5004]
    
    for port in ports:
        try:
            # En Windows, usar netstat para encontrar PIDs
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                            print(f"Terminado proceso en puerto {port} (PID: {pid})")
                        except:
                            pass
        except Exception as e:
            print(f"Error terminando procesos en puerto {port}: {e}")

def start_services():
    """Iniciar todos los servicios"""
    print("\nINICIANDO SERVICIOS")
    print("=" * 50)
    
    services = [
        {'name': 'Belgrano Ahorro', 'script': 'app.py', 'port': 5000},
        {'name': 'Ticketera', 'script': 'app_tickets.py', 'port': 5001},
        {'name': 'DevOps', 'script': 'devops_routes.py', 'port': 5002},
        {'name': 'API Gateway', 'script': 'api_gateway.py', 'port': 5003},
        {'name': 'Sistema Sync', 'script': 'sync_manager.py', 'port': 5004}
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

def wait_for_services():
    """Esperar a que los servicios se inicien"""
    print("\nESPERANDO SERVICIOS")
    print("=" * 50)
    
    print("Esperando 15 segundos para que los servicios se inicien...")
    time.sleep(15)

def verify_services():
    """Verificar que los servicios estén funcionando"""
    print("\nVERIFICANDO SERVICIOS")
    print("=" * 50)
    
    services = {
        'Belgrano Ahorro': 'http://localhost:5000/',
        'Ticketera': 'http://localhost:5001/',
        'DevOps': 'http://localhost:5002/devops/',
        'API Gateway': 'http://localhost:5003/gateway/health',
        'Sistema Sync': 'http://localhost:5004/sync/status'
    }
    
    active_services = 0
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 302]:
                print(f"OK {name} - Activo ({response.status_code})")
                active_services += 1
            else:
                print(f"WARNING {name} - Respuesta {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"ERROR {name} - No se puede conectar")
        except Exception as e:
            print(f"ERROR {name} - {e}")
    
    return active_services, len(services)

def verify_endpoints():
    """Verificar endpoints específicos"""
    print("\nVERIFICANDO ENDPOINTS ESPECIFICOS")
    print("=" * 50)
    
    # Endpoints DevOps
    devops_endpoints = [
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
    
    devops_ok = 0
    
    for endpoint in devops_endpoints:
        try:
            url = f"http://localhost:5002{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302, 401]:
                print(f"OK {endpoint}")
                devops_ok += 1
            else:
                print(f"ERROR {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {endpoint} - {e}")
    
    # APIs Belgrano Ahorro
    belgrano_apis = [
        '/',
        '/api/negocios',
        '/api/productos',
        '/api/ofertas',
        '/api/sucursales',
        '/api/precios'
    ]
    
    belgrano_ok = 0
    
    for api in belgrano_apis:
        try:
            url = f"http://localhost:5000{api}"
            headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code in [200, 401]:
                print(f"OK {api}")
                belgrano_ok += 1
            else:
                print(f"ERROR {api} - {response.status_code}")
        except Exception as e:
            print(f"ERROR {api} - {e}")
    
    return devops_ok, belgrano_ok

def main():
    """Función principal"""
    print("REINICIO COMPLETO DE SERVICIOS DEVOPS")
    print("=" * 60)
    print("Reiniciando todos los servicios y verificando funcionamiento")
    print("")
    
    # 1. Terminar procesos existentes
    kill_existing_processes()
    
    # 2. Esperar un momento
    time.sleep(3)
    
    # 3. Iniciar servicios
    start_services()
    
    # 4. Esperar a que se inicien
    wait_for_services()
    
    # 5. Verificar servicios
    active_services, total_services = verify_services()
    
    # 6. Verificar endpoints
    devops_ok, belgrano_ok = verify_endpoints()
    
    # 7. Reporte final
    print("\n" + "=" * 60)
    print("REPORTE FINAL")
    print("=" * 60)
    
    print(f"Servicios activos: {active_services}/{total_services}")
    print(f"Endpoints DevOps OK: {devops_ok}/11")
    print(f"APIs Belgrano OK: {belgrano_ok}/6")
    
    if active_services >= 4 and devops_ok >= 8:
        print("\nSISTEMA DEVOPS COMPLETAMENTE FUNCIONAL")
        print("Todos los servicios están operativos")
        print("Listo para deploy")
        return True
    else:
        print("\nSISTEMA DEVOPS REQUIERE ATENCION")
        print("Algunos servicios o endpoints no están funcionando")
        return False

if __name__ == "__main__":
    main()
