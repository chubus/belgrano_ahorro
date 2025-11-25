#!/usr/bin/env python3
"""
Script para actualizar TODOS los templates HTML automáticamente
Reemplaza producto.imagen con el patrón correcto que prioriza image_url
"""

import os
import re

def update_image_references(content):
    """Actualizar todas las referencias de imágenes en el contenido"""
    
    # Patrón 1: <img src="{{ producto.imagen }}" class="..." alt="...">
    pattern1 = r'<img\s+src="\{\{\s*producto\.imagen\s*\}\}"\s+class="([^"]+)"\s+alt="([^"]+)">'
    replacement1 = r'{% if producto.image_url %}<img src="{{ producto.image_url }}" class="\1" alt="\2">{% elif producto.imagen %}<img src="{{ producto.imagen }}" class="\1" alt="\2">{% else %}<div class="d-flex align-items-center justify-content-center bg-light h-100"><i class="fas fa-image fa-2x text-muted"></i></div>{% endif %}'
    
    content = re.sub(pattern1, replacement1, content)
    
    # Patrón 2: <img src="{{ producto.imagen }}" alt="..." class="...">
    pattern2 = r'<img\s+src="\{\{\s*producto\.imagen\s*\}\}"\s+alt="([^"]+)"\s+class="([^"]+)">'
    replacement2 = r'{% if producto.image_url %}<img src="{{ producto.image_url }}" alt="\1" class="\2">{% elif producto.imagen %}<img src="{{ producto.imagen }}" alt="\1" class="\2">{% else %}<div class="d-flex align-items-center justify-content-center bg-light h-100"><i class="fas fa-image fa-2x text-muted"></i></div>{% endif %}'
    
    content = re.sub(pattern2, replacement2, content)
    
    # Patrón 3: <img src="{{ item.producto.imagen }}" ... (para carrito)
    pattern3 = r'<img\s+src="\{\{\s*item\.producto\.imagen\s*\}\}"\s+class="([^"]+)"([^>]*)>'
    replacement3 = r'{% if item.producto.image_url %}<img src="{{ item.producto.image_url }}" class="\1"\2>{% elif item.producto.imagen %}<img src="{{ item.producto.imagen }}" class="\1"\2>{% else %}<div class="d-flex align-items-center justify-content-center bg-light h-100"><i class="fas fa-image fa-2x text-muted"></i></div>{% endif %}'
    
    content = re.sub(pattern3, replacement3, content)
    
    return content

def update_template_file(file_path):
    """Actualizar un archivo de template"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        updated_content = update_image_references(original_content)
        
        if updated_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
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
    
    print("=" * 70)
    print("ACTUALIZANDO TEMPLATES - CORRECCIÓN DE IMÁGENES")
    print("=" * 70)
    print()
    
    updated_count = 0
    total_count = 0
    
    for file_name in files_to_update:
        file_path = os.path.join(base_dir, file_name)
        total_count += 1
        
        if not os.path.exists(file_path):
            print(f"⏭️  [{total_count}/{len(files_to_update)}] Saltando (no existe): {file_name}")
            continue
        
        print(f"📄 [{total_count}/{len(files_to_update)}] Procesando: {file_name}")
        
        if update_template_file(file_path):
            print(f"  ✅ ACTUALIZADO - Imágenes corregidas")
            updated_count += 1
        else:
            print(f"  ⏭️  Sin cambios necesarios")
        
        print()
    
    print("=" * 70)
    print(f"✅ Proceso completado: {updated_count}/{len(files_to_update)} archivos actualizados")
    print("=" * 70)
    print()
    print("📊 Resumen:")
    print(f"  ✅ Archivos actualizados: {updated_count}")
    print(f"  ⏭️  Archivos sin cambios: {len(files_to_update) - updated_count}")
    print()
    print("🎯 Próximo paso: Verificar en el navegador que las imágenes se muestran correctamente")

if __name__ == "__main__":
    main()
