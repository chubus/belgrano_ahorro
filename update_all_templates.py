#!/usr/bin/env python3
"""
Script para actualizar TODOS los templates HTML automáticamente
Reemplaza producto.imagen con el patrón correcto que prioriza image_url
"""

import os
import re

def update_template(file_path):
    """Actualizar un template HTML"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patrón: <img src="{{ producto.imagen }}" class="..." alt="...">
    # Reemplazar con el patrón completo que prioriza image_url
    
    pattern = r'<img\s+src="{{producto\.imagen}}"\s+class="([^"]+)"\s+alt="([^"]+)">'
    
    replacement = r'''{% if producto.image_url %}<img src="{{ producto.image_url }}" class="\1" alt="\2">{% elif producto.imagen %}<img src="{{ producto.imagen }}" class="\1" alt="\2">{% else %}<div class="d-flex align-items-center justify-content-center bg-light h-100"><i class="fas fa-image fa-2x text-muted"></i></div>{% endif %}'''
    
    content = re.sub(pattern, replacement, content)
    
    # También manejar variaciones con atributos en diferente orden
    pattern2 = r'<img\s+src="{{producto\.imagen}}"\s+alt="([^"]+)"\s+class="([^"]+)">'
    replacement2 = r'''{% if producto.image_url %}<img src="{{ producto.image_url }}" alt="\1" class="\2">{% elif producto.imagen %}<img src="{{ producto.imagen }}" alt="\1" class="\2">{% else %}<div class="d-flex align-items-center justify-content-center bg-light h-100"><i class="fas fa-image fa-2x text-muted"></i></div>{% endif %}'''
    
    content = re.sub(pattern2, replacement2, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    base_dir = r"c:\Users\rey_a\Documents\Belgrano_ahorro-back\templates"
    
    files_to_update = [
        'index.html',
        'negocio.html',
        'categoria.html',
        'carrito.html',
        'partials/producto_card_con_cantidad.html',
    ]
    
    print("=" * 60)
    print("ACTUALIZANDO TEMPLATES - REFERENCIAS DE IMÁGENES")
    print("=" * 60)
    print()
    
    updated_count = 0
    
    for file_name in files_to_update:
        file_path = os.path.join(base_dir, file_name)
        
        if not os.path.exists(file_path):
            print(f"⏭️  Saltando (no existe): {file_name}")
            continue
        
        print(f"📄 Procesando: {file_name}")
        
        if update_template(file_path):
            print(f"  ✅ ACTUALIZADO")
            updated_count += 1
        else:
            print(f"  ⏭️  Sin cambios necesarios")
        
        print()
    
    print("=" * 60)
    print(f"✅ Proceso completado: {updated_count} archivos actualizados")
    print("=" * 60)

if __name__ == "__main__":
    main()
