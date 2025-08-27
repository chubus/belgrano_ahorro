#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validadores para parámetros de URL y datos de entrada
"""

import re
from flask import abort, request
import logging

logger = logging.getLogger(__name__)

def validate_int_param(param_value, param_name="ID"):
    """Validar que un parámetro sea un entero válido"""
    try:
        int_value = int(param_value)
        if int_value <= 0:
            logger.warning(f"Parámetro {param_name} inválido: {param_value} (debe ser mayor a 0)")
            abort(400, description=f"{param_name} debe ser un número válido mayor a 0")
        return int_value
    except (ValueError, TypeError):
        logger.warning(f"Parámetro {param_name} inválido: {param_value} (no es un número)")
        abort(400, description=f"{param_name} debe ser un número válido")

def validate_string_param(param_value, param_name="Parámetro", min_length=1, max_length=100):
    """Validar que un parámetro sea una cadena válida"""
    if not param_value or not isinstance(param_value, str):
        logger.warning(f"Parámetro {param_name} inválido: {param_value} (debe ser una cadena)")
        abort(400, description=f"{param_name} debe ser una cadena válida")
    
    param_value = param_value.strip()
    
    if len(param_value) < min_length:
        logger.warning(f"Parámetro {param_name} muy corto: {param_value} (mínimo {min_length} caracteres)")
        abort(400, description=f"{param_name} debe tener al menos {min_length} caracteres")
    
    if len(param_value) > max_length:
        logger.warning(f"Parámetro {param_name} muy largo: {param_value} (máximo {max_length} caracteres)")
        abort(400, description=f"{param_name} debe tener máximo {max_length} caracteres")
    
    return param_value

def validate_email(email):
    """Validar formato de email"""
    if not email:
        return False
    
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(email_pattern, email))

def validate_phone(phone):
    """Validar formato de teléfono"""
    if not phone:
        return True  # Teléfono es opcional
    
    # Patrón para teléfonos argentinos
    phone_pattern = r"^(\+54\s?)?(11|15|2\d{3})\s?(\d{4})\s?(\d{4})$"
    return bool(re.match(phone_pattern, phone))

def validate_password(password):
    """Validar contraseña"""
    if not password:
        return False, "La contraseña es requerida"
    
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 50:
        return False, "La contraseña debe tener máximo 50 caracteres"
    
    return True, "Contraseña válida"

def validate_payment_method(method):
    """Validar método de pago"""
    valid_methods = ['efectivo', 'tarjeta', 'transferencia', 'mercadopago']
    if method.lower() not in valid_methods:
        logger.warning(f"Método de pago inválido: {method}")
        abort(400, description=f"Método de pago inválido. Opciones válidas: {', '.join(valid_methods)}")
    
    return method.lower()

def validate_ticket_status(status):
    """Validar estado de ticket"""
    valid_statuses = ['pendiente', 'en_proceso', 'en_camino', 'entregado', 'cancelado']
    if status.lower() not in valid_statuses:
        logger.warning(f"Estado de ticket inválido: {status}")
        abort(400, description=f"Estado inválido. Opciones válidas: {', '.join(valid_statuses)}")
    
    return status.lower()

def validate_product_data(product_data):
    """Validar datos de producto"""
    required_fields = ['nombre', 'precio']
    
    for field in required_fields:
        if not product_data.get(field):
            logger.warning(f"Campo requerido faltante en producto: {field}")
            abort(400, description=f"Campo requerido: {field}")
    
    # Validar precio
    try:
        precio = float(product_data['precio'])
        if precio < 0:
            abort(400, description="El precio no puede ser negativo")
    except (ValueError, TypeError):
        abort(400, description="El precio debe ser un número válido")
    
    return product_data

def validate_cart_item(item_data):
    """Validar item del carrito"""
    required_fields = ['producto_id', 'cantidad']
    
    for field in required_fields:
        if not item_data.get(field):
            logger.warning(f"Campo requerido faltante en item del carrito: {field}")
            abort(400, description=f"Campo requerido: {field}")
    
    # Validar cantidad
    try:
        cantidad = int(item_data['cantidad'])
        if cantidad <= 0:
            abort(400, description="La cantidad debe ser mayor a 0")
        if cantidad > 100:
            abort(400, description="La cantidad no puede ser mayor a 100")
    except (ValueError, TypeError):
        abort(400, description="La cantidad debe ser un número válido")
    
    return item_data

def validate_user_data(user_data):
    """Validar datos de usuario"""
    required_fields = ['nombre', 'email', 'password']
    
    for field in required_fields:
        if not user_data.get(field):
            logger.warning(f"Campo requerido faltante en usuario: {field}")
            abort(400, description=f"Campo requerido: {field}")
    
    # Validar email
    if not validate_email(user_data['email']):
        abort(400, description="Formato de email inválido")
    
    # Validar contraseña
    is_valid, message = validate_password(user_data['password'])
    if not is_valid:
        abort(400, description=message)
    
    # Validar nombre
    if len(user_data['nombre'].strip()) < 2:
        abort(400, description="El nombre debe tener al menos 2 caracteres")
    
    return user_data

def sanitize_input(input_string):
    """Sanitizar entrada de usuario"""
    if not input_string:
        return ""
    
    # Remover caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        input_string = input_string.replace(char, '')
    
    # Limitar longitud
    if len(input_string) > 1000:
        input_string = input_string[:1000]
    
    return input_string.strip()

def validate_request_data(required_fields=None, optional_fields=None):
    """Decorador para validar datos de request"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                data = request.get_json() if request.is_json else request.form
                
                # Validar campos requeridos
                if required_fields:
                    for field in required_fields:
                        if not data.get(field):
                            logger.warning(f"Campo requerido faltante: {field} en {request.endpoint}")
                            abort(400, description=f"Campo requerido: {field}")
                
                # Sanitizar datos
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = sanitize_input(value)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
