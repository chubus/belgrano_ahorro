#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANZADOR DE APLICACIONES PARA TESTING
Lanza las aplicaciones para que el usuario pueda testearlas
"""

import subprocess
import time
import os
import signal
import sys

class AppLauncher:
    """Lanzador de aplicaciones para testing"""
    
    def __init__(self):
        self.processes = {}
        
    def launch_app(self, app_file, app_name, port):
        """Lanzar una aplicación específica"""
        print(f"\n🚀 LANZANDO {app_name.upper()}...")
        print("=" * 50)
        
        try:
            # Configurar variables de entorno
            env = os.environ.copy()
            env['FLASK_ENV'] = 'development'
            env['SECRET_KEY'] = 'test_key_12345'
            env['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
            env['TICKETERA_API_KEY'] = 'ticketera_api_key_2025'
            
            # Lanzar aplicación
            process = subprocess.Popen([
                'python', app_file
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes[app_name] = {
                'process': process,
                'port': port,
                'file': app_file
            }
            
            print(f"✅ {app_name} iniciado (PID: {process.pid})")
            print(f"🌐 URL: http://localhost:{port}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error lanzando {app_name}: {e}")
            return False
    
    def launch_belgrano_ahorro(self):
        """Lanzar Belgrano Ahorro"""
        return self.launch_app('app.py', 'Belgrano Ahorro', 5000)
    
    def launch_ticketera(self):
        """Lanzar Ticketera"""
        return self.launch_app('app_tickets.py', 'Ticketera', 5001)
    
    def launch_devops(self):
        """Lanzar DevOps"""
        return self.launch_app('app_unificado.py', 'DevOps', 5002)
    
    def show_status(self):
        """Mostrar estado de las aplicaciones"""
        print("\n📊 ESTADO DE LAS APLICACIONES:")
        print("=" * 50)
        
        for app_name, info in self.processes.items():
            process = info['process']
            port = info['port']
            
            if process.poll() is None:
                print(f"✅ {app_name}: Ejecutándose en puerto {port}")
            else:
                print(f"❌ {app_name}: Detenido")
    
    def show_urls(self):
        """Mostrar URLs de acceso"""
        print("\n🌐 URLs DE ACCESO:")
        print("=" * 50)
        print("🏪 Belgrano Ahorro: http://localhost:5000/")
        print("🎫 Ticketera: http://localhost:5001/")
        print("⚙️ DevOps: http://localhost:5002/devops/")
        
        print("\n🔐 CREDENCIALES DEVOPS:")
        print("=" * 50)
        print("Usuario: devops")
        print("Contraseña: DevOps2025!Secure")
        
        print("\n🔍 ENDPOINTS DE API:")
        print("=" * 50)
        print("Health Check: http://localhost:5000/api/health")
        print("Status: http://localhost:5000/api/status")
        print("Productos: http://localhost:5000/api/productos")
        print("Categorías: http://localhost:5000/api/categorias")
        print("Negocios: http://localhost:5000/api/negocios")
    
    def show_testing_guide(self):
        """Mostrar guía de testing"""
        print("\n📋 GUÍA DE TESTING:")
        print("=" * 50)
        print("1. Acceder a DevOps: http://localhost:5002/devops/")
        print("   - Usuario: devops")
        print("   - Contraseña: DevOps2025!Secure")
        print("")
        print("2. Crear un producto desde DevOps")
        print("   - Ir a 'Gestión de Productos'")
        print("   - Crear nuevo producto")
        print("")
        print("3. Verificar en Belgrano Ahorro: http://localhost:5000/")
        print("   - Buscar el producto creado")
        print("   - Verificar que aparece en la lista")
        print("")
        print("4. Probar compra en Belgrano Ahorro")
        print("   - Agregar producto al carrito")
        print("   - Proceder al checkout")
        print("")
        print("5. Verificar ticket en Ticketera: http://localhost:5001/")
        print("   - Verificar que se generó el ticket")
        print("   - Revisar detalles del pedido")
    
    def stop_all(self):
        """Detener todas las aplicaciones"""
        print("\n⏹️ DETENIENDO APLICACIONES...")
        print("=" * 50)
        
        for app_name, info in self.processes.items():
            process = info['process']
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {app_name} detenido")
            except:
                try:
                    process.kill()
                    print(f"✅ {app_name} forzado a detener")
                except:
                    print(f"❌ No se pudo detener {app_name}")
        
        self.processes.clear()
        print("✅ Todas las aplicaciones detenidas")
    
    def run(self):
        """Ejecutar lanzador"""
        print("🚀 LANZADOR DE APLICACIONES PARA TESTING")
        print("=" * 60)
        print("Este script lanzará las aplicaciones para que puedas testearlas")
        print("Presiona Ctrl+C para detener todas las aplicaciones")
        print("=" * 60)
        
        try:
            # Lanzar aplicaciones
            apps_launched = 0
            
            if self.launch_belgrano_ahorro():
                apps_launched += 1
                time.sleep(2)  # Esperar entre lanzamientos
            
            if self.launch_ticketera():
                apps_launched += 1
                time.sleep(2)
            
            if self.launch_devops():
                apps_launched += 1
                time.sleep(2)
            
            print(f"\n📊 APLICACIONES LANZADAS: {apps_launched}/3")
            
            if apps_launched > 0:
                self.show_status()
                self.show_urls()
                self.show_testing_guide()
                
                print("\n⏳ Aplicaciones ejecutándose...")
                print("Presiona Ctrl+C para detener todas las aplicaciones")
                
                # Mantener aplicaciones ejecutándose
                while True:
                    time.sleep(1)
                    
                    # Verificar que las aplicaciones sigan funcionando
                    for app_name in list(self.processes.keys()):
                        if self.processes[app_name]['process'].poll() is not None:
                            print(f"⚠️ {app_name} se detuvo inesperadamente")
                            del self.processes[app_name]
                    
                    if not self.processes:
                        print("❌ Todas las aplicaciones se detuvieron")
                        break
                        
        except KeyboardInterrupt:
            print("\n🛑 Interrumpido por usuario")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
        finally:
            self.stop_all()

def main():
    """Función principal"""
    launcher = AppLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
