#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar todos los servicios del sistema DevOps-Belgrano Ahorro
"""

import subprocess
import time
import sys
import os
import threading
from datetime import datetime

class ServiciosManager:
    def __init__(self):
        self.procesos = {}
        self.puertos = {
            'belgrano_ahorro': 5000,
            'ticketera': 5001,
            'devops': 5002
        }
        
    def iniciar_servicio(self, nombre, comando, puerto):
        """Iniciar un servicio en un hilo separado"""
        def ejecutar_servicio():
            try:
                print(f"🚀 Iniciando {nombre} en puerto {puerto}...")
                proceso = subprocess.Popen(
                    comando,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.procesos[nombre] = proceso
                print(f"✅ {nombre} iniciado (PID: {proceso.pid})")
                
                # Mantener el proceso vivo
                proceso.wait()
                
            except Exception as e:
                print(f"❌ Error iniciando {nombre}: {e}")
        
        hilo = threading.Thread(target=ejecutar_servicio, daemon=True)
        hilo.start()
        return hilo
    
    def iniciar_todos_servicios(self):
        """Iniciar todos los servicios del sistema"""
        print("🔧 INICIANDO SISTEMA COMPLETO DEVOPS-BELGRANO AHORRO")
        print("="*60)
        
        # Comandos para iniciar cada servicio
        comandos = {
            'belgrano_ahorro': 'python app.py',
            'ticketera': 'python app_tickets.py', 
            'devops': 'python devops_routes.py'
        }
        
        hilos = {}
        
        # Iniciar cada servicio
        for servicio, comando in comandos.items():
            puerto = self.puertos[servicio]
            hilo = self.iniciar_servicio(servicio, comando, puerto)
            hilos[servicio] = hilo
            time.sleep(2)  # Esperar entre servicios
        
        print(f"\n⏳ Esperando que los servicios se inicialicen...")
        time.sleep(10)  # Dar tiempo para que se inicialicen
        
        # Verificar que los servicios estén funcionando
        self.verificar_servicios()
        
        return hilos
    
    def verificar_servicios(self):
        """Verificar que todos los servicios estén funcionando"""
        print("\n🔍 VERIFICANDO SERVICIOS...")
        
        import requests
        
        for servicio, puerto in self.puertos.items():
            try:
                url = f"http://localhost:{puerto}"
                if servicio == 'devops':
                    url += '/devops/'
                elif servicio == 'ticketera':
                    url += '/'
                else:
                    url += '/'
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {servicio} (puerto {puerto}): FUNCIONANDO")
                else:
                    print(f"⚠️ {servicio} (puerto {puerto}): Respuesta {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"❌ {servicio} (puerto {puerto}): NO CONECTADO")
            except Exception as e:
                print(f"❌ {servicio} (puerto {puerto}): ERROR - {e}")
    
    def mostrar_urls(self):
        """Mostrar URLs de acceso"""
        print(f"\n🌐 URLs DE ACCESO:")
        print(f"   🛒 Belgrano Ahorro: http://localhost:5000")
        print(f"   🎫 Ticketera: http://localhost:5001")
        print(f"   🔧 DevOps: http://localhost:5002/devops/")
        
        print(f"\n🔐 CREDENCIALES:")
        print(f"   DevOps: devops / DevOps2025!Secure")
        print(f"   Ticketera Admin: admin@belgranoahorro.com / admin123")
        print(f"   Ticketera Flota: repartidor1@belgranoahorro.com / flota123")
    
    def detener_servicios(self):
        """Detener todos los servicios"""
        print("\n🛑 DETENIENDO SERVICIOS...")
        
        for nombre, proceso in self.procesos.items():
            try:
                proceso.terminate()
                print(f"✅ {nombre} detenido")
            except Exception as e:
                print(f"❌ Error deteniendo {nombre}: {e}")

def main():
    """Función principal"""
    manager = ServiciosManager()
    
    try:
        # Iniciar servicios
        hilos = manager.iniciar_todos_servicios()
        
        # Mostrar información
        manager.mostrar_urls()
        
        print(f"\n🎉 SISTEMA INICIADO CORRECTAMENTE")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n💡 Para detener los servicios, presiona Ctrl+C")
        
        # Mantener el script ejecutándose
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n🛑 Deteniendo servicios...")
            manager.detener_servicios()
            print(f"✅ Servicios detenidos")
            
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")
        manager.detener_servicios()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
