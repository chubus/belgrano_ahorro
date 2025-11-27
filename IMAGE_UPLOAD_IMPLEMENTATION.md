# Image Upload Implementation for DevOps Routes

## Import Statement (Add after line 17)

```python
# Import image upload utility
try:
    from devops.image_utils import save_uploaded_file
    logger.info("✅ Image upload utility imported successfully")
except ImportError as e:
    save_uploaded_file = None
    logger.warning(f"⚠️ devops.image_utils not available - image upload will not work: {e}")
```

## Business Logo Upload (Add after line 641 in gestion_negocios)

```python
            # Procesar logo si se subió
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename:
                    if save_uploaded_file:
                        # Usamos 0 como ID temporal ya que es creación
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
```

## Product Image Upload (Add after line 747 in gestion_productos)

```python
            # Procesar imagen si se subió
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file and file.filename:
                    if save_uploaded_file:
                        # Usamos 0 como ID temporal ya que es creación
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
```

## Product Update Route (Add after line 768)

```python
@devops_bp.route('/productos/<int:id>', methods=['POST'])
@devops_login_required
def actualizar_producto(id):
    """Actualizar un producto existente"""
    try:
        # Obtener datos del formulario
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
```
