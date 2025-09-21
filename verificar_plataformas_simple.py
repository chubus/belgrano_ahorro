#!/usr/bin/env python3
"""
Script simplificado para verificar las 3 plataformas sin dependencias externas
"""

import os
import sys
from datetime import datetime

def verificar_archivos_criticos():
    """Verificar que los archivos críticos existan"""
    print("🔍 VERIFICANDO ARCHIVOS CRÍTICOS...")
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
    archivos_presentes = []
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"✅ {archivo} ({size:,} bytes)")
            archivos_presentes.append(archivo)
        else:
            print(f"❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    print(f"\n📊 RESUMEN ARCHIVOS:")
    print(f"   ✅ Presentes: {len(archivos_presentes)}")
    print(f"   ❌ Faltantes: {len(archivos_faltantes)}")
    
    if archivos_faltantes:
        print(f"\n⚠️  ARCHIVOS FALTANTES:")
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
    bases_presentes = []
    
    for db in bases_datos:
        if os.path.exists(db):
            size = os.path.getsize(db)
            print(f"✅ {db} ({size:,} bytes)")
            bases_presentes.append(db)
        else:
            print(f"❌ {db} - FALTANTE")
            bases_faltantes.append(db)
    
    print(f"\n📊 RESUMEN BASES DE DATOS:")
    print(f"   ✅ Presentes: {len(bases_presentes)}")
    print(f"   ❌ Faltantes: {len(bases_faltantes)}")
    
    if bases_faltantes:
        print(f"\n⚠️  BASES DE DATOS FALTANTES:")
        for db in bases_faltantes:
            print(f"   - {db}")
        return False
    else:
        print("\n🎉 ¡TODAS LAS BASES DE DATOS ESTÁN PRESENTES!")
        return True

def verificar_estructura_devops():
    """Verificar estructura específica de DevOps"""
    print("\n🔍 VERIFICANDO ESTRUCTURA DEVOPS...")
    print("=" * 60)
    
    estructura_devops = [
        'belgrano_tickets/templates/devops/',
        'belgrano_tickets/templates/devops/ofertas.html',
        'belgrano_tickets/templates/devops/negocios.html',
        'belgrano_tickets/templates/devops/productos.html',
        'belgrano_tickets/templates/devops/precios.html',
        'belgrano_tickets/templates/devops/logs.html',
        'belgrano_tickets/templates/devops/config.html',
        'belgrano_tickets/templates/devops/sync.html',
        'belgrano_tickets/templates/devops/health.html'
    ]
    
    estructura_faltante = []
    estructura_presente = []
    
    for item in estructura_devops:
        if os.path.exists(item):
            if os.path.isdir(item):
                print(f"✅ {item}/ (directorio)")
            else:
                size = os.path.getsize(item)
                print(f"✅ {item} ({size:,} bytes)")
            estructura_presente.append(item)
        else:
            print(f"❌ {item} - FALTANTE")
            estructura_faltante.append(item)
    
    print(f"\n📊 RESUMEN ESTRUCTURA DEVOPS:")
    print(f"   ✅ Presentes: {len(estructura_presente)}")
    print(f"   ❌ Faltantes: {len(estructura_faltante)}")
    
    if estructura_faltante:
        print(f"\n⚠️  ESTRUCTURA DEVOPS FALTANTE:")
        for item in estructura_faltante:
            print(f"   - {item}")
        return False
    else:
        print("\n🎉 ¡TODA LA ESTRUCTURA DEVOPS ESTÁ PRESENTE!")
        return True

def verificar_sintaxis_python():
    """Verificar sintaxis de archivos Python críticos"""
    print("\n🔍 VERIFICANDO SINTAXIS PYTHON...")
    print("=" * 60)
    
    archivos_python = [
        'app.py',
        'app_unificado.py',
        'app_tickets.py',
        'devops_routes.py',
        'belgrano_tickets/app.py'
    ]
    
    errores_sintaxis = []
    archivos_ok = []
    
    for archivo in archivos_python:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    compile(f.read(), archivo, 'exec')
                print(f"✅ {archivo} - Sintaxis OK")
                archivos_ok.append(archivo)
            except SyntaxError as e:
                print(f"❌ {archivo} - ERROR DE SINTAXIS: {e}")
                errores_sintaxis.append(archivo)
            except Exception as e:
                print(f"⚠️  {archivo} - Error: {e}")
        else:
            print(f"❌ {archivo} - ARCHIVO NO ENCONTRADO")
            errores_sintaxis.append(archivo)
    
    print(f"\n📊 RESUMEN SINTAXIS PYTHON:")
    print(f"   ✅ Correctos: {len(archivos_ok)}")
    print(f"   ❌ Con errores: {len(errores_sintaxis)}")
    
    if errores_sintaxis:
        print(f"\n⚠️  ARCHIVOS CON ERRORES DE SINTAXIS:")
        for archivo in errores_sintaxis:
            print(f"   - {archivo}")
        return False
    else:
        print("\n🎉 ¡TODOS LOS ARCHIVOS PYTHON TIENEN SINTAXIS CORRECTA!")
        return True

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN COMPLETA DE PLATAFORMAS")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar archivos críticos
    archivos_ok = verificar_archivos_criticos()
    
    # Verificar bases de datos
    bases_ok = verificar_bases_datos()
    
    # Verificar estructura DevOps
    devops_ok = verificar_estructura_devops()
    
    # Verificar sintaxis Python
    sintaxis_ok = verificar_sintaxis_python()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL:")
    print("-" * 30)
    print(f"Archivos críticos: {'✅ OK' if archivos_ok else '❌ FALTANTES'}")
    print(f"Bases de datos: {'✅ OK' if bases_ok else '❌ FALTANTES'}")
    print(f"Estructura DevOps: {'✅ OK' if devops_ok else '❌ FALTANTE'}")
    print(f"Sintaxis Python: {'✅ OK' if sintaxis_ok else '❌ ERRORES'}")
    
    total_ok = sum([archivos_ok, bases_ok, devops_ok, sintaxis_ok])
    
    print(f"\n🎯 TOTAL: {total_ok}/4 verificaciones exitosas")
    
    if total_ok == 4:
        print("\n🎉 ¡TODAS LAS PLATAFORMAS ESTÁN LISTAS PARA DEPLOY!")
        return 0
    else:
        print("\n⚠️  HAY PROBLEMAS QUE REQUIEREN ATENCIÓN")
        return 1

if __name__ == "__main__":
    sys.exit(main())
