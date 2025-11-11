#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script rápido para crear archivo .env"""

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(current_dir, '.env')

content = """# Variables de Entorno para DevOps - PRODUCCIÓN
# Configurar estas variables en Render Dashboard o en el archivo .env

# Belgrano Ahorro API (OBLIGATORIO)
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Configuración de API
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0

# Ticketera (OPCIONAL)
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_URL=https://ticketerabelgrano.onrender.com

# Seguridad DevOps
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password

# Flask
FLASK_ENV=production
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion
"""

try:
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo .env creado exitosamente en: {env_file}")
    print("\n📋 Contenido:")
    print(content)
except Exception as e:
    print(f"❌ Error al crear archivo: {e}")

