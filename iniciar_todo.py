#!/usr/bin/env python3
"""
Script simple para iniciar todas las aplicaciones
"""
import subprocess
import sys
import time

def main():
    print("🚀 INICIANDO TODAS LAS APLICACIONES")
    print("=" * 50)
    
    print("🛒 Iniciando Belgrano Ahorro...")
    belgrano_process = subprocess.Popen([sys.executable, "app_unificado.py"])
    time.sleep(3)
    
    print("🎫 Iniciando Ticketera...")
    ticketera_process = subprocess.Popen([sys.executable, "app_tickets.py"])
    time.sleep(3)
    
    print("🔧 Iniciando DevOps...")
    devops_process = subprocess.Popen([sys.executable, "devops_routes.py"])
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
        belgrano_process.wait()
        ticketera_process.wait()
        devops_process.wait()
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo aplicaciones...")
        belgrano_process.terminate()
        ticketera_process.terminate()
        devops_process.terminate()

if __name__ == "__main__":
    main()
