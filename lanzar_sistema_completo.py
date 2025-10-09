#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanzador Completo del Sistema DevOps-Belgrano Ahorro
Inicia todos los servicios para testing antes del deploy
"""

import subprocess
import time
import requests
import sys
import os
from datetime import datetime
import threading

def verificar_puerto(puerto):
    """Verificar si un puerto está en uso"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', puerto))
        sock.close()
        return result == 0
    except:
        return False

def iniciar_belgrano_ahorro():
    """Iniciar Belgrano Ahorro en puerto 5000"""
    print("🚀 Iniciando Belgrano Ahorro (puerto 5000)...")
    try:
        process = subprocess.Popen([
            sys.executable, 'app_unificado.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que se inicie
        time.sleep(5)
        
        # Verificar que esté funcionando
        try:
            response = requests.get("http://localhost:5000/health", timeout=10)
            if response.status_code == 200:
                print("✅ Belgrano Ahorro: FUNCIONANDO")
                return process
            else:
                print(f"⚠️ Belgrano Ahorro: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Belgrano Ahorro: ERROR - {e}")
            return None
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return None

def iniciar_ticketera():
    """Iniciar Ticketera en puerto 5001"""
    print("🚀 Iniciando Ticketera (puerto 5001)...")
    try:
        process = subprocess.Popen([
            sys.executable, 'app_tickets.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que se inicie
        time.sleep(5)
        
        # Verificar que esté funcionando
        try:
            response = requests.get("http://localhost:5001/health", timeout=10)
            if response.status_code == 200:
                print("✅ Ticketera: FUNCIONANDO")
                return process
            else:
                print(f"⚠️ Ticketera: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ticketera: ERROR - {e}")
            return None
    except Exception as e:
        print(f"❌ Error iniciando Ticketera: {e}")
        return None

def iniciar_devops():
    """Iniciar DevOps en puerto 5002"""
    print("🚀 Iniciando DevOps (puerto 5002)...")
    try:
        process = subprocess.Popen([
            sys.executable, 'devops_simple_funcional.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que se inicie
        time.sleep(5)
        
        # Verificar que esté funcionando
        try:
            response = requests.get("http://localhost:5002/devops/", timeout=10)
            if response.status_code in [200, 302]:  # 302 es redirect a login
                print("✅ DevOps: FUNCIONANDO")
                return process
            else:
                print(f"⚠️ DevOps: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ DevOps: ERROR - {e}")
            return None
    except Exception as e:
        print(f"❌ Error iniciando DevOps: {e}")
        return None

def test_sistema_completo():
    """Test completo del sistema"""
    print("\n🧪 TESTEANDO SISTEMA COMPLETO...")
    print("=" * 60)
    
    servicios = {
        "Belgrano Ahorro": "http://localhost:5000",
        "Ticketera": "http://localhost:5001", 
        "DevOps": "http://localhost:5002/devops/"
    }
    
    resultados = {}
    
    for nombre, url in servicios.items():
        try:
            if nombre == "DevOps":
                response = requests.get(url, timeout=10)
                if response.status_code in [200, 302]:
                    print(f"✅ {nombre}: FUNCIONANDO")
                    resultados[nombre] = True
                else:
                    print(f"⚠️ {nombre}: Status {response.status_code}")
                    resultados[nombre] = False
            else:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {nombre}: FUNCIONANDO")
                    resultados[nombre] = True
                else:
                    print(f"⚠️ {nombre}: Status {response.status_code}")
                    resultados[nombre] = False
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
            resultados[nombre] = False
    
    # Test APIs de Belgrano Ahorro
    print("\n🛒 TESTEANDO APIs DE BELGRANO AHORRO...")
    try:
        headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
        endpoints = ['negocios', 'productos', 'ofertas', 'sucursales', 'health']
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:5000/api/{endpoint}", 
                                      headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"✅ GET /api/{endpoint}: OK")
                else:
                    print(f"⚠️ GET /api/{endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ GET /api/{endpoint}: ERROR - {e}")
    except Exception as e:
        print(f"❌ Error testeando APIs: {e}")
    
    return resultados

def main():
    """Función principal"""
    print("🚀 LANZADOR COMPLETO DEL SISTEMA")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar puertos
    puertos = [5000, 5001, 5002]
    for puerto in puertos:
        if verificar_puerto(puerto):
            print(f"⚠️ Puerto {puerto} ya está en uso")
    
    # Detener procesos existentes
    print("🛑 Deteniendo procesos existentes...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, text=True)
        time.sleep(2)
    except:
        pass
    
    # Iniciar servicios
    procesos = {}
    
    print("\n🚀 INICIANDO SERVICIOS...")
    print("=" * 40)
    
    # Belgrano Ahorro
    proceso_ba = iniciar_belgrano_ahorro()
    if proceso_ba:
        procesos['belgrano_ahorro'] = proceso_ba
    
    # Ticketera
    proceso_tick = iniciar_ticketera()
    if proceso_tick:
        procesos['ticketera'] = proceso_tick
    
    # DevOps
    proceso_devops = iniciar_devops()
    if proceso_devops:
        procesos['devops'] = proceso_devops
    
    # Esperar un momento para que todos se estabilicen
    print("\n⏳ Esperando que los servicios se estabilicen...")
    time.sleep(10)
    
    # Test completo
    resultados = test_sistema_completo()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    servicios_funcionando = sum(1 for status in resultados.values() if status)
    total_servicios = len(resultados)
    
    print(f"🔗 Servicios funcionando: {servicios_funcionando}/{total_servicios}")
    
    if servicios_funcionando == total_servicios:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
    elif servicios_funcionando > 0:
        print("⚠️ Sistema parcialmente funcional")
    else:
        print("❌ Sistema no funcional")
    
    print("\n🌐 URLs DE ACCESO:")
    print("   🛒 Belgrano Ahorro: http://localhost:5000")
    print("   🎫 Ticketera: http://localhost:5001")
    print("   🔧 DevOps: http://localhost:5002/devops/")
    
    print("\n🔐 CREDENCIALES:")
    print("   DevOps: devops / DevOps2025!Secure")
    print("   Ticketera Admin: admin@belgranoahorro.com / admin123")
    print("   Ticketera Flota: repartidor1@belgranoahorro.com / flota123")
    
    print(f"\n⏰ Sistema iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 Para detener los servicios, presiona Ctrl+C")
    
    # Mantener el sistema activo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo sistema...")
        for nombre, proceso in procesos.items():
            try:
                proceso.terminate()
                print(f"✅ {nombre} detenido")
            except:
                pass
        print("🎉 Sistema detenido correctamente")

if __name__ == "__main__":
    main()
