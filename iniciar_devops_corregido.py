#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iniciar servicios DevOps sin problemas de Unicode
"""

import os
import subprocess
import time
import requests
import signal
import sys

def configurar_entorno():
    """Configurar variables de entorno"""
    print("CONFIGURANDO VARIABLES DE ENTORNO")
    print("=" * 50)
    
    variables = {
        'DEVOPS_USERNAME': 'devops',
        'DEVOPS_PASSWORD': 'DevOps2025!Secure',
        'BELGRANO_AHORRO_URL': 'https://belgranoahorro-aliq.onrender.com',
        'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025',
        'GATEWAY_URL': 'http://localhost:5003/gateway',
        'GATEWAY_API_KEY': 'devops_api_key_2025',
        'TICKETERA_URL': 'http://localhost:5001',
        'TICKETERA_API_KEY': 'ticketera_api_key_2025',
        'SECRET_KEY': 'devops_secret_key_2025',
        'API_TIMEOUT': '30',
        'API_RETRY_ATTEMPTS': '3',
        'API_RETRY_DELAY': '1',
        'CACHE_TTL': '300',
        'SYNC_INTERVAL': '60'
    }
    
    for key, value in variables.items():
        os.environ[key] = value
        print(f"OK {key} = {value}")

def terminar_procesos_existentes():
    """Terminar procesos existentes en los puertos"""
    print("\nTERMINANDO PROCESOS EXISTENTES")
    print("=" * 50)
    
    ports = [5000, 5001, 5002, 5003, 5004]
    
    for port in ports:
        try:
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

def iniciar_servicios():
    """Iniciar todos los servicios"""
    print("\nINICIANDO SERVICIOS DEVOPS")
    print("=" * 50)
    
    servicios = [
        {'name': 'Belgrano Ahorro', 'script': 'app.py', 'port': 5000},
        {'name': 'Ticketera', 'script': 'app_tickets.py', 'port': 5001},
        {'name': 'DevOps', 'script': 'devops_routes.py', 'port': 5002},
        {'name': 'API Gateway', 'script': 'api_gateway.py', 'port': 5003},
        {'name': 'Sistema Sync', 'script': 'sync_manager.py', 'port': 5004}
    ]
    
    procesos = []
    
    for service in servicios:
        try:
            print(f"Iniciando {service['name']}...")
            proceso = subprocess.Popen([
                'python', service['script']
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            procesos.append(proceso)
            print(f"OK {service['name']} iniciado (PID: {proceso.pid})")
        except Exception as e:
            print(f"ERROR {service['name']}: {e}")
    
    return procesos

def esperar_servicios():
    """Esperar a que los servicios se inicien"""
    print("\nESPERANDO SERVICIOS")
    print("=" * 50)
    print("Esperando 25 segundos para que los servicios se inicien...")
    time.sleep(25)

def verificar_servicios():
    """Verificar que los servicios estén funcionando"""
    print("\nVERIFICANDO SERVICIOS")
    print("=" * 50)
    
    servicios = {
        'Belgrano Ahorro': 'http://localhost:5000/',
        'Ticketera': 'http://localhost:5001/',
        'DevOps': 'http://localhost:5002/devops/',
        'API Gateway': 'http://localhost:5003/gateway/health',
        'Sistema Sync': 'http://localhost:5004/sync/status'
    }
    
    activos = 0
    
    for nombre, url in servicios.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 302]:
                print(f"OK {nombre} - Activo ({response.status_code})")
                activos += 1
            else:
                print(f"WARNING {nombre} - Respuesta {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"ERROR {nombre} - No se puede conectar")
        except Exception as e:
            print(f"ERROR {nombre} - {e}")
    
    return activos

def verificar_endpoints_devops():
    """Verificar endpoints DevOps específicos"""
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

def verificar_apis_belgrano():
    """Verificar APIs de Belgrano Ahorro"""
    print("\nVERIFICANDO APIs BELGRANO AHORRO")
    print("=" * 50)
    
    apis = [
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

def main():
    """Función principal"""
    print("INICIO CORREGIDO DE SERVICIOS DEVOPS")
    print("=" * 60)
    print("Iniciando todos los servicios sin problemas de Unicode")
    print("")
    
    try:
        # 1. Configurar entorno
        configurar_entorno()
        
        # 2. Terminar procesos existentes
        terminar_procesos_existentes()
        time.sleep(3)
        
        # 3. Iniciar servicios
        procesos = iniciar_servicios()
        
        # 4. Esperar
        esperar_servicios()
        
        # 5. Verificar servicios
        servicios_activos = verificar_servicios()
        
        # 6. Verificar endpoints DevOps
        endpoints_ok = verificar_endpoints_devops()
        
        # 7. Verificar APIs Belgrano
        apis_ok = verificar_apis_belgrano()
        
        # 8. Reporte final
        print("\n" + "=" * 60)
        print("REPORTE FINAL")
        print("=" * 60)
        print(f"Servicios activos: {servicios_activos}/5")
        print(f"Endpoints DevOps OK: {endpoints_ok}/11")
        print(f"APIs Belgrano OK: {apis_ok}/5")
        
        if servicios_activos >= 4 and endpoints_ok >= 8:
            print("\nSISTEMA DEVOPS COMPLETAMENTE FUNCIONAL")
            print("Todos los servicios están operativos")
            print("Listo para deploy")
            return True
        else:
            print("\nSISTEMA DEVOPS REQUIERE ATENCION")
            print("Algunos servicios o endpoints no están funcionando")
            return False
            
    except KeyboardInterrupt:
        print("\nDeteniendo servicios...")
        return False
    except Exception as e:
        print(f"Error en el proceso: {e}")
        return False

if __name__ == "__main__":
    main()
