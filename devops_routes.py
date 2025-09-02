# devops_routes.py
# =================================================================
# RUTAS DE DEVOPS - BELGRANO AHORRO
# =================================================================

from flask import Blueprint, jsonify
import os
from datetime import datetime
import logging

# Crear el blueprint de DevOps
devops_bp = Blueprint('devops', __name__, url_prefix='/devops')

# Configurar logging
logger = logging.getLogger(__name__)

@devops_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificacion de salud del sistema
    """
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'belgrano-ahorro',
            'timestamp': str(datetime.utcnow()),
            'environment': os.environ.get('FLASK_ENV', 'development')
        }), 200
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@devops_bp.route('/status', methods=['GET'])
def status_check():
    """
    Endpoint de verificacion de estado detallado
    """
    try:
        return jsonify({
            'status': 'running',
            'service': 'belgrano-ahorro',
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'render_environment': os.environ.get('RENDER_ENVIRONMENT', 'local')
        }), 200
    except Exception as e:
        logger.error(f"Error en status check: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@devops_bp.route('/ping', methods=['GET'])
def ping():
    """
    Endpoint simple de ping
    """
    return jsonify({'message': 'pong'}), 200
