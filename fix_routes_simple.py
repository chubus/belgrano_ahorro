#!/usr/bin/env python3
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Código correcto para insertar
CODIGO_IMAGEN = """            # Procesar imagen si se subió
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file and file.filename:
                    if save_uploaded_file:
                        image_url, error = save_uploaded_file(file, 'product', 0)
                        if image_url:
                            # CORRECCIÓN: Guardar URL en image_url, no en imagen
                            producto_data['image_url'] = image_url
                            producto_data['imagen'] = file.filename
                            logger.info(f"Imagen subida para nuevo producto: {image_url}")
                        else:
                            logger.error(f"Error subiendo imagen: {error}")
                            flash(f'Error subiendo imagen: {error}', 'warning')
                    else:
                        logger.error("save_uploaded_file no disponible")
                        flash('Sistema de subida de imagenes no disponible', 'warning')
            
"""

archivo = 'belgrano_tickets/devops_routes.py'

print(f"Leyendo {archivo}...")
with open(archivo, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar el bloque corrupto
# Patrón: desde "producto_data = {" hasta "if devops_manager:"
import re

# Patrón para encontrar la sección corrupta
pattern = r"(producto_data = \{\s+.*?'activo': True\s+\})\s+(# Procesar imagen.*?)(if devops_manager:)"

# Reemplazo
replacement = r"\1\n\n" + CODIGO_IMAGEN + r"            \3"

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if new_content == content:
    print("No se encontró el patrón para reemplazar")
    print("Intentando enfoque alternativo...")
    
    # Buscar línea específica
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Si encontramos la línea problemática
        if "'activo': True" in line and i > 760 and i < 780:
            # Buscar el cierre del dict
            if i+1 < len(lines) and lines[i+1].strip() == '}':
                new_lines.append(lines[i+1])  # Agregar }
                i += 1
                # Saltar líneas corruptas hasta encontrar "if devops_manager:"
                while i+1 < len(lines) and 'if devops_manager:' not in lines[i+1]:
                    i += 1
                # Insertar código correcto
                new_lines.append('')
                new_lines.extend(CODIGO_IMAGEN.split('\n'))
        i += 1
    
    new_content = '\n'.join(new_lines)

# Guardar
print(f"Guardando {archivo}...")
with open(archivo, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] Archivo corregido")
