#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la configuración de DevOps
Ejecutar: python devops/verificar_config.py
"""

import os
import sys

# Agregar ruta del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_paths = [
        os.path.join(current_dir, '.env'),
        os.path.join(current_dir, 'env', '.env'),
        os.path.join(parent_dir, '.env'),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ Archivo .env cargado desde: {env_path}")
            break
    else:
        print("⚠️  No se encontró archivo .env")
except ImportError:
    print("⚠️  python-dotenv no instalado, usando solo variables de entorno del sistema")

print("\n" + "=" * 60)
print("🔍 Verificación de Configuración DevOps")
print("=" * 60)
print()

# Verificar variables obligatorias
belgrano_url = os.getenv('BELGRANO_AHORRO_URL', '')
belgrano_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '')

print("📋 Variables de Entorno:")
print(f"   BELGRANO_AHORRO_URL: {belgrano_url if belgrano_url else '❌ NO CONFIGURADA'}")
print(f"   BELGRANO_AHORRO_API_KEY: {'✅ Configurada (' + '*' * min(len(belgrano_api_key), 10) + ')' if belgrano_api_key else '❌ NO CONFIGURADA'}")

print()
print("🔧 Estado de Configuración:")
if belgrano_url and belgrano_api_key:
    print("   ✅ Configuración completa - El dashboard debería funcionar")
else:
    print("   ❌ Configuración incompleta - El dashboard NO funcionará")
    if not belgrano_url:
        print("      - Falta: BELGRANO_AHORRO_URL")
    if not belgrano_api_key:
        print("      - Falta: BELGRANO_AHORRO_API_KEY")

print()
print("💡 Solución:")
if not belgrano_url or not belgrano_api_key:
    print("   1. Edita el archivo devops/.env")
    print("   2. O ejecuta: python devops/configurar_env.py")
    print("   3. O configura las variables de entorno del sistema")
    print("   4. Reinicia la aplicación")
else:
    print("   ✅ Todo está configurado correctamente")

print()
print("=" * 60)

