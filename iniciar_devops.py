#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio para DevOps
"""

import os
import sys
import subprocess
import time

def iniciar_devops():
    """Iniciar sistema DevOps"""
    print("INICIANDO SISTEMA DEVOPS")
    print("=" * 40)
    
    # Cargar configuración
    from configurar_devops import configurar_variables_entorno
    configurar_variables_entorno()
    
    # Iniciar servicios
    servicios = [
        ('Belgrano Ahorro', 'python app.py'),
        ('Ticketera', 'python app_tickets.py'),
        ('DevOps', 'python devops_routes.py'),
        ('API Gateway', 'python api_gateway.py'),
        ('Sync Manager', 'python sync_manager.py')
    ]
    
    procesos = []
    
    for nombre, comando in servicios:
        try:
            print(f"Iniciando {nombre}...")
            proceso = subprocess.Popen(comando, shell=True)
            procesos.append((nombre, proceso))
            time.sleep(2)
            print(f"✅ {nombre} iniciado")
        except Exception as e:
            print(f"❌ Error iniciando {nombre}: {e}")
    
    print("\nSistema DevOps iniciado correctamente")
    print("Presiona Ctrl+C para detener todos los servicios")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servicios...")
        for nombre, proceso in procesos:
            try:
                proceso.terminate()
                print(f"✅ {nombre} detenido")
            except:
                print(f"⚠️ Error deteniendo {nombre}")

if __name__ == "__main__":
    iniciar_devops()
