#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Probar Ticketera específicamente
"""

import subprocess
import time
import requests
import sys

def probar_ticketera():
    """Probar Ticketera paso a paso"""
    print("PROBANDO TICKETERA")
    print("=" * 50)
    
    try:
        # 1. Verificar sintaxis
        print("1. Verificando sintaxis...")
        result = subprocess.run(['python', '-m', 'py_compile', 'app_tickets.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("OK Sintaxis correcta")
        else:
            print(f"ERROR Sintaxis: {result.stderr}")
            return False
        
        # 2. Iniciar Ticketera
        print("2. Iniciando Ticketera...")
        proceso = subprocess.Popen(['python', 'app_tickets.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 3. Esperar
        print("3. Esperando 10 segundos...")
        time.sleep(10)
        
        # 4. Verificar si está corriendo
        print("4. Verificando proceso...")
        if proceso.poll() is None:
            print("OK Proceso corriendo")
        else:
            stdout, stderr = proceso.communicate()
            print(f"ERROR Proceso terminado")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        # 5. Probar conectividad
        print("5. Probando conectividad...")
        try:
            response = requests.get('http://localhost:5001/', timeout=5)
            if response.status_code == 200:
                print("OK Ticketera conectado")
                return True
            else:
                print(f"ERROR Respuesta {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("ERROR No se puede conectar")
            return False
        except Exception as e:
            print(f"ERROR {e}")
            return False
            
    except Exception as e:
        print(f"ERROR General: {e}")
        return False
    finally:
        # Terminar proceso
        try:
            proceso.terminate()
        except:
            pass

def probar_endpoints_ticketera():
    """Probar endpoints específicos de Ticketera"""
    print("\nPROBANDO ENDPOINTS TICKETERA")
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

def main():
    """Función principal"""
    print("PRUEBA ESPECIFICA DE TICKETERA")
    print("=" * 60)
    
    # Probar Ticketera
    if probar_ticketera():
        print("\nTicketera iniciado correctamente")
        
        # Probar endpoints
        endpoints_ok = probar_endpoints_ticketera()
        
        print(f"\nEndpoints funcionando: {endpoints_ok}/10")
        
        if endpoints_ok >= 8:
            print("TICKETERA COMPLETAMENTE FUNCIONAL")
            return True
        else:
            print("TICKETERA PARCIALMENTE FUNCIONAL")
            return False
    else:
        print("TICKETERA NO FUNCIONA")
        return False

if __name__ == "__main__":
    main()
