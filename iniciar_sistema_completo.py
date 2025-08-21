#!/usr/bin/env python3
"""
Script para iniciar el sistema completo de Belgrano Ahorro + Belgrano Tickets
"""

import subprocess
import time
import sys
import os
import requests
from threading import Thread

def iniciar_belgrano_ahorro():
    """Iniciar la aplicación principal de Belgrano Ahorro"""
    print("🚀 Iniciando Belgrano Ahorro...")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ Belgrano Ahorro detenido")

def iniciar_belgrano_tickets():
    """Iniciar Belgrano Tickets"""
    print("🎫 Iniciando Belgrano Tickets...")
    try:
        os.chdir("belgrano_tickets")
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ Belgrano Tickets detenido")
    finally:
        os.chdir("..")

def verificar_servicios():
    """Verificar que ambos servicios estén funcionando"""
    print("\n🔍 Verificando servicios...")
    
    # Verificar Belgrano Ahorro
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro funcionando en http://localhost:5000")
        else:
            print(f"⚠️ Belgrano Ahorro responde con código: {response.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Ahorro no está disponible: {e}")
    
    # Verificar Belgrano Tickets
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Tickets funcionando en http://localhost:5001")
        else:
            print(f"⚠️ Belgrano Tickets responde con código: {response.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Tickets no está disponible: {e}")

def probar_integracion():
    """Probar la integración entre ambos sistemas"""
    print("\n🧪 Probando integración...")
    try:
        from test_integracion_tickets import test_integracion_tickets
        test_integracion_tickets()
    except ImportError:
        print("⚠️ No se pudo importar el script de prueba")
    except Exception as e:
        print(f"❌ Error al probar integración: {e}")

def main():
    """Función principal"""
    print("🎯 SISTEMA COMPLETO BELGRANO AHORRO + BELGRANO TICKETS")
    print("=" * 60)
    
    # Iniciar Belgrano Tickets en un hilo separado
    tickets_thread = Thread(target=iniciar_belgrano_tickets, daemon=True)
    tickets_thread.start()
    
    # Esperar un poco para que Belgrano Tickets se inicie
    print("⏳ Esperando que Belgrano Tickets se inicie...")
    time.sleep(3)
    
    # Verificar servicios
    verificar_servicios()
    
    # Probar integración
    probar_integracion()
    
    print("\n🎉 Sistema iniciado correctamente!")
    print("📱 Belgrano Ahorro: http://localhost:5000")
    print("🎫 Belgrano Tickets: http://localhost:5001")
    print("\nPresiona Ctrl+C para detener ambos servicios")
    
    try:
        # Iniciar Belgrano Ahorro en el hilo principal
        iniciar_belgrano_ahorro()
    except KeyboardInterrupt:
        print("\n👋 Sistema detenido")

if __name__ == "__main__":
    main()
