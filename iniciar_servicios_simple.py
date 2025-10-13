#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para iniciar servicios uno por uno
"""

import subprocess
import sys
import time
import os

def iniciar_belgrano_ahorro():
    """Iniciar Belgrano Ahorro en puerto 5000"""
    print("🚀 Iniciando Belgrano Ahorro en puerto 5000...")
    try:
        env = os.environ.copy()
        env['FLASK_PORT'] = '5000'
        env['FLASK_ENV'] = 'development'
        
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env
        )
        print(f"✅ Belgrano Ahorro iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def iniciar_ticketera():
    """Iniciar Ticketera en puerto 5001"""
    print("🚀 Iniciando Ticketera en puerto 5001...")
    try:
        env = os.environ.copy()
        env['FLASK_PORT'] = '5001'
        env['FLASK_ENV'] = 'development'
        env['TICKETERA_PORT'] = '5001'
        
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env=env
        )
        print(f"✅ Ticketera iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 50)
    print("🚀 INICIANDO SERVICIOS BELGRANO")
    print("=" * 50)
    
    # Iniciar Belgrano Ahorro
    proceso_ahorro = iniciar_belgrano_ahorro()
    if not proceso_ahorro:
        return
    
    time.sleep(3)
    
    # Iniciar Ticketera
    proceso_ticketera = iniciar_ticketera()
    if not proceso_ticketera:
        return
    
    print("\n" + "=" * 50)
    print("📊 SERVICIOS INICIADOS")
    print("=" * 50)
    print("🌐 Belgrano Ahorro: http://localhost:5000")
    print("🎫 Ticketera:      http://localhost:5001")
    print("🔧 DevOps:         http://localhost:5002 (dentro de Ticketera)")
    print("\n💡 Para detener, presiona Ctrl+C")
    print("=" * 50)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        if proceso_ahorro:
            proceso_ahorro.terminate()
        if proceso_ticketera:
            proceso_ticketera.terminate()
        print("✅ Servicios detenidos")

if __name__ == "__main__":
    main()
