#!/usr/bin/env python3
"""
Script simple para lanzar ambas aplicaciones
"""
import subprocess
import time
import sys
import os

def main():
    print("🚀 LANZANDO BELGRANO AHORRO Y LA TICKETERA")
    print("=" * 50)
    
    # Lanzar aplicación principal
    print("🛒 Iniciando Belgrano Ahorro en puerto 5000...")
    belgrano_process = subprocess.Popen([sys.executable, "app.py"])
    
    # Esperar un momento
    time.sleep(3)
    
    # Lanzar ticketera
    print("🎫 Iniciando La Ticketera en puerto 5001...")
    os.chdir("belgrano_tickets")
    ticketera_process = subprocess.Popen([sys.executable, "app.py"])
    os.chdir("..")
    
    print("\n✅ Ambas aplicaciones iniciadas:")
    print("   🛒 Belgrano Ahorro: http://localhost:5000")
    print("   🎫 La Ticketera: http://localhost:5001")
    print("\n🔐 Credenciales:")
    print("   👑 Admin: admin@belgranoahorro.com / admin123")
    print("   🚚 Flota: repartidor1@belgranoahorro.com / repartidor123")
    print("\n📝 Presiona Ctrl+C para detener")
    
    try:
        # Esperar a que terminen
        belgrano_process.wait()
        ticketera_process.wait()
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo aplicaciones...")
        belgrano_process.terminate()
        ticketera_process.terminate()

if __name__ == "__main__":
    main()
