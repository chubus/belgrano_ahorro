#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de autenticación y autorización para Belgrano Ahorro
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('usuario_id'):
            logger.warning(f"Intento de acceso no autorizado a {request.endpoint} desde {request.remote_addr}")
            if request.is_xhr or request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado', 'redirect': '/login'}), 401
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('usuario_id'):
            logger.warning(f"Intento de acceso no autorizado a {request.endpoint} desde {request.remote_addr}")
            if request.is_xhr or request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado', 'redirect': '/login'}), 401
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        
        if session.get('usuario_rol') != 'admin':
            logger.warning(f"Intento de acceso sin permisos de admin a {request.endpoint} por usuario {session.get('usuario_id')}")
            if request.is_xhr or request.path.startswith('/api/'):
                return jsonify({'error': 'Acceso denegado', 'redirect': '/'}), 403
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def flota_required(f):
    """Decorador para requerir rol de flota"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('usuario_id'):
            logger.warning(f"Intento de acceso no autorizado a {request.endpoint} desde {request.remote_addr}")
            if request.is_xhr or request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado', 'redirect': '/login'}), 401
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        
        if session.get('usuario_rol') not in ['admin', 'flota']:
            logger.warning(f"Intento de acceso sin permisos de flota a {request.endpoint} por usuario {session.get('usuario_id')}")
            if request.is_xhr or request.path.startswith('/api/'):
                return jsonify({'error': 'Acceso denegado', 'redirect': '/'}), 403
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def validate_input_data(required_fields=None, optional_fields=None):
    """Decorador para validar datos de entrada"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                data = request.get_json() if request.is_json else request.form
                
                # Validar campos requeridos
                if required_fields:
                    for field in required_fields:
                        if not data.get(field):
                            logger.warning(f"Campo requerido faltante: {field} en {request.endpoint}")
                            if request.is_xhr or request.path.startswith('/api/'):
                                return jsonify({'error': f'Campo requerido: {field}'}), 400
                            flash(f'El campo {field} es requerido', 'danger')
                            return redirect(request.url)
                
                # Validar formato de email si está presente
                if 'email' in data and data.get('email'):
                    import re
                    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
                    if not re.match(email_pattern, data['email']):
                        logger.warning(f"Email inválido: {data['email']} en {request.endpoint}")
                        if request.is_xhr or request.path.startswith('/api/'):
                            return jsonify({'error': 'Formato de email inválido'}), 400
                        flash('Por favor ingresa un email válido', 'danger')
                        return redirect(request.url)
                
                # Validar longitud de contraseña si está presente
                if 'password' in data and data.get('password'):
                    if len(data['password']) < 6:
                        logger.warning(f"Contraseña muy corta en {request.endpoint}")
                        if request.is_xhr or request.path.startswith('/api/'):
                            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
                        flash('La contraseña debe tener al menos 6 caracteres', 'danger')
                        return redirect(request.url)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def production_only(f):
    """Decorador para endpoints que solo deben estar disponibles en desarrollo"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        if current_app.config.get('ENV') == 'production':
            logger.warning(f"Intento de acceso a endpoint de desarrollo en producción: {request.endpoint}")
            return jsonify({'error': 'Endpoint no disponible en producción'}), 404
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=5, window=60):
    """Decorador para limitar el número de requests por ventana de tiempo"""
    from collections import defaultdict
    import time
    
    request_counts = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Usar IP como identificador
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Limpiar requests antiguos
            request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                       if current_time - req_time < window]
            
            # Verificar límite
            if len(request_counts[client_ip]) >= max_requests:
                logger.warning(f"Rate limit excedido para IP: {client_ip} en {request.endpoint}")
                if request.is_xhr or request.path.startswith('/api/'):
                    return jsonify({'error': 'Demasiadas solicitudes. Intenta más tarde.'}), 429
                flash('Demasiadas solicitudes. Intenta más tarde.', 'warning')
                return redirect(request.url)
            
            # Agregar request actual
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
