#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración Centralizada de Cloudinary
Usado por: Belgrano Ahorro, Ticketera, DevOps
"""
import os
import logging

logger = logging.getLogger(__name__)

# Importar cloudinary
try:
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    logger.warning("Cloudinary no está instalado. Instalar con: pip install cloudinary")

logger = logging.getLogger(__name__)

def init_cloudinary():
    """
    Inicializa Cloudinary con variables de entorno.
    
    Variables requeridas:
    - CLOUDINARY_CLOUD_NAME
    - CLOUDINARY_API_KEY
    - CLOUDINARY_API_SECRET
    
    Returns:
        bool: True si la configuración es válida, False si falta alguna variable
    """
    if not CLOUDINARY_AVAILABLE:
        logger.error("❌ CLOUDINARY ERROR: Módulo cloudinary no está instalado")
        return False
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    # Verificar que todas las variables estén presentes
    missing = []
    if not cloud_name:
        missing.append('CLOUDINARY_CLOUD_NAME')
    if not api_key:
        missing.append('CLOUDINARY_API_KEY')
    if not api_secret:
        missing.append('CLOUDINARY_API_SECRET')
    
    if missing:
        logger.error(f"❌ CLOUDINARY ERROR: Faltan variables de entorno: {', '.join(missing)}")
        logger.error("   Las imágenes NO funcionarán hasta que se configuren estas variables.")
        return False
    
    # Configurar Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    # Log de confirmación (sin mostrar el secret completo)
    masked_secret = api_secret[:4] + '***' + api_secret[-4:] if len(api_secret) > 8 else '***'
    logger.info(f"✅ CLOUDINARY CHECK: cloud={cloud_name} key={api_key} secret={masked_secret}")
    logger.info(f"   Cloudinary configurado correctamente para: {cloud_name}")
    
    return True


def get_cloudinary_status():
    """
    Obtiene el estado actual de la configuración de Cloudinary.
    
    Returns:
        dict: Estado de la configuración
    """
    config = cloudinary.config()
    
    return {
        'configured': bool(config.cloud_name and config.api_key and config.api_secret),
        'cloud_name': config.cloud_name or None,
        'api_key': config.api_key or None,
        'has_secret': bool(config.api_secret)
    }


def verify_cloudinary_connection():
    """
    Verifica que Cloudinary esté accesible haciendo un ping.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import cloudinary.api
        cloudinary.api.ping()
        return True, "Cloudinary connection OK"
    except Exception as e:
        return False, f"Cloudinary connection failed: {str(e)}"
