#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API RESTful Mejorada para Belgrano Ahorro
Endpoints completos con múltiples métodos de autenticación
Soporte bilingüe: español e inglés
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from functools import wraps
from contextlib import contextmanager
from sqlalchemy import text

# Configurar logging con prefijo [API]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar configuración centralizada
try:
    from config import DATABASE_URL, BELGRANO_AHORRO_API_KEY
except ImportError:
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
    if not DATABASE_URL:
        raise ValueError("[API] ERROR: DATABASE_URL no configurada")

# Crear blueprint para la API
api_bp = Blueprint('belgrano_api', __name__, url_prefix='/api')

def register_api_blueprint(app):
    """Registrar el blueprint de API en la aplicación Flask"""
    if 'belgrano_api' not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(api_bp)
        logger.info("API blueprint registrado correctamente")
    else:
        logger.info("API blueprint ya estaba registrado")

def require_api_key(f):
    """Decorator mejorado para requerir API key válida con múltiples métodos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_api_key = BELGRANO_AHORRO_API_KEY
        api_key = None
        
        # Método 1: Bearer token en Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ')[1]
        
        # Método 2: X-API-Key header
        if not api_key:
            api_key = request.headers.get('X-API-Key')
        
        # Método 3: Query parameter
        if not api_key:
            api_key = request.args.get('api_key')
        
        # Verificar API key
        if not api_key:
            return jsonify({'error': 'API key required', 'methods': ['Bearer token', 'X-API-Key header', 'api_key query param']}), 401
        
        if api_key != expected_api_key:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Obtener conexión a la base de datos PostgreSQL"""
    from db_abstraction import get_db_connection as get_db_conn_abstracted
    return get_db_conn_abstracted()

@contextmanager
def db_connection():
    """
    Context manager para conexión de base de datos PostgreSQL
    """
    session = get_db_connection()
    try:
        yield session
    finally:
        session.close()

