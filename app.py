#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada para Render.com - Belgrano Ahorro
Importa la aplicación principal desde app_unificado.py
"""

import os
import sys

# Configurar variables de entorno por defecto para producción
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'production'

# Variables de entorno con validación y warnings
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY')

if not BELGRANO_AHORRO_URL:
    os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-aliq.onrender.com'
    print("WARNING: BELGRANO_AHORRO_URL no configurada, usando valor por defecto")

if not BELGRANO_AHORRO_API_KEY:
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
    print("WARNING: BELGRANO_AHORRO_API_KEY no configurada, usando valor por defecto")

# Otras variables de entorno
if 'TICKETERA_URL' not in os.environ:
    os.environ['TICKETERA_URL'] = 'https://ticketerabelgrano.onrender.com'
if 'TICKETERA_API_KEY' not in os.environ:
    os.environ['TICKETERA_API_KEY'] = 'ticketera_api_key_2025'

# Configurar deploy
try:
    from config_deploy import configure_deploy
    configure_deploy()
except ImportError:
    print("WARNING: config_deploy.py no encontrado, usando configuración básica")

# Importar la aplicación principal con manejo de errores
try:
    from app_unificado import app
    print("OK: Aplicación importada correctamente desde app_unificado.py")
except ImportError as e:
    print(f"ERROR: Error importando app_unificado: {e}")
    # Crear una aplicación Flask básica como fallback
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'belgrano_ahorro_secret_key_2025')

    @app.route('/')
    def index():
        return "Belgrano Ahorro - Aplicación en mantenimiento"

    @app.route('/health')
    def health():
        return "OK"
    
    @app.route('/healthz')
    def healthz():
        """Endpoint de salud para Render"""
        return "ok", 200

# Configurar para producción
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)