#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar toda la arquitectura completa
Belgrano Ahorro + Ticketera + API Gateway + Sistema de Sincronización
"""

import os
import sys
import subprocess
import time
import signal
import threading
from datetime import datetime

class ArquitecturaCompleta:
    """Gestor para iniciar toda la arquitectura"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # Configuración de puertos
        self.ports = {
            'belgrano_ahorro': 5000,
            'ticketera': 5001,
            'devops': 5002,
            'api_gateway': 5003,
            'sync_manager': 5004
        }
        
        # Configuración de archivos
        self.files = {
            'belgrano_ahorro': 'app.py',
            'ticketera': 'app_tickets.py',
            'devops': 'devops_routes.py',
            'api_gateway': 'api_gateway.py',
            'sync_manager': 'sync_manager.py'
        }
        
        # Configuración de variables de entorno
        self.env_vars = {
            'BELGRANO_AHORRO_URL': 'https://belgranoahorro-aliq.onrender.com',
            'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025',
            'TICKETERA_API_KEY': 'ticketera_api_key_2025',
            'GATEWAY_API_KEY': 'devops_api_key_2025',
            'API_TIMEOUT': '30',
            'API_RETRY_ATTEMPTS': '3',
            'API_RETRY_DELAY': '1',
            'CACHE_TTL': '300',
            'SYNC_INTERVAL': '60'
        }
    
    def setup_environment(self):
        """Configurar variables de entorno"""
        print("🔧 Configurando variables de entorno...")
        
        for key, value in self.env_vars.items():
            os.environ[key] = value
            print(f"   {key} = {value}")
    
    def start_service(self, name, file, port):
        """Iniciar un servicio específico"""
        try:
            print(f"🚀 Iniciando {name} en puerto {port}...")
            
            # Comando para iniciar el servicio
            cmd = [sys.executable, file]
            
            # Iniciar proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[name] = process
            
            # Esperar un poco para que inicie
            time.sleep(2)
            
            # Verificar si está corriendo
            if process.poll() is None:
                print(f"✅ {name} iniciado correctamente (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Error iniciando {name}: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando {name}: {e}")
            return False
    
    def start_all_services(self):
        """Iniciar todos los servicios"""
        print("🏗️ INICIANDO ARQUITECTURA COMPLETA")
        print("=" * 60)
        
        # Configurar entorno
        self.setup_environment()
        
        # Iniciar servicios en orden
        services_order = [
            ('belgrano_ahorro', 'Belgrano Ahorro'),
            ('ticketera', 'Ticketera'),
            ('devops', 'DevOps'),
            ('api_gateway', 'API Gateway'),
            ('sync_manager', 'Sistema de Sincronización')
        ]
        
        started_services = []
        
        for service, display_name in services_order:
            if service in self.files and service in self.ports:
                file = self.files[service]
                port = self.ports[service]
                
                # Verificar que el archivo existe
                if not os.path.exists(file):
                    print(f"⚠️ Archivo {file} no encontrado, saltando {display_name}")
                    continue
                
                if self.start_service(display_name, file, port):
                    started_services.append(display_name)
                else:
                    print(f"❌ No se pudo iniciar {display_name}")
        
        print(f"\n✅ Servicios iniciados: {len(started_services)}/{len(services_order)}")
        for service in started_services:
            print(f"   • {service}")
        
        return started_services
    
    def monitor_services(self):
        """Monitorear servicios"""
        print("\n📊 Monitoreando servicios...")
        print("Presiona Ctrl+C para detener todos los servicios")
        
        try:
            while self.running:
                time.sleep(5)
                
                # Verificar estado de cada proceso
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        print(f"⚠️ {name} se detuvo inesperadamente")
                        stdout, stderr = process.communicate()
                        if stderr:
                            print(f"   Error: {stderr}")
                
        except KeyboardInterrupt:
            print("\n⏹️ Deteniendo todos los servicios...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """Detener todos los servicios"""
        print("🛑 Deteniendo servicios...")
        
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    print(f"   Deteniendo {name}...")
                    process.terminate()
                    
                    # Esperar a que termine
                    try:
                        process.wait(timeout=5)
                        print(f"   ✅ {name} detenido")
                    except subprocess.TimeoutExpired:
                        print(f"   ⚠️ {name} no respondió, forzando cierre...")
                        process.kill()
                        process.wait()
                        print(f"   ✅ {name} forzado a cerrar")
                        
            except Exception as e:
                print(f"   ❌ Error deteniendo {name}: {e}")
        
        print("✅ Todos los servicios detenidos")
    
    def show_status(self):
        """Mostrar estado de los servicios"""
        print("\n📊 ESTADO DE SERVICIOS")
        print("=" * 40)
        
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"✅ {name}: Ejecutándose (PID: {process.pid})")
            else:
                print(f"❌ {name}: Detenido")
    
    def show_urls(self):
        """Mostrar URLs de acceso"""
        print("\n🌐 URLs DE ACCESO")
        print("=" * 40)
        print("Belgrano Ahorro:     http://localhost:5000/")
        print("Ticketera:          http://localhost:5001/")
        print("DevOps:             http://localhost:5002/devops/")
        print("API Gateway:        http://localhost:5003/gateway/")
        print("Sistema Sync:       http://localhost:5004/sync/")
        print("\n🔐 CREDENCIALES")
        print("=" * 40)
        print("DevOps Login:       devops / DevOps2025!Secure")
        print("API Key Belgrano:   belgrano_ahorro_api_key_2025")
        print("API Key Gateway:    devops_api_key_2025")
        print("API Key Ticketera:  ticketera_api_key_2025")
    
    def run(self):
        """Ejecutar la arquitectura completa"""
        try:
            # Iniciar servicios
            started_services = self.start_all_services()
            
            if not started_services:
                print("❌ No se pudo iniciar ningún servicio")
                return False
            
            # Mostrar información
            self.show_urls()
            self.show_status()
            
            # Configurar manejador de señales
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Monitorear servicios
            self.monitor_services()
            
        except Exception as e:
            print(f"❌ Error en arquitectura: {e}")
            self.stop_all_services()
            return False
        
        return True
    
    def signal_handler(self, signum, frame):
        """Manejador de señales para detener servicios"""
        print(f"\n📡 Señal {signum} recibida")
        self.running = False
        self.stop_all_services()
        sys.exit(0)

def main():
    """Función principal"""
    print("🏗️ ARQUITECTURA COMPLETA BELGRANO AHORRO + TICKETERA")
    print("=" * 60)
    print("Iniciando todos los servicios...")
    print("")
    
    # Crear instancia del gestor
    arquitectura = ArquitecturaCompleta()
    
    # Ejecutar
    success = arquitectura.run()
    
    if success:
        print("\n✅ Arquitectura ejecutada correctamente")
    else:
        print("\n❌ Error en la ejecución de la arquitectura")
        sys.exit(1)

if __name__ == "__main__":
    main()
