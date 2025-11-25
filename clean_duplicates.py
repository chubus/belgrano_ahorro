#!/usr/bin/env python3
"""
Script para limpiar y corregir las referencias de imágenes duplicadas
"""

import os
import re

def clean_duplicated_conditionals(content):
    """Limpiar condicionales duplicados"""
    
    # Patrón para encontrar y limpiar duplicados
    # {% if producto.image_url %}...{% elif producto.imagen %}{% if producto.image_url %}...{% elif producto.imagen %}...{% else %}...{% endif %}{% else %}...{% endif %}
    
    # Simplemente reemplazar todo el patrón duplicado con uno limpio
    pattern = r'{% if producto\.image_url %}(<img[^>]+>){% elif producto\.imagen %}{% if producto\.image_url %}<img[^>]+>{% elif producto\.imagen %}(<img[^>]+>){% else %}(<div[^>]+>[^<]+</div>){% endif %}{% else %}<div[^>]+>[^<]+</div>{% endif %}'
    
    replacement = r'{% if producto.image_url %}\1{% elif producto.imagen %}\2{% else %}\3{% endif %}'
    
    content = re.sub(pattern, replacement, content)
    
    # Para item.producto
    pattern2 = r'{% if item\.producto\.image_url %}(<img[^>]+>){% elif item\.producto\.imagen %}{% if item\.producto\.image_url %}<img[^>]+>{% elif item\.producto\.imagen %}(<img[^>]+>){% else %}(<div[^>]+>[^<]+</div>){% endif %}{% else %}<div[^>]+>[^<]+</div>{% endif %}'
    
    replacement2 = r'{% if item.producto.image_url %}\1{% elif item.producto.imagen %}\2{% else %}\3{% endif %}'
    
    content = re.sub(pattern2, replacement2, content)
    
    return content

def fix_template_file(file_path):
    """Corregir un archivo de template"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        updated_content = clean_duplicated_conditionals(original_content)
        
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
    
    files_to_fix = [
        'index.html',
        'negocio.html',
        'categoria.html',
        'carrito.html',
    ]
    
    print("=" * 70)
    print("LIMPIANDO TEMPLATES - ELIMINANDO DUPLICADOS")
    print("=" * 70)
    print()
    
    fixed_count = 0
    
    for file_name in files_to_fix:
        file_path = os.path.join(base_dir, file_name)
        
        if not os.path.exists(file_path):
            print(f"⏭️  Saltando (no existe): {file_name}")
            continue
        
        print(f"📄 Procesando: {file_name}")
        
        if fix_template_file(file_path):
            print(f"  ✅ LIMPIADO - Duplicados eliminados")
            fixed_count += 1
        else:
            print(f"  ⏭️  Sin cambios necesarios")
        
        print()
    
    print("=" * 70)
    print(f"✅ Proceso completado: {fixed_count} archivos limpiados")
    print("=" * 70)

if __name__ == "__main__":
    main()
