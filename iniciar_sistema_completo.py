#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar el sistema completo: Belgrano Ahorro + Ticketera
"""

import subprocess
import time
import sys
import os
import signal
import threading

def iniciar_belgrano_ahorro():
    """Iniciar Belgrano Ahorro en puerto 5000"""
    print("🚀 Iniciando Belgrano Ahorro...")
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("✅ Belgrano Ahorro iniciado en puerto 5000")
        return process
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return None

def iniciar_ticketera():
    """Iniciar Ticketera en puerto 5001"""
    print("🎫 Iniciando Ticketera...")
    try:
        # Cambiar al directorio de la ticketera
        ticketera_dir = "belgrano_tickets"
        if os.path.exists(ticketera_dir):
            os.chdir(ticketera_dir)
            process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            os.chdir("..")  # Volver al directorio original
            print("✅ Ticketera iniciada en puerto 5001")
            return process
        else:
            print(f"❌ Directorio {ticketera_dir} no encontrado")
            return None
    except Exception as e:
        print(f"❌ Error iniciando Ticketera: {e}")
        return None

def verificar_servicios():
    """Verificar que ambos servicios estén funcionando"""
    import requests
    
    print("\n🔍 Verificando servicios...")
    
    # Verificar Belgrano Ahorro
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro funcionando")
        else:
            print("⚠️ Belgrano Ahorro no responde correctamente")
    except:
        print("❌ Belgrano Ahorro no está disponible")
    
    # Verificar Ticketera
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Ticketera funcionando")
        else:
            print("⚠️ Ticketera no responde correctamente")
    except:
        print("❌ Ticketera no está disponible")

def mostrar_urls():
    """Mostrar URLs del sistema"""
    print("\n🌐 URLs del Sistema:")
    print("=" * 40)
    print("🛒 Belgrano Ahorro: http://localhost:5000")
    print("🎫 Ticketera: http://localhost:5001")
    print("📡 API Ticketera: http://localhost:5001/api/tickets")
    print("🏥 Health Check: http://localhost:5001/health")
    
    print("\n🔐 Credenciales Ticketera:")
    print("- Admin: admin@belgranoahorro.com / admin123")
    print("- Flota: repartidor1@belgranoahorro.com / flota123")
    
    print("\n📋 Flujo de Integración:")
    print("1. Cliente hace pedido en Belgrano Ahorro")
    print("2. Belgrano Ahorro envía automáticamente a Ticketera")
    print("3. Ticketera recibe y crea ticket")
    print("4. Ticket visible en panel de administración")

def main():
    """Función principal"""
    print("🎯 SISTEMA COMPLETO - BELGRANO AHORRO + TICKETERA")
    print("=" * 60)
    
    # Iniciar Belgrano Ahorro
    ahorro_process = iniciar_belgrano_ahorro()
    if not ahorro_process:
        print("❌ No se pudo iniciar Belgrano Ahorro")
        return
    
    # Esperar un poco
    time.sleep(3)
    
    # Iniciar Ticketera
    ticketera_process = iniciar_ticketera()
    if not ticketera_process:
        print("❌ No se pudo iniciar Ticketera")
        ahorro_process.terminate()
        return
    
    # Esperar a que ambos servicios estén listos
    print("\n⏳ Esperando que los servicios estén listos...")
    time.sleep(5)
    
    # Verificar servicios
    verificar_servicios()
    
    # Mostrar URLs
    mostrar_urls()
    
    print("\n🎉 Sistema completo iniciado exitosamente!")
    print("Presiona Ctrl+C para detener ambos servicios")
    
    try:
        # Mantener los procesos ejecutándose
        while True:
            time.sleep(1)
            
            # Verificar si algún proceso se cerró
            if ahorro_process.poll() is not None:
                print("❌ Belgrano Ahorro se cerró inesperadamente")
                break
                
            if ticketera_process.poll() is not None:
                print("❌ Ticketera se cerró inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        
        # Terminar procesos
        if ahorro_process:
            ahorro_process.terminate()
            print("✅ Belgrano Ahorro detenido")
            
        if ticketera_process:
            ticketera_process.terminate()
            print("✅ Ticketera detenida")
            
        print("👋 Sistema completo detenido")

if __name__ == "__main__":
    main()
