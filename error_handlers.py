"""
Manejadores de errores para la aplicación Flask
"""
from flask import jsonify, request
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
    """Registrar manejadores de errores personalizados"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        logger.warning(f"ValidationError: {str(e)}")
        return jsonify({'error': 'Validation Error', 'message': str(e)}), 400
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(e):
        logger.warning(f"AuthenticationError: {str(e)}")
        return jsonify({'error': 'Authentication Error', 'message': str(e)}), 401
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(e):
        logger.warning(f"AuthorizationError: {str(e)}")
        return jsonify({'error': 'Authorization Error', 'message': str(e)}), 403
    
    @app.errorhandler(404)
    def handle_not_found(e):
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        logger.error(f"500 Internal Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': 'An internal error occurred'}), 500

