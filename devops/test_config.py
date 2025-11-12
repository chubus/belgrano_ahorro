#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar que la configuración funciona correctamente
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
    print("⚠️  python-dotenv no instalado")

# Establecer valores por defecto si no existen
if not os.getenv('BELGRANO_AHORRO_URL'):
    os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
    print("✅ Establecida URL por defecto")

if not os.getenv('BELGRANO_AHORRO_API_KEY'):
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
    print("✅ Establecida API key por defecto")

print("\n" + "="*60)
print("🧪 PRUEBA DE CONFIGURACIÓN")
print("="*60)

# Probar importación del manager
try:
    from devops.manager_unified import devops_manager_unified
    
    print("\n✅ Manager importado correctamente")
    print(f"   Tipo: {type(devops_manager_unified)}")
    
    # Acceder al manager para forzar inicialización
    manager = devops_manager_unified
    print(f"   Manager accedido: {manager}")
    
    # Verificar configuración
    if hasattr(manager, 'is_configured'):
        is_configured = manager.is_configured()
        print(f"   ✅ is_configured(): {is_configured}")
        
        if is_configured:
            print(f"   ✅ URL: {manager.belgrano_url}")
            print(f"   ✅ API Key configurada: {'Sí' if manager.api_key else 'No'}")
        else:
            print("   ❌ Manager NO está configurado")
    else:
        print("   ⚠️  Manager no tiene método is_configured()")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ PRUEBA COMPLETADA")
print("="*60)

