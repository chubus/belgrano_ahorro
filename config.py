#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración centralizada del proyecto
Lee variables de entorno UNA SOLA VEZ al inicio
Valida DATABASE_URL antes de usarla
"""

import os
import logging
from urllib.parse import urlparse

# Configurar logger con prefijo [CONFIG]
logger = logging.getLogger(__name__)

# ==========================================
# VARIABLES DE ENTORNO - LECTURA ÚNICA
# ==========================================

# PostgreSQL - OBLIGATORIO
# Intentar DATABASE_URL primero, luego POSTGRES_URL como fallback
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if not DATABASE_URL:
    DATABASE_URL = os.getenv('POSTGRES_URL', '').strip()

if not DATABASE_URL:
    error_msg = "[CONFIG] ERROR: DATABASE_URL no configurada. Configure DATABASE_URL o POSTGRES_URL en Render Dashboard."
    logger.error(error_msg)
    raise ValueError(error_msg)

# Validar formato de la URL
try:
    parsed = urlparse(DATABASE_URL)
    if not parsed.hostname:
        raise ValueError("[CONFIG] ERROR: DATABASE_URL no tiene un hostname válido")
    
    # Verificar que el hostname no sea solo un fragmento
    if parsed.hostname.startswith('dpg-') and '.' not in parsed.hostname:
        error_msg = f"[CONFIG] ERROR: Hostname incompleto detectado: '{parsed.hostname}'. La URL debe incluir el dominio completo (ej: dpg-xxx.frankfurt-postgres.render.com)"
        logger.error(error_msg)
        raise ValueError(error_msg)
except Exception as e:
    logger.error(f"[CONFIG] ERROR validando DATABASE_URL: {e}")
    raise ValueError(f"[CONFIG] ERROR: DATABASE_URL inválida: {e}")

# Convertir postgres:// a postgresql:// si es necesario
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    logger.info("[CONFIG] ✅ Convertido postgres:// a postgresql://")

# Asegurar que la URL tenga sslmode=require para Render
if 'sslmode' not in DATABASE_URL:
    separator = '&' if '?' in DATABASE_URL else '?'
    DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
    logger.info("[CONFIG] ✅ Agregado sslmode=require a DATABASE_URL")

# Belgrano Ahorro
BELGRANO_AHORRO_URL = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com').strip().rstrip('/')
BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025').strip()

# Ticketera
TICKETERA_URL = os.getenv('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com').strip().rstrip('/')
TICKETS_API_URL = os.getenv('TICKETS_API_URL', TICKETERA_URL).strip().rstrip('/')

# DevOps
DEVOPS_USERNAME = os.getenv('DEVOPS_USERNAME', 'devops').strip()
DEVOPS_PASSWORD = os.getenv('DEVOPS_PASSWORD', 'devops_password').strip()
DEVOPS_API_URL = os.getenv('DEVOPS_API_URL', '').strip().rstrip('/')

# Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'production').strip()
SECRET_KEY = os.getenv('SECRET_KEY', 'belgrano_ahorro_secret_key_2025').strip()
PORT = int(os.getenv('PORT', '5000'))
HOST = os.getenv('HOST', '0.0.0.0')

# API Configuration
API_TIMEOUT_SECS = int(os.getenv('API_TIMEOUT_SECS', '60'))
API_RETRY_TOTAL = int(os.getenv('API_RETRY_TOTAL', '1'))
API_RETRY_BACKOFF = float(os.getenv('API_RETRY_BACKOFF', '1.0'))

# Log configuración una sola vez (solo mostrar parte de la URL por seguridad)
safe_url = DATABASE_URL[:50] + "..." if len(DATABASE_URL) > 50 else DATABASE_URL
logger.info("[CONFIG] ✅ Variables de entorno cargadas:")
logger.info(f"[CONFIG]    DATABASE_URL: {safe_url}")
logger.info(f"[CONFIG]    BELGRANO_AHORRO_URL: {BELGRANO_AHORRO_URL}")
logger.info(f"[CONFIG]    TICKETERA_URL: {TICKETERA_URL}")
logger.info(f"[CONFIG]    FLASK_ENV: {FLASK_ENV}")
