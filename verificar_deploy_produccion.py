#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado del deploy en producción
"""

import requests
import time
import sys

def verificar_deploy():
    """Verificar el estado de las aplicaciones en producción"""
    
    print("🔍 VERIFICANDO DEPLOY EN PRODUCCIÓN")
    print("=" * 60)
    print()
    
    # URLs de producción
    app_principal = "https://belgrano-ahorro.onrender.com"
    ticketera = "https://belgrano-ticketera.onrender.com"
    
    print("📋 URLs de producción:")
    print(f"   • Aplicación principal: {app_principal}")
    print(f"   • Ticketera: {ticketera}")
    print()
    
    # Verificar aplicación principal
    print("1️⃣ Verificando aplicación principal...")
    try:
        response = requests.get(app_principal, timeout=10)
        if response.status_code == 200:
            print("   ✅ Aplicación principal funcionando")
        else:
            print(f"   ❌ Aplicación principal error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a aplicación principal: {e}")
    
    # Verificar ticketera
    print("2️⃣ Verificando ticketera...")
    try:
        response = requests.get(ticketera, timeout=10)
        if response.status_code == 200:
            print("   ✅ Ticketera funcionando")
        else:
            print(f"   ❌ Ticketera error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a ticketera: {e}")
    
    # Verificar rutas de redirección
    print("3️⃣ Verificando rutas de redirección...")
    try:
        response = requests.get(f"{app_principal}/ticketera", timeout=10, allow_redirects=False)
        if response.status_code in [301, 302]:
            print("   ✅ Ruta /ticketera redirigiendo correctamente")
            print(f"   📍 Redirige a: {response.headers.get('Location', 'No encontrado')}")
        else:
            print(f"   ❌ Ruta /ticketera error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en ruta /ticketera: {e}")
    
    try:
        response = requests.get(f"{app_principal}/admin", timeout=10, allow_redirects=False)
        if response.status_code in [301, 302]:
            print("   ✅ Ruta /admin redirigiendo correctamente")
            print(f"   📍 Redirige a: {response.headers.get('Location', 'No encontrado')}")
        else:
            print(f"   ❌ Ruta /admin error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en ruta /admin: {e}")
    
    print()
    print("=" * 60)
    print("🔐 CREDENCIALES PARA PRODUCCIÓN:")
    print("   • Admin: admin@belgranoahorro.com / admin123")
    print("   • Flota: repartidor1@belgranoahorro.com / flota123")
    print()
    print("🌐 ACCESO DIRECTO:")
    print(f"   • Ticketera: {ticketera}")
    print(f"   • Desde app principal: {app_principal}/ticketera")
    print("=" * 60)

if __name__ == "__main__":
    verificar_deploy()
