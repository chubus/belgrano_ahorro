#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Simple: Crear producto con imagen via API
"""
import os
import sys
import io
import requests
from PIL import Image

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv('devops/.env')
except:
    pass

BELGRANO_URL = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
DEVOPS_USER = os.getenv('DEVOPS_USERNAME', 'devops')
DEVOPS_PASS = os.getenv('DEVOPS_PASSWORD', 'DevOps2025!Secure')

print("="*60)
print("TEST: Crear producto con imagen")
print("="*60)
print(f"URL: {BELGRANO_URL}\n")

# 1. Login
print("1. Login en DevOps...")
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
    print(f"[ERROR] {e}")
    sys.exit(1)

# 2. Crear imagen
print("2. Creando imagen de prueba...")
img = Image.new('RGB', (400, 400), color='green')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)
print("[OK] Imagen creada\n")

# 3. Subir producto
print("3. Subiendo producto con imagen...")
producto_nombre = f"Test Cloudinary {os.urandom(3).hex()}"

files = {'imagen_file': ('test.jpg', img_bytes, 'image/jpeg')}
data = {
    'nombre': producto_nombre,
    'descripcion': 'Test de Cloudinary',
    'precio': '50.00',
    'categoria': 'Test',
    'negocio_id': '1',
    'stock': '5',
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
        print("[OK] Producto creado\n")
    else:
        print(f"[ERROR] HTTP {upload_resp.status_code}\n")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}\n")
    sys.exit(1)

# 4. Verificar
print("4. Verificando en API...")
import time
time.sleep(2)

try:
    api_resp = requests.get(
        f"{BELGRANO_URL}/api/productos",
        headers={'Authorization': f'Bearer {API_KEY}', 'X-API-Key': API_KEY},
        timeout=30
    )
    
    if api_resp.status_code != 200:
        print(f"[ERROR] API respondio {api_resp.status_code}")
        sys.exit(1)
    
    productos = api_resp.json().get('data', [])
    test_producto = next((p for p in productos if p.get('nombre') == producto_nombre), None)
    
    if not test_producto:
        print(f"[ERROR] Producto '{producto_nombre}' no encontrado")
        sys.exit(1)
    
    print(f"[OK] Producto encontrado:")
    print(f"    ID: {test_producto.get('id')}")
    print(f"    Nombre: {test_producto.get('nombre')}")
    
    imagen = test_producto.get('imagen', '')
    image_url = test_producto.get('image_url', '')
    
    print(f"    imagen: {imagen if imagen else '[VACIO]'}")
    print(f"    image_url: {image_url if image_url else '[VACIO]'}")
    
    if image_url and 'cloudinary.com' in image_url:
        print("\n[OK] CLOUDINARY FUNCIONA!")
        print(f"    URL: {image_url}")
        
        # Verificar URL accesible
        img_check = requests.head(image_url, timeout=5)
        if img_check.status_code == 200:
            print("    [OK] Imagen accesible")
        else:
            print(f"    [WARN] Imagen no accesible: HTTP {img_check.status_code}")
    else:
        print("\n[ERROR] CLOUDINARY NO FUNCIONA")
        print("    El producto se creo pero sin image_url de Cloudinary")
        print("\nPosibles causas:")
        print("  1. Cloudinary no configurado en Render")
        print("  2. Error en el codigo de devops_routes.py")
        print("  3. Ver logs del servicio DevOps en Render")
        
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
