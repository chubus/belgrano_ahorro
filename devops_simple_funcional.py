#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevOps Simplificado y Funcional
Versión optimizada que funciona correctamente
"""

import os
import json
import requests
import time
from datetime import datetime
import logging
from flask import Flask, request, jsonify, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = 'devops_secret_key_2025'

# Configuración optimizada
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configuración de API
BELGRANO_AHORRO_URL = 'http://localhost:5000'
BELGRANO_AHORRO_API_KEY = 'belgrano_ahorro_api_key_2025'
API_TIMEOUT_SECS = 15

# Credenciales de DevOps
DEVOPS_USERNAME = 'devops'
DEVOPS_PASSWORD_HASH = generate_password_hash('DevOps2025!Secure')

# Middleware de optimización
@app.before_request
def before_request():
    """Middleware para optimizar requests"""
    pass

@app.after_request
def after_request(response):
    """Middleware para optimizar respuestas"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def devops_is_authenticated():
    """Verificar si DevOps está autenticado"""
    return session.get('devops_authenticated') is True

def devops_login_required(fn):
    """Decorador para requerir autenticación de DevOps"""
    def wrapper(*args, **kwargs):
        if not devops_is_authenticated():
            return redirect(url_for('devops_login'))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def make_api_request(method, endpoint, data=None):
    """Realizar request a la API de Belgrano Ahorro con manejo de errores optimizado"""
    try:
        headers = {
            'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        url = f"{BELGRANO_AHORRO_URL}/api/{endpoint}"
        
        logger.info(f"Making {method} request to {url}")
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=API_TIMEOUT_SECS)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=API_TIMEOUT_SECS)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=API_TIMEOUT_SECS)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=API_TIMEOUT_SECS)
        else:
            return {'success': False, 'error': f'Método no soportado: {method}'}
        
        logger.info(f"Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json() if response.content else {}
            return {
                'success': True,
                'data': result.get('data', result),
                'status_code': response.status_code
            }
        else:
            error_data = response.json() if response.content else {}
            return {
                'success': False,
                'error': error_data.get('error', f'HTTP {response.status_code}'),
                'status_code': response.status_code
            }
                
    except requests.exceptions.Timeout:
        logger.error(f"Timeout en request a {url}")
        return {'success': False, 'error': 'Request timeout', 'data': []}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error en request a {url}")
        return {'success': False, 'error': 'Connection error', 'data': []}
    except Exception as e:
        logger.error(f"Error en API request: {e}")
        return {'success': False, 'error': str(e), 'data': []}

# =============================
# RUTAS DE DEVOPS
# =============================

@app.route('/devops/login', methods=['GET', 'POST'])
def devops_login():
    """Login de DevOps"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == DEVOPS_USERNAME and check_password_hash(DEVOPS_PASSWORD_HASH, password):
            session['devops_authenticated'] = True
            session.permanent = True
            logger.info(f"Login exitoso de DevOps: {username}")
            return redirect(url_for('devops_home'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('devops/login.html', 
                         username=DEVOPS_USERNAME)

@app.route('/devops/')
@devops_login_required
def devops_home():
    """Panel principal de DevOps"""
    return render_template('devops/dashboard.html')

@app.route('/devops/logout')
def devops_logout():
    """Cerrar sesión de DevOps"""
    session.pop('devops_authenticated', None)
    return redirect(url_for('devops_login'))

@app.route('/devops/negocios')
@devops_login_required
def gestion_negocios():
    """Gestión de negocios"""
    try:
        result = make_api_request('GET', 'negocios')
        
        if result['success']:
            negocios = result['data']
            return render_template('devops/negocios.html', negocios=negocios)
        else:
            flash(f"Error obteniendo negocios: {result['error']}", 'error')
            return render_template('devops/negocios.html', negocios=[])
    except Exception as e:
        logger.error(f"Error en gestión de negocios: {e}")
        flash(f"Error interno: {e}", 'error')
        return render_template('devops/negocios.html', negocios=[])

@app.route('/devops/productos')
@devops_login_required
def gestion_productos():
    """Gestión de productos"""
    try:
        result = make_api_request('GET', 'productos')
        
        if result['success']:
            productos = result['data']
            return render_template('devops/productos.html', productos=productos)
        else:
            flash(f"Error obteniendo productos: {result['error']}", 'error')
            return render_template('devops/productos.html', productos=[])
    except Exception as e:
        logger.error(f"Error en gestión de productos: {e}")
        flash(f"Error interno: {e}", 'error')
        return render_template('devops/productos.html', productos=[])

@app.route('/devops/sucursales')
@devops_login_required
def gestion_sucursales():
    """Gestión de sucursales"""
    try:
        result = make_api_request('GET', 'sucursales')
        
        if result['success']:
            sucursales = result['data']
            return render_template('devops/sucursales.html', sucursales=sucursales)
        else:
            flash(f"Error obteniendo sucursales: {result['error']}", 'error')
            return render_template('devops/sucursales.html', sucursales=[])
    except Exception as e:
        logger.error(f"Error en gestión de sucursales: {e}")
        flash(f"Error interno: {e}", 'error')
        return render_template('devops/sucursales.html', sucursales=[])

@app.route('/devops/health')
def devops_health():
    """Health check de DevOps"""
    try:
        # Verificar conectividad con Belgrano Ahorro
        result = make_api_request('GET', 'health')
        
        if result['success']:
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'belgrano_ahorro': 'connected'
            }), 200
        else:
            return jsonify({
                'status': 'degraded',
                'timestamp': datetime.now().isoformat(),
                'belgrano_ahorro': 'disconnected',
                'error': result['error']
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# =============================
# RUTA PRINCIPAL
# =============================

@app.route('/')
def index():
    """Página principal"""
    return redirect(url_for('devops_login'))

# =============================
# MANEJO DE ERRORES
# =============================

@app.errorhandler(404)
def not_found(error):
    return render_template('devops/error.html', 
                         error='Página no encontrada', 
                         code=404), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('devops/error.html', 
                         error='Error interno del servidor', 
                         code=500), 500

if __name__ == '__main__':
    print("🚀 Iniciando DevOps Simplificado...")
    print("📱 Acceso: http://localhost:5002/devops/")
    print("🔐 Usuario: devops")
    print("🔑 Contraseña: DevOps2025!Secure")
    print("⏹️ Presiona Ctrl+C para detener")
    
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
