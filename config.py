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

# SEGURIDAD: En producción, requerir API key explícita
FLASK_ENV = os.getenv('FLASK_ENV', 'production').strip()
is_production = FLASK_ENV.lower() == 'production'

if is_production:
    BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', '').strip()
    if not BELGRANO_AHORRO_API_KEY:
        error_msg = "[CONFIG] ERROR: BELGRANO_AHORRO_API_KEY debe estar configurada en producción. Configure en Render Dashboard → Environment."
        logger.error(error_msg)
        raise ValueError(error_msg)
else:
    # En desarrollo, permitir valor por defecto
    BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025_dev').strip()
    logger.warning("[CONFIG] ⚠️ Usando API key por defecto (solo desarrollo). En producción configure BELGRANO_AHORRO_API_KEY.")

# Ticketera
TICKETERA_URL = os.getenv('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com').strip().rstrip('/')
TICKETS_API_URL = os.getenv('TICKETS_API_URL', TICKETERA_URL).strip().rstrip('/')

# DevOps
DEVOPS_USERNAME = os.getenv('DEVOPS_USERNAME', 'devops').strip()
DEVOPS_PASSWORD = os.getenv('DEVOPS_PASSWORD', 'devops_password').strip()
DEVOPS_API_URL = os.getenv('DEVOPS_API_URL', '').strip().rstrip('/')

# Flask - SEGURIDAD: En producción, requerir SECRET_KEY explícita
if is_production:
    SECRET_KEY = os.getenv('SECRET_KEY', '').strip()
    if not SECRET_KEY:
        error_msg = "[CONFIG] ERROR: SECRET_KEY debe estar configurada en producción. Configure en Render Dashboard → Environment."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if len(SECRET_KEY) < 32:
        error_msg = "[CONFIG] ERROR: SECRET_KEY debe tener al menos 32 caracteres. Use: openssl rand -hex 32"
        logger.error(error_msg)
        raise ValueError(error_msg)
else:
    # En desarrollo, permitir valor por defecto
    SECRET_KEY = os.getenv('SECRET_KEY', 'belgrano_ahorro_secret_key_2025_dev').strip()
    logger.warning("[CONFIG] ⚠️ Usando SECRET_KEY por defecto (solo desarrollo). En producción configure SECRET_KEY.")

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
# Configuración para carga de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB máximo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Asegurarse de que el directorio de uploads exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'business'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'branch'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'product'), exist_ok=True)

logger.info(f"[CONFIG]    BELGRANO_AHORRO_URL: {BELGRANO_AHORRO_URL}")
logger.info(f"[CONFIG]    TICKETERA_URL: {TICKETERA_URL}")
logger.info(f"[CONFIG]    FLASK_ENV: {FLASK_ENV}")
logger.info(f"[CONFIG]    UPLOAD_FOLDER: {UPLOAD_FOLDER}")
logger.info("[CONFIG] ✅ Configuración de carga de archivos inicializada")
