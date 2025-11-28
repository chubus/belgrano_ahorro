#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migracion de Imagenes a Cloudinary
Migra productos que tienen 'imagen' pero no 'image_url'
"""
import os
import sys
import io
import requests
from PIL import Image

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("MIGRACION: Imagenes a Cloudinary")
print("="*60)

# Verificar Cloudinary
try:
    import cloudinary
    import cloudinary.uploader
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("[ERROR] Cloudinary no configurado")
        print("\nConfigura las siguientes variables de entorno:")
        print("  CLOUDINARY_CLOUD_NAME")
        print("  CLOUDINARY_API_KEY")
        print("  CLOUDINARY_API_SECRET")
        sys.exit(1)
    
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    print(f"[OK] Cloudinary configurado: {cloud_name}\n")
except ImportError:
    print("[ERROR] Modulo cloudinary no instalado")
    print("Instalar con: pip install cloudinary")
    sys.exit(1)

# Conectar a base de datos
try:
    from db_abstraction import get_db_connection
    from sqlalchemy import text
    
    session = get_db_connection()
    print("[OK] Conexion a base de datos establecida\n")
except Exception as e:
    print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
    sys.exit(1)

# Buscar productos sin image_url
try:
    query = text("""
        SELECT id, nombre, imagen, image_url
        FROM productos
        WHERE imagen IS NOT NULL 
          AND imagen != ''
          AND (image_url IS NULL OR image_url = '')
          AND activo = TRUE
        ORDER BY id
    """)
    
    result = session.execute(query)
    productos = result.fetchall()
    
    print(f"Productos a migrar: {len(productos)}")
    print("-"*60)
    
    if len(productos) == 0:
        print("\n[OK] No hay productos para migrar")
        session.close()
        sys.exit(0)
    
    # Mostrar productos
    for p in productos:
        print(f"  ID {p[0]}: {p[1]} - imagen: {p[2]}")
    
    print("\n" + "="*60)
    respuesta = input("Continuar con la migracion? (s/n): ")
    
    if respuesta.lower() != 's':
        print("Migracion cancelada")
        session.close()
        sys.exit(0)
    
    print("\nIniciando migracion...\n")
    
    # Migrar cada producto
    exitosos = 0
    fallidos = 0
    
    for p in productos:
        producto_id = p[0]
        nombre = p[1]
        imagen = p[2]
        
        print(f"Procesando ID {producto_id}: {nombre}")
        print(f"  Imagen actual: {imagen}")
        
        try:
            # Intentar descargar la imagen si es URL
            if imagen.startswith('http'):
                print(f"  Descargando imagen desde URL...")
                img_resp = requests.get(imagen, timeout=10)
                if img_resp.status_code != 200:
                    print(f"  [ERROR] No se pudo descargar imagen: HTTP {img_resp.status_code}")
                    fallidos += 1
                    continue
                
                img_bytes = io.BytesIO(img_resp.content)
            else:
                # Si no es URL, asumir que es un archivo local (probablemente no exista)
                print(f"  [WARN] '{imagen}' no es URL, no se puede migrar automaticamente")
                fallidos += 1
                continue
            
            # Validar que sea imagen
            try:
                img = Image.open(img_bytes)
                img_bytes.seek(0)
            except:
                print(f"  [ERROR] El archivo no es una imagen valida")
                fallidos += 1
                continue
            
            # Subir a Cloudinary
            print(f"  Subiendo a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                img_bytes,
                folder="belgrano_ahorro/product",
                resource_type="image",
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            
            secure_url = upload_result.get('secure_url')
            
            if not secure_url:
                print(f"  [ERROR] No se obtuvo URL de Cloudinary")
                fallidos += 1
                continue
            
            print(f"  [OK] Subida exitosa: {secure_url[:60]}...")
            
            # Actualizar base de datos
            update_query = text("""
                UPDATE productos
                SET image_url = :image_url,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            """)
            
            session.execute(update_query, {
                'image_url': secure_url,
                'id': producto_id
            })
            session.commit()
            
            print(f"  [OK] Base de datos actualizada")
            exitosos += 1
            
        except Exception as e:
            print(f"  [ERROR] Error procesando producto: {e}")
            fallidos += 1
            session.rollback()
        
        print()
    
    print("="*60)
    print("RESUMEN DE MIGRACION")
    print("="*60)
    print(f"Total procesados: {len(productos)}")
    print(f"Exitosos: {exitosos}")
    print(f"Fallidos: {fallidos}")
    
    if exitosos > 0:
        print("\n[OK] Migracion completada")
        print("Verifica que las imagenes se muestren en Belgrano Ahorro")
    
except Exception as e:
    print(f"[ERROR] Error en migracion: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
