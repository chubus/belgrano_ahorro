#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación de APIs DevOps con servicios activos
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def esperar_servicios():
    """Esperar a que los servicios estén listos"""
    print("Esperando a que los servicios estén listos...")
    
    servicios = [
        ('Belgrano Ahorro', 'http://localhost:5000/', 30),
        ('Ticketera', 'http://localhost:5001/', 30),
        ('DevOps', 'http://localhost:5002/devops/', 30),
        ('API Gateway', 'http://localhost:5003/gateway/health', 30),
        ('Sistema Sync', 'http://localhost:5004/sync/status', 30)
    ]
    
    servicios_listos = 0
    
    for nombre, url, timeout in servicios:
        print(f"Verificando {nombre}...")
        for i in range(timeout):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code in [200, 302]:
                    print(f"✅ {nombre} listo")
                    servicios_listos += 1
                    break
            except:
                if i < timeout - 1:
                    print(f"⏳ {nombre} - Esperando... ({i+1}/{timeout})")
                    time.sleep(1)
                else:
                    print(f"❌ {nombre} - No disponible después de {timeout}s")
    
    print(f"\nServicios listos: {servicios_listos}/{len(servicios)}")
    return servicios_listos == len(servicios)

def verificar_apis_devops():
    """Verificar APIs DevOps con servicios activos"""
    print("VERIFICANDO APIS DEVOPS CON SERVICIOS ACTIVOS")
    print("=" * 60)
    
    # Esperar a que los servicios estén listos
    if not esperar_servicios():
        print("⚠️ Algunos servicios no están disponibles")
        print("Continuando con la verificación...")
    
    # Ejecutar chequeo de APIs
    try:
        from chequeo_apis_devops import DevOpsAPIChecker
        checker = DevOpsAPIChecker()
        return checker.run_full_check()
    except ImportError:
        print("❌ No se puede importar DevOpsAPIChecker")
        return False
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DE APIS DEVOPS CON SERVICIOS ACTIVOS")
    print("=" * 60)
    print("Este script verifica las APIs después de iniciar los servicios")
    print("")
    
    # Verificar que el script de inicio existe
    if not os.path.exists('iniciar_servicios_devops.py'):
        print("❌ Script de inicio no encontrado: iniciar_servicios_devops.py")
        return False
    
    print("📋 INSTRUCCIONES:")
    print("1. Abre una nueva terminal")
    print("2. Ejecuta: python iniciar_servicios_devops.py")
    print("3. Espera a que todos los servicios estén listos")
    print("4. Presiona Enter aquí para continuar con la verificación")
    print("")
    
    input("Presiona Enter cuando los servicios estén listos...")
    
    # Ejecutar verificación
    resultado = verificar_apis_devops()
    
    if resultado:
        print("\n✅ TODAS LAS APIS DEVOPS ESTÁN FUNCIONANDO CORRECTAMENTE")
        print("Sistema listo para deploy")
    else:
        print("\n⚠️ ALGUNAS APIS REQUIEREN CORRECCIONES")
        print("Revisar errores antes del deploy")
    
    return resultado

if __name__ == "__main__":
    main()
<<<<<<< HEAD

=======
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
