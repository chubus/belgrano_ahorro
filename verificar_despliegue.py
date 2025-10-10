#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación para despliegue en Render
Verifica que no haya conflictos de merge y que todo esté listo
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def verificar_conflictos_merge():
    """Verificar que no haya conflictos de merge en archivos críticos"""
    print("🔍 Verificando conflictos de merge...")
    
    archivos_criticos = [
        'app.py',
        'app_unificado.py', 
        'devops_routes.py',
        'belgrano_tickets/api_client.py',
        'belgrano_tickets/devops_routes.py',
        'belgrano_client_gateway.py'
    ]
    
    conflictos_encontrados = []
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                if re.search(r'^<<<<<<<|^=======|^>>>>>>>', contenido, re.MULTILINE):
                    conflictos_encontrados.append(archivo)
                    print(f"   ❌ {archivo} - Conflictos de merge encontrados")
                else:
                    print(f"   ✅ {archivo} - Sin conflictos")
            except Exception as e:
                print(f"   ⚠️  {archivo} - Error leyendo archivo: {e}")
        else:
            print(f"   ⚠️  {archivo} - Archivo no encontrado")
    
    return len(conflictos_encontrados) == 0

def verificar_endpoints():
    """Verificar que los endpoints críticos estén definidos"""
    print("\n🔍 Verificando endpoints críticos...")
    
    endpoints_requeridos = [
        '/healthz',
        '/health',
        '/devops/health',
        '/devops/status'
    ]
    
    # Verificar en app.py
    if os.path.exists('app.py'):
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if '/healthz' in contenido:
            print("   ✅ /healthz encontrado en app.py")
        else:
            print("   ❌ /healthz NO encontrado en app.py")
    
    # Verificar en app_unificado.py
    if os.path.exists('app_unificado.py'):
        with open('app_unificado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if '/healthz' in contenido:
            print("   ✅ /healthz encontrado en app_unificado.py")
        else:
            print("   ❌ /healthz NO encontrado en app_unificado.py")
    
    return True

def verificar_variables_entorno():
    """Verificar que las variables de entorno se carguen correctamente"""
    print("\n🔍 Verificando carga de variables de entorno...")
    
    # Verificar en app.py
    if os.path.exists('app.py'):
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if 'os.environ.get(' in contenido:
            print("   ✅ Variables de entorno se cargan con os.environ.get() en app.py")
        else:
            print("   ⚠️  Variables de entorno no se cargan correctamente en app.py")
    
    # Verificar en api_client.py
    if os.path.exists('belgrano_tickets/api_client.py'):
        with open('belgrano_tickets/api_client.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if 'os.environ.get(' in contenido:
            print("   ✅ Variables de entorno se cargan con os.environ.get() en api_client.py")
        else:
            print("   ⚠️  Variables de entorno no se cargan correctamente en api_client.py")
    
    return True

def verificar_estructura_proyecto():
    """Verificar que la estructura del proyecto esté completa"""
    print("\n🔍 Verificando estructura del proyecto...")
    
    archivos_requeridos = [
        'app.py',
        'app_unificado.py',
        'devops_routes.py',
        'belgrano_tickets/api_client.py',
        'requirements.txt'
    ]
    
    todos_presentes = True
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
            todos_presentes = False
    
    return todos_presentes

def verificar_sintaxis_python():
    """Verificar que no haya errores de sintaxis en archivos Python"""
    print("\n🔍 Verificando sintaxis de archivos Python...")
    
    archivos_python = [
        'app.py',
        'app_unificado.py',
        'devops_routes.py',
        'belgrano_tickets/api_client.py',
        'belgrano_tickets/devops_routes.py'
    ]
    
    errores_sintaxis = []
    
    for archivo in archivos_python:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    codigo = f.read()
                
                # Compilar para verificar sintaxis
                compile(codigo, archivo, 'exec')
                print(f"   ✅ {archivo} - Sintaxis correcta")
            except SyntaxError as e:
                print(f"   ❌ {archivo} - Error de sintaxis: {e}")
                errores_sintaxis.append(archivo)
            except Exception as e:
                print(f"   ⚠️  {archivo} - Error verificando: {e}")
    
    return len(errores_sintaxis) == 0

def main():
    """Función principal de verificación"""
    print("🚀 Verificación de Despliegue - Belgrano Ahorro")
    print("=" * 50)
    
    # Ejecutar todas las verificaciones
    verificaciones = [
        ("Conflictos de merge", verificar_conflictos_merge),
        ("Endpoints críticos", verificar_endpoints),
        ("Variables de entorno", verificar_variables_entorno),
        ("Estructura del proyecto", verificar_estructura_proyecto),
        ("Sintaxis Python", verificar_sintaxis_python)
    ]
    
    resultados = []
    
    for nombre, funcion in verificaciones:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"   ❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    exitosos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: APROBADO")
            exitosos += 1
        else:
            print(f"❌ {nombre}: FALLÓ")
    
    print(f"\n🎯 RESULTADO: {exitosos}/{total} verificaciones exitosas")
    
    if exitosos == total:
        print("🎉 ¡Proyecto listo para despliegue en Render!")
        return 0
    else:
        print("⚠️  Hay problemas que deben corregirse antes del despliegue")
        return 1

if __name__ == "__main__":
    sys.exit(main())
