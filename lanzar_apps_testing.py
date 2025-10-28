#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANZADOR SIMPLE DE APLICACIONES
Lanza cada aplicación por separado para testing
"""

import subprocess
import time
import os

def launch_belgrano_ahorro():
    """Lanzar Belgrano Ahorro"""
    print("🚀 LANZANDO BELGRANO AHORRO...")
    print("=" * 50)
    
    try:
        # Configurar entorno
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['SECRET_KEY'] = 'test_key_12345'
        env['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        
        # Lanzar aplicación
        process = subprocess.Popen([
            'python', 'app.py'
        ], env=env)
        
        print(f"✅ Belgrano Ahorro iniciado (PID: {process.pid})")
        print("🌐 URL: http://localhost:5000/")
        print("🔍 Endpoints de API:")
        print("   - Health: http://localhost:5000/api/health")
        print("   - Status: http://localhost:5000/api/status")
        print("   - Productos: http://localhost:5000/api/productos")
        print("   - Categorías: http://localhost:5000/api/categorias")
        print("   - Negocios: http://localhost:5000/api/negocios")
        
        return process
        
    except Exception as e:
        print(f"❌ Error lanzando Belgrano Ahorro: {e}")
        return None

def launch_ticketera():
    """Lanzar Ticketera"""
    print("\n🚀 LANZANDO TICKETERA...")
    print("=" * 50)
    
    try:
        # Configurar entorno
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['SECRET_KEY'] = 'test_key_12345'
        env['TICKETERA_API_KEY'] = 'ticketera_api_key_2025'
        
        # Lanzar aplicación
        process = subprocess.Popen([
            'python', 'app_tickets.py'
        ], env=env)
        
        print(f"✅ Ticketera iniciado (PID: {process.pid})")
        print("🌐 URL: http://localhost:5001/")
        
        return process
        
    except Exception as e:
        print(f"❌ Error lanzando Ticketera: {e}")
        return None

def launch_devops():
    """Lanzar DevOps"""
    print("\n🚀 LANZANDO DEVOPS...")
    print("=" * 50)
    
    try:
        # Configurar entorno
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['SECRET_KEY'] = 'test_key_12345'
        env['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
        
        # Lanzar aplicación
        process = subprocess.Popen([
            'python', 'app_unificado.py'
        ], env=env)
        
        print(f"✅ DevOps iniciado (PID: {process.pid})")
        print("🌐 URL: http://localhost:5002/devops/")
        print("🔐 Credenciales:")
        print("   Usuario: devops")
        print("   Contraseña: DevOps2025!Secure")
        
        return process
        
    except Exception as e:
        print(f"❌ Error lanzando DevOps: {e}")
        return None

def main():
    """Función principal"""
    print("🚀 LANZADOR DE APLICACIONES PARA TESTING")
    print("=" * 60)
    print("Este script lanzará las aplicaciones para que puedas testearlas")
    print("Presiona Ctrl+C para detener todas las aplicaciones")
    print("=" * 60)
    
    processes = []
    
    try:
        # Lanzar aplicaciones
        print("\n📋 LANZANDO APLICACIONES...")
        
        # Belgrano Ahorro
        belgrano_process = launch_belgrano_ahorro()
        if belgrano_process:
            processes.append(('Belgrano Ahorro', belgrano_process))
            time.sleep(3)
        
        # Ticketera
        ticketera_process = launch_ticketera()
        if ticketera_process:
            processes.append(('Ticketera', ticketera_process))
            time.sleep(3)
        
        # DevOps
        devops_process = launch_devops()
        if devops_process:
            processes.append(('DevOps', devops_process))
            time.sleep(3)
        
        print(f"\n📊 APLICACIONES LANZADAS: {len(processes)}/3")
        
        if processes:
            print("\n🌐 URLs DE ACCESO:")
            print("=" * 50)
            print("🏪 Belgrano Ahorro: http://localhost:5000/")
            print("🎫 Ticketera: http://localhost:5001/")
            print("⚙️ DevOps: http://localhost:5002/devops/")
            
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
            
            print("\n⏳ Aplicaciones ejecutándose...")
            print("Presiona Ctrl+C para detener todas las aplicaciones")
            
            # Mantener aplicaciones ejecutándose
            while True:
                time.sleep(1)
                
                # Verificar que las aplicaciones sigan funcionando
                for app_name, process in processes[:]:
                    if process.poll() is not None:
                        print(f"⚠️ {app_name} se detuvo inesperadamente")
                        processes.remove((app_name, process))
                
                if not processes:
                    print("❌ Todas las aplicaciones se detuvieron")
                    break
        else:
            print("❌ No se pudo lanzar ninguna aplicación")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        # Detener todas las aplicaciones
        print("\n⏹️ DETENIENDO APLICACIONES...")
        for app_name, process in processes:
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
        
        print("✅ Todas las aplicaciones detenidas")

if __name__ == "__main__":
    main()

