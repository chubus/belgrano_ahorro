#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funciones adicionales para el registro de usuarios
"""

import hashlib
import secrets
import json
from datetime import datetime

def verificar_email_existe(email):
    """Verificar si un email ya existe en la base de datos"""
    try:
        usuarios = database.obtener_todos_los_usuarios()
        for usuario in usuarios:
            if usuario.get('email', '').lower() == email.lower():
                return True
        return False
    except Exception as e:
        print(f"Error verificando email: {e}")
        return False

def crear_usuario(usuario_data):
    """Crear un nuevo usuario en la base de datos"""
    try:
        # Generar hash de contraseña
        password_hash = generate_password_hash(usuario_data['password'])
        
        # Preparar datos del usuario
        nuevo_usuario = {
            'id': secrets.token_hex(8),
            'nombre': usuario_data['nombre'],
            'apellido': usuario_data.get('apellido', ''),
            'email': usuario_data['email'].lower(),
            'telefono': usuario_data.get('telefono', ''),
            'password': password_hash,
            'tipo': usuario_data.get('tipo', 'cliente'),
            'activo': usuario_data.get('activo', True),
            'fecha_registro': datetime.now().isoformat(),
            'datos_adicionales': usuario_data.get('datos_negocio', {})
        }
        
        # Obtener usuarios existentes
        usuarios = database.obtener_todos_los_usuarios()
        usuarios.append(nuevo_usuario)
        
        # Guardar usuarios actualizados
        database.guardar_usuarios(usuarios)
        
        print(f"✅ Usuario creado: {nuevo_usuario['email']} ({nuevo_usuario['tipo']})")
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

def generate_password_hash(password):
    """Generar hash de contraseña usando PBKDF2"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f'pbkdf2:sha256:100000${salt}${hash_obj.hex()}'

def check_password_hash(password_hash, password):
    """Verificar contraseña contra hash"""
    try:
        # Extraer salt del hash
        parts = password_hash.split('$')
        if len(parts) != 3 or parts[0] != 'pbkdf2:sha256:100000':
            return False
        
        salt = parts[1]
        stored_hash = parts[2]
        
        # Generar hash con el mismo salt
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        computed_hash = hash_obj.hex()
        
        return stored_hash == computed_hash
    except Exception as e:
        print(f"Error verificando contraseña: {e}")
        return False
