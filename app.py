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
if 'BELGRANO_AHORRO_URL' not in os.environ:
    os.environ['BELGRANO_AHORRO_URL'] = 'https://belgranoahorro-hp30.onrender.com'
if 'BELGRANO_AHORRO_API_KEY' not in os.environ:
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
if 'TICKETERA_URL' not in os.environ:
    os.environ['TICKETERA_URL'] = 'https://ticketerabelgrano.onrender.com'
if 'TICKETERA_API_KEY' not in os.environ:
    os.environ['TICKETERA_API_KEY'] = 'ticketera_api_key_2025'

# Importar la aplicación principal con manejo de errores
try:
    from app_unificado import app
    print("✅ Aplicación importada correctamente desde app_unificado.py")
except ImportError as e:
    print(f"❌ Error importando app_unificado: {e}")
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

# Configurar para producción
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
