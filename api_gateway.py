#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Gateway Unificado para Belgrano Ahorro y Ticketera
Centraliza todas las comunicaciones entre aplicaciones
"""

import os
import json
import requests
import logging
from datetime import datetime
from flask import Flask, request, jsonify, Blueprint
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
TICKETERA_URL = os.environ.get('TICKETERA_URL', 'http://localhost:5001')
API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))

# API Keys
BELGRANO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
TICKETERA_API_KEY = os.environ.get('TICKETERA_API_KEY', 'ticketera_api_key_2025')
DEVOPS_API_KEY = os.environ.get('DEVOPS_API_KEY', 'devops_api_key_2025')

# Crear blueprint
gateway_bp = Blueprint('api_gateway', __name__, url_prefix='/gateway')

def require_gateway_auth(f):
    """Decorator para autenticación del gateway"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("No Authorization header provided")
            return jsonify({'error': 'Authorization header required'}), 401
        
        api_key = auth_header.split(' ')[1]
        valid_keys = [BELGRANO_API_KEY, TICKETERA_API_KEY, DEVOPS_API_KEY]
        
        logger.info(f"Received API key: {api_key[:10]}...")
        logger.info(f"Valid keys: {[key[:10] + '...' for key in valid_keys]}")
        
        if api_key not in valid_keys:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return jsonify({'error': 'Invalid API key', 'received': api_key[:10] + '...'}), 401
        
        logger.info("API key validated successfully")
        return f(*args, **kwargs)
    return decorated_function

