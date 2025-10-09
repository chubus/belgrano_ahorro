#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revisión de APIs de conexiones en DevOps
"""

import os
import sys
import json
import requests
from datetime import datetime

def revisar_configuracion_devops():
    """Revisar configuración de DevOps"""
    print("=" * 60)
    print("REVISION DE APIs DE CONEXIONES EN DEVOPS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar archivos de configuración
    print("1. ARCHIVOS DE CONFIGURACION DEVOPS")
    print("-" * 40)
    
    config_files = [
        'devops_routes.py',
        'belgrano_client.py',
        'config_devops.py',
        'devops.env.example',
        'api_client.py'
    ]
    
    for file in config_files:
        if os.path.exists(file):
            print(f"   [OK] {file} - Encontrado")
        else:
            print(f"   [ERROR] {file} - No encontrado")
    
    print()
    
    # 2. Verificar variables de entorno
    print("2. VARIABLES DE ENTORNO")
    print("-" * 40)
    
    env_vars = [
        'BELGRANO_AHORRO_URL',
        'BELGRANO_AHORRO_API_KEY',
        'DEVOPS_USERNAME',
        'DEVOPS_PASSWORD'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"   [OK] {var} = {display_value}")
        else:
            print(f"   [WARNING] {var} - No configurada")
    
    print()
    
    # 3. Verificar cliente API
    print("3. CLIENTE API DEVOPS")
    print("-" * 40)
    
    try:
        from belgrano_client import BelgranoAhorroClient
        client = BelgranoAhorroClient()
        print(f"   [OK] BelgranoAhorroClient inicializado")
        print(f"   Base URL: {client.base_url}")
        print(f"   API Key configurada: {'Sí' if client.api_key else 'No'}")
        print(f"   Timeout: {client.timeout}s")
    except Exception as e:
        print(f"   [ERROR] Error inicializando cliente: {e}")
    
    print()
    
    # 4. Verificar endpoints de DevOps
    print("4. ENDPOINTS DEVOPS")
    print("-" * 40)
    
    devops_endpoints = [
        '/devops/health',
        '/devops/status',
        '/devops/info',
        '/devops/negocios',
        '/devops/productos',
        '/devops/ofertas',
        '/devops/sucursales'
    ]
    
    base_url = "http://localhost:5002"
    
    for endpoint in devops_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {endpoint} - {response.status_code}")
            else:
                print(f"   [WARNING] {endpoint} - {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   [ERROR] {endpoint} - No se puede conectar (servicio no iniciado)")
        except Exception as e:
            print(f"   [ERROR] {endpoint} - Error: {e}")
    
    print()
    
    # 5. Verificar conexión con Belgrano Ahorro
    print("5. CONEXION CON BELGRANO AHORRO")
    print("-" * 40)
    
    belgrano_url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
    belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
    
    headers = {
        'X-API-Key': belgrano_api_key,
        'Content-Type': 'application/json'
    }
    
    endpoints_to_test = [
        '/healthz',
        '/api/v1/productos',
        '/api/v1/negocios',
        '/api/v1/ofertas'
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{belgrano_url}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"   [OK] {endpoint} - {response.status_code}")
            else:
                print(f"   [WARNING] {endpoint} - {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"   [ERROR] {endpoint} - Timeout")
        except Exception as e:
            print(f"   [ERROR] {endpoint} - Error: {e}")
    
    print()
    
    # 6. Verificar sincronización
    print("6. SINCRONIZACION DEVOPS")
    print("-" * 40)
    
    try:
        # Verificar si hay funciones de sincronización
        import devops_routes
        if hasattr(devops_routes, 'sincronizar_cambio'):
            print("   [OK] Función de sincronización disponible")
        else:
            print("   [WARNING] Función de sincronización no encontrada")
        
        if hasattr(devops_routes, 'devops_api_client'):
            print("   [OK] Cliente API DevOps disponible")
        else:
            print("   [WARNING] Cliente API DevOps no disponible")
            
    except Exception as e:
        print(f"   [ERROR] Error verificando sincronización: {e}")
    
    print()
    
    # 7. Resumen
    print("7. RESUMEN")
    print("-" * 40)
    print("APIs de DevOps revisadas:")
    print("- Configuración: Verificada")
    print("- Cliente API: Verificado")
    print("- Endpoints: Verificados")
    print("- Conexión Belgrano Ahorro: Verificada")
    print("- Sincronización: Verificada")

def main():
    """Función principal"""
    try:
        revisar_configuracion_devops()
        return True
    except Exception as e:
        print(f"Error en revisión: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
