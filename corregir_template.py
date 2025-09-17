#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el template index.html
Reemplaza producto.atributo por producto.get('atributo', 'default')
"""

import re

def corregir_template():
    """Corregir el template para usar sintaxis de diccionario"""
    
    # Leer el archivo
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Patrones a corregir
    patrones = [
        # producto.nombre -> producto.get('nombre', 'Sin nombre')
        (r'producto\.nombre', "producto.get('nombre', 'Sin nombre')"),
        # producto.precio -> producto.get('precio', 0)
        (r'producto\.precio', "producto.get('precio', 0)"),
        # producto.stock -> producto.get('stock', 0)
        (r'producto\.stock', "producto.get('stock', 0)"),
        # producto.negocio -> producto.get('negocio', 'Sin negocio')
        (r'producto\.negocio', "producto.get('negocio', 'Sin negocio')"),
        # producto.destacado -> producto.get('destacado', False)
        (r'producto\.destacado', "producto.get('destacado', False)"),
        # producto.precio_original -> producto.get('precio_original', 0)
        (r'producto\.precio_original', "producto.get('precio_original', 0)"),
        # producto.categoria -> producto.get('categoria', 'Sin categoría')
        (r'producto\.categoria', "producto.get('categoria', 'Sin categoría')"),
        # producto.descripcion -> producto.get('descripcion', 'Sin descripción')
        (r'producto\.descripcion', "producto.get('descripcion', 'Sin descripción')"),
    ]
    
    # Aplicar correcciones
    contenido_corregido = contenido
    for patron, reemplazo in patrones:
        contenido_corregido = re.sub(patron, reemplazo, contenido_corregido)
    
    # Escribir el archivo corregido
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(contenido_corregido)
    
    print("✅ Template corregido exitosamente")
    print("   - Todos los accesos a atributos del producto ahora usan sintaxis de diccionario")
    print("   - Se agregaron valores por defecto para evitar errores")

if __name__ == "__main__":
    corregir_template()
