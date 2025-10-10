#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar servicios y probar DevOps con datos reales
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime

def start_belgrano_ahorro():
    """Iniciar Belgrano Ahorro"""
    print("🚀 Iniciando Belgrano Ahorro...")
    
    # Configurar variables de entorno
    env = os.environ.copy()
    env['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    env['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
    env['API_TIMEOUT_SECS'] = '10'
    env['DEVOPS_USERNAME'] = 'devops'
    env['DEVOPS_PASSWORD'] = 'devops_password'
    
    try:
        # Intentar iniciar con app_unificado.py
        process = subprocess.Popen([
            sys.executable, 'app_unificado.py'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un poco para que inicie
        time.sleep(5)
        
        # Verificar si está funcionando
        try:
            response = requests.get('http://localhost:5000/healthz', timeout=5)
            if response.status_code == 200:
                print("✅ Belgrano Ahorro iniciado correctamente")
                return process
        except:
            pass
        
        # Si no funciona, intentar con app.py
        process.terminate()
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(5)
        
        try:
            response = requests.get('http://localhost:5000/', timeout=5)
            if response.status_code == 200:
                print("✅ Belgrano Ahorro iniciado correctamente")
                return process
        except:
            pass
        
        print("❌ No se pudo iniciar Belgrano Ahorro")
        return None
        
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return None

def test_devops_connectivity():
    """Probar conectividad DevOps"""
    print("\n🔍 Probando conectividad DevOps...")
    
    try:
        # Probar endpoint de conectividad
        response = requests.get('http://localhost:5000/devops/conectar-belgrano', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conectividad DevOps: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Error de conectividad: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando conectividad: {e}")
        return False

def test_devops_endpoints():
    """Probar endpoints DevOps"""
    print("\n🔍 Probando endpoints DevOps...")
    
    endpoints = ['/devops/negocios', '/devops/productos', '/devops/ofertas', '/devops/precios']
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5000{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    print(f"❌ {endpoint}: Devuelve JSON crudo")
                else:
                    print(f"✅ {endpoint}: Devuelve HTML correctamente")
            else:
                print(f"⚠️ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    """Función principal"""
    print("=" * 80)
    print("🧪 INICIANDO SERVICIOS Y PROBANDO DEVOPS")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Iniciar Belgrano Ahorro
    process = start_belgrano_ahorro()
    
    if not process:
        print("❌ No se pudo iniciar Belgrano Ahorro. Abortando.")
        return
    
    try:
        # Esperar un poco más para que esté completamente listo
        time.sleep(3)
        
        # Probar conectividad
        if test_devops_connectivity():
            # Probar endpoints
            test_devops_endpoints()
        else:
            print("❌ No se pudo establecer conectividad DevOps")
    
    finally:
        # Terminar proceso
        print("\n🛑 Terminando proceso...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()

