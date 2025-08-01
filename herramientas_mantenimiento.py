#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERRAMIENTAS DE MANTENIMIENTO - BELGRANO AHORRO
================================================

Este script proporciona herramientas para facilitar el mantenimiento
del sistema de productos, ofertas y categorías.

USO:
    python herramientas_mantenimiento.py [comando]

COMANDOS DISPONIBLES:
    - verificar_productos: Verifica que todos los productos estén correctos
    - verificar_imagenes: Verifica que todas las imágenes existan
    - agregar_producto: Agrega un nuevo producto al sistema
    - agregar_negocio: Agrega un nuevo negocio al sistema
    - agregar_categoria: Agrega una nueva categoría al sistema
    - crear_oferta: Crea una nueva oferta
    - estadisticas: Muestra estadísticas del sistema
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def cargar_datos():
    """Cargar datos del archivo productos.json"""
    try:
        with open('productos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo productos.json")
        return None
    except json.JSONDecodeError:
        print("❌ Error: El archivo productos.json tiene formato inválido")
        return None

def guardar_datos(datos):
    """Guardar datos en el archivo productos.json"""
    try:
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print("✅ Datos guardados correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al guardar datos: {e}")
        return False

def verificar_productos():
    """Verificar que todos los productos estén correctos"""
    print("🔍 Verificando productos...")
    datos = cargar_datos()
    if not datos:
        return
    
    productos = datos.get('productos', [])
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    
    errores = []
    advertencias = []
    
    for producto in productos:
        # Verificar campos obligatorios
        campos_obligatorios = ['id', 'nombre', 'precio', 'negocio', 'categoria', 'imagen']
        for campo in campos_obligatorios:
            if campo not in producto:
                errores.append(f"Producto {producto.get('id', 'sin_id')}: Falta campo '{campo}'")
        
        # Verificar que el negocio existe
        if producto.get('negocio') not in negocios:
            errores.append(f"Producto {producto.get('id')}: Negocio '{producto.get('negocio')}' no existe")
        
        # Verificar que la categoría existe
        if producto.get('categoria') not in categorias:
            errores.append(f"Producto {producto.get('id')}: Categoría '{producto.get('categoria')}' no existe")
        
        # Verificar que la imagen existe
        imagen_path = producto.get('imagen', '').replace('/static/', 'static/')
        if not os.path.exists(imagen_path):
            advertencias.append(f"Producto {producto.get('id')}: Imagen '{imagen_path}' no existe")
    
    print(f"📊 Total de productos: {len(productos)}")
    print(f"❌ Errores encontrados: {len(errores)}")
    print(f"⚠️  Advertencias: {len(advertencias)}")
    
    if errores:
        print("\n❌ ERRORES:")
        for error in errores:
            print(f"  - {error}")
    
    if advertencias:
        print("\n⚠️  ADVERTENCIAS:")
        for advertencia in advertencias:
            print(f"  - {advertencia}")
    
    if not errores and not advertencias:
        print("✅ Todos los productos están correctos")

def verificar_imagenes():
    """Verificar que todas las imágenes existan"""
    print("🖼️ Verificando imágenes...")
    datos = cargar_datos()
    if not datos:
        return
    
    productos = datos.get('productos', [])
    imagenes_faltantes = []
    
    for producto in productos:
        imagen_path = producto.get('imagen', '').replace('/static/', 'static/')
        if not os.path.exists(imagen_path):
            imagenes_faltantes.append({
                'producto': producto.get('id'),
                'imagen': imagen_path
            })
    
    print(f"📊 Total de productos: {len(productos)}")
    print(f"❌ Imágenes faltantes: {len(imagenes_faltantes)}")
    
    if imagenes_faltantes:
        print("\n❌ IMÁGENES FALTANTES:")
        for item in imagenes_faltantes:
            print(f"  - Producto {item['producto']}: {item['imagen']}")
    else:
        print("✅ Todas las imágenes existen")

def agregar_producto():
    """Agregar un nuevo producto al sistema"""
    print("➕ Agregando nuevo producto...")
    datos = cargar_datos()
    if not datos:
        return
    
    # Obtener información del producto
    producto_id = input("ID del producto: ").strip()
    nombre = input("Nombre del producto: ").strip()
    descripcion = input("Descripción: ").strip()
    precio = float(input("Precio: "))
    negocio = input("Negocio (ID): ").strip()
    categoria = input("Categoría (ID): ").strip()
    imagen = input("Ruta de la imagen: ").strip()
    stock = int(input("Stock: "))
    
    # Crear el producto
    nuevo_producto = {
        "id": producto_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "negocio": negocio,
        "categoria": categoria,
        "imagen": imagen,
        "stock": stock,
        "activo": True,
        "destacado": False,
        "oferta": False
    }
    
    # Agregar al sistema
    datos['productos'].append(nuevo_producto)
    
    if guardar_datos(datos):
        print("✅ Producto agregado correctamente")

def agregar_negocio():
    """Agregar un nuevo negocio al sistema"""
    print("🏪 Agregando nuevo negocio...")
    datos = cargar_datos()
    if not datos:
        return
    
    # Obtener información del negocio
    negocio_id = input("ID del negocio: ").strip()
    nombre = input("Nombre del negocio: ").strip()
    descripcion = input("Descripción: ").strip()
    logo = input("Ruta del logo: ").strip()
    color = input("Color (hex): ").strip()
    
    # Crear el negocio
    nuevo_negocio = {
        "id": len(datos['negocios']) + 1,
        "nombre": nombre,
        "descripcion": descripcion,
        "logo": logo,
        "color": color,
        "activo": True
    }
    
    # Agregar al sistema
    datos['negocios'][negocio_id] = nuevo_negocio
    
    if guardar_datos(datos):
        print("✅ Negocio agregado correctamente")

def agregar_categoria():
    """Agregar una nueva categoría al sistema"""
    print("🏷️ Agregando nueva categoría...")
    datos = cargar_datos()
    if not datos:
        return
    
    # Obtener información de la categoría
    categoria_id = input("ID de la categoría: ").strip()
    nombre = input("Nombre de la categoría: ").strip()
    descripcion = input("Descripción: ").strip()
    icono = input("Icono (emoji): ").strip()
    
    # Crear la categoría
    nueva_categoria = {
        "id": len(datos['categorias']) + 1,
        "nombre": nombre,
        "descripcion": descripcion,
        "icono": icono
    }
    
    # Agregar al sistema
    datos['categorias'][categoria_id] = nueva_categoria
    
    if guardar_datos(datos):
        print("✅ Categoría agregada correctamente")

def crear_oferta():
    """Crear una nueva oferta"""
    print("🔥 Creando nueva oferta...")
    datos = cargar_datos()
    if not datos:
        return
    
    # Obtener información de la oferta
    oferta_id = input("ID de la oferta: ").strip()
    nombre = input("Nombre de la oferta: ").strip()
    descripcion = input("Descripción: ").strip()
    imagen = input("Ruta de la imagen: ").strip()
    fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
    fecha_fin = input("Fecha de fin (YYYY-MM-DD): ").strip()
    
    # Crear la oferta
    nueva_oferta = {
        "id": oferta_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "imagen": imagen,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "activa": True,
        "productos": []
    }
    
    # Agregar al sistema
    datos['ofertas'][oferta_id] = nueva_oferta
    
    if guardar_datos(datos):
        print("✅ Oferta creada correctamente")

def estadisticas():
    """Mostrar estadísticas del sistema"""
    print("📊 Estadísticas del sistema...")
    datos = cargar_datos()
    if not datos:
        return
    
    productos = datos.get('productos', [])
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    ofertas = datos.get('ofertas', {})
    
    print(f"📦 Total de productos: {len(productos)}")
    print(f"🏪 Total de negocios: {len(negocios)}")
    print(f"🏷️ Total de categorías: {len(categorias)}")
    print(f"🔥 Total de ofertas: {len(ofertas)}")
    
    # Productos activos
    productos_activos = [p for p in productos if p.get('activo', True)]
    print(f"✅ Productos activos: {len(productos_activos)}")
    
    # Productos destacados
    productos_destacados = [p for p in productos if p.get('destacado', False)]
    print(f"⭐ Productos destacados: {len(productos_destacados)}")
    
    # Productos en oferta
    productos_oferta = [p for p in productos if p.get('oferta', False)]
    print(f"💰 Productos en oferta: {len(productos_oferta)}")
    
    # Ofertas activas
    ofertas_activas = [o for o in ofertas.values() if isinstance(o, dict) and o.get('activa', False)]
    print(f"🔥 Ofertas activas: {len(ofertas_activas)}")
    
    # Negocios activos
    negocios_activos = [n for n in negocios.values() if isinstance(n, dict) and n.get('activo', True)]
    print(f"🏪 Negocios activos: {len(negocios_activos)}")

def mostrar_ayuda():
    """Mostrar ayuda del script"""
    print("""
🛠️ HERRAMIENTAS DE MANTENIMIENTO - BELGRANO AHORRO
====================================================

USO:
    python herramientas_mantenimiento.py [comando]

COMANDOS DISPONIBLES:
    verificar_productos    - Verifica que todos los productos estén correctos
    verificar_imagenes    - Verifica que todas las imágenes existan
    agregar_producto      - Agrega un nuevo producto al sistema
    agregar_negocio       - Agrega un nuevo negocio al sistema
    agregar_categoria     - Agrega una nueva categoría al sistema
    crear_oferta          - Crea una nueva oferta
    estadisticas          - Muestra estadísticas del sistema
    ayuda                 - Muestra esta ayuda

EJEMPLOS:
    python herramientas_mantenimiento.py verificar_productos
    python herramientas_mantenimiento.py estadisticas
    python herramientas_mantenimiento.py agregar_producto
""")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    
    comandos = {
        'verificar_productos': verificar_productos,
        'verificar_imagenes': verificar_imagenes,
        'agregar_producto': agregar_producto,
        'agregar_negocio': agregar_negocio,
        'agregar_categoria': agregar_categoria,
        'crear_oferta': crear_oferta,
        'estadisticas': estadisticas,
        'ayuda': mostrar_ayuda
    }
    
    if comando in comandos:
        comandos[comando]()
    else:
        print(f"❌ Comando '{comando}' no reconocido")
        mostrar_ayuda()

if __name__ == "__main__":
    main() 