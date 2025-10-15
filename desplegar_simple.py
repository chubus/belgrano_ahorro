#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de despliegue simple para servicios integrados
Funciona sin problemas de conectividad
"""

import os
import sys
import subprocess
import time
import signal

def iniciar_servicio(nombre, archivo, puerto, env_vars=None):
    """Iniciar un servicio de forma simple"""
    print(f"Iniciando {nombre} en puerto {puerto}...")
    
    env = os.environ.copy()
    env.update({
        'FLASK_PORT': str(puerto),
        'FLASK_ENV': 'development',
        'PYTHONIOENCODING': 'utf-8'
    })
    if env_vars:
        env.update(env_vars)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, archivo],
            env=env
        )
        print(f"OK: {nombre} iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    print("=" * 50)
    print("DESPLEGANDO SERVICIOS INTEGRADOS")
    print("=" * 50)
    
    procesos = []
    
    try:
        # Iniciar Belgrano Ahorro
        proceso_ahorro = iniciar_servicio(
            "Belgrano Ahorro", "app.py", 5000
        )
        if proceso_ahorro:
            procesos.append(proceso_ahorro)
        
        time.sleep(5)
        
        # Iniciar Ticketera + DevOps
        proceso_ticketera = iniciar_servicio(
            "Ticketera + DevOps", "belgrano_tickets/app.py", 5001
        )
        if proceso_ticketera:
            procesos.append(proceso_ticketera)
        
        print("\n" + "=" * 50)
        print("SERVICIOS INICIADOS")
        print("=" * 50)
        print("Belgrano Ahorro: http://localhost:5000")
        print("Ticketera:      http://localhost:5001")
        print("DevOps:         http://localhost:5001/devops")
        print("\nPara detener, presiona Ctrl+C")
        print("=" * 50)
        
        # Mantener corriendo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo servicios...")
            for proceso in procesos:
                if proceso:
                    proceso.terminate()
                    proceso.wait()
            print("Servicios detenidos")
    
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        for proceso in procesos:
            if proceso:
                proceso.terminate()
                proceso.wait()

if __name__ == "__main__":
    main()
