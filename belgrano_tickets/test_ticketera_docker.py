#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la instalación y funcionamiento de Belgrano Tickets Docker
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def verificar_archivos_ticketera():
    """Verificar que todos los archivos necesarios estén presentes"""
    print("🔍 VERIFICACIÓN DE ARCHIVOS DE LA TICKETERA")
    print("=" * 50)
    
    archivos_requeridos = [
        'Dockerfile',
        'docker-compose.yml',
        'start_ticketera.sh',
        'start_ticketera.bat',
        'requirements_ticketera.txt',
        'config_ticketera.py',
        'render_ticketera.yaml',
        'app.py',
        'models.py'
    ]
    
    print("📁 Archivos de la Ticketera:")
    archivos_ok = True
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
            archivos_ok = False
    
    return archivos_ok

def verificar_docker():
    """Verificar que Docker esté instalado y funcionando"""
    print(f"\n🐳 Verificación de Docker:")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ Docker instalado: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Docker no está funcionando")
            return False
    except FileNotFoundError:
        print(f"   ❌ Docker no está instalado")
        return False
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout al verificar Docker")
        return False

def verificar_docker_compose():
    """Verificar que Docker Compose esté disponible"""
    print(f"📦 Verificación de Docker Compose:")
    
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ Docker Compose disponible: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Docker Compose no está funcionando")
            return False
    except FileNotFoundError:
        print(f"   ❌ Docker Compose no está instalado")
        return False
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout al verificar Docker Compose")
        return False

def verificar_imagen_docker():
    """Verificar si la imagen de la ticketera existe"""
    print(f"🖼️ Verificación de Imagen Docker:")
    
    try:
        result = subprocess.run(['docker', 'images', 'belgrano-ticketera:latest'], 
                              capture_output=True, text=True, timeout=10)
        if 'belgrano-ticketera' in result.stdout:
            print(f"   ✅ Imagen belgrano-ticketera existe")
            return True
        else:
            print(f"   ⚠️ Imagen belgrano-ticketera no existe (se creará al hacer build)")
            return False
    except Exception as e:
        print(f"   ❌ Error al verificar imagen: {e}")
        return False

def verificar_puertos():
    """Verificar que los puertos necesarios estén libres"""
    print(f"\n🔌 Verificación de Puertos:")
    
    puertos = [5000, 5001]
    puertos_ok = True
    
    for puerto in puertos:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', puerto))
            sock.close()
            
            if result == 0:
                print(f"   ⚠️ Puerto {puerto} está en uso")
                puertos_ok = False
            else:
                print(f"   ✅ Puerto {puerto} está libre")
        except Exception as e:
            print(f"   ❌ Error al verificar puerto {puerto}: {e}")
            puertos_ok = False
    
    return puertos_ok

def verificar_base_datos():
    """Verificar archivos de base de datos"""
    print(f"\n📊 Verificación de Base de Datos:")
    
    archivos_db = [
        'belgrano_tickets.db',
        '../belgrano_ahorro.db'
    ]
    
    db_ok = True
    for archivo_db in archivos_db:
        if os.path.exists(archivo_db):
            size = os.path.getsize(archivo_db)
            print(f"   ✅ {archivo_db} existe ({size} bytes)")
        else:
            print(f"   ⚠️ {archivo_db} no existe (se creará automáticamente)")
            db_ok = False
    
    return db_ok

def verificar_dependencias():
    """Verificar archivo de dependencias"""
    print(f"\n📦 Verificación de Dependencias:")
    
    if os.path.exists('requirements_ticketera.txt'):
        with open('requirements_ticketera.txt', 'r') as f:
            contenido = f.read()
        
        dependencias_requeridas = [
            'Flask',
            'Flask-SocketIO',
            'Flask-SQLAlchemy',
            'Flask-Login'
        ]
        
        dependencias_ok = True
        for dep in dependencias_requeridas:
            if dep in contenido:
                print(f"   ✅ {dep}")
            else:
                print(f"   ❌ {dep} - FALTANTE")
                dependencias_ok = False
        
        return dependencias_ok
    else:
        print(f"   ❌ requirements_ticketera.txt no existe")
        return False

def test_build_docker():
    """Probar el build de Docker de la ticketera"""
    print(f"\n🏗️ Probando Build de Docker:")
    
    try:
        print("   🔄 Construyendo imagen...")
        result = subprocess.run(
            ['docker', 'build', '-f', 'Dockerfile', '-t', 'belgrano-ticketera-test', '..'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("   ✅ Build exitoso!")
            return True
        else:
            print("   ❌ Error en el build:")
            print(f"      {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Timeout en el build")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🎫 VERIFICACIÓN DE BELGRANO TICKETS DOCKER")
    print("=" * 60)
    
    # Verificar archivos
    archivos_ok = verificar_archivos_ticketera()
    
    # Verificar Docker
    docker_ok = verificar_docker()
    docker_compose_ok = verificar_docker_compose()
    
    # Verificar imagen
    imagen_ok = verificar_imagen_docker()
    
    # Verificar puertos
    puertos_ok = verificar_puertos()
    
    # Verificar base de datos
    db_ok = verificar_base_datos()
    
    # Verificar dependencias
    dependencias_ok = verificar_dependencias()
    
    # Probar build (opcional)
    build_ok = True
    if all([archivos_ok, docker_ok, docker_compose_ok]):
        build_ok = test_build_docker()
    
    print(f"\n📋 RESUMEN DE VERIFICACIÓN:")
    print("=" * 40)
    
    checks = [
        ("Archivos", archivos_ok),
        ("Docker", docker_ok),
        ("Docker Compose", docker_compose_ok),
        ("Imagen", imagen_ok),
        ("Puertos", puertos_ok),
        ("Base de Datos", db_ok),
        ("Dependencias", dependencias_ok),
        ("Build", build_ok)
    ]
    
    total_checks = len(checks)
    passed_checks = sum(1 for _, ok in checks if ok)
    
    for check_name, check_ok in checks:
        status = "✅" if check_ok else "❌"
        print(f"   {status} {check_name}")
    
    print(f"\n📊 Resultado: {passed_checks}/{total_checks} verificaciones exitosas")
    
    if passed_checks == total_checks:
        print(f"\n🎉 ¡Todo está listo para ejecutar Belgrano Tickets!")
        print(f"\n🚀 Comandos para iniciar:")
        print(f"   1. docker-compose up --build")
        print(f"   2. O ejecutar: start_ticketera.bat")
        print(f"\n📱 La ticketera estará disponible en: http://localhost:5001")
    else:
        print(f"\n⚠️ Hay problemas que necesitan resolverse antes de continuar")
        print(f"\n🔧 Acciones recomendadas:")
        if not docker_ok:
            print(f"   - Instalar Docker Desktop")
        if not archivos_ok:
            print(f"   - Verificar archivos faltantes")
        if not puertos_ok:
            print(f"   - Liberar puertos en uso")
        if not build_ok:
            print(f"   - Revisar errores de build")

if __name__ == "__main__":
    main()
