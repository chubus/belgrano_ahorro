#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir definitivamente el template index.html
"""

import re

def corregir_template_final():
    """Corregir todos los errores de sintaxis en el template"""
    
    # Leer el archivo
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    print("🔧 Corrigiendo errores de sintaxis en el template...")
    
    # Patrones problemáticos a corregir
    patrones_problematicos = [
        # Corregir producto.get('precio', 0)_original -> producto.get('precio_original', 0)
        (r"producto\.get\('precio', 0\)_original", "producto.get('precio_original', 0)"),
        # Corregir producto.get('precio', 0)_original -> producto.get('precio_original', 0) en otros contextos
        (r"producto\.get\('precio', 0\)_original", "producto.get('precio_original', 0)"),
        # Corregir cualquier acceso a precio_original mal formado
        (r"producto\.get\('precio', \d+\)_original", "producto.get('precio_original', 0)"),
    ]
    
    # Aplicar correcciones
    contenido_corregido = contenido
    for patron, reemplazo in patrones_problematicos:
        contenido_corregido = re.sub(patron, reemplazo, contenido_corregido)
    
    # Correcciones específicas adicionales
    correcciones_especificas = [
        # Corregir accesos a atributos que pueden no existir
        ("producto.imagen", "producto.get('imagen', '/static/images/no-image.png')"),
        ("producto.id", "producto.get('id', 'unknown')"),
        ("categorias[producto.get('categoria', 'Sin categoría')].nombre", "categorias.get(producto.get('categoria', 'default'), {}).get('nombre', 'Sin categoría')"),
    ]
    
    for patron, reemplazo in correcciones_especificas:
        contenido_corregido = contenido_corregido.replace(patron, reemplazo)
    
    # Escribir el archivo corregido
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(contenido_corregido)
    
    print("✅ Template corregido exitosamente")
    print("   - Errores de sintaxis corregidos")
    print("   - Accesos a atributos seguros implementados")
    print("   - Valores por defecto agregados")

if __name__ == "__main__":
    corregir_template_final()