def execute_insert_returning_id(query: str, params: tuple, table_name: str = None):
    """
    Ejecutar INSERT y retornar el ID del registro insertado
    SIEMPRE usa PostgreSQL
    
    Args:
        query: Query INSERT (puede usar ? para parámetros)
        params: Tupla de parámetros
        table_name: Nombre de la tabla (para PostgreSQL RETURNING)
    
    Returns:
        ID del registro insertado
    """
    session = get_db_connection()
    try:
        # Convertir ? a :param para PostgreSQL
        adapted_query = query
        param_dict = {}
        if '?' in query and params:
            for i, param in enumerate(params):
                param_name = f'p{i}'
                adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                param_dict[param_name] = param
        
        # Agregar RETURNING si no está
        if 'RETURNING' not in adapted_query.upper():
            # Extraer nombre de tabla del query si no se proporciona
            if not table_name:
                # Intentar extraer de "INSERT INTO tabla"
                import re
                match = re.search(r'INSERT\s+INTO\s+(\w+)', adapted_query, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
            
            if table_name:
                adapted_query = adapted_query.rstrip(';') + f' RETURNING {table_name}.id'
        
        result = session.execute(text(adapted_query), param_dict)
        row = result.fetchone()
        if row:
            inserted_id = row[0] if hasattr(row, '__getitem__') else row.id
            session.commit()
            return inserted_id
        else:
            session.commit()
            return None
    except Exception as e:
        session.rollback()
        logger.error(f"[API] Error en execute_insert_returning_id: {e}")
        raise
    finally:
        session.close()

def execute_select(query: str, params: tuple = None):
    """
    Ejecutar SELECT y retornar resultados en PostgreSQL
    
    Returns:
        Lista de diccionarios con los resultados
    """
    session = get_db_connection()
    try:
        # Convertir ? a :param si es necesario
        adapted_query = query
        param_dict = {}
        if '?' in query and params:
            for i, param in enumerate(params):
                param_name = f'p{i}'
                adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                param_dict[param_name] = param
        
        result = session.execute(text(adapted_query), param_dict if param_dict else {})
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
    finally:
        session.close()

def execute_update_delete(query: str, params: tuple = None):
    """
    Ejecutar UPDATE o DELETE en PostgreSQL
    
    Returns:
        Número de filas afectadas
    """
    session = get_db_connection()
    try:
        # Convertir ? a :param si es necesario
        adapted_query = query
        param_dict = {}
        if '?' in query and params:
            for i, param in enumerate(params):
                param_name = f'p{i}'
                adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                param_dict[param_name] = param
        
        result = session.execute(text(adapted_query), param_dict if param_dict else {})
        session.commit()
        return result.rowcount
    except Exception as e:
        session.rollback()
        logger.error(f"[API] Error en execute_update_delete: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        session.close()

def ensure_tables():
    """
    Crear tablas requeridas si no existen en PostgreSQL
    DEPRECATED: Usar init_db() de init_db.py en su lugar
    """
    logger.warning("[API] ensure_tables() está deprecado. Use init_db() de init_db.py")
    try:
        from init_db import init_db
        init_db()
        logger.info("[API] ✅ Tablas verificadas/creadas usando init_db()")
    except ImportError:
        logger.error("[API] ❌ No se pudo importar init_db. Las tablas deben crearse manualmente.")
    except Exception as e:
        logger.error(f"[API] ❌ Error en ensure_tables: {e}")
        import traceback
        logger.error(traceback.format_exc())

# =============================
# ENDPOINTS DE NEGOCIOS
# =============================

@api_bp.route('/negocios', methods=['GET'])
@require_api_key
def api_negocios():
    """Obtener lista de negocios"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT id, nombre, descripcion, direccion, telefono, email, activo,
                       fecha_creacion, fecha_actualizacion
                FROM negocios 
                WHERE activo = TRUE
                ORDER BY nombre
            '''))
            negocios = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': negocios,
                'total': len(negocios),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_negocios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios', methods=['POST'])
@require_api_key
def api_negocio_create():
    """Crear nuevo negocio"""
    try:
        # Asegurar que las tablas existan antes de insertar
        ensure_tables()
        
        data = request.get_json()
        if not data or 'nombre' not in data:
            return jsonify({'error': 'Nombre es requerido'}), 400
        
        # Aceptar activo (booleano o entero) y convertirlo
        activo = 1
        if 'activo' in data:
            activo = 1 if (data['activo'] is True or data['activo'] == 1 or str(data['activo']).lower() == 'true') else 0
        
        # Validar que los campos no sean None
        nombre = str(data['nombre']).strip() if data.get('nombre') else ''
        if not nombre:
            return jsonify({'error': 'Nombre no puede estar vacío'}), 400
        
        # Usar función helper para PostgreSQL
        try:
            negocio_id = execute_insert_returning_id(
                '''
                INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    nombre,
                    str(data.get('descripcion', '')).strip(),
                    str(data.get('direccion', '')).strip(),
                    str(data.get('telefono', '')).strip(),
                    str(data.get('email', '')).strip(),
                    activo
                ),
                table_name='negocios'
            )
        except Exception as db_error:
            logger.error(f"Error en execute_insert_returning_id: {db_error}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f'Error al insertar en base de datos: {str(db_error)}',
                'status_code': 500
            }), 500
        
        if negocio_id:
            logger.info(f"✅ Negocio creado exitosamente: ID {negocio_id}, Nombre: {nombre}")
            return jsonify({
                'status': 'success',
                'message': 'Negocio creado exitosamente',
                'data': {'id': negocio_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            logger.error("❌ Error: execute_insert_returning_id retornó None")
            return jsonify({
                'error': 'Error al crear negocio: No se pudo obtener el ID del registro insertado',
                'status_code': 500
            }), 500
            
    except Exception as e:
        logger.error(f"Error in api_negocio_create: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'status_code': 500
        }), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['GET'])
@require_api_key
def api_negocio_detail(negocio_id):
    """Obtener detalles de un negocio específico"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT id, nombre, descripcion, direccion, telefono, email, activo,
                       fecha_creacion, fecha_actualizacion
                FROM negocios 
                WHERE id = :id AND activo = TRUE
            '''), {'id': negocio_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'error': 'Negocio no encontrado'}), 404
            
            return jsonify({
                'status': 'success',
                'data': dict(row._mapping),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_negocio_detail: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['PUT'])
@require_api_key
def api_negocio_update(negocio_id):
    """Actualizar negocio existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Verificar que el negocio existe
            result = session.execute(text('SELECT id FROM negocios WHERE id = :id AND activo = TRUE'), {'id': negocio_id})
            if not result.fetchone():
                return jsonify({'error': 'Negocio no encontrado'}), 404
            
            # Actualizar campos
            update_fields = []
            params = {}
            
            for field in ['nombre', 'descripcion', 'direccion', 'telefono', 'email']:
                if field in data:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            if not update_fields:
                return jsonify({'error': 'No hay campos para actualizar'}), 400
            
            update_fields.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            params['id'] = negocio_id
            
            session.execute(text(f'''
                UPDATE negocios 
                SET {', '.join(update_fields)}
                WHERE id = :id
            '''), params)
            
            session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Negocio actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            session.rollback()
            logger.error(f"[API] Error in api_negocio_update: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_negocio_update: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['DELETE'])
@require_api_key
def api_negocio_delete(negocio_id):
    """Eliminar negocio (soft delete)"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Verificar que el negocio existe
            result = session.execute(text('SELECT id FROM negocios WHERE id = :id AND activo = TRUE'), {'id': negocio_id})
            if not result.fetchone():
                return jsonify({'error': 'Negocio no encontrado'}), 404
            
            # Soft delete
            session.execute(text('''
                UPDATE negocios 
                SET activo = FALSE, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'id': negocio_id})
            
            session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Negocio eliminado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            session.rollback()
            logger.error(f"[API] Error in api_negocio_delete: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_negocio_delete: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE PRODUCTOS
# =============================

@api_bp.route('/productos', methods=['GET'])
@require_api_key
def api_productos():
    """Obtener lista de productos"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT p.id, p.nombre, p.store, p.precio, p.original_price, p.categoria,
                       p.imagen, p.stock, p.stock_minimo, p.negocio_id, p.activo, p.destacado,
                       p.fecha_creacion, p.fecha_actualizacion,
                       n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.activo = TRUE
                ORDER BY p.destacado DESC, p.nombre
            '''))
            
            productos = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': productos,
                'total': len(productos),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_productos: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos', methods=['POST'])
@require_api_key
def api_producto_create():
    """Crear nuevo producto"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'precio' not in data:
            return jsonify({'error': 'Nombre y precio son requeridos'}), 400
        
        # Mapear campos: DevOps puede enviar 'descripcion' -> 'store', 'categoria_id' -> 'categoria'
        store = data.get('store', data.get('descripcion', ''))
        categoria = data.get('categoria', '')
        # Si viene categoria_id, intentar obtener el nombre de la categoría (por ahora usar el ID como string)
        if not categoria and 'categoria_id' in data:
            categoria = str(data['categoria_id'])
        
        # Aceptar activo (booleano o entero) y convertirlo a 1 o 0
        activo = 1
        if 'activo' in data:
            activo = 1 if (data['activo'] is True or data['activo'] == 1 or str(data['activo']).lower() == 'true') else 0
        
        # Usar función helper para PostgreSQL
        producto_id = execute_insert_returning_id(
            '''
            INSERT INTO productos (nombre, store, precio, original_price, categoria, imagen, 
                                stock, stock_minimo, negocio_id, activo, destacado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                store,
                float(data['precio']),
                float(data.get('original_price', data['precio'])),
                categoria,
                data.get('imagen', ''),
                int(data.get('stock', 0)),
                int(data.get('stock_minimo', 5)),
                int(data.get('negocio_id', 1)),
                activo,
                int(data.get('destacado', 0))
            ),
            table_name='productos'
        )
        
        if producto_id:
            return jsonify({
                'status': 'success',
                'message': 'Producto creado exitosamente',
                'data': {'id': producto_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear producto'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_producto_create: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['GET'])
@require_api_key
def api_producto_detail(producto_id):
    """Obtener detalles de un producto específico"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT p.id, p.nombre, p.store, p.precio, p.original_price, p.categoria,
                       p.imagen, p.stock, p.stock_minimo, p.negocio_id, p.activo, p.destacado,
                       p.fecha_creacion, p.fecha_actualizacion,
                       n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.id = :id AND p.activo = TRUE
            '''), {'id': producto_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            return jsonify({
                'status': 'success',
                'data': dict(row._mapping),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_producto_detail: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_producto_update(producto_id):
    """Actualizar producto existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Verificar que el producto existe
            result = session.execute(text('SELECT id FROM productos WHERE id = :id AND activo = TRUE'), {'id': producto_id})
            if not result.fetchone():
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            # Actualizar campos
            update_fields = []
            params = {}
            
            for field in ['nombre', 'store', 'precio', 'original_price', 'categoria', 'imagen', 
                         'stock', 'stock_minimo', 'negocio_id', 'activo', 'destacado']:
                if field in data:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            if not update_fields:
                return jsonify({'error': 'No hay campos para actualizar'}), 400
            
            update_fields.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            params['id'] = producto_id
            
            session.execute(text(f'''
                UPDATE productos 
                SET {', '.join(update_fields)}
                WHERE id = :id
            '''), params)
            
            session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Producto actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            session.rollback()
            logger.error(f"[API] Error in api_producto_update: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_producto_update: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['DELETE'])
@require_api_key
def api_producto_delete(producto_id):
    """Eliminar producto (soft delete)"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Verificar que el producto existe
            result = session.execute(text('SELECT id FROM productos WHERE id = :id AND activo = TRUE'), {'id': producto_id})
            if not result.fetchone():
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            # Soft delete
            session.execute(text('''
                UPDATE productos 
                SET activo = FALSE, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'id': producto_id})
            
            session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Producto eliminado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            session.rollback()
            logger.error(f"[API] Error in api_producto_delete: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_producto_delete: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE CATEGORÍAS (NUEVO)
# =============================

@api_bp.route('/categorias', methods=['GET'])
@require_api_key
def api_categorias():
    """Obtener lista de categorías"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT id, nombre, descripcion, activa, fecha_creacion
                FROM categorias 
                WHERE activa = TRUE
                ORDER BY nombre
            '''))
            
            categorias = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': categorias,
                'total': len(categorias),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_categorias: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categorias', methods=['POST'])
@require_api_key
def api_categoria_create():
    """Crear nueva categoría"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data:
            return jsonify({'error': 'Nombre es requerido'}), 400
        
        # Usar función helper para PostgreSQL
        categoria_id = execute_insert_returning_id(
            '''
            INSERT INTO categorias (nombre, descripcion)
            VALUES (?, ?)
            ''',
            (
                data['nombre'],
                data.get('descripcion', '')
            ),
            table_name='categorias'
        )
        
        if categoria_id:
            return jsonify({
                'status': 'success',
                'message': 'Categoría creada exitosamente',
                'data': {'id': categoria_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear categoría'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_categoria_create: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE OFERTAS
# =============================

@api_bp.route('/ofertas', methods=['GET'])
@require_api_key
def api_ofertas():
    """Obtener lista de ofertas"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT o.id, o.nombre, o.descripcion, o.descuento, o.fecha_inicio, o.fecha_fin,
                       o.producto_id, o.negocio_id, o.activo, o.fecha_creacion, o.fecha_actualizacion,
                       p.nombre as producto_nombre, n.nombre as negocio_nombre
                FROM ofertas o
                LEFT JOIN productos p ON o.producto_id = p.id
                LEFT JOIN negocios n ON o.negocio_id = n.id
                WHERE o.activo = TRUE
                ORDER BY o.fecha_inicio DESC
            '''))
            
            ofertas = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': ofertas,
                'total': len(ofertas),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_ofertas: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ofertas', methods=['POST'])
@require_api_key
def api_oferta_create():
    """Crear nueva oferta"""
    try:
        data = request.get_json()
        # Aceptar tanto 'nombre' como 'titulo' (DevOps envía 'titulo')
        nombre_oferta = data.get('nombre') or data.get('titulo')
        if not nombre_oferta or 'descuento' not in data:
            return jsonify({'error': 'Nombre/titulo y descuento son requeridos'}), 400
        
        # Aceptar activa (booleano) o activo (entero) y convertirlo a 1 o 0
        activo = 1
        if 'activa' in data:
            activo = 1 if (data['activa'] is True or data['activa'] == 1 or str(data['activa']).lower() == 'true') else 0
        elif 'activo' in data:
            activo = 1 if (data['activo'] is True or data['activo'] == 1 or str(data['activo']).lower() == 'true') else 0
        
        # Obtener negocio_id del producto si no viene directamente
        negocio_id = data.get('negocio_id')
        if not negocio_id and data.get('producto_id'):
            try:
                resultados = execute_select('SELECT negocio_id FROM productos WHERE id = ?', (data['producto_id'],))
                if resultados:
                    negocio_id = resultados[0]['negocio_id']
            except Exception:
                pass  # Si falla, negocio_id queda None
        
        # Usar función helper para PostgreSQL
        oferta_id = execute_insert_returning_id(
            '''
            INSERT INTO ofertas (nombre, descripcion, descuento, fecha_inicio, fecha_fin,
                              producto_id, negocio_id, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                nombre_oferta,
                data.get('descripcion', ''),
                float(data['descuento']),
                data.get('fecha_inicio'),
                data.get('fecha_fin'),
                data.get('producto_id'),
                negocio_id,
                activo
            ),
            table_name='ofertas'
        )
        
        if oferta_id:
            return jsonify({
                'status': 'success',
                'message': 'Oferta creada exitosamente',
                'data': {'id': oferta_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear oferta'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_oferta_create: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE SUCURSALES
# =============================

@api_bp.route('/sucursales', methods=['GET'])
@require_api_key
def api_sucursales():
    """Obtener lista de sucursales"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT s.id, s.nombre, s.direccion, s.telefono, s.email, s.negocio_id, s.activo,
                       s.fecha_creacion, s.fecha_actualizacion, n.nombre as negocio_nombre
                FROM sucursales s
                LEFT JOIN negocios n ON s.negocio_id = n.id
                WHERE s.activo = TRUE
                ORDER BY s.nombre
            '''))
            
            sucursales = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': sucursales,
                'total': len(sucursales),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_sucursales: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sucursales', methods=['POST'])
@require_api_key
def api_sucursal_create():
    """Crear nueva sucursal"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'negocio_id' not in data:
            return jsonify({'error': 'Nombre y negocio_id son requeridos'}), 400
        
        # Usar función helper para PostgreSQL
        sucursal_id = execute_insert_returning_id(
            '''
            INSERT INTO sucursales (nombre, direccion, telefono, email, negocio_id)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                data.get('direccion', ''),
                data.get('telefono', ''),
                data.get('email', ''),
                data['negocio_id']
            ),
            table_name='sucursales'
        )
        
        if sucursal_id:
            return jsonify({
                'status': 'success',
                'message': 'Sucursal creada exitosamente',
                'data': {'id': sucursal_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear sucursal'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_sucursal_create: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE PRECIOS
# =============================

@api_bp.route('/precios', methods=['GET'])
@require_api_key
def api_precios_list():
    """Obtener lista de precios"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            result = session.execute(text('''
                SELECT p.id as producto_id, p.nombre as producto_nombre, p.precio, p.original_price,
                       p.categoria, n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.activo = TRUE
                ORDER BY p.categoria, p.nombre
            '''))
            
            precios = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': precios,
                'total': len(precios),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_precios_list: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/precios/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_precios_update(producto_id):
    """Actualizar precio de producto"""
    try:
        data = request.get_json()
        if not data or 'precio' not in data:
            return jsonify({'error': 'Precio es requerido'}), 400
        
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Verificar que el producto existe
            result = session.execute(text('SELECT id FROM productos WHERE id = :id AND activo = TRUE'), {'id': producto_id})
            if not result.fetchone():
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            # Actualizar precio
            session.execute(text('''
                UPDATE productos 
                SET precio = :precio, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'precio': data['precio'], 'id': producto_id})
            
            session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Precio actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            session.rollback()
            logger.error(f"[API] Error in api_precios_update: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_precios_update: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS V1 (COMPATIBILIDAD)
# =============================

# Crear endpoints v1 que redirijan a los endpoints principales
@api_bp.route('/v1/negocios', methods=['GET', 'POST'])
@require_api_key
def api_v1_negocios():
    """Endpoint v1 para negocios"""
    if request.method == 'GET':
        return api_negocios()
    else:
        return api_negocio_create()

@api_bp.route('/v1/negocios/<int:negocio_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_v1_negocio_detail(negocio_id):
    """Endpoint v1 para detalle de negocio"""
    if request.method == 'GET':
        return api_negocio_detail(negocio_id)
    elif request.method == 'PUT':
        return api_negocio_update(negocio_id)
    else:
        return api_negocio_delete(negocio_id)

@api_bp.route('/v1/productos', methods=['GET', 'POST'])
@require_api_key
def api_v1_productos():
    """Endpoint v1 para productos"""
    if request.method == 'GET':
        return api_productos()
    else:
        return api_producto_create()

@api_bp.route('/v1/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_v1_producto_detail(producto_id):
    """Endpoint v1 para detalle de producto"""
    if request.method == 'GET':
        return api_producto_detail(producto_id)
    elif request.method == 'PUT':
        return api_producto_update(producto_id)
    else:
        return api_producto_delete(producto_id)

@api_bp.route('/v1/categorias', methods=['GET', 'POST'])
@require_api_key
def api_v1_categorias():
    """Endpoint v1 para categorías"""
    if request.method == 'GET':
        return api_categorias()
    else:
        return api_categoria_create()

@api_bp.route('/v1/ofertas', methods=['GET', 'POST'])
@require_api_key
def api_v1_ofertas():
    """Endpoint v1 para ofertas"""
    if request.method == 'GET':
        return api_ofertas()
    else:
        return api_oferta_create()

@api_bp.route('/v1/sucursales', methods=['GET', 'POST'])
@require_api_key
def api_v1_sucursales():
    """Endpoint v1 para sucursales"""
    if request.method == 'GET':
        return api_sucursales()
    else:
        return api_sucursal_create()

@api_bp.route('/v1/precios', methods=['GET'])
@require_api_key
def api_v1_precios():
    """Endpoint v1 para precios"""
    return api_precios_list()

@api_bp.route('/v1/precios/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_v1_precios_update(producto_id):
    """Endpoint v1 para actualizar precios"""
    return api_precios_update(producto_id)

# =============================
# ALIAS EN INGLÉS (COMPATIBILIDAD)
# =============================

# Negocios
api_bp.add_url_rule('/businesses', view_func=api_negocios, methods=['GET', 'POST'])
api_bp.add_url_rule('/businesses/<int:negocio_id>', view_func=api_negocio_detail, methods=['GET', 'PUT', 'DELETE'])

# Sucursales
api_bp.add_url_rule('/branches', view_func=api_sucursales, methods=['GET', 'POST'])
api_bp.add_url_rule('/branches/<int:sucursal_id>', view_func=api_sucursales, methods=['GET', 'PUT', 'DELETE'])

# Productos
api_bp.add_url_rule('/products', view_func=api_productos, methods=['GET', 'POST'])
api_bp.add_url_rule('/products/<int:producto_id>', view_func=api_producto_detail, methods=['GET', 'PUT', 'DELETE'])

# Ofertas
api_bp.add_url_rule('/offers', view_func=api_ofertas, methods=['GET', 'POST'])
api_bp.add_url_rule('/offers/<int:oferta_id>', view_func=api_ofertas, methods=['GET', 'PUT', 'DELETE'])

# Precios
api_bp.add_url_rule('/prices', view_func=api_precios_list, methods=['GET'])
api_bp.add_url_rule('/prices/<int:producto_id>', view_func=api_precios_update, methods=['PUT'])

# Categorías
api_bp.add_url_rule('/categories', view_func=api_categorias, methods=['GET', 'POST'])

# =============================
# ENDPOINTS DE UTILIDAD
# =============================

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Belgrano Ahorro API is running',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'negocios': '/api/negocios',
            'productos': '/api/productos',
            'categorias': '/api/categorias',
            'ofertas': '/api/ofertas',
            'sucursales': '/api/sucursales',
            'precios': '/api/precios',
            'v1': '/api/v1/*'
        }
    })

@api_bp.route('/status', methods=['GET'])
@require_api_key
def api_status():
    """Status detallado de la API"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Contar registros
            result = session.execute(text('SELECT COUNT(*) FROM negocios WHERE activo = TRUE'))
            negocios_count = result.scalar()
            
            result = session.execute(text('SELECT COUNT(*) FROM productos WHERE activo = TRUE'))
            productos_count = result.scalar()
            
            result = session.execute(text('SELECT COUNT(*) FROM categorias WHERE activa = TRUE'))
            categorias_count = result.scalar()
            
            result = session.execute(text('SELECT COUNT(*) FROM ofertas WHERE activo = TRUE'))
            ofertas_count = result.scalar()
            
            result = session.execute(text('SELECT COUNT(*) FROM sucursales WHERE activo = TRUE'))
            sucursales_count = result.scalar()
            
            return jsonify({
                'status': 'success',
                'api_version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'negocios': negocios_count,
                    'productos': productos_count,
                    'categorias': categorias_count,
                    'ofertas': ofertas_count,
                    'sucursales': sucursales_count
                },
                'authentication': {
                    'methods': ['Bearer token', 'X-API-Key header', 'api_key query param'],
                    'required': True
                }
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_status: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE COMPRAS/PEDIDOS
# =============================

@api_bp.route('/compras', methods=['POST'])
@require_api_key
def api_crear_compra():
    """Crear una nueva compra con validación de stock"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Validar campos requeridos
        required_fields = ['usuario_id', 'items', 'metodo_pago', 'direccion_entrega']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        items = data['items']
        if not items or not isinstance(items, list):
            return jsonify({'error': 'Items debe ser una lista no vacía'}), 400
        
        # Importar funciones de validación de stock
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import db as database
        
        # Validar stock para todos los items
        items_para_validar = []
        for item in items:
            if 'producto_id' not in item or 'cantidad' not in item:
                return jsonify({'error': 'Cada item debe tener producto_id y cantidad'}), 400
            items_para_validar.append({
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad']
            })
        
        stock_valido, errores_stock, productos_validos = database.validar_stock_carrito(items_para_validar)
        
        if not stock_valido:
            return jsonify({
                'error': 'Stock insuficiente',
                'detalles': errores_stock
            }), 400
        
        # Calcular total
        total = 0
        carrito_items = []
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            for item in items:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                
                result = session.execute(text('''
                    SELECT id, nombre, precio FROM productos 
                    WHERE id = :id AND activo = TRUE
                '''), {'id': producto_id})
                row = result.fetchone()
                
                if not row:
                    return jsonify({'error': f'Producto {producto_id} no encontrado'}), 404
                
                producto = dict(row._mapping)
                precio = float(producto['precio'])
                subtotal = precio * cantidad
                total += subtotal
                
                carrito_items.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal
                })
        finally:
            session.close()
        
        # Generar número de pedido
        numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{data['usuario_id']}"
        
        # Guardar pedido
        pedido_id = database.guardar_pedido(
            usuario_id=data['usuario_id'],
            numero_pedido=numero_pedido,
            total=total,
            metodo_pago=data['metodo_pago'],
            direccion_entrega=data['direccion_entrega'],
            notas=data.get('notas', '')
        )
        
        if not pedido_id:
            return jsonify({'error': 'Error al crear el pedido'}), 500
        
        # Guardar items del pedido
        items_db = []
        for item in carrito_items:
            items_db.append({
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'subtotal': item['subtotal']
            })
        
        database.guardar_items_pedido(pedido_id, items_db)
        
        # Actualizar stock
        stock_actualizado, resultados_stock, errores_stock = database.actualizar_stock_carrito(items_para_validar)
        
        if not stock_actualizado:
            logger.error(f"Error actualizando stock después de compra: {errores_stock}")
            # El pedido ya está guardado, pero registrar el error
        
        # Intentar enviar a Ticketera si está configurado
        ticket_creado = None
        try:
            ticketera_url = os.getenv('TICKETERA_URL', '')
            if ticketera_url:
                # Obtener datos del usuario
                session = get_db_connection()
                try:
                    from sqlalchemy import text
                    result = session.execute(text('SELECT * FROM usuarios WHERE id = :id'), {'id': data['usuario_id']})
                    row = result.fetchone()
                    
                    if row:
                        usuario = dict(row._mapping)
                        # Preparar datos para Ticketera
                        productos_lista = []
                        for item in carrito_items:
                            result = session.execute(text('SELECT nombre FROM productos WHERE id = :id'), {'id': item['producto_id']})
                            prod_row = result.fetchone()
                            productos_lista.append({
                                'id': item['producto_id'],
                                'nombre': dict(prod_row._mapping)['nombre'] if prod_row else 'Producto',
                                'precio': item['precio_unitario'],
                                'cantidad': item['cantidad']
                            })
                        
                        # Enviar a Ticketera
                        import requests
                        ticket_data = {
                            'numero': numero_pedido,
                            'cliente_nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() or usuario.get('email', 'Cliente'),
                            'cliente_direccion': data['direccion_entrega'],
                            'cliente_telefono': usuario.get('telefono', ''),
                            'cliente_email': usuario.get('email', ''),
                            'productos': json.dumps(productos_lista),
                            'total': total,
                            'estado': 'pendiente',
                            'prioridad': 'normal'
                        }
                        
                        response = requests.post(
                            f"{ticketera_url.rstrip('/')}/api/tickets",
                            json=ticket_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=10
                        )
                        
                        if response.status_code == 201:
                            ticket_creado = response.json()
                            logger.info(f"[API] ✅ Ticket creado en Ticketera para pedido {numero_pedido}")
                finally:
                    session.close()
        except Exception as e:
            logger.warning(f"⚠️ No se pudo enviar a Ticketera: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Compra realizada exitosamente',
            'data': {
                'pedido_id': pedido_id,
                'numero_pedido': numero_pedido,
                'total': total,
                'items': carrito_items,
                'stock_actualizado': stock_actualizado,
                'ticket_creado': ticket_creado is not None
            },
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"[API] Error in api_crear_compra: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api_bp.route('/compras/<int:pedido_id>', methods=['GET'])
@require_api_key
def api_obtener_compra(pedido_id):
    """Obtener detalles de una compra"""
    try:
        session = get_db_connection()
        try:
            from sqlalchemy import text
            
            # Obtener pedido
            result = session.execute(text('''
                SELECT p.*, u.email, u.nombre, u.apellido
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.id = :id
            '''), {'id': pedido_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'error': 'Pedido no encontrado'}), 404
            
            pedido = dict(row._mapping)
            
            # Obtener items del pedido
            result = session.execute(text('''
                SELECT pi.*, pr.nombre as producto_nombre
                FROM items_pedido pi
                LEFT JOIN productos pr ON pi.producto_id = pr.id
                WHERE pi.pedido_id = :id
            '''), {'id': pedido_id})
            
            items = [dict(row._mapping) for row in result.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'pedido': pedido,
                    'items': items
                },
                'timestamp': datetime.now().isoformat()
            })
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"[API] Error in api_obtener_compra: {e}")
        return jsonify({'error': str(e)}), 500

# Inicializar tablas al importar el módulo usando init_db() centralizada
try:
    from init_db import init_db
    # Solo inicializar si no se ha inicializado antes
    _db_initialized = False
    if not _db_initialized:
        try:
            init_db()
            _db_initialized = True
            logger.info("[API] ✅ Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"[API] ❌ Error inicializando base de datos: {e}")
            # No fallar la app, pero registrar el error
except ImportError:
    logger.warning("[API] ⚠️ No se pudo importar init_db. Las tablas deben crearse manualmente.")
