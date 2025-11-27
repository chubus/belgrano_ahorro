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
        
        # Generar nombre único
        public_id = f"belgrano_ahorro/{entity_type}/{uuid.uuid4()}"
        
        # Subir a Cloudinary
        upload_result = cloudinary.uploader.upload(
            img_byte_arr,
            public_id=public_id,
            folder=f"belgrano_ahorro/{entity_type}",
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
