#!/usr/bin/env python3
"""
Script para actualizar todos los templates HTML para usar image_url (Base64)
en lugar de producto.imagen (ruta estática)
"""

import os
import re

def fix_image_references(file_path):
    """Actualizar referencias de imágenes en un archivo HTML"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # Patrón 1: <img src="{{ producto.imagen }}" ...>
    # Reemplazar con: {% if producto.image_url %}<img src="{{ producto.image_url }}" ...>{% elif producto.imagen %}...{% else %}...{% endif %}
    pattern1 = r'<img\s+src="{{producto\.imagen}}"\s+([^>]+)>'
    
    if re.search(pattern1, content):
        print(f"  ⚠️  Encontrado patrón simple: <img src=\"{{{{producto.imagen}}}}\"")
        # Este patrón es más complejo, mejor hacerlo manualmente
    
    # Patrón 2: Buscar bloques que solo verifican producto.imagen
    pattern2 = r'{%\s*if\s+producto\.imagen\s*%}\s*<img\s+src="{{producto\.imagen}}"'
    
    if re.search(pattern2, content):
        print(f"  ⚠️  Encontrado patrón condicional: {{% if producto.imagen %}}")
        # Reemplazar con el patrón correcto
        content = re.sub(
            r'{%\s*if\s+producto\.imagen\s*%}\s*<img\s+src="{{producto\.imagen}}"([^>]+)>\s*{%\s*else\s*%}',
            r'{% if producto.image_url %}<img src="{{ producto.image_url }}"\1>{% elif producto.imagen %}<img src="{{ producto.imagen }}"\1>{% else %}',
            content
        )
        changes_made = True
    
    # Patrón 3: Imágenes directas sin condicional
    pattern3 = r'<img\s+src="{{producto\.imagen}}"'
    
    if re.search(pattern3, content):
        print(f"  ⚠️  Encontrado imagen directa sin condicional")
        # Agregar condicional
        content = re.sub(
            r'<img\s+src="{{producto\.imagen}}"([^>]+)>',
            r'{% if producto.image_url %}<img src="{{ producto.image_url }}"\1>{% elif producto.imagen %}<img src="{{ producto.imagen }}"\1>{% else %}<div class="text-muted"><i class="fas fa-image"></i></div>{% endif %}',
            content
        )
        changes_made = True
    
    if changes_made and content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def scan_templates(base_dir):
    """Escanear todos los templates HTML"""
    templates_dir = os.path.join(base_dir, 'templates')
    
    if not os.path.exists(templates_dir):
        print(f"❌ No se encontró el directorio: {templates_dir}")
        return
    
    print(f"🔍 Escaneando templates en: {templates_dir}\n")
    
    files_to_check = [
        'index.html',
        'productos.html',
        'negocio.html',
        'categoria.html',
        'carrito.html',
        'partials/producto_card_con_cantidad.html',
    ]
    
    for file_name in files_to_check:
        file_path = os.path.join(templates_dir, file_name)
        
        if not os.path.exists(file_path):
            print(f"⏭️  Saltando (no existe): {file_name}")
            continue
        
        print(f"📄 Revisando: {file_name}")
        
        # Leer y analizar
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar referencias a producto.imagen
        if 'producto.imagen' in content or 'producto.image_url' in content:
            print(f"  ✅ Contiene referencias a imágenes")
            
            # Verificar si ya usa image_url
            if 'producto.image_url' in content:
                print(f"  ✅ Ya usa image_url")
            else:
                print(f"  ⚠️  Solo usa producto.imagen - NECESITA ACTUALIZACIÓN")
        else:
            print(f"  ⏭️  No contiene referencias a imágenes de productos")
        
        print()

if __name__ == "__main__":
    base_dir = r"c:\Users\rey_a\Documents\Belgrano_ahorro-back"
    
    print("=" * 60)
    print("ESCÁNER DE TEMPLATES - REFERENCIAS DE IMÁGENES")
    print("=" * 60)
    print()
    
    scan_templates(base_dir)
    
    print("\n" + "=" * 60)
    print("RECOMENDACIÓN:")
    print("=" * 60)
    print("""
Los templates deben usar este patrón:

{% if producto.image_url %}
    <img src="{{ producto.image_url }}" ...>
{% elif producto.imagen %}
    <img src="{{ producto.imagen }}" ...>
{% else %}
    <div class="text-muted"><i class="fas fa-image"></i></div>
{% endif %}

Esto permite:
1. Priorizar image_url (Base64 desde DevOps)
2. Fallback a imagen (ruta estática)
3. Placeholder si no hay imagen
""")
