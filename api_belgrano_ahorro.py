#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API REST para Belgrano Ahorro
Expone endpoints para que Belgrano Tickets pueda consumir datos
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import sqlite3
import json
import logging
from functools import wraps

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint para la API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# ==========================================
# UTILIDADES Y DECORADORES
# ==========================================

def require_api_key(f):
    """Decorador para requerir API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != 'belgrano_ahorro_api_key_2025':
            return jsonify({'error': 'API key requerida'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('belgrano_ahorro.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# ENDPOINTS DE PRODUCTOS
# ==========================================

@api_bp.route('/productos', methods=['GET'])
@require_api_key
def get_productos():
    """Obtener todos los productos disponibles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener productos con información de comerciantes
        query = """
        SELECT p.*, c.nombre as comerciante_nombre, c.direccion as comerciante_direccion
        FROM productos p
        LEFT JOIN comerciantes c ON p.comerciante_id = c.id
        WHERE p.activo = 1
        ORDER BY p.nombre
        """
        
        cursor.execute(query)
        productos = cursor.fetchall()
        
        productos_list = []
        for producto in productos:
            productos_list.append({
                'id': producto['id'],
                'nombre': producto['nombre'],
                'descripcion': producto['descripcion'],
                'precio': producto['precio'],
                'categoria': producto['categoria'],
                'stock': producto['stock'],
                'imagen': producto['imagen'],
                'comerciante': {
                    'id': producto['comerciante_id'],
                    'nombre': producto['comerciante_nombre'],
                    'direccion': producto['comerciante_direccion']
                },
                'activo': bool(producto['activo']),
                'fecha_creacion': producto['fecha_creacion']
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'total': len(productos_list),
            'productos': productos_list,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/productos/<int:producto_id>', methods=['GET'])
@require_api_key
def get_producto(producto_id):
    """Obtener un producto específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT p.*, c.nombre as comerciante_nombre, c.direccion as comerciante_direccion
        FROM productos p
        LEFT JOIN comerciantes c ON p.comerciante_id = c.id
        WHERE p.id = ? AND p.activo = 1
        """
        
        cursor.execute(query, (producto_id,))
        producto = cursor.fetchone()
        
        if not producto:
            return jsonify({
                'status': 'error',
                'error': 'Producto no encontrado'
            }), 404
        
        producto_data = {
            'id': producto['id'],
            'nombre': producto['nombre'],
            'descripcion': producto['descripcion'],
            'precio': producto['precio'],
            'categoria': producto['categoria'],
            'stock': producto['stock'],
            'imagen': producto['imagen'],
            'comerciante': {
                'id': producto['comerciante_id'],
                'nombre': producto['comerciante_nombre'],
                'direccion': producto['comerciante_direccion']
            },
            'activo': bool(producto['activo']),
            'fecha_creacion': producto['fecha_creacion']
        }
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'producto': producto_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo producto {producto_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/productos/categoria/<categoria>', methods=['GET'])
@require_api_key
def get_productos_por_categoria(categoria):
    """Obtener productos por categoría"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT p.*, c.nombre as comerciante_nombre
        FROM productos p
        LEFT JOIN comerciantes c ON p.comerciante_id = c.id
        WHERE p.categoria = ? AND p.activo = 1
        ORDER BY p.nombre
        """
        
        cursor.execute(query, (categoria,))
        productos = cursor.fetchall()
        
        productos_list = []
        for producto in productos:
            productos_list.append({
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'stock': producto['stock'],
                'comerciante': producto['comerciante_nombre']
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'categoria': categoria,
            'total': len(productos_list),
            'productos': productos_list,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo productos por categoría {categoria}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# ENDPOINTS DE PEDIDOS
# ==========================================

@api_bp.route('/pedidos', methods=['GET'])
@require_api_key
def get_pedidos():
    """Obtener todos los pedidos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT p.*, u.nombre as cliente_nombre, u.email as cliente_email
        FROM pedidos p
        LEFT JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.fecha_pedido DESC
        LIMIT 100
        """
        
        cursor.execute(query)
        pedidos = cursor.fetchall()
        
        pedidos_list = []
        for pedido in pedidos:
            # Obtener items del pedido
            cursor.execute("""
                SELECT pi.*, p.nombre as producto_nombre
                FROM pedido_items pi
                LEFT JOIN productos p ON pi.producto_id = p.id
                WHERE pi.pedido_id = ?
            """, (pedido['id'],))
            
            items = cursor.fetchall()
            items_list = []
            for item in items:
                items_list.append({
                    'producto_id': item['producto_id'],
                    'producto_nombre': item['producto_nombre'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario'],
                    'subtotal': item['subtotal']
                })
            
            pedidos_list.append({
                'id': pedido['id'],
                'numero_pedido': pedido['numero_pedido'],
                'cliente': {
                    'id': pedido['usuario_id'],
                    'nombre': pedido['cliente_nombre'],
                    'email': pedido['cliente_email']
                },
                'total': pedido['total'],
                'estado': pedido['estado'],
                'metodo_pago': pedido['metodo_pago'],
                'direccion': pedido['direccion'],
                'notas': pedido['notas'],
                'fecha_pedido': pedido['fecha_pedido'],
                'items': items_list
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'total': len(pedidos_list),
            'pedidos': pedidos_list,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pedidos: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/pedidos/<numero_pedido>', methods=['GET'])
@require_api_key
def get_pedido(numero_pedido):
    """Obtener un pedido específico por número"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener pedido
        query = """
        SELECT p.*, u.nombre as cliente_nombre, u.email as cliente_email, u.telefono
        FROM pedidos p
        LEFT JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.numero_pedido = ?
        """
        
        cursor.execute(query, (numero_pedido,))
        pedido = cursor.fetchone()
        
        if not pedido:
            return jsonify({
                'status': 'error',
                'error': 'Pedido no encontrado'
            }), 404
        
        # Obtener items del pedido
        cursor.execute("""
            SELECT pi.*, p.nombre as producto_nombre
            FROM pedido_items pi
            LEFT JOIN productos p ON pi.producto_id = p.id
            WHERE pi.pedido_id = ?
        """, (pedido['id'],))
        
        items = cursor.fetchall()
        items_list = []
        for item in items:
            items_list.append({
                'producto_id': item['producto_id'],
                'producto_nombre': item['producto_nombre'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'subtotal': item['subtotal']
            })
        
        pedido_data = {
            'id': pedido['id'],
            'numero_pedido': pedido['numero_pedido'],
            'cliente': {
                'id': pedido['usuario_id'],
                'nombre': pedido['cliente_nombre'],
                'email': pedido['cliente_email'],
                'telefono': pedido['telefono']
            },
            'total': pedido['total'],
            'estado': pedido['estado'],
            'metodo_pago': pedido['metodo_pago'],
            'direccion': pedido['direccion'],
            'notas': pedido['notas'],
            'fecha_pedido': pedido['fecha_pedido'],
            'items': items_list
        }
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'pedido': pedido_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pedido {numero_pedido}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/pedidos/<numero_pedido>/estado', methods=['PUT'])
@require_api_key
def actualizar_estado_pedido(numero_pedido):
    """Actualizar estado de un pedido"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        if not nuevo_estado:
            return jsonify({
                'status': 'error',
                'error': 'Estado requerido'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Actualizar estado
        cursor.execute("""
            UPDATE pedidos 
            SET estado = ?, fecha_actualizacion = ?
            WHERE numero_pedido = ?
        """, (nuevo_estado, datetime.now().isoformat(), numero_pedido))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'error': 'Pedido no encontrado'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Estado actualizado a {nuevo_estado}',
            'numero_pedido': numero_pedido,
            'estado': nuevo_estado,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando estado del pedido {numero_pedido}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# ENDPOINTS DE USUARIOS
# ==========================================

@api_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@require_api_key
def get_usuario(usuario_id):
    """Obtener información de un usuario"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT id, nombre, email, telefono, direccion, fecha_registro, activo
        FROM usuarios
        WHERE id = ?
        """
        
        cursor.execute(query, (usuario_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({
                'status': 'error',
                'error': 'Usuario no encontrado'
            }), 404
        
        usuario_data = {
            'id': usuario['id'],
            'nombre': usuario['nombre'],
            'email': usuario['email'],
            'telefono': usuario['telefono'],
            'direccion': usuario['direccion'],
            'fecha_registro': usuario['fecha_registro'],
            'activo': bool(usuario['activo'])
        }
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'usuario': usuario_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario {usuario_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# ENDPOINTS DE ESTADÍSTICAS
# ==========================================

@api_bp.route('/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Obtener estadísticas generales"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar usuarios
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = 1")
        total_usuarios = cursor.fetchone()['total']
        
        # Contar productos
        cursor.execute("SELECT COUNT(*) as total FROM productos WHERE activo = 1")
        total_productos = cursor.fetchone()['total']
        
        # Contar pedidos
        cursor.execute("SELECT COUNT(*) as total FROM pedidos")
        total_pedidos = cursor.fetchone()['total']
        
        # Pedidos por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as total
            FROM pedidos
            GROUP BY estado
        """)
        pedidos_por_estado = {row['estado']: row['total'] for row in cursor.fetchall()}
        
        # Total de ventas
        cursor.execute("SELECT SUM(total) as total_ventas FROM pedidos WHERE estado = 'completado'")
        total_ventas = cursor.fetchone()['total_ventas'] or 0
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_usuarios': total_usuarios,
                'total_productos': total_productos,
                'total_pedidos': total_pedidos,
                'pedidos_por_estado': pedidos_por_estado,
                'total_ventas': total_ventas
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# ENDPOINTS DE HEALTH CHECK
# ==========================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check para la API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar conexión a BD
        cursor.execute("SELECT 1")
        db_status = "connected"
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'Belgrano Ahorro API',
            'version': '1.0.0',
            'database': db_status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'Belgrano Ahorro API',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# ENDPOINTS DE SINCRONIZACIÓN
# ==========================================

@api_bp.route('/sync/tickets', methods=['POST'])
@require_api_key
def sync_tickets():
    """Sincronizar tickets desde Belgrano Tickets"""
    try:
        data = request.get_json()
        
        if not data or 'tickets' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Datos de tickets requeridos'
            }), 400
        
        tickets = data['tickets']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla de tickets si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido TEXT UNIQUE,
                ticket_id INTEGER,
                estado TEXT,
                repartidor TEXT,
                fecha_creacion TEXT,
                fecha_actualizacion TEXT,
                datos_completos TEXT
            )
        """)
        
        # Sincronizar tickets
        for ticket in tickets:
            cursor.execute("""
                INSERT OR REPLACE INTO tickets_sync 
                (numero_pedido, ticket_id, estado, repartidor, fecha_creacion, fecha_actualizacion, datos_completos)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket.get('numero_pedido'),
                ticket.get('ticket_id'),
                ticket.get('estado'),
                ticket.get('repartidor'),
                ticket.get('fecha_creacion'),
                ticket.get('fecha_actualizacion'),
                json.dumps(ticket)
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'{len(tickets)} tickets sincronizados',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error sincronizando tickets: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/sync/tickets', methods=['GET'])
@require_api_key
def get_sync_tickets():
    """Obtener tickets sincronizados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tickets_sync 
            ORDER BY fecha_actualizacion DESC
        """)
        
        tickets = cursor.fetchall()
        tickets_list = []
        
        for ticket in tickets:
            tickets_list.append({
                'numero_pedido': ticket['numero_pedido'],
                'ticket_id': ticket['ticket_id'],
                'estado': ticket['estado'],
                'repartidor': ticket['repartidor'],
                'fecha_creacion': ticket['fecha_creacion'],
                'fecha_actualizacion': ticket['fecha_actualizacion'],
                'datos_completos': json.loads(ticket['datos_completos']) if ticket['datos_completos'] else {}
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'total': len(tickets_list),
            'tickets': tickets_list,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo tickets sincronizados: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

# ==========================================
# MANEJO DE ERRORES
# ==========================================

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'error': 'Endpoint no encontrado',
        'timestamp': datetime.now().isoformat()
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'error': 'Error interno del servidor',
        'timestamp': datetime.now().isoformat()
    }), 500

# ==========================================
# FUNCIÓN PARA REGISTRAR EL BLUEPRINT
# ==========================================

def register_api_blueprint(app):
    """Registrar el blueprint de la API en la aplicación Flask"""
    app.register_blueprint(api_bp)
    logger.info("API blueprint registrado en /api/v1")
