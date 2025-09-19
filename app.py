#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada para Render.com
Importa la aplicación principal desde app_unificado.py
"""

import os

# Configurar variables de entorno por defecto para producción
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'production'

# Importar la aplicación principal
from app_unificado import app

# Configurar para producción
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
