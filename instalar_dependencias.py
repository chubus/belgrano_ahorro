#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador de dependencias para el sistema de conectividad
"""

import subprocess
import sys
import os

def instalar_dependencias():
    """Instalar dependencias necesarias"""
    print("📦 INSTALANDO DEPENDENCIAS...")
    
    dependencias = [
        'requests',
        'flask',
        'werkzeug',
        'flask-login'
    ]
    
    for dep in dependencias:
        try:
            print(f"Instalando {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} instalado correctamente")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {dep}: {e}")
            return False
    
    return True

def verificar_instalacion():
    """Verificar que las dependencias están instaladas"""
    print("\n🔍 VERIFICANDO INSTALACIÓN...")
    
    dependencias = ['requests', 'flask', 'werkzeug']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep} disponible")
        except ImportError:
            print(f"❌ {dep} no disponible")
            return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INSTALADOR DE DEPENDENCIAS PARA CONECTIVIDAD")
    print("=" * 50)
    
    if instalar_dependencias():
        if verificar_instalacion():
            print("\n✅ TODAS LAS DEPENDENCIAS INSTALADAS CORRECTAMENTE")
            print("🎯 Ahora puedes ejecutar: python test_conectividad_completa.py")
        else:
            print("\n❌ ERROR EN LA VERIFICACIÓN")
    else:
        print("\n❌ ERROR EN LA INSTALACIÓN")

if __name__ == "__main__":
    main()
