# =================================================================
# API ENDPOINTS PARA SINCRONIZACIÓN BIDIRECCIONAL
# BELGRANO AHORRO ↔ BELGRANO TICKETERA
# =================================================================

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from bidirectional_sync import bidirectional_sync
from sync_config import sync_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint para la API de sincronización
sync_api = Blueprint('sync_api', __name__, url_prefix='/api/sync')

@sync_api.route('/status', methods=['GET'])
def get_sync_status():
    """Obtener estado actual de la sincronización"""
    try:
        status = bidirectional_sync.get_sync_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error obteniendo estado de sincronización: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@sync_api.route('/productos', methods=['POST'])
def sync_productos():
    """Sincronizar productos desde Ticketera hacia Ahorro"""
    try:
        # Verificar API key
        api_key = request.headers.get('X-API-Key')
        if api_key != sync_config.TICKETERA_API_KEY:
            return jsonify({
                'success': False,
                'error': 'API key inválida'
            }), 401
        
        # Ejecutar sincronización
        resultado = bidirectional_sync.sync_productos_from_ticketera()
        
        if resultado['success']:
            return jsonify({
                'success': True,
                'data': resultado,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error desconocido'),
                'timestamp': datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error en sincronización de productos: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def register_sync_api(app):
    """Registrar blueprint de sincronización en la aplicación Flask"""
    try:
        app.register_blueprint(sync_api)
        logger.info("✅ API de sincronización registrada en /api/sync")
        return True
    except Exception as e:
        logger.error(f"❌ Error registrando API de sincronización: {e}")
        return False
