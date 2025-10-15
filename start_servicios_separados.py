#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar todos los servicios en puertos separados
Evita conflictos entre Belgrano Ahorro, Ticketera y DevOps
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

# Configuración de puertos
SERVICIOS = {
    'belgrano_ahorro': {
        'puerto': 5000,
        'archivo': 'app.py',
        'descripcion': 'Belgrano Ahorro - Aplicación principal'
    },
    'ticketera': {
        'puerto': 5001,
        'archivo': 'belgrano_tickets/app.py',
        'descripcion': 'Ticketera - Sistema de tickets'
    },
    'devops': {
        'puerto': 5002,
        'archivo': 'belgrano_tickets/app.py',
        'descripcion': 'DevOps - Panel de administración'
    }
}

def iniciar_servicio(nombre, config):
    """Iniciar un servicio en su puerto específico"""
    puerto = config['puerto']
    archivo = config['archivo']
    descripcion = config['descripcion']
    
    print(f"🚀 Iniciando {nombre} en puerto {puerto}...")
    print(f"   📁 Archivo: {archivo}")
    print(f"   📝 Descripción: {descripcion}")
    
    # Variables de entorno específicas para cada servicio
    env = os.environ.copy()
    env['FLASK_PORT'] = str(puerto)
    env['FLASK_ENV'] = 'development'
    
    # Configuraciones específicas por servicio
    if nombre == 'belgrano_ahorro':
        env['FLASK_APP'] = 'app.py'
        env['DATABASE_URL'] = 'sqlite:///belgrano_ahorro.db'
    elif nombre == 'ticketera':
        env['FLASK_APP'] = 'belgrano_tickets/app.py'
        env['TICKETS_DB_PATH'] = 'belgrano_tickets.db'
        env['TICKETERA_PORT'] = str(puerto)
    elif nombre == 'devops':
        env['FLASK_APP'] = 'belgrano_tickets/app.py'
        env['DEVOPS_PORT'] = str(puerto)
        env['DEVOPS_MODE'] = 'true'
    
    try:
        # Ejecutar el servicio
        proceso = subprocess.Popen(
            [sys.executable, archivo],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ {nombre} iniciado en puerto {puerto} (PID: {proceso.pid})")
        return proceso
        
    except Exception as e:
        print(f"❌ Error iniciando {nombre}: {e}")
        return None

def verificar_puerto(puerto):
    """Verificar si un puerto está disponible"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', puerto))
            return True
    except OSError:
        return False

def main():
    """Función principal para iniciar todos los servicios"""
    print("=" * 60)
    print("🚀 INICIANDO SERVICIOS BELGRANO AHORRO")
    print("=" * 60)
    print()
    
    # Verificar que los archivos existen
    for nombre, config in SERVICIOS.items():
        archivo = config['archivo']
        if not os.path.exists(archivo):
            print(f"❌ Error: No se encuentra {archivo}")
            return False
    
    # Verificar puertos disponibles
    for nombre, config in SERVICIOS.items():
        puerto = config['puerto']
        if not verificar_puerto(puerto):
            print(f"❌ Error: Puerto {puerto} no disponible para {nombre}")
            return False
    
    print("✅ Todos los puertos están disponibles")
    print()
    
    # Iniciar servicios
    procesos = {}
    hilos = []
    
    for nombre, config in SERVICIOS.items():
        # Crear hilo para cada servicio
        hilo = threading.Thread(
            target=lambda n=nombre, c=config: iniciar_servicio(n, c),
            daemon=True
        )
        hilo.start()
        hilos.append(hilo)
        time.sleep(2)  # Esperar entre servicios
    
    print()
    print("=" * 60)
    print("📊 SERVICIOS INICIADOS")
    print("=" * 60)
    print("🌐 Belgrano Ahorro: http://localhost:5000")
    print("🎫 Ticketera:      http://localhost:5001")
    print("🔧 DevOps:         http://localhost:5002")
    print()
    print("💡 Para detener todos los servicios, presiona Ctrl+C")
    print("=" * 60)
    
    try:
        # Mantener el script corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        for proceso in procesos.values():
            if proceso:
                proceso.terminate()
        print("✅ Servicios detenidos")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Script para iniciar todos los servicios en puertos separados
Evita conflictos entre Belgrano Ahorro, Ticketera y DevOps
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

# Configuración de puertos
SERVICIOS = {
    'belgrano_ahorro': {
        'puerto': 5000,
        'archivo': 'app.py',
        'descripcion': 'Belgrano Ahorro - Aplicación principal'
    },
    'ticketera': {
        'puerto': 5001,
        'archivo': 'belgrano_tickets/app.py',
        'descripcion': 'Ticketera - Sistema de tickets'
    },
    'devops': {
        'puerto': 5002,
        'archivo': 'belgrano_tickets/app.py',
        'descripcion': 'DevOps - Panel de administración'
    }
}

def iniciar_servicio(nombre, config):
    """Iniciar un servicio en su puerto específico"""
    puerto = config['puerto']
    archivo = config['archivo']
    descripcion = config['descripcion']
    
    print(f"🚀 Iniciando {nombre} en puerto {puerto}...")
    print(f"   📁 Archivo: {archivo}")
    print(f"   📝 Descripción: {descripcion}")
    
    # Variables de entorno específicas para cada servicio
    env = os.environ.copy()
    env['FLASK_PORT'] = str(puerto)
    env['FLASK_ENV'] = 'development'
    
    # Configuraciones específicas por servicio
    if nombre == 'belgrano_ahorro':
        env['FLASK_APP'] = 'app.py'
        env['DATABASE_URL'] = 'sqlite:///belgrano_ahorro.db'
    elif nombre == 'ticketera':
        env['FLASK_APP'] = 'belgrano_tickets/app.py'
        env['TICKETS_DB_PATH'] = 'belgrano_tickets.db'
        env['TICKETERA_PORT'] = str(puerto)
    elif nombre == 'devops':
        env['FLASK_APP'] = 'belgrano_tickets/app.py'
        env['DEVOPS_PORT'] = str(puerto)
        env['DEVOPS_MODE'] = 'true'
    
    try:
        # Ejecutar el servicio
        proceso = subprocess.Popen(
            [sys.executable, archivo],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ {nombre} iniciado en puerto {puerto} (PID: {proceso.pid})")
        return proceso
        
    except Exception as e:
        print(f"❌ Error iniciando {nombre}: {e}")
        return None

def verificar_puerto(puerto):
    """Verificar si un puerto está disponible"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', puerto))
            return True
    except OSError:
        return False

def main():
    """Función principal para iniciar todos los servicios"""
    print("=" * 60)
    print("🚀 INICIANDO SERVICIOS BELGRANO AHORRO")
    print("=" * 60)
    print()
    
    # Verificar que los archivos existen
    for nombre, config in SERVICIOS.items():
        archivo = config['archivo']
        if not os.path.exists(archivo):
            print(f"❌ Error: No se encuentra {archivo}")
            return False
    
    # Verificar puertos disponibles
    for nombre, config in SERVICIOS.items():
        puerto = config['puerto']
        if not verificar_puerto(puerto):
            print(f"❌ Error: Puerto {puerto} no disponible para {nombre}")
            return False
    
    print("✅ Todos los puertos están disponibles")
    print()
    
    # Iniciar servicios
    procesos = {}
    hilos = []
    
    for nombre, config in SERVICIOS.items():
        # Crear hilo para cada servicio
        hilo = threading.Thread(
            target=lambda n=nombre, c=config: iniciar_servicio(n, c),
            daemon=True
        )
        hilo.start()
        hilos.append(hilo)
        time.sleep(2)  # Esperar entre servicios
    
    print()
    print("=" * 60)
    print("📊 SERVICIOS INICIADOS")
    print("=" * 60)
    print("🌐 Belgrano Ahorro: http://localhost:5000")
    print("🎫 Ticketera:      http://localhost:5001")
    print("🔧 DevOps:         http://localhost:5002")
    print()
    print("💡 Para detener todos los servicios, presiona Ctrl+C")
    print("=" * 60)
    
    try:
        # Mantener el script corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        for proceso in procesos.values():
            if proceso:
                proceso.terminate()
        print("✅ Servicios detenidos")

if __name__ == "__main__":
    main()


