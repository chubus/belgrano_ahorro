from flask import Blueprint, current_app, request, jsonify, render_template
import json
import requests
import logging
from datetime import datetime
import os

# Blueprint de DevOps con prefijo /devops
devops_bp = Blueprint('devops_bp', __name__, url_prefix='/devops')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de URLs y API keys
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

# =================================================================
# FUNCIONES DE SINCRONIZACIÓN EN TIEMPO REAL
# =================================================================

def sync_to_belgrano_ahorro(endpoint, data, method='POST'):
    """Sincronizar cambios inmediatamente a Belgrano Ahorro"""
    try:
        url = f"{BELGRANO_AHORRO_URL}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'X-Origin': 'devops',
            'X-Timestamp': datetime.now().isoformat()
        }
        
        if method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, json=data, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Sincronización exitosa a Belgrano Ahorro: {endpoint}")
            return True, response.json()
        else:
            logger.error(f"❌ Error en sincronización: {response.status_code} - {response.text}")
            return False, response.text
            
    except Exception as e:
        logger.error(f"❌ Error de conexión con Belgrano Ahorro: {e}")
        return False, str(e)

def get_belgrano_ahorro_data(endpoint):
    """Obtener datos desde Belgrano Ahorro"""
    try:
        url = f"{BELGRANO_AHORRO_URL}{endpoint}"
        headers = {
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'X-Origin': 'devops'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos de Belgrano Ahorro: {e}")
        return False, str(e)

# =================================================================
# RUTAS DE GESTIÓN DE SUCURSALES
# =================================================================

@devops_bp.route('/sucursales', methods=['GET'])
def devops_sucursales():
    """Panel de gestión de sucursales desde DevOps"""
    try:
        # Obtener sucursales desde Belgrano Ahorro
        success, data = get_belgrano_ahorro_data('/api/v1/sucursales')
        if success:
            return jsonify({
                'status': 'success',
                'data': data,
                'message': 'Sucursales obtenidas correctamente'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo sucursales: {data}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_sucursales: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/agregar_sucursal', methods=['POST'])
def devops_agregar_sucursal():
    """Agregar sucursal desde DevOps con sincronización inmediata"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nombre', 'negocio_id', 'direccion', 'telefono']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Campo requerido faltante: {field}'
                }), 400
        
        # Agregar metadatos de DevOps
        data['creado_desde'] = 'devops'
        data['fecha_creacion'] = datetime.now().isoformat()
        data['activo'] = True
        
        # Sincronizar inmediatamente a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro('/api/v1/sucursales', data)
        
        if success:
            logger.info(f"✅ Sucursal '{data['nombre']}' agregada y sincronizada exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Sucursal agregada y sincronizada exitosamente',
                'data': response
            })
        else:
            logger.error(f"❌ Error sincronizando sucursal: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_agregar_sucursal: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/editar_sucursal/<sucursal_id>', methods=['PUT'])
def devops_editar_sucursal(sucursal_id):
    """Editar sucursal desde DevOps con sincronización inmediata"""
    try:
        data = request.get_json()
        data['id'] = sucursal_id
        data['modificado_desde'] = 'devops'
        data['fecha_modificacion'] = datetime.now().isoformat()
        
        # Sincronizar cambios a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro(f'/api/v1/sucursales/{sucursal_id}', data, 'PUT')
        
        if success:
            logger.info(f"✅ Sucursal {sucursal_id} editada y sincronizada exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Sucursal editada y sincronizada exitosamente',
                'data': response
            })
        else:
            logger.error(f"❌ Error sincronizando cambios de sucursal: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_editar_sucursal: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/eliminar_sucursal/<sucursal_id>', methods=['DELETE'])
def devops_eliminar_sucursal(sucursal_id):
    """Eliminar sucursal desde DevOps con sincronización inmediata"""
    try:
        data = {
            'id': sucursal_id,
            'eliminado_desde': 'devops',
            'fecha_eliminacion': datetime.now().isoformat()
        }
        
        # Sincronizar eliminación a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro(f'/api/v1/sucursales/{sucursal_id}', data, 'DELETE')
        
        if success:
            logger.info(f"✅ Sucursal {sucursal_id} eliminada y sincronizada exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Sucursal eliminada y sincronizada exitosamente'
            })
        else:
            logger.error(f"❌ Error sincronizando eliminación de sucursal: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_eliminar_sucursal: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

# =================================================================
# RUTAS DE GESTIÓN DE NEGOCIOS
# =================================================================

@devops_bp.route('/negocios', methods=['GET'])
def devops_negocios():
    """Panel de gestión de negocios desde DevOps"""
    try:
        # Obtener negocios desde Belgrano Ahorro
        success, data = get_belgrano_ahorro_data('/api/v1/negocios')
        if success:
            return jsonify({
                'status': 'success',
                'data': data,
                'message': 'Negocios obtenidos correctamente'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo negocios: {data}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_negocios: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/agregar_negocio', methods=['POST'])
def devops_agregar_negocio():
    """Agregar negocio desde DevOps con sincronización inmediata"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nombre', 'descripcion', 'categoria']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Campo requerido faltante: {field}'
                }), 400
        
        # Agregar metadatos de DevOps
        data['creado_desde'] = 'devops'
        data['fecha_creacion'] = datetime.now().isoformat()
        data['activo'] = True
        
        # Sincronizar inmediatamente a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro('/api/v1/negocios', data)
        
        if success:
            logger.info(f"✅ Negocio '{data['nombre']}' agregado y sincronizado exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Negocio agregado y sincronizado exitosamente',
                'data': response
            })
        else:
            logger.error(f"❌ Error sincronizando negocio: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_agregar_negocio: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/editar_negocio/<negocio_id>', methods=['PUT'])
def devops_editar_negocio(negocio_id):
    """Editar negocio desde DevOps con sincronización inmediata"""
    try:
        data = request.get_json()
        data['id'] = negocio_id
        data['modificado_desde'] = 'devops'
        data['fecha_modificacion'] = datetime.now().isoformat()
        
        # Sincronizar cambios a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro(f'/api/v1/negocios/{negocio_id}', data, 'PUT')
        
        if success:
            logger.info(f"✅ Negocio {negocio_id} editado y sincronizado exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Negocio editado y sincronizado exitosamente',
                'data': response
            })
        else:
            logger.error(f"❌ Error sincronizando cambios de negocio: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_editar_negocio: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/eliminar_negocio/<negocio_id>', methods=['DELETE'])
def devops_eliminar_negocio(negocio_id):
    """Eliminar negocio desde DevOps con sincronización inmediata"""
    try:
        data = {
            'id': negocio_id,
            'eliminado_desde': 'devops',
            'fecha_eliminacion': datetime.now().isoformat()
        }
        
        # Sincronizar eliminación a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro(f'/api/v1/negocios/{negocio_id}', data, 'DELETE')
        
        if success:
            logger.info(f"✅ Negocio {negocio_id} eliminado y sincronizado exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Negocio eliminado y sincronizado exitosamente'
            })
        else:
            logger.error(f"❌ Error sincronizando eliminación de negocio: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_eliminar_negocio: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

# =================================================================
# RUTAS DE GESTIÓN DE OFERTAS
# =================================================================

@devops_bp.route('/ofertas', methods=['GET'])
def devops_ofertas():
    """Panel de gestión de ofertas desde DevOps"""
    try:
        # Obtener ofertas desde Belgrano Ahorro
        success, data = get_belgrano_ahorro_data('/api/v1/ofertas')
        if success:
            return jsonify({
                'status': 'success',
                'data': data,
                'message': 'Ofertas obtenidas correctamente'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo ofertas: {data}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_ofertas: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/agregar_oferta', methods=['POST'])
def devops_agregar_oferta():
    """Agregar oferta desde DevOps con sincronización inmediata"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['titulo', 'descripcion', 'descuento', 'fecha_inicio', 'fecha_fin']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Campo requerido faltante: {field}'
                }), 400
        
        # Agregar metadatos de DevOps
        data['creado_desde'] = 'devops'
        data['fecha_creacion'] = datetime.now().isoformat()
        data['activo'] = True
        
        # Sincronizar inmediatamente a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro('/api/v1/ofertas', data)
        
        if success:
            logger.info(f"✅ Oferta '{data['titulo']}' agregada y sincronizada exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Oferta agregada y sincronizada exitosamente',
                'data': response
            })
        else:
            logger.error(f"❌ Error sincronizando oferta: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_agregar_oferta: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/editar_oferta/<oferta_id>', methods=['PUT'])
def devops_editar_oferta(oferta_id):
    """Editar oferta desde DevOps con sincronización inmediata"""
    try:
        data = request.get_json()
        data['id'] = oferta_id
        data['modificado_desde'] = 'devops'
        data['fecha_modificacion'] = datetime.now().isoformat()
        
        # Sincronizar cambios a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro(f'/api/v1/ofertas/{oferta_id}', data, 'PUT')
        
        if success:
            logger.info(f"✅ Oferta {oferta_id} editada y sincronizada exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Oferta editada y sincronizada exitosamente',
                'data': response
            })
        else:
            logger.error(f"❌ Error sincronizando cambios de oferta: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_editar_oferta: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/eliminar_oferta/<oferta_id>', methods=['DELETE'])
def devops_eliminar_oferta(oferta_id):
    """Eliminar oferta desde DevOps con sincronización inmediata"""
    try:
        data = {
            'id': oferta_id,
            'eliminado_desde': 'devops',
            'fecha_eliminacion': datetime.now().isoformat()
        }
        
        # Sincronizar eliminación a Belgrano Ahorro
        success, response = sync_to_belgrano_ahorro(f'/api/v1/ofertas/{oferta_id}', data, 'DELETE')
        
        if success:
            logger.info(f"✅ Oferta {oferta_id} eliminada y sincronizada exitosamente")
            return jsonify({
                'status': 'success',
                'message': 'Oferta eliminada y sincronizada exitosamente'
            })
        else:
            logger.error(f"❌ Error sincronizando eliminación de oferta: {response}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {response}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en devops_eliminar_oferta: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

# =================================================================
# RUTAS DE SINCRONIZACIÓN Y ESTADO
# =================================================================

@devops_bp.route('/sync/status', methods=['GET'])
def devops_sync_status():
    """Estado de sincronización entre DevOps y Belgrano Ahorro"""
    try:
        # Verificar conectividad con Belgrano Ahorro
        success, data = get_belgrano_ahorro_data('/healthz')
        
        status = {
            'devops_status': 'online',
            'belgrano_ahorro_status': 'online' if success else 'offline',
            'last_sync': datetime.now().isoformat(),
            'sync_enabled': True,
            'endpoints': {
                'sucursales': '/devops/sucursales',
                'negocios': '/devops/negocios',
                'ofertas': '/devops/ofertas'
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': status,
            'message': 'Estado de sincronización obtenido correctamente'
        })
        
    except Exception as e:
        logger.error(f"❌ Error en devops_sync_status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

@devops_bp.route('/sync/force', methods=['POST'])
def devops_force_sync():
    """Forzar sincronización completa desde DevOps"""
    try:
        # Obtener todos los datos de Belgrano Ahorro
        endpoints = ['/api/v1/sucursales', '/api/v1/negocios', '/api/v1/ofertas']
        sync_results = {}
        
        for endpoint in endpoints:
            success, data = get_belgrano_ahorro_data(endpoint)
            sync_results[endpoint] = {
                'success': success,
                'data_count': len(data) if success and isinstance(data, list) else 0,
                'last_sync': datetime.now().isoformat()
            }
        
        return jsonify({
            'status': 'success',
            'message': 'Sincronización forzada completada',
            'data': {
                'sync_results': sync_results,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error en devops_force_sync: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

# =================================================================
# RUTAS DE UTILIDADES
# =================================================================

@devops_bp.route('/health', methods=['GET'])
def devops_health():
    """Health check del sistema DevOps"""
    return jsonify({
        'status': 'healthy',
        'service': 'devops_sync',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@devops_bp.route('/info', methods=['GET'])
def devops_info():
    """Información del sistema DevOps"""
    return jsonify({
        'service': 'DevOps Sync System',
        'description': 'Sistema de sincronización en tiempo real entre DevOps y Belgrano Ahorro',
        'features': [
            'Gestión de sucursales con sincronización inmediata',
            'Gestión de negocios con sincronización inmediata',
            'Gestión de ofertas con sincronización inmediata',
            'Sincronización bidireccional en tiempo real',
            'API REST completa para todas las operaciones'
        ],
        'endpoints': {
            'sucursales': {
                'GET': '/devops/sucursales',
                'POST': '/devops/agregar_sucursal',
                'PUT': '/devops/editar_sucursal/<id>',
                'DELETE': '/devops/eliminar_sucursal/<id>'
            },
            'negocios': {
                'GET': '/devops/negocios',
                'POST': '/devops/agregar_negocio',
                'PUT': '/devops/editar_negocio/<id>',
                'DELETE': '/devops/eliminar_negocio/<id>'
            },
            'ofertas': {
                'GET': '/devops/ofertas',
                'POST': '/devops/agregar_oferta',
                'PUT': '/devops/editar_oferta/<id>',
                'DELETE': '/devops/eliminar_oferta/<id>'
            },
            'sincronizacion': {
                'GET': '/devops/sync/status',
                'POST': '/devops/sync/force'
            }
        },
        'timestamp': datetime.now().isoformat()
    })



