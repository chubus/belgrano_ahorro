#!/usr/bin/env python3
"""
Script para crear belgrano_tickets/devops_routes.py con código correcto
Copia la lógica de procesamiento de imágenes de devops/routes.py
"""
import sys

# Leer archivo corrupto
with open('belgrano_tickets/devops_routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Código correcto para la sección de crear producto
CODIGO_CORRECTO = """            # Crear producto usando el gestor DevOps
            producto_data = {
                'nombre': nombre,
                'precio': precio_float,
                'categoria': categoria,
                'negocio': negocio,
                'descripcion': request.form.get('descripcion', ''),
                'imagen': request.form.get('imagen', ''),
                'activo': True
            }

            # Procesar imagen si se subió
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file and file.filename:
                    if save_uploaded_file:
                        image_url, error = save_uploaded_file(file, 'product', 0)
                        if image_url:
                            # CORRECCIÓN: Guardar URL en image_url, no en imagen
                            producto_data['image_url'] = image_url
                            producto_data['imagen'] = file.filename
                            logger.info(f"✅ Imagen subida para nuevo producto: {image_url}")
                        else:
                            logger.error(f"❌ Error subiendo imagen: {error}")
                            flash(f'Error subiendo imagen: {error}', 'warning')
                    else:
                        logger.error("❌ save_uploaded_file no disponible")
                        flash('Sistema de subida de imágenes no disponible', 'warning')
            
            if devops_manager:
                success, message = devops_manager.create_producto(producto_data)
                if success:
                    flash(f'Producto "{nombre}" creado exitosamente', 'success')
                    logger.info(f"Producto creado desde DevOps: {nombre}")
"""

# Encontrar donde insertar (después de "except ValueError:")
new_lines = []
skip_until = None

for i, line in enumerate(lines):
    # Si estamos saltando líneas corruptas
    if skip_until and i < skip_until:
        continue
    
    # Detectar inicio de sección corrupta
    if i >= 760 and i <= 770 and "'negocio': negocio," in line:
        # Agregar líneas hasta aquí
        new_lines.append(line)
        # Insertar código correcto
        # Primero, retroceder para eliminar la línea que acabamos de agregar
        new_lines.pop()
        # Buscar el inicio del dict producto_data
        j = i
        while j > 0 and 'producto_data = {' not in lines[j]:
            j -= 1
        
        # Retroceder new_lines hasta esa posición
        while len(new_lines) > 0 and 'producto_data = {' not in new_lines[-1]:
            new_lines.pop()
        if len(new_lines) > 0:
            new_lines.pop()  # Quitar la línea "producto_data = {"
        
        # Agregar código correcto
        for code_line in CODIGO_CORRECTO.split('\n'):
            new_lines.append(code_line + '\n')
        
        # Saltar hasta encontrar "else:" después de la corrupción
        skip_until = i + 1
        while skip_until < len(lines) and 'else:' not in lines[skip_until]:
            skip_until += 1
        continue
    
    new_lines.append(line)

# Guardar
print("Guardando belgrano_tickets/devops_routes.py...")
with open('belgrano_tickets/devops_routes.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Archivo creado con código correcto")
print("\nVerificando...")

# Verificar
with open('belgrano_tickets/devops_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if "producto_data['image_url'] = image_url" in content:
        print("✅ Código de image_url encontrado")
    else:
        print("❌ Código de image_url NO encontrado")
    
    if "producto_data['imagen'] = file.filename" in content:
        print("✅ Código de imagen filename encontrado")
    else:
        print("❌ Código de imagen filename NO encontrado")
