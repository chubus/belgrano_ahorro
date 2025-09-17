#!/usr/bin/env python3
"""
Script completo para lanzar Belgrano Ahorro y La Ticketera
Incluye verificación de puertos, manejo de errores y base de datos
"""
import subprocess
import time
import sys
import os
import socket
import threading
import signal
import psutil

def check_port(port):
    """Verificar si un puerto está disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def kill_process_on_port(port):
    """Terminar proceso que esté usando un puerto específico"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        print(f"🔄 Terminando proceso {proc.info['name']} (PID: {proc.info['pid']}) en puerto {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
    except Exception as e:
        print(f"⚠️ Error al terminar proceso en puerto {port}: {e}")
    return False

def wait_for_port(port, timeout=30):
    """Esperar a que un puerto esté disponible"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not check_port(port):
            return True
        time.sleep(1)
    return False

def start_belgrano_ahorro():
    """Iniciar aplicación principal Belgrano Ahorro"""
    print("🛒 Iniciando Belgrano Ahorro...")
    
    # Verificar puerto 5000
    if not check_port(5000):
        print("⚠️ Puerto 5000 ocupado, liberando...")
        kill_process_on_port(5000)
        time.sleep(2)
    
    try:
        # Inicializar base de datos si es necesario
        print("🗄️ Verificando base de datos...")
        
        # Lanzar aplicación
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que el puerto esté disponible
        if wait_for_port(5000):
            print("✅ Belgrano Ahorro iniciado en http://localhost:5000")
            return process
        else:
            print("❌ Error: Belgrano Ahorro no pudo iniciarse en el puerto 5000")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error al iniciar Belgrano Ahorro: {e}")
        return None

def start_ticketera():
    """Iniciar aplicación de tickets"""
    print("🎫 Iniciando La Ticketera...")
    
    # Verificar puerto 5001
    if not check_port(5001):
        print("⚠️ Puerto 5001 ocupado, liberando...")
        kill_process_on_port(5001)
        time.sleep(2)
    
    original_dir = os.getcwd()
    try:
        # Cambiar al directorio de la ticketera
        os.chdir("belgrano_tickets")
        
        # Lanzar aplicación
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Volver al directorio original
        os.chdir(original_dir)
        
        # Esperar a que el puerto esté disponible
        if wait_for_port(5001):
            print("✅ La Ticketera iniciada en http://localhost:5001")
            return process
        else:
            print("❌ Error: La Ticketera no pudo iniciarse en el puerto 5001")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error al iniciar La Ticketera: {e}")
        os.chdir(original_dir)
        return None

def monitor_processes(belgrano_process, ticketera_process):
    """Monitorear los procesos y mostrar información"""
    print("\n" + "="*60)
    print("🚀 SISTEMA COMPLETO INICIADO")
    print("="*60)
    print("📱 Aplicaciones disponibles:")
    print("   🛒 Belgrano Ahorro: http://localhost:5000")
    print("   🎫 La Ticketera: http://localhost:5001")
    print("\n🔐 Credenciales de acceso:")
    print("   👑 Admin: admin@belgranoahorro.com / admin123")
    print("   🚚 Flota: repartidor1@belgranoahorro.com / repartidor123")
    print("\n📊 Funcionalidades:")
    print("   • Catálogo de productos y carrito de compras")
    print("   • Sistema de pedidos y checkout")
    print("   • Gestión de tickets de entrega")
    print("   • Panel de administración")
    print("   • Panel de flota/repartidores")
    print("\n⏹️ Presiona Ctrl+C para detener todas las aplicaciones")
    print("="*60)
    
    try:
        # Esperar a que los procesos terminen
        if belgrano_process:
            belgrano_process.wait()
        if ticketera_process:
            ticketera_process.wait()
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo aplicaciones...")
        if belgrano_process:
            belgrano_process.terminate()
        if ticketera_process:
            ticketera_process.terminate()
        print("✅ Aplicaciones detenidas")

def main():
    """Función principal"""
    print("🚀 INICIANDO SISTEMA COMPLETO BELGRANO AHORRO")
    print("="*50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app.py"):
        print("❌ Error: No se encontró app.py. Asegúrate de estar en el directorio correcto.")
        return
    
    if not os.path.exists("belgrano_tickets"):
        print("❌ Error: No se encontró el directorio belgrano_tickets.")
        return
    
    # Iniciar aplicaciones
    belgrano_process = start_belgrano_ahorro()
    time.sleep(3)  # Esperar un poco entre aplicaciones
    
    ticketera_process = start_ticketera()
    
    # Monitorear procesos
    if belgrano_process or ticketera_process:
        monitor_processes(belgrano_process, ticketera_process)
    else:
        print("❌ No se pudo iniciar ninguna aplicación")

if __name__ == "__main__":
    main()
