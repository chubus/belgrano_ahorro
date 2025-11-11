#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que la API key esté configurada correctamente
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
            print(f"✅ Variables cargadas desde: {env_path}")
            break
except ImportError:
    print("⚠️  python-dotenv no instalado, usando variables del sistema")

print("\n" + "="*60)
print("🔍 VERIFICACIÓN DE API KEY")
print("="*60)

# Verificar API key
expected_key = "belgrano_ahorro_api_key_2025"
belgrano_url = os.getenv('BELGRANO_AHORRO_URL', '')
belgrano_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '')

print(f"\n📋 Configuración:")
print(f"   BELGRANO_AHORRO_URL: {belgrano_url if belgrano_url else '❌ NO CONFIGURADA'}")
print(f"   BELGRANO_AHORRO_API_KEY: {'✅ Configurada' if belgrano_api_key else '❌ NO CONFIGURADA'}")

if belgrano_api_key:
    if belgrano_api_key == expected_key:
        print(f"   ✅ API Key correcta: {expected_key}")
    else:
        print(f"   ⚠️  API Key diferente a la esperada")
        print(f"      Esperada: {expected_key}")
        print(f"      Actual: {belgrano_api_key[:20]}...")

# Verificar en app_unificado.py
print(f"\n📋 Verificación en código:")
try:
    # Verificar que app_unificado.py use la API key correcta
    app_unificado_path = os.path.join(parent_dir, 'app_unificado.py')
    if os.path.exists(app_unificado_path):
        with open(app_unificado_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if expected_key in content:
                print(f"   ✅ app_unificado.py usa la API key correcta")
            else:
                print(f"   ⚠️  app_unificado.py no usa la API key esperada")
    
    # Verificar que api_belgrano_ahorro.py use la API key correcta
    api_path = os.path.join(parent_dir, 'api_belgrano_ahorro.py')
    if os.path.exists(api_path):
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if expected_key in content:
                print(f"   ✅ api_belgrano_ahorro.py usa la API key correcta")
            else:
                print(f"   ⚠️  api_belgrano_ahorro.py no usa la API key esperada")
except Exception as e:
    print(f"   ⚠️  Error verificando código: {e}")

# Verificar manager
print(f"\n📋 Verificación de Manager:")
try:
    from devops.manager_unified import devops_manager_unified
    if devops_manager_unified.is_configured():
        print(f"   ✅ Manager configurado correctamente")
        print(f"   URL: {devops_manager_unified.belgrano_url}")
        if devops_manager_unified.api_key == expected_key:
            print(f"   ✅ API Key correcta en manager")
        else:
            print(f"   ⚠️  API Key en manager: {devops_manager_unified.api_key[:20]}...")
    else:
        print(f"   ❌ Manager NO configurado")
except Exception as e:
    print(f"   ⚠️  Error verificando manager: {e}")

print("\n" + "="*60)
if belgrano_api_key == expected_key:
    print("✅ TODO CONFIGURADO CORRECTAMENTE")
else:
    print("⚠️  REVISAR CONFIGURACIÓN")
print("="*60 + "\n")

