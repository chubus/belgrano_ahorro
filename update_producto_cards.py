#!/usr/bin/env python3
"""
Script para actualizar las tarjetas de productos con el nuevo botón circular de carrito
"""

import os
import re

def actualizar_botones_carrito():
    """Actualizar todos los botones de carrito en los templates"""
    
    # Archivos a actualizar
    archivos = [
        'templates/index.html',
        'templates/categoria.html',
        'templates/negocio.html'
    ]
    
    # Patrón para encontrar botones de carrito
    patron_viejo = r'<button type="button" class="btn btn-sm btn-primary" onclick="agregarAlCarrito\(\'{{ producto\.id }}\'\)">\s*🛒\s*</button>'
    patron_nuevo = '<button type="button" class="btn-cart-circle" onclick="agregarAlCarrito(\'{{ producto.id }}\')" title="Agregar al carrito">\n                            🛒\n                        </button>'
    
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"Actualizando {archivo}...")
            
            # Leer el archivo
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Reemplazar todos los botones
            contenido_nuevo = re.sub(patron_viejo, patron_nuevo, contenido)
            
            # Escribir el archivo actualizado
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(contenido_nuevo)
            
            print(f"✅ {archivo} actualizado")
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")

if __name__ == "__main__":
    print("🔄 Actualizando botones de carrito...")
    actualizar_botones_carrito()
    print("✅ Proceso completado")
