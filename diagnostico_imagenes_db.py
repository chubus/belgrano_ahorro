#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostico de Imagenes en Base de Datos
Verifica que productos tienen imagenes guardadas
"""
import os
import sys

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Variables de entorno cargadas\n")
except:
    print("[WARN] No se pudieron cargar variables de entorno\n")

# Importar db_abstraction
try:
    from db_abstraction import get_db_connection
    print("[OK] db_abstraction importado\n")
except ImportError as e:
    print(f"[ERROR] No se pudo importar db_abstraction: {e}")
    sys.exit(1)

print("="*60)
print("DIAGNOSTICO: Imagenes en Base de Datos")
print("="*60)

# Conectar a base de datos
try:
    session = get_db_connection()
    print("[OK] Conexion a base de datos establecida\n")
except Exception as e:
    print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
    sys.exit(1)

# Consultar productos
try:
    from sqlalchemy import text
    
    query = text("""
        SELECT id, nombre, imagen, image_url, precio, categoria, negocio_id, activo
        FROM productos
        ORDER BY id DESC
        LIMIT 10
    """)
    
    result = session.execute(query)
    productos = result.fetchall()
    
    print(f"Ultimos {len(productos)} productos en la base de datos:")
    print("-"*60)
    
    for p in productos:
        print(f"\nID: {p[0]}")
        print(f"  Nombre: {p[1]}")
        print(f"  Precio: ${p[4]}")
        print(f"  Categoria: {p[5]}")
        print(f"  Negocio ID: {p[6]}")
        print(f"  Activo: {p[7]}")
        print(f"  Campo 'imagen': {p[2] if p[2] else '[VACIO]'}")
        print(f"  Campo 'image_url': {p[3] if p[3] else '[VACIO]'}")
        
        # Verificar si tiene imagen
        if p[3]:  # image_url
            if 'cloudinary.com' in p[3]:
                print("  [OK] Tiene URL de Cloudinary")
            else:
                print(f"  [WARN] Tiene image_url pero no es de Cloudinary: {p[3][:50]}...")
        elif p[2]:  # imagen
            print(f"  [WARN] Solo tiene campo 'imagen': {p[2][:50]}...")
        else:
            print("  [ERROR] NO TIENE IMAGEN")
    
    print("\n" + "="*60)
    
    # Estadisticas
    query_stats = text("""
        SELECT 
            COUNT(*) as total,
            COUNT(image_url) as con_image_url,
            COUNT(imagen) as con_imagen
        FROM productos
        WHERE activo = TRUE
    """)
    
    result = session.execute(query_stats)
    stats = result.fetchone()
    
    print("ESTADISTICAS:")
    print(f"  Total productos activos: {stats[0]}")
    print(f"  Con 'image_url': {stats[1]} ({stats[1]*100//stats[0] if stats[0] > 0 else 0}%)")
    print(f"  Con 'imagen': {stats[2]} ({stats[2]*100//stats[0] if stats[0] > 0 else 0}%)")
    print(f"  Sin imagen: {stats[0] - max(stats[1], stats[2])}")
    
except Exception as e:
    print(f"[ERROR] Error consultando productos: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
