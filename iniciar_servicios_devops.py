#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar todos los servicios DevOps
"""

import os
import sys
import subprocess
import time
import signal
import threading
from datetime import datetime

class DevOpsServiceManager:
    def __init__(self):
        self.services = {}
        self.running = True
        
    def start_service(self, name, command, port, delay=2):
        """Iniciar un servicio"""
        try:
            print(f"Iniciando {name} en puerto {port}...")
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.services[name] = {
                'process': process,
                'command': command,
                'port': port,
                'started_at': datetime.now()
            }
            
            time.sleep(delay)
            
            # Verificar si el proceso está ejecutándose
            if process.poll() is None:
                print(f"✅ {name} iniciado correctamente")
                return True
            else:
                print(f"❌ {name} falló al iniciar")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando {name}: {e}")
            return False
    
    def stop_service(self, name):
        """Detener un servicio"""
        if name in self.services:
            try:
                process = self.services[name]['process']
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} detenido")
                del self.services[name]
            except Exception as e:
                print(f"❌ Error deteniendo {name}: {e}")
    
    def stop_all_services(self):
        """Detener todos los servicios"""
        print("\nDeteniendo todos los servicios...")
        for name in list(self.services.keys()):
            self.stop_service(name)
    
    def check_service_status(self, name, port):
        """Verificar estado de un servicio"""
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def monitor_services(self):
        """Monitorear servicios en segundo plano"""
        while self.running:
            try:
                for name, service_info in self.services.items():
                    if service_info['process'].poll() is not None:
                        print(f"⚠️ {name} se detuvo inesperadamente")
                        # Intentar reiniciar
                        self.start_service(
                            name, 
                            service_info['command'], 
                            service_info['port']
                        )
                time.sleep(10)
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                break
    
    def start_all_services(self):
        """Iniciar todos los servicios DevOps"""
        print("🚀 INICIANDO SERVICIOS DEVOPS")
        print("=" * 50)
        
        # Configurar variables de entorno
        os.environ['DEVOPS_USERNAME'] = 'devops'
        os.environ['DEVOPS_PASSWORD'] = 'DevOps2025!Secure'
        os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
        os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        os.environ['GATEWAY_URL'] = 'http://localhost:5003/gateway'
        os.environ['GATEWAY_API_KEY'] = 'devops_api_key_2025'
        os.environ['TICKETERA_URL'] = 'http://localhost:5001'
        os.environ['TICKETERA_API_KEY'] = 'ticketera_api_key_2025'
        os.environ['SECRET_KEY'] = 'devops_secret_key_2025'
        
        # Definir servicios
        services_config = [
            ('Belgrano Ahorro', 'python app.py', 5000),
            ('Ticketera', 'python app_tickets.py', 5001),
            ('DevOps', 'python devops_routes.py', 5002),
            ('API Gateway', 'python api_gateway.py', 5003),
            ('Sistema Sync', 'python sync_manager.py', 5004)
        ]
        
        services_started = 0
        
        for name, command, port in services_config:
            if self.start_service(name, command, port):
                services_started += 1
        
        print(f"\nServicios iniciados: {services_started}/{len(services_config)}")
        
        if services_started > 0:
            print("\n🌐 URLs DE ACCESO:")
            print("=" * 30)
            print("Belgrano Ahorro: http://localhost:5000/")
            print("Ticketera: http://localhost:5001/")
            print("DevOps: http://localhost:5002/devops/")
            print("API Gateway: http://localhost:5003/gateway/")
            print("Sistema Sync: http://localhost:5004/sync/")
            print("\n🔐 CREDENCIALES DEVOPS:")
            print("Usuario: devops")
            print("Contraseña: DevOps2025!Secure")
            print("\n📝 Presiona Ctrl+C para detener todos los servicios")
            
            # Iniciar monitoreo en segundo plano
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⏹️ Deteniendo servicios...")
                self.running = False
                self.stop_all_services()
                print("✅ Todos los servicios detenidos")
        else:
            print("❌ No se pudo iniciar ningún servicio")
            return False
        
        return True

def main():
    """Función principal"""
    manager = DevOpsServiceManager()
    
    # Manejar señales para detener servicios
    def signal_handler(sig, frame):
        print("\n⏹️ Recibida señal de interrupción")
        manager.running = False
        manager.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return manager.start_all_services()

if __name__ == "__main__":
    main()

