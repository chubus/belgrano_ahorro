#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script rápido para crear archivo .env"""

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(current_dir, '.env')

content = """# ============================================================
# Variables de Entorno para DevOps - PRODUCCIÓN
# Configurado para funcionar con Belgrano Ahorro
# ============================================================
# 
# IMPORTANTE: Este archivo contiene la API key real
# NO subir a git (debe estar en .gitignore)
# 
# Para Render Dashboard: Copia estas variables a Environment
# ============================================================

# ============================================================
# BELGRANO AHORRO API (OBLIGATORIO)
# ============================================================
# URL de la API de Belgrano Ahorro en producción
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com

# API Key para autenticación - DEBE ser la misma que en Belgrano Ahorro
# Esta es la API key configurada en api_belgrano_ahorro.py
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# ============================================================
# CONFIGURACIÓN DE API (Optimizado para Render)
# ============================================================
# Timeout en segundos para requests HTTP (20s para servicios en Render)
API_TIMEOUT_SECS=20

# Número total de reintentos en caso de fallo
API_RETRY_TOTAL=3

# Factor de espera entre reintentos en segundos
API_RETRY_BACKOFF=1.0

# Tiempo de vida del cache en segundos (solo para manager_unified)
API_CACHE_TTL_SECS=120

# ============================================================
# TICKETERA / SISTEMA DE TICKETS (OPCIONAL)
# ============================================================
# URL de la API de Ticketera
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_URL=https://ticketerabelgrano.onrender.com
DEVOPS_API_URL=https://ticketerabelgrano.onrender.com

# API Key para Ticketera (si aplica - dejar vacío si no se usa)
TICKETS_API_KEY=
TICKETERA_API_KEY=
DEVOPS_API_KEY=

# Credenciales Username/Password para Ticketera (alternativa a API Key)
# Usar estas si Ticketera requiere autenticación por usuario/password
TICKETS_API_USERNAME=admin@belgranoahorro.com
TICKETS_API_PASSWORD=admin123

# ============================================================
# SEGURIDAD DEVOPS (Login del Dashboard)
# ============================================================
# Usuario para login en panel DevOps
DEVOPS_USERNAME=devops

# Contraseña para login en panel DevOps
# ⚠️ CAMBIAR EN PRODUCCIÓN por una contraseña segura
DEVOPS_PASSWORD=devops_password

# ============================================================
# FLASK / APLICACIÓN
# ============================================================
# Entorno de Flask
FLASK_ENV=production

# Secret key de Flask para sesiones
# ⚠️ CAMBIAR EN PRODUCCIÓN por una clave segura y única
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion

# Configuración de cookies de sesión
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=false
REMEMBER_COOKIE_SECURE=false

# ============================================================
# NOTAS
# ============================================================
# 
# 1. Variables OBLIGATORIAS para que funcione el dashboard:
#    - BELGRANO_AHORRO_URL
#    - BELGRANO_AHORRO_API_KEY
#
# 2. La API key DEBE ser exactamente: belgrano_ahorro_api_key_2025
#    (la misma que está configurada en Belgrano Ahorro)
#
# 3. Para producción en Render:
#    - Configura estas variables en Render Dashboard → Environment
#    - Cambia DEVOPS_PASSWORD y SECRET_KEY por valores seguros
#    - SESSION_COOKIE_SECURE=true si usas HTTPS
#
# 4. Para desarrollo local:
#    - Este archivo se carga automáticamente
#    - Puedes editar los valores según necesites
#
# ============================================================
"""

try:
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo .env creado exitosamente en: {env_file}")
    print("\n📋 Contenido:")
    print(content)
except Exception as e:
    print(f"❌ Error al crear archivo: {e}")

