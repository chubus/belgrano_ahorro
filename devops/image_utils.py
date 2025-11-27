#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para manejo de imágenes con Cloudinary
Sube imágenes a Cloudinary para almacenamiento permanente
"""

import os
import io
import uuid
import logging
from PIL import Image
from PIL.Image import Resampling
import cloudinary
import cloudinary.uploader
import cloudinary.api

logger = logging.getLogger(__name__)

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def save_uploaded_file(file, entity_type, entity_id):
    """
    Sube un archivo a Cloudinary y retorna la URL pública.
    
    Args:
        file: FileStorage object de Flask
        entity_type: Tipo de entidad (business, branch, product)
        entity_id: ID de la entidad
        
    Returns:
        tuple: (public_url, error_message)
    """
    if entity_type not in ['business', 'branch', 'product']:
        return None, "Tipo de entidad no válido"
    
    try:
        # Validar que el archivo sea una imagen
        try:
            image = Image.open(file)
        except Exception:
            return None, "El archivo no es una imagen válida."
        
        # Convertir y optimizar
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Redimensionar (max 1200x1200)
        image.thumbnail((1200, 1200), Resampling.LANCZOS)
        
        # Convertir a bytes en formato JPEG
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr.seek(0)
        
        # Generar nombre único (solo UUID, la carpeta se especifica en folder)
        unique_id = str(uuid.uuid4())
        
        # Subir a Cloudinary
        upload_result = cloudinary.uploader.upload(
            img_byte_arr,
            public_id=unique_id,  # Solo el UUID
            folder=f"belgrano_ahorro/{entity_type}",  # La carpeta completa
            resource_type="image",
            format="jpg",
            transformation=[
                {'width': 1200, 'height': 1200, 'crop': 'limit'},
                {'quality': 'auto:good'}
            ]
        )
        
        # Obtener URL segura
        secure_url = upload_result.get('secure_url')
        
        if not secure_url:
            return None, "Error al obtener URL de Cloudinary"
        
        logger.info(f"✅ Imagen subida a Cloudinary: {secure_url}")
        
        return secure_url, None
        
    except Exception as e:
        logger.error(f"❌ Error subiendo a Cloudinary: {e}")
        return None, f"Error al subir imagen: {str(e)}"


def delete_cloudinary_image(image_url):
    """
    Elimina una imagen de Cloudinary dado su URL.
    
    Args:
        image_url: URL de la imagen en Cloudinary
        
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        # Extraer public_id del URL
        # URL format: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{format}
        if 'cloudinary.com' not in image_url:
            return False
        
        parts = image_url.split('/')
        # Encontrar el índice de 'upload'
        try:
            upload_index = parts.index('upload')
            # El public_id está después de upload y la versión
            public_id_parts = parts[upload_index + 2:]  # Skip 'upload' y versión
            public_id = '/'.join(public_id_parts).rsplit('.', 1)[0]  # Remover extensión
            
            # Eliminar de Cloudinary
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') == 'ok':
                logger.info(f"✅ Imagen eliminada de Cloudinary: {public_id}")
                return True
            else:
                logger.warning(f"⚠️ No se pudo eliminar imagen de Cloudinary: {result}")
                return False
                
        except (ValueError, IndexError) as e:
            logger.error(f"❌ Error parseando URL de Cloudinary: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error eliminando imagen de Cloudinary: {e}")
        return False


# Funciones de compatibilidad con el código existente
def delete_old_image(image_path):
    """
    Alias para delete_cloudinary_image para compatibilidad.
    """
    if not image_path:
        return False
    return delete_cloudinary_image(image_path)


def get_image_url(image_path):
    """
    Retorna la URL de la imagen.
    En Cloudinary, la URL ya es pública, así que solo la retornamos.
    """
    return image_path if image_path else None


def validate_image(file_stream):
    """
    Valida que el archivo sea una imagen válida.
    Retorna True si es válida, False en caso contrario.
    """
    try:
        # Guardar posición actual
        current_position = file_stream.tell()
        
        # Intentar abrir con Pillow
        image = Image.open(file_stream)
        
        # Restaurar posición
        file_stream.seek(current_position)
        
        return True
    except Exception as e:
        logger.error(f"❌ Error validando imagen: {e}")
        # Restaurar posición en caso de error
        try:
            file_stream.seek(current_position)
        except:
            pass
        return False


def image_to_base64(file):
    """
    DEPRECATED: Esta función ya no se usa con Cloudinary.
    Se mantiene solo para compatibilidad con código legacy.
    
    En lugar de convertir a Base64, ahora subimos directamente a Cloudinary.
    Esta función retorna un error sugiriendo usar save_uploaded_file.
    """
    logger.warning("⚠️ image_to_base64 está deprecated. Use save_uploaded_file en su lugar.")
    return None, "Esta función está deprecated. Las imágenes ahora se suben a Cloudinary automáticamente."
