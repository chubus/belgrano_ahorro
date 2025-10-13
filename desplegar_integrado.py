#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de despliegue para servicios integrados
Belgrano Ahorro + Ticketera con DevOps integrado
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Configuración
PORT_BELGRANO = 5000
PORT_TICKETERA_DEVOPS = 5001

# Variables de entorno para producción
ENV_VARS = {
    'FLASK_ENV': 'production',
    'FLASK_DEBUG': 'False',
    'TICKETERA_URL': f'http://localhost:{PORT_TICKETERA_DEVOPS}',
    'BELGRANO_AHORRO_URL': f'http://localhost:{PORT_BELGRANO_AHORRO}',
    'DEVOPS_URL': f'http://localhost:{PORT_TICKETERA_DEVOPS}/devops',
    'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025'
}

class ServicioIntegrado:
    def __init__(self):
        self.procesos = {}
        self.running = False
    
    def iniciar_belgrano_ahorro(self):
        """Iniciar Belgrano Ahorro"""
        print(f"🌐 Iniciando Belgrano Ahorro en puerto {PORT_BELGRANO}...")
        
        env = os.environ.copy()
        env.update(ENV_VARS)
        env['FLASK_PORT'] = str(PORT_BELGRANO)
        
        try:
            proceso = subprocess.Popen(
                [sys.executable, 'app.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.procesos['belgrano'] = proceso
            print(f"✅ Belgrano Ahorro iniciado (PID: {proceso.pid})")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def iniciar_ticketera_devops(self):
        """Iniciar Ticketera con DevOps integrado"""
        print(f"🎫 Iniciando Ticketera + DevOps en puerto {PORT_TICKETERA_DEVOPS}...")
        
        env = os.environ.copy()
        env.update(ENV_VARS)
        env['FLASK_PORT'] = str(PORT_TICKETERA_DEVOPS)
        env['TICKETERA_PORT'] = str(PORT_TICKETERA_DEVOPS)
        
        try:
            proceso = subprocess.Popen(
                [sys.executable, 'belgrano_tickets/app.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.procesos['ticketera'] = proceso
            print(f"✅ Ticketera + DevOps iniciado (PID: {proceso.pid})")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def verificar_servicios(self):
        """Verificar que los servicios estén funcionando"""
        import requests
        import time
        
        print("\n🔍 Verificando servicios...")
        time.sleep(5)
        
        servicios = [
            ("Belgrano Ahorro", f"http://localhost:{PORT_BELGRANO}"),
            ("Ticketera", f"http://localhost:{PORT_TICKETERA_DEVOPS}"),
            ("DevOps", f"http://localhost:{PORT_TICKETERA_DEVOPS}/devops")
        ]
        
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {nombre}: Funcionando")
                else:
                    print(f"⚠️ {nombre}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {nombre}: {e}")
    
    def iniciar_todos(self):
        """Iniciar todos los servicios"""
        print("=" * 60)
        print("🚀 DESPLEGANDO SERVICIOS INTEGRADOS")
        print("=" * 60)
        
        # Iniciar Belgrano Ahorro
        if not self.iniciar_belgrano_ahorro():
            print("❌ No se pudo iniciar Belgrano Ahorro")
            return False
        
        time.sleep(3)
        
        # Iniciar Ticketera + DevOps
        if not self.iniciar_ticketera_devops():
            print("❌ No se pudo iniciar Ticketera + DevOps")
            self.detener_todos()
            return False
        
        self.running = True
        self.verificar_servicios()
        
        print("\n" + "=" * 60)
        print("📊 SERVICIOS INTEGRADOS INICIADOS")
        print("=" * 60)
        print(f"🌐 Belgrano Ahorro: http://localhost:{PORT_BELGRANO}")
        print(f"🎫 Ticketera:      http://localhost:{PORT_TICKETERA_DEVOPS}")
        print(f"🔧 DevOps:         http://localhost:{PORT_TICKETERA_DEVOPS}/devops")
        print("\n💡 Para detener, presiona Ctrl+C")
        print("=" * 60)
        
        return True
    
    def detener_todos(self):
        """Detener todos los servicios"""
        print("\n🛑 Deteniendo servicios...")
        for nombre, proceso in self.procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                print(f"✅ {nombre} detenido")
        self.running = False
        print("✅ Todos los servicios detenidos")
    
    def monitorear(self):
        """Monitorear servicios"""
        try:
            while self.running:
                time.sleep(1)
                # Verificar si algún proceso se cerró
                for nombre, proceso in self.procesos.items():
                    if proceso and proceso.poll() is not None:
                        print(f"⚠️ {nombre} se cerró inesperadamente")
                        self.running = False
                        break
        except KeyboardInterrupt:
            self.detener_todos()

def main():
    servicio = ServicioIntegrado()
    
    # Configurar manejo de señales
    def signal_handler(signum, frame):
        print("\n🛑 Señal de interrupción recibida")
        servicio.detener_todos()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar servicios
    if servicio.iniciar_todos():
        servicio.monitorear()
    else:
        print("❌ No se pudieron iniciar los servicios")
        sys.exit(1)

if __name__ == "__main__":
    main()
