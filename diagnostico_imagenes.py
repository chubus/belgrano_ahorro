#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar el sistema de imágenes
"""

import os
import sys

print("=" * 60)
print("DIAGNÓSTICO DEL SISTEMA DE IMÁGENES")
print("=" * 60)

# 1. Verificar configuración
print("\n1. VERIFICANDO CONFIGURACIÓN...")
try:
    from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
    print(f"   ✅ UPLOAD_FOLDER: {UPLOAD_FOLDER}")
    print(f"   ✅ ALLOWED_EXTENSIONS: {ALLOWED_EXTENSIONS}")
    print(f"   ✅ MAX_CONTENT_LENGTH: {MAX_CONTENT_LENGTH / (1024*1024)}MB")
    
    # Verificar si el directorio existe
    if os.path.exists(UPLOAD_FOLDER):
        print(f"   ✅ Directorio uploads existe")
        # Listar subdirectorios
        subdirs = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
        print(f"   ✅ Subdirectorios: {subdirs}")
    else:
        print(f"   ❌ Directorio uploads NO existe")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar app.config
print("\n2. VERIFICANDO APP.CONFIG...")
try:
    from app_unificado import app
    print(f"   ✅ app.config['UPLOAD_FOLDER']: {app.config.get('UPLOAD_FOLDER', 'NO CONFIGURADO')}")
    print(f"   ✅ app.config['UPLOAD_EXTENSIONS']: {app.config.get('UPLOAD_EXTENSIONS', 'NO CONFIGURADO')}")
    print(f"   ✅ app.config['MAX_CONTENT_LENGTH']: {app.config.get('MAX_CONTENT_LENGTH', 'NO CONFIGURADO')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar devops/image_utils.py
print("\n3. VERIFICANDO DEVOPS IMAGE_UTILS...")
try:
    from devops.image_utils import save_uploaded_file
    print(f"   ✅ save_uploaded_file importado correctamente")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Verificar endpoint /media/
print("\n4. VERIFICANDO ENDPOINT /media/...")
try:
    from app_unificado import app
    rules = [str(rule) for rule in app.url_map.iter_rules() if '/media/' in str(rule)]
    if rules:
        print(f"   ✅ Endpoint /media/ registrado: {rules}")
    else:
        print(f"   ❌ Endpoint /media/ NO registrado")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Verificar API routes
print("\n5. VERIFICANDO API ROUTES...")
try:
    from app_unificado import app
    api_routes = [str(rule) for rule in app.url_map.iter_rules() if '/api/' in str(rule)]
    print(f"   ✅ Rutas API encontradas: {len(api_routes)}")
    for route in sorted(api_routes)[:5]:
        print(f"      - {route}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Verificar base de datos
print("\n6. VERIFICANDO BASE DE DATOS...")
try:
    from api_belgrano_ahorro import get_db_connection
    from sqlalchemy import text
    
    session = get_db_connection()
    # Verificar si existe la columna image_url en productos
    result = session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'productos' AND column_name = 'image_url'
    """))
    if result.fetchone():
        print(f"   ✅ Columna 'image_url' existe en tabla 'productos'")
    else:
        print(f"   ❌ Columna 'image_url' NO existe en tabla 'productos'")
    session.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
