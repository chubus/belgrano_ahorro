#!/usr/bin/env python3
"""
Script para verificar la conectividad de las 3 plataformas:
1. Belgrano Ahorro (principal)
2. Ticketera (sistema de tickets)
3. DevOps (panel de administración)
"""

import requests
import sys
import os
from datetime import datetime

def verificar_conectividad():
    """Verificar conectividad de todas las plataformas"""
    print("🔍 VERIFICACIÓN DE CONECTIVIDAD DE PLATAFORMAS")
    print("=" * 60)
    
    resultados = {
        'belgrano_ahorro': False,
        'ticketera': False,
        'devops': False
    }
    
    # URLs base (ajustar según el entorno)
    urls = {
        'belgrano_ahorro': 'http://localhost:5000',
        'ticketera': 'http://localhost:5001', 
        'devops': 'http://localhost:5000/devops'
    }
    
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar Belgrano Ahorro
    print("1️⃣ VERIFICANDO BELGRANO AHORRO...")
    try:
        response = requests.get(f"{urls['belgrano_ahorro']}/", timeout=10)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro: CONECTADO")
            resultados['belgrano_ahorro'] = True
        else:
            print(f"❌ Belgrano Ahorro: ERROR {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Belgrano Ahorro: NO CONECTADO - {str(e)}")
    
    print()
    
    # 2. Verificar Ticketera
    print("2️⃣ VERIFICANDO TICKETERA...")
    try:
        response = requests.get(f"{urls['ticketera']}/", timeout=10)
        if response.status_code == 200:
            print("✅ Ticketera: CONECTADO")
            resultados['ticketera'] = True
        else:
            print(f"❌ Ticketera: ERROR {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ticketera: NO CONECTADO - {str(e)}")
    
    print()
    
    # 3. Verificar DevOps
    print("3️⃣ VERIFICANDO DEVOPS...")
    try:
        response = requests.get(f"{urls['devops']}/", timeout=10)
        if response.status_code == 200:
            print("✅ DevOps: CONECTADO")
            resultados['devops'] = True
        else:
            print(f"❌ DevOps: ERROR {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ DevOps: NO CONECTADO - {str(e)}")
    
    print()
    
    # Resumen
    print("📊 RESUMEN DE CONECTIVIDAD:")
    print("-" * 40)
    total_conectadas = sum(resultados.values())
    
    for plataforma, estado in resultados.items():
        status = "✅ CONECTADO" if estado else "❌ NO CONECTADO"
        print(f"{plataforma.upper()}: {status}")
    
    print(f"\n🎯 TOTAL: {total_conectadas}/3 plataformas conectadas")
    
    if total_conectadas == 3:
        print("🎉 ¡TODAS LAS PLATAFORMAS ESTÁN CONECTADAS!")
        return True
    else:
        print("⚠️  ALGUNAS PLATAFORMAS NO ESTÁN CONECTADAS")
        return False

def verificar_archivos_criticos():
    """Verificar que los archivos críticos existan"""
    print("\n🔍 VERIFICANDO ARCHIVOS CRÍTICOS...")
    print("=" * 60)
    
    archivos_criticos = [
        'app.py',
        'app_unificado.py', 
        'app_tickets.py',
        'devops_routes.py',
        'belgrano_tickets/app.py',
        'belgrano_tickets/templates/devops/ofertas.html',
        'belgrano_tickets/templates/devops/negocios.html',
        'belgrano_tickets/templates/devops/productos.html',
        'belgrano_tickets/templates/devops/precios.html',
        'belgrano_tickets/templates/devops/logs.html',
        'belgrano_tickets/templates/devops/config.html',
        'belgrano_tickets/templates/devops/sync.html'
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"\n⚠️  ARCHIVOS FALTANTES: {len(archivos_faltantes)}")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        return False
    else:
        print("\n🎉 ¡TODOS LOS ARCHIVOS CRÍTICOS ESTÁN PRESENTES!")
        return True

def verificar_bases_datos():
    """Verificar que las bases de datos existan"""
    print("\n🔍 VERIFICANDO BASES DE DATOS...")
    print("=" * 60)
    
    bases_datos = [
        'belgrano_ahorro.db',
        'belgrano_tickets.db'
    ]
    
    bases_faltantes = []
    
    for db in bases_datos:
        if os.path.exists(db):
            size = os.path.getsize(db)
            print(f"✅ {db} ({size:,} bytes)")
        else:
            print(f"❌ {db} - FALTANTE")
            bases_faltantes.append(db)
    
    if bases_faltantes:
        print(f"\n⚠️  BASES DE DATOS FALTANTES: {len(bases_faltantes)}")
        for db in bases_faltantes:
            print(f"   - {db}")
        return False
    else:
        print("\n🎉 ¡TODAS LAS BASES DE DATOS ESTÁN PRESENTES!")
        return True

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN COMPLETA DE PLATAFORMAS")
    print("=" * 60)
    
    # Verificar archivos críticos
    archivos_ok = verificar_archivos_criticos()
    
    # Verificar bases de datos
    bases_ok = verificar_bases_datos()
    
    # Verificar conectividad
    conectividad_ok = verificar_conectividad()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL:")
    print("-" * 30)
    print(f"Archivos críticos: {'✅ OK' if archivos_ok else '❌ FALTANTES'}")
    print(f"Bases de datos: {'✅ OK' if bases_ok else '❌ FALTANTES'}")
    print(f"Conectividad: {'✅ OK' if conectividad_ok else '❌ PROBLEMAS'}")
    
    if archivos_ok and bases_ok and conectividad_ok:
        print("\n🎉 ¡TODAS LAS PLATAFORMAS ESTÁN OPERATIVAS!")
        return 0
    else:
        print("\n⚠️  HAY PROBLEMAS QUE REQUIEREN ATENCIÓN")
        return 1

if __name__ == "__main__":
    sys.exit(main())
