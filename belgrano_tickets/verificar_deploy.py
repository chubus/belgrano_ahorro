#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la configuración de deploy de Belgrano Tickets
"""

import os
import sys
from pathlib import Path

def verificar_archivos_esenciales():
    """Verificar que todos los archivos esenciales estén presentes"""
    print("🔍 Verificando archivos esenciales...")
    
    archivos_requeridos = [
        'app.py',
        'models.py',
        'config_ticketera.py',
        'requirements_ticketera.txt',
        'start_ticketera.sh',
        'belgrano_client.py'
    ]
    
    directorios_requeridos = [
        'templates',
        'static'
    ]
    
    archivos_faltantes = []
    directorios_faltantes = []
    
    for archivo in archivos_requeridos:
        if not Path(archivo).exists():
            archivos_faltantes.append(archivo)
    
    for directorio in directorios_requeridos:
        if not Path(directorio).is_dir():
            directorios_faltantes.append(directorio)
    
    if archivos_faltantes:
        print(f"❌ Archivos faltantes: {archivos_faltantes}")
        return False
    
    if directorios_faltantes:
        print(f"❌ Directorios faltantes: {directorios_faltantes}")
        return False
    
    print("✅ Todos los archivos esenciales están presentes")
    return True

def verificar_dockerfile():
    """Verificar que el Dockerfile esté correctamente configurado"""
    print("\n🐳 Verificando Dockerfile...")
    
    dockerfiles = ['Dockerfile', 'Dockerfile.render']
    dockerfile_encontrado = None
    
    for dockerfile in dockerfiles:
        if Path(dockerfile).exists():
            dockerfile_encontrado = dockerfile
            break
    
    if not dockerfile_encontrado:
        print("❌ No se encontró ningún Dockerfile")
        return False
    
    print(f"✅ Dockerfile encontrado: {dockerfile_encontrado}")
    
    # Verificar contenido básico del Dockerfile
    with open(dockerfile_encontrado, 'r') as f:
        contenido = f.read()
        
    elementos_requeridos = [
        'FROM python:3.12',
        'WORKDIR /app',
        'COPY',
        'RUN pip install',
        'CMD'
    ]
    
    elementos_faltantes = []
    for elemento in elementos_requeridos:
        if elemento not in contenido:
            elementos_faltantes.append(elemento)
    
    if elementos_faltantes:
        print(f"⚠️ Elementos faltantes en Dockerfile: {elementos_faltantes}")
        return False
    
    print("✅ Dockerfile configurado correctamente")
    return True

def verificar_dockerignore():
    """Verificar que .dockerignore esté configurado"""
    print("\n🚫 Verificando .dockerignore...")
    
    if not Path('.dockerignore').exists():
        print("❌ No se encontró .dockerignore")
        return False
    
    with open('.dockerignore', 'r') as f:
        contenido = f.read()
    
    # Verificar que incluya elementos importantes
    elementos_importantes = [
        '__pycache__',
        '*.pyc',
        '.git',
        'venv',
        '*.log'
    ]
    
    elementos_faltantes = []
    for elemento in elementos_importantes:
        if elemento not in contenido:
            elementos_faltantes.append(elemento)
    
    if elementos_faltantes:
        print(f"⚠️ Elementos faltantes en .dockerignore: {elementos_faltantes}")
        return False
    
    print("✅ .dockerignore configurado correctamente")
    return True

def verificar_requirements():
    """Verificar que requirements_ticketera.txt esté completo"""
    print("\n📦 Verificando requirements_ticketera.txt...")
    
    if not Path('requirements_ticketera.txt').exists():
        print("❌ No se encontró requirements_ticketera.txt")
        return False
    
    with open('requirements_ticketera.txt', 'r') as f:
        contenido = f.read()
    
    dependencias_requeridas = [
        'Flask',
        'Flask-SocketIO',
        'Flask-SQLAlchemy',
        'requests'
    ]
    
    dependencias_faltantes = []
    for dependencia in dependencias_requeridas:
        if dependencia not in contenido:
            dependencias_faltantes.append(dependencia)
    
    if dependencias_faltantes:
        print(f"⚠️ Dependencias faltantes: {dependencias_faltantes}")
        return False
    
    print("✅ requirements_ticketera.txt está completo")
    return True

def verificar_configuracion_render():
    """Verificar archivos de configuración de Render"""
    print("\n⚙️ Verificando configuración de Render...")
    
    archivos_render = ['render.yaml', 'render_ticketera.yaml', 'render_independiente.yaml', 'render_docker.yaml']
    archivos_encontrados = []
    
    for archivo in archivos_render:
        if Path(archivo).exists():
            archivos_encontrados.append(archivo)
    
    if not archivos_encontrados:
        print("❌ No se encontraron archivos de configuración de Render")
        return False
    
    print(f"✅ Archivos de configuración encontrados: {archivos_encontrados}")
    return True

def generar_reporte():
    """Generar reporte completo de verificación"""
    print("📋 VERIFICACIÓN DE CONFIGURACIÓN DE DEPLOY")
    print("=" * 50)
    
    verificaciones = [
        ("Archivos esenciales", verificar_archivos_esenciales),
        ("Dockerfile", verificar_dockerfile),
        (".dockerignore", verificar_dockerignore),
        ("Requirements", verificar_requirements),
        ("Configuración Render", verificar_configuracion_render)
    ]
    
    resultados = []
    for nombre, funcion in verificaciones:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en verificación {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen
    print("\n📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 30)
    
    exitos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ OK" if resultado else "❌ FALLA"
        print(f"{nombre}: {estado}")
    
    print(f"\n🎯 Resultado: {exitos}/{total} verificaciones exitosas")
    
    if exitos == total:
        print("🎉 ¡Configuración lista para deploy!")
        return True
    else:
        print("⚠️ Hay problemas que deben resolverse antes del deploy")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICADOR DE CONFIGURACIÓN DE DEPLOY")
    print("=" * 50)
    
    # Cambiar al directorio de belgrano_tickets si es necesario
    if not Path('app.py').exists() and Path('../belgrano_tickets').exists():
        os.chdir('../belgrano_tickets')
        print("📁 Cambiando al directorio belgrano_tickets...")
    
    # Generar reporte
    exito = generar_reporte()
    
    if exito:
        print("\n✅ ¡Todo listo para deploy en Render!")
        print("💡 Usa uno de los archivos render_*.yaml para el deploy")
    else:
        print("\n❌ Corrige los problemas antes de hacer deploy")
        sys.exit(1)

if __name__ == "__main__":
    main()
