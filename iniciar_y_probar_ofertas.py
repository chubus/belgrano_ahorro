#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar la aplicación y probar el endpoint de ofertas
"""

import subprocess
import time
import requests
import json
import sys
import os

def iniciar_aplicacion():
    """Iniciar la aplicación en segundo plano"""
    print("Iniciando aplicación Belgrano Ahorro...")
    
    try:
        # Intentar iniciar con app_unificado.py
        process = subprocess.Popen([
            sys.executable, 'app_unificado.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Aplicación iniciada en segundo plano")
        return process
        
    except Exception as e:
        print(f"Error iniciando aplicación: {e}")
        return None

def probar_endpoint_ofertas():
    """Probar el endpoint de ofertas"""
    
    base_url = "http://localhost:5000"
    api_key = "belgrano_ahorro_api_key_2025"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("\n" + "=" * 60)
    print("PROBANDO ENDPOINT DE OFERTAS CORREGIDO")
    print("=" * 60)
    
    # Esperar a que la aplicación esté lista
    print("Esperando que la aplicación esté lista...")
    for i in range(30):  # Esperar hasta 30 segundos
        try:
            response = requests.get(f"{base_url}/healthz", timeout=2)
            if response.status_code == 200:
                print("✓ Aplicación lista")
                break
        except:
            pass
        time.sleep(1)
        print(f"Esperando... ({i+1}/30)")
    else:
        print("✗ Timeout esperando aplicación")
        return False
    
    # Probar endpoint de ofertas
    print("\nProbando GET /api/v1/ofertas...")
    try:
        response = requests.get(f"{base_url}/api/v1/ofertas", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Endpoint funcionando correctamente")
            print(f"Total ofertas: {data.get('total', 0)}")
            
            if data.get('data'):
                print("\nPrimeras ofertas:")
                for oferta in data['data'][:3]:
                    print(f"  - ID: {oferta.get('id')}")
                    print(f"    Título: {oferta.get('titulo')}")
                    print(f"    Descuento: {oferta.get('descuento_porcentaje')}%")
                    print(f"    Activa: {oferta.get('activa')}")
                    print()
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Función principal"""
    print("INICIANDO Y PROBANDO ENDPOINT DE OFERTAS")
    print("=" * 60)
    
    # Iniciar aplicación
    process = iniciar_aplicacion()
    if not process:
        return False
    
    try:
        # Probar endpoint
        success = probar_endpoint_ofertas()
        
        if success:
            print("\n✓ ENDPOINT DE OFERTAS CORREGIDO Y FUNCIONANDO")
        else:
            print("\n✗ ENDPOINT AÚN TIENE PROBLEMAS")
        
        return success
        
    finally:
        # Terminar proceso
        if process:
            print("\nTerminando aplicación...")
            process.terminate()
            process.wait()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
