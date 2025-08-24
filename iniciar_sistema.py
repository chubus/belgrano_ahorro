#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar el sistema completo de Belgrano Ahorro
Inicia tanto la aplicación principal como la ticketera
"""

import subprocess
import time
import sys
import os

def iniciar_sistema():
    """Iniciar el sistema completo"""
    
    print("🚀 INICIANDO SISTEMA COMPLETO - BELGRANO AHORRO")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encuentra app.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        return
    
    print("📋 INFORMACIÓN DEL SISTEMA:")
    print("   • Aplicación principal: http://localhost:5000")
    print("   • Ticketera: http://localhost:5001")
    print("   • Acceso directo: http://localhost:5000/ticketera")
    print("   • Acceso admin: http://localhost:5000/admin")
    print()
    
    print("🔐 CREDENCIALES TICKETERA:")
    print("   • Admin: admin@belgranoahorro.com / admin123")
    print("   • Flota: repartidor1@belgranoahorro.com / flota123")
    print()
    
    print("⚡ INICIANDO APLICACIONES...")
    print()
    
    try:
        # Iniciar aplicación principal en segundo plano
        print("1️⃣ Iniciando aplicación principal (puerto 5000)...")
        proceso_principal = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un momento para que inicie
        time.sleep(3)
        
        # Iniciar ticketera en segundo plano
        print("2️⃣ Iniciando ticketera (puerto 5001)...")
        proceso_ticketera = subprocess.Popen([
            sys.executable, 'belgrano_tickets/app_simple.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un momento para que inicie
        time.sleep(3)
        
        print()
        print("✅ SISTEMA INICIADO EXITOSAMENTE")
        print("=" * 60)
        print("🌐 APLICACIÓN PRINCIPAL: http://localhost:5000")
        print("🎫 TICKETERA: http://localhost:5001")
        print("🔗 ACCESO DIRECTO: http://localhost:5000/ticketera")
        print()
        print("⏹️  Para detener el sistema, presiona Ctrl+C")
        print("=" * 60)
        
        # Mantener el script ejecutándose
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo sistema...")
            proceso_principal.terminate()
            proceso_ticketera.terminate()
            print("✅ Sistema detenido")
            
    except Exception as e:
        print(f"❌ Error al iniciar el sistema: {e}")
        return

if __name__ == "__main__":
    iniciar_sistema()
