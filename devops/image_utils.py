"""
Módulo para manejar la carga y gestión de imágenes en el sistema.
"""
import os
import uuid
import logging
import base64
from werkzeug.utils import secure_filename
from flask import jsonify
from functools import wraps
from PIL import Image, UnidentifiedImageError
import io

# Configure logging
logger = logging.getLogger(__name__)

def image_to_base64(file):
    """
    Convertir archivo de imagen a string Base64 para almacenamiento en DB
    
    Args:
        file: FileStorage object de Flask
        
    Returns:
        tuple: (base64_data_url, error_message)
               base64_data_url es un string con formato "data:image/jpeg;base64,..."
               error_message es None si no hay error
    """
    try:
        # Validar que sea una imagen válida
        file_ext = validate_image(file.stream)
        if not file_ext:
            return None, "Formato de archivo no válido. Use JPG, PNG o WebP"
        
        # Volver al inicio del archivo
        file.seek(0)
        file_data = file.read()
        
        # Validar tamaño (máximo 2MB para Base64)
        # Base64 aumenta el tamaño ~33%, así que 2MB se convierte en ~2.7MB
        max_size = 2 * 1024 * 1024  # 2MB
        if len(file_data) > max_size:
            size_mb = len(file_data) / (1024 * 1024)
            return None, f"Imagen demasiado grande ({size_mb:.1f}MB). Máximo 2MB"
        
        # Convertir a Base64
        base64_string = base64.b64encode(file_data).decode('utf-8')
        
        # Determinar MIME type
        mime_type = {
            'jpeg': 'image/jpeg',
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp'
        }.get(file_ext.lower(), 'image/jpeg')
        
        # Crear data URL (formato estándar para Base64 en HTML)
        data_url = f"data:{mime_type};base64,{base64_string}"
        
        logger.info(f"✅ Imagen convertida a Base64: {len(base64_string)} caracteres, tipo: {mime_type}")
        
        return data_url, None
        
    except Exception as e:
        logger.error(f"Error convirtiendo imagen a Base64: {e}")
        return None, f"Error procesando imagen: {str(e)}"


def validate_image(stream):
    """
    Valida que el archivo sea una imagen válida (jpg, png, webp).
    Devuelve la extensión si es válida, None en caso contrario.
    """
    try:
        # Read the first few bytes to check the image
        header = stream.read(512)
        stream.seek(0)
        
        # Try to open the image with Pillow
        image = Image.open(io.BytesIO(header))
        
        # Check if it's a supported format
        if image.format.lower() in ['jpeg', 'png', 'webp']:
            return image.format.lower()
            
        return None
    except UnidentifiedImageError:
        return None
    except Exception as e:
        logger.error(f"Error validando imagen: {e}")
        return None

def save_uploaded_file(file, entity_type, entity_id):
    """
    Guarda un archivo subido en el sistema de archivos.
    
    Args:
        file: Archivo a guardar (objeto FileStorage de Flask)
        entity_type: Tipo de entidad (business, branch, product)
        entity_id: ID de la entidad
        
    Returns:
        str: Ruta relativa al archivo guardado o None en caso de error
    """
    if entity_type not in ['business', 'branch', 'product']:
        return None, "Tipo de entidad no válido"
        
    # Validar que el archivo sea una imagen
    file_ext = validate_image(file.stream)
    if not file_ext or file_ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
        return None, "Formato de archivo no soportado. Use JPG, PNG o WebP"
        
    # Validar tamaño del archivo (máximo 5MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        return None, "El archivo es demasiado grande. Tamaño máximo: 5MB"
    
    # Crear directorio si no existe
    upload_dir = os.path.join('uploads', entity_type)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único para el archivo usando UUID completo
    filename = f"{str(uuid.uuid4())}{file_ext}"
    filepath = os.path.join(upload_dir, filename)
    
    try:
        # Guardar el archivo
        file.save(filepath)
        # Devolver ruta relativa para almacenar en la base de datos
        return filepath, None
    except Exception as e:
        logger.error(f"Error al guardar archivo: {str(e)}")
        return None, f"Error al guardar el archivo: {str(e)}"

def delete_old_image(image_path):
    """
    Elimina una imagen del sistema de archivos si existe.
    
    Args:
        image_path: Ruta relativa de la imagen a eliminar
    """
    if not image_path:
        return
        
    try:
        # Use absolute path if provided, otherwise treat as relative to current directory
        full_path = image_path if os.path.isabs(image_path) else os.path.abspath(image_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            os.remove(full_path)
    except Exception as e:
        logger.error(f"Error al eliminar archivo {image_path}: {str(e)}")

def get_image_url(image_path):
    """
    Devuelve la URL completa para acceder a una imagen.
    
    Args:
        image_path: Ruta relativa de la imagen (ej: uploads/business/uuid.jpg)
        
    Returns:
        str: URL completa de la imagen o None si no existe
    """
    if not image_path:
        return None
        
    # Verificar si la ruta ya es una URL
    if image_path.startswith(('http://', 'https://')):
        return image_path
        
    # Verificar si el archivo existe localmente
    full_path = image_path if os.path.isabs(image_path) else os.path.abspath(image_path)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        # Aún así devolver la URL, el servidor la manejará
        pass
        
    # Construir URL relativa al servidor
    return f"/devops/media/{image_path}"

def handle_image_upload(entity_type, entity_id, image_field):
    """
    Decorador para manejar la carga de imágenes en los endpoints de la API.
    
    Args:
        entity_type: Tipo de entidad (business, branch, product)
        entity_id: ID de la entidad
        image_field: Nombre del campo en el formulario que contiene la imagen
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if image_field in request.files:
                file = request.files[image_field]
                if file.filename != '':
                    # Eliminar imagen anterior si existe
                    if 'image_url' in request.form:
                        delete_old_image(request.form['image_url'])
                    
                    # Guardar nueva imagen
                    filepath, error = save_uploaded_file(file, entity_type, entity_id)
                    if error:
                        return jsonify({"error": error}), 400
                        
                    # Agregar la ruta de la imagen al form data
                    if request.form:
                        request.form = request.form.to_dict()
                        request.form['image_url'] = filepath
                    else:
                        request.form = {'image_url': filepath}
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
