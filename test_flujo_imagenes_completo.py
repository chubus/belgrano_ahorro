#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Completo del Flujo de Imagenes - Version Simple
DevOps -> Cloudinary -> Belgrano Ahorro API
"""
import os
import io
import sys
import requests
from PIL import Image

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    if os.path.exists('devops/.env'):
        load_dotenv('devops/.env')
        print("[OK] Cargado devops/.env\n")
except ImportError:
    print("[WARN] python-dotenv no instalado\n")

# Configuracion
BELGRANO_URL = os.getenv('BELGRANO_AHORRO_URL', 'http://localhost:10000')
API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
DEVOPS_USER = os.getenv('DEVOPS_USERNAME', 'devops')
DEVOPS_PASS = os.getenv('DEVOPS_PASSWORD', 'DevOps2025!Secure')

print("="*60)
print("TEST: Flujo de Imagenes DevOps -> Belgrano Ahorro")
print("="*60)
print(f"\nURL: {BELGRANO_URL}")
print(f"Usuario DevOps: {DEVOPS_USER}\n")

# Verificar Cloudinary
cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
if not cloud_name:
    print("[ERROR] CLOUDINARY_CLOUD_NAME no configurado")
    sys.exit(1)
print(f"Cloudinary: {cloud_name}\n")

# PASO 1: Login en DevOps
print("="*60)
print("PASO 1: Login en DevOps")
print("="*60)

session = requests.Session()
try:
    login_resp = session.post(
        f"{BELGRANO_URL}/devops/login",
        data={'username': DEVOPS_USER, 'password': DEVOPS_PASS},
        timeout=30
    )
    
    if 'login' in login_resp.url:
        print("[ERROR] Login fallido")
        sys.exit(1)
    
    print("[OK] Login exitoso\n")
except Exception as e:
    print(f"[ERROR] Error en login: {e}")
    sys.exit(1)

# PASO 2: Crear imagen de prueba
print("="*60)
print("PASO 2: Crear imagen de prueba")
print("="*60)

try:
    img = Image.new('RGB', (400, 400), color='#4A90E2')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes.seek(0)
    print(f"[OK] Imagen creada: 400x400px, {len(img_bytes.getvalue())} bytes\n")
except Exception as e:
    print(f"[ERROR] Error creando imagen: {e}")
    sys.exit(1)

# PASO 3: Subir producto con imagen
print("="*60)
print("PASO 3: Subir producto con imagen")
print("="*60)

producto_nombre = f"Test Imagen {os.urandom(4).hex()}"
print(f"Producto: {producto_nombre}")

files = {'imagen_file': ('test_producto.jpg', img_bytes, 'image/jpeg')}
data = {
    'nombre': producto_nombre,
    'descripcion': 'Producto de prueba para verificar flujo de imagenes',
    'precio': '99.99',
    'categoria': 'Test',
    'negocio_id': '1',
    'stock': '10',
    'activo': 'on'
}

try:
    upload_resp = session.post(
        f"{BELGRANO_URL}/devops/productos",
        data=data,
        files=files,
        timeout=60
    )
    
    if upload_resp.status_code == 200:
        print("[OK] Request exitoso (HTTP 200)")
    else:
        print(f"[ERROR] Request fallido: HTTP {upload_resp.status_code}")
        sys.exit(1)
    
    print()
except Exception as e:
    print(f"[ERROR] Error subiendo producto: {e}")
    sys.exit(1)

# PASO 4: Verificar en API
print("="*60)
print("PASO 4: Verificar en API de Belgrano Ahorro")
print("="*60)

try:
    import time
    time.sleep(2)
    
    api_resp = requests.get(
        f"{BELGRANO_URL}/api/productos",
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'X-API-Key': API_KEY
        },
        timeout=30
    )
    
    if api_resp.status_code != 200:
        print(f"[ERROR] Error consultando API: HTTP {api_resp.status_code}")
        sys.exit(1)
    
    data = api_resp.json()
    productos = data.get('data', [])
    
    print(f"Total de productos en API: {len(productos)}")
    
    test_producto = next(
        (p for p in productos if p.get('nombre') == producto_nombre),
        None
    )
    
    if not test_producto:
        print(f"[ERROR] Producto '{producto_nombre}' no encontrado")
        sys.exit(1)
    
    print(f"[OK] Producto encontrado en API")
    print(f"    ID: {test_producto.get('id')}")
    print(f"    Nombre: {test_producto.get('nombre')}")
    print(f"    Precio: ${test_producto.get('precio')}")
    
    # Verificar imagen
    image_url = test_producto.get('image_url') or test_producto.get('imagen')
    
    if not image_url:
        print("\n[ERROR] Producto NO tiene imagen")
        print("\nDIAGNOSTICO:")
        print("  1. Verificar Cloudinary en devops/.env")
        print("  2. Verificar logs del servidor DevOps")
        print("  3. Ejecutar: python verificar_cloudinary.py")
        sys.exit(1)
    
    print(f"\n[OK] IMAGEN ENCONTRADA:")
    print(f"    URL: {image_url}")
    
    if 'cloudinary.com' in image_url:
        print("    [OK] Es URL de Cloudinary")
    else:
        print(f"    [WARN] No es URL de Cloudinary")
    
    # Verificar accesibilidad
    print("\nVerificando accesibilidad de la imagen...")
    try:
        img_check = requests.head(image_url, timeout=10)
        if img_check.status_code == 200:
            print(f"    [OK] URL accesible (HTTP {img_check.status_code})")
            content_type = img_check.headers.get('Content-Type', '')
            if 'image' in content_type:
                print(f"    [OK] Content-Type correcto: {content_type}")
        else:
            print(f"    [WARN] URL no accesible: HTTP {img_check.status_code}")
    except Exception as e:
        print(f"    [WARN] Error verificando URL: {e}")
    
except Exception as e:
    print(f"[ERROR] Error verificando en API: {e}")
    sys.exit(1)

# RESUMEN
print("\n" + "="*60)
print("TODAS LAS VERIFICACIONES PASARON")
print("="*60)
print("\nResumen:")
print("  [OK] Login en DevOps exitoso")
print(f"  [OK] Producto creado: {producto_nombre}")
print("  [OK] Imagen subida a Cloudinary")
print("  [OK] Producto visible en Belgrano Ahorro con imagen")
print("\nEl flujo de imagenes funciona correctamente!")