class APIGateway:
    """Gateway unificado para comunicación entre aplicaciones"""
    
    def __init__(self):
        self.belgrano_url = BELGRANO_AHORRO_URL
        self.ticketera_url = TICKETERA_URL
        self.timeout = API_TIMEOUT
        
    def make_request(self, method, service, endpoint, data=None, headers=None):
        """Realizar request a cualquier servicio"""
        try:
            # Determinar URL base
            if service == 'belgrano':
                base_url = self.belgrano_url
                api_key = BELGRANO_API_KEY
            elif service == 'ticketera':
                base_url = self.ticketera_url
                api_key = TICKETERA_API_KEY
            else:
                raise ValueError(f"Servicio no válido: {service}")
            
            # Construir URL completa
            url = f"{base_url}/api/{endpoint}"
            
            # Headers por defecto
            default_headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Source': 'gateway'
            }
            
            # Combinar headers
            if headers:
                default_headers.update(headers)
            
            # Realizar request
            response = requests.request(
                method=method,
                url=url,
                headers=default_headers,
                json=data,
                timeout=self.timeout
            )
            
            # Log de la operación
            logger.info(f"Gateway request: {method} {service}/{endpoint} -> {response.status_code}")
            
            return {
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'headers': dict(response.headers),
                'success': response.status_code < 400
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout en {service}/{endpoint}")
            return {
                'status_code': 408,
                'data': {'error': 'Request timeout'},
                'success': False
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error en {service}/{endpoint}")
            return {
                'status_code': 503,
                'data': {'error': 'Service unavailable'},
                'success': False
            }
        except Exception as e:
            logger.error(f"Error en gateway: {e}")
            return {
                'status_code': 500,
                'data': {'error': str(e)},
                'success': False
            }

# Instancia global del gateway
gateway = APIGateway()

# =============================
# RUTAS DEL GATEWAY
# =============================

@gateway_bp.route('/health', methods=['GET'])
def gateway_health():
    """Health check del gateway"""
    return jsonify({
        'status': 'success',
        'message': 'API Gateway is running',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'belgrano_ahorro': BELGRANO_AHORRO_URL,
            'ticketera': TICKETERA_URL
        }
    })

@gateway_bp.route('/sync/status', methods=['GET'])
@require_gateway_auth
def sync_status():
    """Estado de sincronización entre servicios"""
    try:
        # Verificar estado de Belgrano Ahorro
        belgrano_status = gateway.make_request('GET', 'belgrano', 'health')
        
        # Verificar estado de Ticketera
        ticketera_status = gateway.make_request('GET', 'ticketera', 'health')
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'belgrano_ahorro': {
                    'url': BELGRANO_AHORRO_URL,
                    'status': 'online' if belgrano_status['success'] else 'offline',
                    'response_time': belgrano_status.get('response_time', 0)
                },
                'ticketera': {
                    'url': TICKETERA_URL,
                    'status': 'online' if ticketera_status['success'] else 'offline',
                    'response_time': ticketera_status.get('response_time', 0)
                }
            },
            'sync_status': 'operational' if all([belgrano_status['success'], ticketera_status['success']]) else 'degraded'
        })
        
    except Exception as e:
        logger.error(f"Error en sync status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@gateway_bp.route('/sync/force', methods=['POST'])
@require_gateway_auth
def sync_force():
    """Forzar sincronización completa"""
    try:
        sync_results = {}
        
        # Sincronizar negocios
        negocios_result = gateway.make_request('GET', 'belgrano', 'negocios')
        sync_results['negocios'] = {
            'count': len(negocios_result.get('data', {}).get('data', [])),
            'status': 'success' if negocios_result['success'] else 'error'
        }
        
        # Sincronizar productos
        productos_result = gateway.make_request('GET', 'belgrano', 'productos')
        sync_results['productos'] = {
            'count': len(productos_result.get('data', {}).get('data', [])),
            'status': 'success' if productos_result['success'] else 'error'
        }
        
        # Sincronizar ofertas
        ofertas_result = gateway.make_request('GET', 'belgrano', 'ofertas')
        sync_results['ofertas'] = {
            'count': len(ofertas_result.get('data', {}).get('data', [])),
            'status': 'success' if ofertas_result['success'] else 'error'
        }
        
        # Sincronizar sucursales
        sucursales_result = gateway.make_request('GET', 'belgrano', 'sucursales')
        sync_results['sucursales'] = {
            'count': len(sucursales_result.get('data', {}).get('data', [])),
            'status': 'success' if sucursales_result['success'] else 'error'
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Sincronización forzada completada',
            'timestamp': datetime.now().isoformat(),
            'results': sync_results
        })
        
    except Exception as e:
        logger.error(f"Error en sync force: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@gateway_bp.route('/proxy/<service>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_gateway_auth
def proxy_request(service, endpoint):
    """Proxy para requests a cualquier servicio"""
    try:
        method = request.method
        data = request.get_json() if request.is_json else None
        
        result = gateway.make_request(method, service, endpoint, data)
        
        return jsonify(result['data']), result['status_code']
        
    except Exception as e:
        logger.error(f"Error en proxy request: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# RUTAS DE GESTIÓN DE DATOS
# =============================

@gateway_bp.route('/negocios', methods=['GET', 'POST'])
@require_gateway_auth
def gateway_negocios():
    """Gateway para gestión de negocios"""
    if request.method == 'GET':
        result = gateway.make_request('GET', 'belgrano', 'negocios')
        return jsonify(result['data']), result['status_code']
    else:
        data = request.get_json()
        result = gateway.make_request('POST', 'belgrano', 'negocios', data)
        return jsonify(result['data']), result['status_code']

@gateway_bp.route('/negocios/<int:negocio_id>', methods=['GET', 'PUT', 'DELETE'])
@require_gateway_auth
def gateway_negocio_detail(negocio_id):
    """Gateway para gestión de negocio específico"""
    method = request.method
    data = request.get_json() if request.is_json else None
    
    result = gateway.make_request(method, 'belgrano', f'negocios/{negocio_id}', data)
    return jsonify(result['data']), result['status_code']

@gateway_bp.route('/productos', methods=['GET', 'POST'])
@require_gateway_auth
def gateway_productos():
    """Gateway para gestión de productos"""
    if request.method == 'GET':
        result = gateway.make_request('GET', 'belgrano', 'productos')
        return jsonify(result['data']), result['status_code']
    else:
        data = request.get_json()
        result = gateway.make_request('POST', 'belgrano', 'productos', data)
        return jsonify(result['data']), result['status_code']

@gateway_bp.route('/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
@require_gateway_auth
def gateway_producto_detail(producto_id):
    """Gateway para gestión de producto específico"""
    method = request.method
    data = request.get_json() if request.is_json else None
    
    result = gateway.make_request(method, 'belgrano', f'productos/{producto_id}', data)
    return jsonify(result['data']), result['status_code']

@gateway_bp.route('/ofertas', methods=['GET', 'POST'])
@require_gateway_auth
def gateway_ofertas():
    """Gateway para gestión de ofertas"""
    if request.method == 'GET':
        result = gateway.make_request('GET', 'belgrano', 'ofertas')
        return jsonify(result['data']), result['status_code']
    else:
        data = request.get_json()
        result = gateway.make_request('POST', 'belgrano', 'ofertas', data)
        return jsonify(result['data']), result['status_code']

@gateway_bp.route('/ofertas/<int:oferta_id>', methods=['GET', 'PUT', 'DELETE'])
@require_gateway_auth
def gateway_oferta_detail(oferta_id):
    """Gateway para gestión de oferta específica"""
    method = request.method
    data = request.get_json() if request.is_json else None
    
    result = gateway.make_request(method, 'belgrano', f'ofertas/{oferta_id}', data)
    return jsonify(result['data']), result['status_code']

@gateway_bp.route('/sucursales', methods=['GET', 'POST'])
@require_gateway_auth
def gateway_sucursales():
    """Gateway para gestión de sucursales"""
    if request.method == 'GET':
        result = gateway.make_request('GET', 'belgrano', 'sucursales')
        return jsonify(result['data']), result['status_code']
    else:
        data = request.get_json()
        result = gateway.make_request('POST', 'belgrano', 'sucursales', data)
        return jsonify(result['data']), result['status_code']

@gateway_bp.route('/sucursales/<int:sucursal_id>', methods=['GET', 'PUT', 'DELETE'])
@require_gateway_auth
def gateway_sucursal_detail(sucursal_id):
    """Gateway para gestión de sucursal específica"""
    method = request.method
    data = request.get_json() if request.is_json else None
    
    result = gateway.make_request(method, 'belgrano', f'sucursales/{sucursal_id}', data)
    return jsonify(result['data']), result['status_code']

@gateway_bp.route('/precios/<int:producto_id>', methods=['GET', 'PUT'])
@require_gateway_auth
def gateway_precios(producto_id):
    """Gateway para gestión de precios"""
    method = request.method
    data = request.get_json() if request.is_json else None
    
    result = gateway.make_request(method, 'belgrano', f'precios/{producto_id}', data)
    return jsonify(result['data']), result['status_code']

# Crear aplicación Flask para ejecución directa
if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(gateway_bp)
    
    print("🌐 Iniciando API Gateway en puerto 5003...")
    print("🔗 URL: http://localhost:5003/gateway/")
    print("🔐 API Keys: belgrano_ahorro_api_key_2025, ticketera_api_key_2025, devops_api_key_2025")
    print("📝 Presiona Ctrl+C para detener")
    
    try:
        app.run(host='0.0.0.0', port=5003, debug=False)
    except KeyboardInterrupt:
        print("\n⏹️ API Gateway detenido")
    except Exception as e:
        print(f"❌ Error iniciando API Gateway: {e}")
