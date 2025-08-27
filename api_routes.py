#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints de API consolidados para evitar duplicación
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Crear blueprint para APIs
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/tickets', methods=['GET'])
def get_tickets():
    """Obtener todos los tickets - Endpoint consolidado"""
    try:
        # Importar aquí para evitar dependencias circulares
        from models import obtener_todos_los_tickets
        
        tickets = obtener_todos_los_tickets()
        
        return jsonify({
            'status': 'success',
            'total_tickets': len(tickets),
            'tickets': tickets,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo tickets: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/tickets', methods=['POST'])
def create_ticket():
    """Crear nuevo ticket - Endpoint consolidado"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['cliente', 'productos', 'total']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Importar aquí para evitar dependencias circulares
        from models import crear_ticket
        
        # Crear ticket
        ticket_data = {
            'cliente': data['cliente'],
            'productos': data['productos'],
            'total': data['total'],
            'direccion': data.get('direccion', ''),
            'telefono': data.get('telefono', ''),
            'email': data.get('email', ''),
            'metodo_pago': data.get('metodo_pago', 'efectivo'),
            'notas': data.get('notas', ''),
            'estado': 'pendiente',
            'fecha_creacion': datetime.now().isoformat()
        }
        
        ticket_id = crear_ticket(ticket_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Ticket creado exitosamente',
            'ticket_id': ticket_id,
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando ticket: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/tickets/recibir', methods=['POST'])
def recibir_ticket():
    """Recibir ticket desde Belgrano Ahorro - Endpoint consolidado"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['cliente', 'productos', 'total']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Importar aquí para evitar dependencias circulares
        from models import crear_ticket
        
        # Crear ticket con datos de Belgrano Ahorro
        ticket_data = {
            'cliente': data['cliente'],
            'productos': data['productos'],
            'total': data['total'],
            'direccion': data.get('direccion', ''),
            'telefono': data.get('telefono', ''),
            'email': data.get('email', ''),
            'metodo_pago': data.get('metodo_pago', 'efectivo'),
            'notas': data.get('notas', ''),
            'numero_pedido': data.get('numero_pedido', ''),
            'estado': 'pendiente',
            'fecha_creacion': datetime.now().isoformat(),
            'origen': 'belgrano_ahorro'
        }
        
        ticket_id = crear_ticket(ticket_data)
        
        logger.info(f"Ticket recibido desde Belgrano Ahorro: {ticket_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Ticket recibido exitosamente',
            'ticket_id': ticket_id,
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error recibiendo ticket: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/productos_por_sucursal', methods=['POST'])
def productos_por_sucursal():
    """Obtener productos por sucursal - Endpoint consolidado"""
    try:
        data = request.get_json()
        
        if not data.get('sucursal_id'):
            return jsonify({
                'status': 'error',
                'error': 'ID de sucursal requerido'
            }), 400
        
        # Cargar productos desde JSON
        import json
        import os
        
        productos_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'productos.json')
        
        with open(productos_path, 'r', encoding='utf-8') as f:
            productos_data = json.load(f)
        
        # Filtrar productos por sucursal (simulado)
        productos = productos_data.get('productos', [])
        
        return jsonify({
            'status': 'success',
            'sucursal_id': data['sucursal_id'],
            'productos': productos,
            'total_productos': len(productos),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo productos por sucursal: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error interno del servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check para APIs - Endpoint consolidado"""
    try:
        # Verificar base de datos
        from models import contar_tickets, contar_usuarios
        
        total_tickets = contar_tickets()
        total_usuarios = contar_usuarios()
        
        return jsonify({
            'status': 'healthy',
            'service': 'API Consolidada',
            'database': 'connected',
            'total_tickets': total_tickets,
            'total_usuarios': total_usuarios,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }), 200
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
