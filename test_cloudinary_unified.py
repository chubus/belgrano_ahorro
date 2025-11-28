#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Configuración Unificada de Cloudinary
Verifica que la configuración centralizada funcione correctamente
"""
import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv('devops/.env')
    print("[OK] Variables de entorno cargadas desde devops/.env")
except Exception as e:
    print(f"[WARN] No se pudo cargar .env: {e}")

print("\n" + "="*60)
print("TEST: Configuración Unificada de Cloudinary")
print("="*60 + "\n")

# Test 1: Importar módulo
print("1. Importando cloudinary_config...")
try:
    import cloudinary_config
    print("   [OK] Módulo importado correctamente\n")
except Exception as e:
    print(f"   [ERROR] No se pudo importar: {e}\n")
    sys.exit(1)

# Test 2: Verificar variables de entorno
print("2. Verificando variables de entorno...")
cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
api_secret = os.getenv('CLOUDINARY_API_SECRET')

if cloud_name:
    print(f"   [OK] CLOUDINARY_CLOUD_NAME = {cloud_name}")
else:
    print("   [ERROR] CLOUDINARY_CLOUD_NAME no está configurado")

if api_key:
    print(f"   [OK] CLOUDINARY_API_KEY = {api_key}")
else:
    print("   [ERROR] CLOUDINARY_API_KEY no está configurado")

if api_secret:
    masked = api_secret[:4] + '***' + api_secret[-4:] if len(api_secret) > 8 else '***'
    print(f"   [OK] CLOUDINARY_API_SECRET = {masked}")
else:
    print("   [ERROR] CLOUDINARY_API_SECRET no está configurado")

print()

# Test 3: Inicializar Cloudinary
print("3. Inicializando Cloudinary...")
success = cloudinary_config.init_cloudinary()
if success:
    print("   [OK] Cloudinary inicializado correctamente\n")
else:
    print("   [ERROR] Falló la inicialización de Cloudinary\n")
    sys.exit(1)

# Test 4: Obtener estado
print("4. Obteniendo estado de configuración...")
status = cloudinary_config.get_cloudinary_status()
print(f"   Configurado: {status['configured']}")
print(f"   Cloud Name: {status['cloud_name']}")
print(f"   API Key: {status['api_key']}")
print(f"   Tiene Secret: {status['has_secret']}\n")

# Test 5: Verificar conexión
print("5. Verificando conexión con Cloudinary...")
conn_success, conn_message = cloudinary_config.verify_cloudinary_connection()
if conn_success:
    print(f"   [OK] {conn_message}\n")
else:
    print(f"   [ERROR] {conn_message}\n")

# Test 6: Probar upload (opcional)
print("6. Probando upload de imagen de prueba...")
try:
    import cloudinary.uploader
    from PIL import Image
    import io
    
    # Crear imagen de prueba
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Subir a Cloudinary
    result = cloudinary.uploader.upload(
        img_bytes,
        folder='belgrano-ahorro/test',
        public_id='test_unified_config'
    )
    
    print(f"   [OK] Imagen subida exitosamente")
    print(f"   URL: {result['secure_url']}")
    print(f"   Public ID: {result['public_id']}\n")
    
    # Eliminar imagen de prueba
    cloudinary.uploader.destroy(result['public_id'])
    print("   [OK] Imagen de prueba eliminada\n")
    
except Exception as e:
    print(f"   [ERROR] Falló el upload: {e}\n")

print("="*60)
print("RESUMEN: Todos los tests completados")
print("="*60)
