#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración centralizada del proyecto
Lee variables de entorno UNA SOLA VEZ al inicio
"""

import os
import logging

# Configurar logger con prefijo [CONFIG]
logger = logging.getLogger(__name__)

# ==========================================
# VARIABLES DE ENTORNO - LECTURA ÚNICA
# ==========================================

# PostgreSQL - OBLIGATORIO
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if not DATABASE_URL:
    raise ValueError("[CONFIG] ERROR: DATABASE_URL no configurada. Configure DATABASE_URL en Render Dashboard.")

# Convertir postgres:// a postgresql:// si es necesario
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Asegurar que la URL tenga sslmode=require para Render
if 'sslmode' not in DATABASE_URL:
    separator = '&' if '?' in DATABASE_URL else '?'
    DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"

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
API_TIMEOUT_SECS = int(os.getenv('API_TIMEOUT_SECS', '20'))
API_RETRY_TOTAL = int(os.getenv('API_RETRY_TOTAL', '3'))
API_RETRY_BACKOFF = float(os.getenv('API_RETRY_BACKOFF', '1.0'))

# Log configuración una sola vez
logger.info("[CONFIG] ✅ Variables de entorno cargadas:")
logger.info(f"[CONFIG]    DATABASE_URL: {DATABASE_URL[:50]}...")
logger.info(f"[CONFIG]    BELGRANO_AHORRO_URL: {BELGRANO_AHORRO_URL}")
logger.info(f"[CONFIG]    TICKETERA_URL: {TICKETERA_URL}")
logger.info(f"[CONFIG]    FLASK_ENV: {FLASK_ENV}")
