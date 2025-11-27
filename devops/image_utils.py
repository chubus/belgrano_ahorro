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
        # Permitir cualquier formato que Pillow pueda abrir
        try:
            image = Image.open(file)
            format_detected = image.format.lower() if image.format else 'jpeg'
        except Exception:
            return None, "El archivo no es una imagen válida o está corrupto."
            
        # Volver al inicio del archivo
        file.seek(0)
        
        # Procesar imagen con Pillow para estandarizar
        # Convertir a RGB si es necesario
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
            
        # Redimensionar si es muy grande (max 1024x1024 para Base64)
        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Guardar en buffer como JPEG optimizado
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        file_data = buffer.read()
        
        # Validar tamaño (máximo 3MB para Base64 después de optimizar)
        max_size = 3 * 1024 * 1024
        if len(file_data) > max_size:
            size_mb = len(file_data) / (1024 * 1024)
            return None, f"Imagen demasiado grande ({size_mb:.1f}MB). Máximo 3MB"
        
        # Convertir a Base64
        base64_string = base64.b64encode(file_data).decode('utf-8')
        
        # Siempre devolver como JPEG
        mime_type = 'image/jpeg'
        
        # Crear data URL
        data_url = f"data:{mime_type};base64,{base64_string}"
        
        logger.info(f"✅ Imagen procesada y convertida a Base64: {len(base64_string)} chars")
        
        return data_url, None
        
    except Exception as e:
        logger.error(f"Error convirtiendo imagen a Base64: {e}")
        return None, f"Error procesando imagen: {str(e)}"


def validate_image(stream):
    """
    Valida que el archivo sea una imagen válida soportada por Pillow.
    Devuelve el formato detectado o 'jpeg' por defecto si es válida.
    """
    try:
        # Read the first few bytes to check the image
        header = stream.read(512)
        stream.seek(0)
        
        # Try to open the image with Pillow
        image = Image.open(io.BytesIO(header))
        return image.format.lower() if image.format else 'jpeg'
    except UnidentifiedImageError:
        return None
    except Exception as e:
        logger.error(f"Error validando imagen: {e}")
        return None

def save_uploaded_file(file, entity_type, entity_id):
    """
    Guarda un archivo subido en el sistema de archivos, convirtiéndolo a formato web.
    """
    if entity_type not in ['business', 'branch', 'product']:
        return None, "Tipo de entidad no válido"
        
    # Validar que el archivo sea una imagen
    try:
        image = Image.open(file)
    except Exception:
        return None, "El archivo no es una imagen válida."
        
    # Crear directorio si no existe
    upload_dir = os.path.join('uploads', entity_type)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único (siempre .jpg porque convertiremos)
    filename = f"{str(uuid.uuid4())}.jpg"
    filepath = os.path.join(upload_dir, filename)
    
    try:
        # Convertir y optimizar
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
            
        # Redimensionar (max 1200x1200 para archivos en disco)
        image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        # Guardar como JPEG optimizado
        image.save(filepath, format='JPEG', quality=85, optimize=True)
        
        # Devolver ruta relativa
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
