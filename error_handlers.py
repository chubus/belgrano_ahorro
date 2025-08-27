#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manejadores de errores para Belgrano Ahorro
"""

from flask import render_template, jsonify, request
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass

class AuthenticationError(Exception):
    """Excepción para errores de autenticación"""
    pass

class AuthorizationError(Exception):
    """Excepción para errores de autorización"""
    pass

def register_error_handlers(app):
    """Registrar todos los manejadores de errores"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Manejar errores 400 - Bad Request"""
        logger.warning(f"Error 400: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Solicitud incorrecta'}), 400
        return render_template('error_sistema.html', error="Solicitud incorrecta"), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Manejar errores 401 - Unauthorized"""
        logger.warning(f"Error 401: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'No autorizado', 'redirect': '/login'}), 401
        return render_template('error_sistema.html', error="No autorizado"), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Manejar errores 403 - Forbidden"""
        logger.warning(f"Error 403: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Acceso denegado'}), 403
        return render_template('error_sistema.html', error="Acceso denegado"), 403

    @app.errorhandler(404)
    def not_found(error):
        """Manejar errores 404 - Not Found"""
        logger.info(f"Error 404: {request.url} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Recurso no encontrado'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Manejar errores 405 - Method Not Allowed"""
        logger.warning(f"Error 405: {request.method} {request.url} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Método no permitido'}), 405
        return render_template('error_sistema.html', error="Método no permitido"), 405

    @app.errorhandler(429)
    def too_many_requests(error):
        """Manejar errores 429 - Too Many Requests"""
        logger.warning(f"Error 429: {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Demasiadas solicitudes. Intenta más tarde.'}), 429
        return render_template('error_sistema.html', error="Demasiadas solicitudes"), 429

    @app.errorhandler(500)
    def internal_error(error):
        """Manejar errores 500 - Internal Server Error"""
        logger.error(f"Error 500: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Error interno del servidor'}), 500
        return render_template('500.html'), 500

    @app.errorhandler(ValidationError)
    def validation_error(error):
        """Manejar errores de validación"""
        logger.warning(f"Error de validación: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': str(error)}), 400
        return render_template('error_sistema.html', error=str(error)), 400

    @app.errorhandler(AuthenticationError)
    def authentication_error(error):
        """Manejar errores de autenticación"""
        logger.warning(f"Error de autenticación: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'No autorizado', 'redirect': '/login'}), 401
        return render_template('error_sistema.html', error="No autorizado"), 401

    @app.errorhandler(AuthorizationError)
    def authorization_error(error):
        """Manejar errores de autorización"""
        logger.warning(f"Error de autorización: {error} desde {request.remote_addr}")
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Acceso denegado'}), 403
        return render_template('error_sistema.html', error="Acceso denegado"), 403
