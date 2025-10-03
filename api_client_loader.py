#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cargador perezoso del cliente API para DevOps
Resuelve el problema de variables de entorno no detectadas a tiempo
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Cliente API global (inicializado perezosamente)
_api_client = None

def get_api_client():
    """
    Obtiene el cliente API de forma perezosa.
    Lee las variables de entorno en runtime, no en import-time.
    
    Returns:
        Cliente API configurado o None si no se puede inicializar
    """
    global _api_client
    
    # Si ya está inicializado, devolverlo
    if _api_client is not None:
        return _api_client
    
    # Leer variables de entorno en runtime
    belgrano_url = os.environ.get('BELGRANO_AHORRO_URL')
    belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
    
    # Validar variables
    if not belgrano_url:
        logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_URL no está definida")
        return None
    
    if not belgrano_api_key:
        logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_API_KEY no está definida")
        return None
    
    # Intentar inicializar cliente con api_client
    try:
        from belgrano_tickets.api_client import create_api_client
        _api_client = create_api_client(belgrano_url, belgrano_api_key)
        logger.info("✅ Cliente API inicializado (api_client)")
        return _api_client
    except Exception as e:
        logger.info(f"api_client no disponible: {e}")
    
    # Fallback: intentar con belgrano_client
    try:
        from belgrano_client import BelgranoAhorroClient
        _api_client = BelgranoAhorroClient()
        logger.info("✅ Cliente API inicializado (belgrano_client)")
        return _api_client
    except Exception as e:
        logger.warning(f"belgrano_client no disponible: {e}")
        _api_client = None
        return None

def reset_api_client():
    """
    Resetea el cliente API (útil para testing o reconfiguración)
    """
    global _api_client
    _api_client = None

def is_api_client_available():
    """
    Verifica si el cliente API está disponible sin inicializarlo
    
    Returns:
        bool: True si las variables de entorno están configuradas
    """
    belgrano_url = os.environ.get('BELGRANO_AHORRO_URL')
    belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
    return bool(belgrano_url and belgrano_api_key)
