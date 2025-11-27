#!/usr/bin/env python3
"""
Script para agregar lógica de subida de imágenes a devops_routes.py
"""

# Leer el archivo backup
with open('belgrano_tickets/devops_routes.py.backup', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Insertar import después de la línea 17
import_code = """
# Import image upload utility
try:
    from devops.image_utils import save_uploaded_file
    logger.info("✅ Image upload utility imported successfully")
except ImportError as e:
    save_uploaded_file = None
    logger.warning(f"⚠️ devops.image_utils not available - image upload will not work: {e}")

"""

# Código para subida de logo de negocio (después de línea 641)
negocio_upload_code = """
            # Procesar logo si se subió
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename:
                    if save_uploaded_file:
                        image_url, error = save_uploaded_file(file, 'business', 0)
                        if image_url:
                            negocio_data['logo'] = image_url
                            logger.info(f"✅ Logo subido para nuevo negocio: {image_url}")
                        else:
                            logger.error(f"❌ Error subiendo logo: {error}")
                            flash(f'Error subiendo logo: {error}', 'warning')
                    else:
                        logger.error("❌ save_uploaded_file no disponible")
                        flash('Sistema de subida de imágenes no disponible', 'warning')
            
"""

# Código para subida de imagen de producto (después de línea 747)
producto_upload_code = """
            # Procesar imagen si se subió
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file and file.filename:
                    if save_uploaded_file:
                        image_url, error = save_uploaded_file(file, 'product', 0)
                        if image_url:
                            producto_data['imagen'] = image_url
                            logger.info(f"✅ Imagen subida para nuevo producto: {image_url}")
                        else:
                            logger.error(f"❌ Error subiendo imagen: {error}")
                            flash(f'Error subiendo imagen: {error}', 'warning')
                    else:
                        logger.error("❌ save_uploaded_file no disponible")
                        flash('Sistema de subida de imágenes no disponible', 'warning')
            
"""

# Ruta de actualización de producto
update_route_code = """
@devops_bp.route('/productos/<int:id>', methods=['POST'])
@devops_login_required
def actualizar_producto(id):
    \"\"\"Actualizar un producto existente\"\"\"
    try:
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '').strip()
        categoria = request.form.get('categoria', '').strip()
        negocio = request.form.get('negocio', '').strip()
        
        if not all([nombre, precio, categoria, negocio]):
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('devops.gestion_productos'))
            
        try:
            precio_float = float(precio)
        except ValueError:
            flash('El precio debe ser un número válido', 'error')
            return redirect(url_for('devops.gestion_productos'))
            
        producto_data = {
            'nombre': nombre,
            'precio': precio_float,
            'categoria': categoria,
            'negocio': negocio,
            'descripcion': request.form.get('descripcion', ''),
            'activo': request.form.get('activo') == 'on',
            'destacado': request.form.get('destacado') == 'on'
        }

        # Procesar imagen si se subió
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename:
                if save_uploaded_file:
                    image_url, error = save_uploaded_file(file, 'product', id)
                    if image_url:
                        producto_data['imagen'] = image_url
                        logger.info(f"✅ Imagen actualizada para producto {id}: {image_url}")
                    else:
                        logger.error(f"❌ Error subiendo imagen: {error}")
                        flash(f'Error subiendo imagen: {error}', 'warning')
        
        if devops_manager:
            success, message = devops_manager.update_producto(id, producto_data)
            if success:
                flash(f'Producto "{nombre}" actualizado exitosamente', 'success')
            else:
                flash(f'Error al actualizar producto: {message}', 'error')
        else:
            flash('Gestor DevOps no disponible', 'error')
            
    except Exception as e:
        logger.error(f"Error actualizando producto {id}: {e}")
        flash('Error interno al actualizar el producto', 'error')
        
    return redirect(url_for('devops.gestion_productos'))

"""

# Construir nuevo archivo
new_lines = []

for i, line in enumerate(lines, 1):
    new_lines.append(line)
    
    # Después de línea 17 (imports)
    if i == 17:
        new_lines.append(import_code)
    
    # Después de línea 641 (negocio_data)
    elif i == 641:
        new_lines.append(negocio_upload_code)
    
    # Después de línea 747 (producto_data)
    elif i == 747:
        new_lines.append(producto_upload_code)
    
    # Después de línea 768 (fin de gestion_productos)
    elif i == 768:
        new_lines.append(update_route_code)

# Escribir archivo nuevo
with open('belgrano_tickets/devops_routes_FIXED.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Archivo devops_routes_FIXED.py creado exitosamente")
print("📝 Ahora renombra:")
print("   1. devops_routes.py -> devops_routes_OLD.py")
print("   2. devops_routes_FIXED.py -> devops_routes.py")
