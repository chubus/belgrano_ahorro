#!/usr/bin/env python3
"""
Script para iniciar ambas aplicaciones en paralelo
"""
import subprocess
import time
import signal
import sys
import os

def start_belgrano_ahorro():
    """Inicia Belgrano Ahorro"""
    print("🛒 Iniciando Belgrano Ahorro...")
    try:
        process = subprocess.Popen([sys.executable, "app.py"])
        print("✅ Belgrano Ahorro iniciado en puerto 5000")
        return process
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def start_ticketera():
    """Inicia La Ticketera"""
    print("🎫 Iniciando La Ticketera...")
    try:
        process = subprocess.Popen([sys.executable, "app_tickets.py"])
        print("✅ La Ticketera iniciada en puerto 5001")
        return process
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🚀 INICIANDO BELGRANO AHORRO Y LA TICKETERA")
    print("=" * 50)
    
    # Iniciar aplicaciones
    belgrano_process = start_belgrano_ahorro()
    time.sleep(3)
    ticketera_process = start_ticketera()
    
    print("\n✅ Ambas aplicaciones iniciadas:")
    print("   🛒 Belgrano Ahorro: http://localhost:5000")
    print("   🎫 La Ticketera: http://localhost:5001")
    print("\n🔐 Credenciales:")
    print("   👑 Admin: admin@belgranoahorro.com / admin123")
    print("   🚚 Flota: repartidor1@belgranoahorro.com / repartidor123")
    print("\n📝 Presiona Ctrl+C para detener")
    
    try:
        # Esperar a que terminen
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

if __name__ == "__main__":
    main()
