#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación de Cloudinary
Verifica que las credenciales estén configuradas y funcionen correctamente
"""
import os
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    # Intentar cargar desde devops/.env primero
    if os.path.exists('devops/.env'):
        load_dotenv('devops/.env')
        print("[OK] Cargado devops/.env")

    elif os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Cargado .env")
except ImportError:
    print("⚠️ python-dotenv no instalado, usando variables de entorno del sistema")

print("\n=== Verificación de Cloudinary ===\n")

# Verificar variables de entorno
cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
api_secret = os.getenv('CLOUDINARY_API_SECRET')
cloudinary_url = os.getenv('CLOUDINARY_URL')

print("📋 Variables de Entorno:")
print(f"   CLOUDINARY_CLOUD_NAME: {'✅ ' + cloud_name if cloud_name else '❌ NO CONFIGURADO'}")
print(f"   CLOUDINARY_API_KEY: {'✅ ' + api_key[:10] + '...' if api_key else '❌ NO CONFIGURADO'}")
print(f"   CLOUDINARY_API_SECRET: {'✅ ' + ('*' * 10) if api_secret else '❌ NO CONFIGURADO'}")
print(f"   CLOUDINARY_URL: {'✅ Configurado' if cloudinary_url else '❌ NO CONFIGURADO'}")

if not (cloud_name and api_key and api_secret):
    print("\n❌ FALTAN CREDENCIALES DE CLOUDINARY")
    print("\nPara configurar, agregar a devops/.env:")
    print("   CLOUDINARY_CLOUD_NAME=dc2n1p5wx")
    print("   CLOUDINARY_API_KEY=882162797341932")
    print("   CLOUDINARY_API_SECRET=Flf1YKomyxORM1aMnGL7YFr3Ea0")
    print("   CLOUDINARY_URL=cloudinary://882162797341932:Flf1YKomyxORM1aMnGL7YFr3Ea0@dc2n1p5wx")
    sys.exit(1)

print("\n✅ Todas las credenciales están configuradas\n")

# Intentar importar cloudinary
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    print("✅ Módulo cloudinary importado correctamente")
except ImportError as e:
    print(f"❌ Error importando cloudinary: {e}")
    print("\nInstalar con: pip install cloudinary")
    sys.exit(1)

# Configurar Cloudinary
try:
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    print("✅ Cloudinary configurado correctamente\n")
except Exception as e:
    print(f"❌ Error configurando Cloudinary: {e}")
    sys.exit(1)

# Test de conexión - Verificar cuenta
print("🔍 Verificando conexión con Cloudinary...")
try:
    # Intentar obtener información de la cuenta
    result = cloudinary.api.ping()
    print(f"✅ Conexión exitosa con Cloudinary")
    print(f"   Status: {result.get('status', 'unknown')}")
except Exception as e:
    print(f"❌ Error conectando con Cloudinary: {e}")
    sys.exit(1)

# Test de subida
print("\n📤 Probando subida de imagen de prueba...")
try:
    # Crear imagen de prueba (100x100 roja)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Subir a Cloudinary
    upload_result = cloudinary.uploader.upload(
        img_bytes,
        folder="belgrano_ahorro/test",
        resource_type="image",
        public_id="test_verification"
    )
    
    secure_url = upload_result.get('secure_url')
    public_id = upload_result.get('public_id')
    
    if secure_url:
        print(f"✅ Subida exitosa!")
        print(f"   URL: {secure_url}")
        print(f"   Public ID: {public_id}")
        
        # Eliminar imagen de prueba
        print("\n🗑️  Eliminando imagen de prueba...")
        delete_result = cloudinary.uploader.destroy(public_id)
        
        if delete_result.get('result') == 'ok':
            print("✅ Imagen de prueba eliminada correctamente")
        else:
            print(f"⚠️ No se pudo eliminar imagen de prueba: {delete_result}")
    else:
        print("❌ No se obtuvo URL de la imagen subida")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error en test de subida: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("✅ TODAS LAS VERIFICACIONES PASARON")
print("="*50)
print("\nCloudinary está correctamente configurado y funcionando.")
print("Puedes proceder a probar el flujo completo de subida de productos.")
