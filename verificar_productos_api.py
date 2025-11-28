#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar productos via API
Consulta la API de Belgrano Ahorro para ver que imagenes tienen los productos
"""
import os
import sys
import requests
import json

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv('devops/.env')
    print("[OK] Variables cargadas\n")
except:
    pass

BELGRANO_URL = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

print("="*60)
print("DIAGNOSTICO: Productos via API")
print("="*60)
print(f"URL: {BELGRANO_URL}\n")

try:
    print("Consultando API de productos...")
    resp = requests.get(
        f"{BELGRANO_URL}/api/productos",
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'X-API-Key': API_KEY
        },
        timeout=30
    )
    
    if resp.status_code != 200:
        print(f"[ERROR] API respondio con codigo {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)
    
    data = resp.json()
    productos = data.get('data', [])
    
    print(f"[OK] {len(productos)} productos encontrados\n")
    print("-"*60)
    
    # Mostrar ultimos 10 productos
    for p in productos[-10:]:
        print(f"\nID: {p.get('id')}")
        print(f"  Nombre: {p.get('nombre')}")
        print(f"  Precio: ${p.get('precio')}")
        
        imagen = p.get('imagen', '')
        image_url = p.get('image_url', '')
        
        print(f"  Campo 'imagen': {imagen if imagen else '[VACIO]'}")
        print(f"  Campo 'image_url': {image_url if image_url else '[VACIO]'}")
        
        if image_url:
            if 'cloudinary.com' in image_url:
                print("  [OK] Tiene URL de Cloudinary")
                # Verificar si la URL es accesible
                try:
                    img_check = requests.head(image_url, timeout=5)
                    if img_check.status_code == 200:
                        print(f"  [OK] URL accesible (HTTP {img_check.status_code})")
                    else:
                        print(f"  [ERROR] URL no accesible (HTTP {img_check.status_code})")
                except:
                    print("  [WARN] No se pudo verificar URL")
            else:
                print(f"  [WARN] No es URL de Cloudinary: {image_url[:50]}...")
        elif imagen:
            print(f"  [WARN] Solo tiene 'imagen': {imagen[:50]}...")
        else:
            print("  [ERROR] NO TIENE IMAGEN")
    
    print("\n" + "="*60)
    
    # Estadisticas
    total = len(productos)
    con_image_url = sum(1 for p in productos if p.get('image_url'))
    con_imagen = sum(1 for p in productos if p.get('imagen'))
    con_cloudinary = sum(1 for p in productos if p.get('image_url') and 'cloudinary.com' in p.get('image_url', ''))
    
    print("ESTADISTICAS:")
    print(f"  Total productos: {total}")
    print(f"  Con 'image_url': {con_image_url} ({con_image_url*100//total if total > 0 else 0}%)")
    print(f"  Con 'imagen': {con_imagen} ({con_imagen*100//total if total > 0 else 0}%)")
    print(f"  Con URL de Cloudinary: {con_cloudinary} ({con_cloudinary*100//total if total > 0 else 0}%)")
    print(f"  Sin imagen: {total - max(con_image_url, con_imagen)}")
    
    # Buscar producto "eso" especificamente
    print("\n" + "="*60)
    print("BUSCANDO PRODUCTO 'eso':")
    print("-"*60)
    
    producto_eso = next((p for p in productos if 'eso' in p.get('nombre', '').lower()), None)
    
    if producto_eso:
        print(f"\n[OK] Producto encontrado:")
        print(json.dumps(producto_eso, indent=2, ensure_ascii=False))
    else:
        print("\n[WARN] No se encontro producto con nombre 'eso'")
        print("\nProductos disponibles:")
        for p in productos[-5:]:
            print(f"  - {p.get('nombre')}")
    
except requests.Timeout:
    print("[ERROR] Timeout - El servidor tardo mas de 30 segundos en responder")
    print("El servidor de Render probablemente esta en modo sleep.")
    print("Visita https://belgranoahorro-aliq.onrender.com primero para despertarlo.")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
