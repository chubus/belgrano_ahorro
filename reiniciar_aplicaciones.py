#!/usr/bin/env python3
"""
Script para reiniciar las aplicaciones con las correcciones aplicadas
"""
import subprocess
import time
import sys
import os
import signal
import psutil

def kill_processes_on_ports():
    """Terminar procesos en los puertos 5000, 5001, 5002"""
    ports = [5000, 5001, 5002]
    for port in ports:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections']:
                        if conn.laddr.port == port:
                            print(f"🔄 Terminando proceso en puerto {port}")
                            proc.terminate()
                            proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
        except Exception as e:
            print(f"⚠️ Error al terminar procesos en puerto {port}: {e}")

def start_belgrano_ahorro():
    """Iniciar Belgrano Ahorro"""
    print("🛒 Iniciando Belgrano Ahorro...")
    try:
        process = subprocess.Popen([sys.executable, "app_unificado.py"])
        print("✅ Belgrano Ahorro iniciado en puerto 5000")
        return process
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def start_ticketera():
    """Iniciar Ticketera"""
    print("🎫 Iniciando Ticketera...")
    try:
        process = subprocess.Popen([sys.executable, "app_tickets.py"])
        print("✅ Ticketera iniciada en puerto 5001")
        return process
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def start_devops():
    """Iniciar DevOps"""
    print("🔧 Iniciando DevOps...")
    try:
        process = subprocess.Popen([sys.executable, "start_devops.py"])
        print("✅ DevOps iniciado en puerto 5002")
        return process
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🔄 REINICIANDO APLICACIONES CON CORRECCIONES")
    print("=" * 50)
    
    # 1. Terminar procesos existentes
    print("🛑 Terminando procesos existentes...")
    kill_processes_on_ports()
    time.sleep(3)
    
    # 2. Iniciar aplicaciones
    print("\n🚀 Iniciando aplicaciones...")
    belgrano_process = start_belgrano_ahorro()
    time.sleep(3)
    
    ticketera_process = start_ticketera()
    time.sleep(3)
    
    devops_process = start_devops()
    time.sleep(3)
    
    print("\n✅ APLICACIONES INICIADAS:")
    print("   🛒 Belgrano Ahorro: http://localhost:5000")
    print("   🎫 Ticketera: http://localhost:5001")
    print("   🔧 DevOps: http://localhost:5002")
    
    print("\n🔐 Credenciales:")
    print("   👑 Admin: admin@belgranoahorro.com / admin123")
    print("   🚚 Flota: repartidor1@belgranoahorro.com / flota123")
    print("   🔧 DevOps: devops / DevOps2025!Secure")
    
    print("\n📝 Presiona Ctrl+C para detener")
    
    try:
        # Esperar a que terminen
        if belgrano_process:
            belgrano_process.wait()
        if ticketera_process:
            ticketera_process.wait()
        if devops_process:
            devops_process.wait()
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo aplicaciones...")
        if belgrano_process:
            belgrano_process.terminate()
        if ticketera_process:
            ticketera_process.terminate()
        if devops_process:
            devops_process.terminate()

if __name__ == "__main__":
    main()
