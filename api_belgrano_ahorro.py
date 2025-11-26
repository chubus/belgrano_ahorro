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

# ==========================================
# HELPER: Conversión segura a boolean
# ==========================================
def _to_boolean(value, default=True):
    """
    Convertir valor a boolean de forma segura
    Acepta: True/False, 1/0, "true"/"false", "1"/"0"
    Retorna: True o False (nunca integer)
    
    CORRECCIÓN: PostgreSQL requiere boolean, no integer
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        # CORRECCIÓN: Convertir 1/0 explícitamente a True/False
        return True if value != 0 else False
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
            return True
        if value_lower in ('false', '0', 'no', 'off'):
            return False
    return default

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
    """Decorator mejorado para requerir API key válida (solo headers, no query params por seguridad)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_api_key = BELGRANO_AHORRO_API_KEY
        api_key = None
        
        # Método 1: Bearer token en Authorization header (RECOMENDADO)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ')[1]
        
        # Método 2: X-API-Key header (ALTERNATIVO)
        if not api_key:
            api_key = request.headers.get('X-API-Key')
        
        # SEGURIDAD: NO permitir API key en query parameters
        # Query params pueden quedar en logs, historial, referrers, etc.
        
        # Verificar API key
        if not api_key:
            return jsonify({
                'error': 'API key required', 
                'methods': ['Bearer token en Authorization header', 'X-API-Key header'],
                'note': 'API keys en query parameters no están permitidas por seguridad'
            }), 401
        
        if api_key != expected_api_key:
            logger.warning(f"[SECURITY] Invalid API key attempt from {request.remote_addr}: {api_key[:10]}...")
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
        
        # CORRECCIÓN: Detectar campos booleanos en el query y convertir valores automáticamente
        # Buscar nombres de campos booleanos comunes en el INSERT
        boolean_fields = ['activo', 'activa', 'destacado', 'destacada']
        column_names = []  # Definir en scope superior para uso posterior
        
        if '?' in query and params:
            # Extraer nombres de columnas del query
            import re
            # Buscar "INSERT INTO tabla (col1, col2, ...)"
            match = re.search(r'INSERT\s+INTO\s+\w+\s*\(([^)]+)\)', query, re.IGNORECASE)
            if match:
                column_names = [col.strip().lower() for col in match.group(1).split(',')]
                logger.info(f"[API] 🔍 Columnas detectadas en query: {column_names}")
            else:
                logger.warning(f"[API] ⚠️ No se pudieron detectar nombres de columnas en query: {query[:100]}")
            
            # Procesar cada parámetro
            for i, param in enumerate(params):
                param_name = f'p{i}'
                adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                
                # CORRECCIÓN: Convertir a boolean si el campo es booleano
                if i < len(column_names):
                    col_name = column_names[i]
                    if col_name in boolean_fields:
                        # SIEMPRE convertir a boolean, sin importar el tipo actual
                        original_value = param
                        original_type = type(original_value).__name__
                        param_dict[param_name] = _to_boolean(param, default=True)
                        # Siempre loguear la conversión para debugging
                        logger.info(f"[API] ✅ Convertido campo booleano '{col_name}' (índice {i}): {original_value} ({original_type}) -> {param_dict[param_name]} (bool)")
                    else:
                        param_dict[param_name] = param
                else:
                    # Si no hay nombre de columna, verificar si el valor es 1/0 y podría ser boolean
                    if isinstance(param, int) and param in (0, 1):
                        logger.warning(f"[API] ⚠️ Parámetro {i} es {param} (int) pero no se pudo identificar columna. Verificando si podría ser boolean...")
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
        
        # CORRECCIÓN FINAL: Verificar que todos los campos booleanos sean realmente boolean
        # Esto es una verificación de seguridad adicional - FORZAR conversión
        for param_name, param_value in list(param_dict.items()):
            # Extraer índice del parámetro (p0, p1, p2, etc.)
            param_index = int(param_name[1:]) if param_name.startswith('p') and param_name[1:].isdigit() else -1
            if param_index >= 0 and param_index < len(column_names):
                col_name = column_names[param_index]
                if col_name in boolean_fields:
                    # SIEMPRE convertir si es campo booleano, sin importar el tipo actual
                    if not isinstance(param_value, bool):
                        original_value = param_value
                        original_type = type(original_value).__name__
                        param_dict[param_name] = _to_boolean(param_value, default=True)
                        logger.warning(f"[API] ⚠️ FORZANDO conversión de campo booleano '{col_name}' (parámetro {param_name}): {original_value} ({original_type}) -> {param_dict[param_name]} (bool)")
                    else:
                        logger.debug(f"[API] ✅ Campo booleano '{col_name}' ya es boolean: {param_value}")
            else:
                # Si no se pudo identificar la columna pero el valor es 0/1, verificar si podría ser boolean
                if isinstance(param_value, int) and param_value in (0, 1):
                    logger.warning(f"[API] ⚠️ Parámetro {param_name} es {param_value} (int) pero no se pudo identificar columna. Podría ser boolean.")
        
        # Log final de parámetros antes de ejecutar
        logger.info(f"[API] 🔍 Parámetros finales antes de ejecutar: {param_dict}")
        
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
        
        # AUTO-HEALING ROBUSTO
        # Intentar obtener el mensaje de error completo incluyendo la excepción original de DBAPI
        error_str = str(e).lower()
        if hasattr(e, 'orig'):
            error_str += " " + str(e.orig).lower()
            
        # Detectar error de columna faltante (image_url o imagen)
        if "undefinedcolumn" in error_str and ("image_url" in error_str or "imagen" in error_str):
            healing_session = None
            try:
                # Identificar columna faltante
                missing_col = "image_url" if "image_url" in error_str else "imagen"
                
                # Identificar tabla
                target_table = table_name
                if not target_table:
                    import re
                    match = re.search(r'INSERT\s+INTO\s+(\w+)', query, re.IGNORECASE)
                    if match:
                        target_table = match.group(1)
                
                if target_table:
                    logger.warning(f"[API] ⚠️ Detectada columna faltante '{missing_col}' en tabla '{target_table}'. Iniciando AUTO-HEALING con nueva sesión...")
                    
                    # Usar una NUEVA sesión para el DDL para evitar problemas con la transacción anterior
                    healing_session = get_db_connection()
                    
                    # Crear columna
                    healing_session.execute(text(f"ALTER TABLE {target_table} ADD COLUMN IF NOT EXISTS {missing_col} TEXT"))
                    healing_session.commit()
                    logger.info(f"[API] ✅ Columna '{missing_col}' creada exitosamente en '{target_table}'.")
                    
                    # Cerrar sesión de healing
                    healing_session.close()
                    healing_session = None
                    
                    # Reintentar INSERT con la sesión original (que ya hizo rollback)
                    logger.info(f"[API] 🔄 Reintentando INSERT original...")
                    result = session.execute(text(adapted_query), param_dict)
                    row = result.fetchone()
                    if row:
                        inserted_id = row[0] if hasattr(row, '__getitem__') else row.id
                        session.commit()
                        return inserted_id
            except Exception as healing_error:
                logger.error(f"[API] ❌ Falló el AUTO-HEALING: {healing_error}")
                if healing_session:
                    healing_session.close()
                # Si falla el healing, lanzar el error original
        
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
        
        # CORRECCIÓN: Convertir activo a boolean (no integer)
        # PostgreSQL requiere boolean, no integer (1/0)
        activo_raw = data.get('activo', True)
        activo = _to_boolean(activo_raw, default=True)
        
        # Log para debugging
        if activo_raw != activo or not isinstance(activo, bool):
            logger.info(f"[API] ✅ Convertido 'activo' en api_negocio_create: {activo_raw} ({type(activo_raw).__name__}) -> {activo} (bool)")
        
        # Validar que los campos no sean None
        nombre = str(data['nombre']).strip() if data.get('nombre') else ''
        if not nombre:
            return jsonify({'error': 'Nombre no puede estar vacío'}), 400
        
        # Usar función helper para PostgreSQL
        # NOTA: execute_insert_returning_id ahora convierte automáticamente campos booleanos
        try:
            # FORZAR conversión a boolean ANTES de pasar a execute_insert_returning_id
            # Esto es crítico porque JSON puede deserializar True como 1
            if not isinstance(activo, bool):
                logger.warning(f"[API] ⚠️ 'activo' no es boolean antes de execute_insert_returning_id: {activo} ({type(activo).__name__})")
                activo = _to_boolean(activo, default=True)
                logger.info(f"[API] ✅ 'activo' convertido a boolean: {activo} (bool)")
            
            # VERIFICACIÓN FINAL: Asegurar que activo sea boolean
            activo = bool(_to_boolean(activo, default=True))
            if not isinstance(activo, bool):
                logger.error(f"[API] ❌ ERROR CRÍTICO: 'activo' todavía no es boolean después de conversión: {activo} ({type(activo).__name__})")
                activo = True  # Fallback seguro
            
            logger.info(f"[API] 🔍 Verificación final antes de INSERT: activo = {activo} (tipo: {type(activo).__name__})")
            
            negocio_id = execute_insert_returning_id(
                '''
                INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    nombre,
                    str(data.get('descripcion', '')).strip(),
                    str(data.get('direccion', '')).strip(),
                    str(data.get('telefono', '')).strip(),
                    str(data.get('email', '')).strip(),
                    activo,  # DEBE ser boolean (True/False), NO integer
                    data.get('image_url', '')
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
            
            # CORRECCIÓN: Manejar campo activo como boolean
            if 'activo' in data:
                update_fields.append("activo = :activo")
                params['activo'] = _to_boolean(data['activo'], default=True)
            
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
        
        # CORRECCIÓN: Convertir activo y destacado a boolean (no integer)
        # PostgreSQL requiere boolean, no integer (1/0)
        activo = _to_boolean(data.get('activo', True), default=True)
        destacado = _to_boolean(data.get('destacado', False), default=False)
        
        # Usar función helper para PostgreSQL
        producto_id = execute_insert_returning_id(
            '''
            INSERT INTO productos (nombre, store, precio, original_price, categoria, imagen, image_url,
                                stock, stock_minimo, negocio_id, activo, destacado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                store,
                float(data['precio']),
                float(data.get('original_price', data['precio'])),
                categoria,
                data.get('imagen', ''),
                data.get('image_url', ''),
                int(data.get('stock', 0)),
                int(data.get('stock_minimo', 5)),
                int(data.get('negocio_id', 1)),
                activo,  # Ahora es boolean (True/False), no integer
                destacado  # Ahora es boolean (True/False), no integer
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
                         'stock', 'stock_minimo', 'negocio_id']:
                if field in data:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            # CORRECCIÓN: Manejar campos booleanos (activo, destacado) como boolean
            if 'activo' in data:
                update_fields.append("activo = :activo")
                params['activo'] = _to_boolean(data['activo'], default=True)
            
            if 'destacado' in data:
                update_fields.append("destacado = :destacado")
                params['destacado'] = _to_boolean(data['destacado'], default=False)
            
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
        
        # CORRECCIÓN: Convertir activo/activa a boolean (no integer)
        # PostgreSQL requiere boolean, no integer (1/0)
        # Aceptar tanto 'activa' como 'activo' para compatibilidad
        if 'activa' in data:
            activo = _to_boolean(data['activa'], default=True)
        elif 'activo' in data:
            activo = _to_boolean(data['activo'], default=True)
        else:
            activo = True  # Por defecto activo
        
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
                activo  # Ahora es boolean (True/False), no integer
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
        
        # CORRECCIÓN: Convertir activo a boolean (no integer)
        # PostgreSQL requiere boolean, no integer (1/0)
        activo = _to_boolean(data.get('activo', True), default=True)
        
        # Usar función helper para PostgreSQL
        sucursal_id = execute_insert_returning_id(
            '''
            INSERT INTO sucursales (nombre, direccion, telefono, email, negocio_id, activo, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                data.get('direccion', ''),
                data.get('telefono', ''),
                data.get('email', ''),
                int(data['negocio_id']),
                activo,  # Ahora es boolean (True/False), no integer
                data.get('image_url', '')
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
                        logger.info(f"[API] 🔍 Procesando {len(carrito_items)} items para Ticketera...")
                        
                        for idx, item in enumerate(carrito_items, 1):
                            try:
                                # Obtener información completa del producto
                                result = session.execute(text('''
                                    SELECT id, nombre, descripcion, precio, stock, destacado, 
                                           negocio_id, categoria_id, sucursales
                                    FROM productos WHERE id = :producto_id
                                '''), {'producto_id': item['producto_id']})
                                prod_row = result.fetchone()
                                
                                if not prod_row:
                                    logger.warning(f"[API] ⚠️ Producto {item['producto_id']} no encontrado, usando datos básicos")
                                    productos_lista.append({
                                        'id': str(item['producto_id']),
                                        'nombre': 'Producto no encontrado',
                                        'precio': float(item['precio_unitario']),
                                        'cantidad': int(item['cantidad']),
                                        'subtotal': float(item['precio_unitario']) * int(item['cantidad'])
                                    })
                                    continue
                                
                                prod_data = dict(prod_row._mapping)
                                
                                # Obtener información del negocio si existe
                                negocio_nombre = 'Negocio no especificado'
                                if prod_data.get('negocio_id'):
                                    neg_result = session.execute(text('''
                                        SELECT nombre FROM negocios WHERE id = :negocio_id
                                    '''), {'negocio_id': prod_data['negocio_id']})
                                    neg_row = neg_result.fetchone()
                                    if neg_row:
                                        negocio_nombre = dict(neg_row._mapping)['nombre']
                                
                                # Obtener información de la categoría si existe
                                categoria_nombre = 'Sin categoría'
                                if prod_data.get('categoria_id'):
                                    cat_result = session.execute(text('''
                                        SELECT nombre FROM categorias WHERE id = :categoria_id
                                    '''), {'categoria_id': prod_data['categoria_id']})
                                    cat_row = cat_result.fetchone()
                                    if cat_row:
                                        categoria_nombre = dict(cat_row._mapping)['nombre']
                                
                                # Obtener información de la sucursal si existe
                                sucursal_nombre = 'Sucursal no especificada'
                                if prod_data.get('sucursales'):
                                    try:
                                        import json
                                        if isinstance(prod_data['sucursales'], str):
                                            sucursales_ids = json.loads(prod_data['sucursales'])
                                        else:
                                            sucursales_ids = prod_data['sucursales']
                                        
                                        if sucursales_ids and len(sucursales_ids) > 0:
                                            suc_id = sucursales_ids[0] if isinstance(sucursales_ids, list) else sucursales_ids
                                            suc_result = session.execute(text('''
                                                SELECT nombre FROM sucursales WHERE id = :sucursal_id
                                            '''), {'sucursal_id': suc_id})
                                            suc_row = suc_result.fetchone()
                                            if suc_row:
                                                sucursal_nombre = dict(suc_row._mapping)['nombre']
                                    except Exception as e:
                                        logger.debug(f"[API] No se pudo obtener sucursal: {e}")
                                
                                # Construir objeto producto completo para Ticketera
                                cantidad = int(item['cantidad'])
                                precio = float(item['precio_unitario'])
                                subtotal = precio * cantidad
                                
                                producto_ticket = {
                                    'id': str(prod_data.get('id', item['producto_id'])),
                                    'nombre': prod_data.get('nombre', 'Producto sin nombre'),
                                    'precio': precio,
                                    'cantidad': cantidad,
                                    'subtotal': subtotal,
                                    'sucursal': sucursal_nombre,
                                    'negocio': negocio_nombre,
                                    'categoria': categoria_nombre,
                                    'descripcion': prod_data.get('descripcion', 'Sin descripción'),
                                    'stock': int(prod_data.get('stock', 0)),
                                    'destacado': bool(prod_data.get('destacado', False))
                                }
                                
                                productos_lista.append(producto_ticket)
                                logger.debug(f"[API] ✅ Producto {idx} procesado: {producto_ticket['nombre']} x{producto_ticket['cantidad']}")
                                
                            except Exception as e:
                                logger.error(f"[API] ❌ Error procesando item {idx}: {e}")
                                import traceback
                                logger.error(traceback.format_exc())
                                continue
                        
                        logger.info(f"[API] ✅ {len(productos_lista)} productos procesados correctamente para Ticketera")
                        
                        # Enviar a Ticketera
                        import requests
                        from config import BELGRANO_AHORRO_API_KEY
                        ticket_data = {
                            'numero': numero_pedido,
                            'cliente_nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() or usuario.get('email', 'Cliente'),
                            'cliente_direccion': data['direccion_entrega'],
                            'cliente_telefono': usuario.get('telefono', ''),
                            'cliente_email': usuario.get('email', ''),
                            'productos': productos_lista,  # CORRECCIÓN: Enviar lista, no JSON string
                            'total': total,
                            'estado': 'pendiente',
                            'prioridad': 'normal',
                            'origen': 'belgrano_ahorro',
                            'fecha_creacion': datetime.now().isoformat()
                        }
                        
                        headers = {
                            'Content-Type': 'application/json',
                            'X-API-Key': BELGRANO_AHORRO_API_KEY  # CORRECCIÓN: Agregar API Key requerida
                        }
                        
                        response = requests.post(
                            f"{ticketera_url.rstrip('/')}/api/tickets/recibir",  # CORRECCIÓN: Usar endpoint correcto
                            json=ticket_data,
                            headers=headers,
                            timeout=20  # Aumentar timeout
                        )
                        
                        if response.status_code in (200, 201):
                            ticket_creado = response.json()
                            logger.info(f"[API] ✅ Ticket creado en Ticketera para pedido {numero_pedido}")
                            logger.info(f"[API]    Ticket ID: {ticket_creado.get('ticket_id', 'N/A')}")
                            logger.info(f"[API]    Productos enviados: {len(productos_lista)} items")
                            
                            # Verificar productos en la respuesta
                            productos_respuesta = ticket_creado.get('productos', [])
                            if productos_respuesta:
                                logger.info(f"[API]    Productos recibidos en respuesta: {len(productos_respuesta)} items")
                                for idx, prod in enumerate(productos_respuesta[:5], 1):  # Mostrar primeros 5
                                    logger.info(f"[API]       {idx}. {prod.get('nombre', 'Sin nombre')} x{prod.get('cantidad', 0)}")
                            else:
                                logger.warning(f"[API]    ⚠️ No se recibieron productos en la respuesta de Ticketera")
                        else:
                            logger.warning(f"[API] ⚠️ Ticketera respondió con código {response.status_code}: {response.text[:200]}")
                            logger.warning(f"[API]    Productos que se intentaron enviar: {len(productos_lista)} items")
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

# NO inicializar tablas al importar el módulo
# La inicialización debe hacerse explícitamente desde app_unificado.py o wsgi.py
# Esto evita doble inicialización y problemas de importación circular
logger.debug("[API] Módulo api_belgrano_ahorro importado. La inicialización de DB se hace desde app_unificado.py")
