#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación de Tickets - Sistema independiente para gestión de pedidos
Versión original restaurada
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

# Crear la instancia de Flask
app = Flask(__name__, template_folder='templates_tickets')
app.secret_key = 'belgrano_tickets_secret_2025'

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# =============================
# MODELOS DE BASE DE DATOS
# =============================

class User(UserMixin):
    def __init__(self, id, email, nombre, rol):
        self.id = id
        self.email = email
        self.nombre = nombre
        self.rol = rol

# =============================
# FUNCIONES DE BASE DE DATOS
# =============================

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('belgrano_tickets.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializar base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'flota',
            activo BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de tickets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pedido TEXT UNIQUE NOT NULL,
            cliente TEXT NOT NULL,
            productos TEXT NOT NULL,
            total REAL NOT NULL,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            metodo_pago TEXT,
            notas TEXT,
            estado TEXT DEFAULT 'pendiente',
            prioridad TEXT DEFAULT 'normal',
            repartidor TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega TIMESTAMP
        )
    ''')
    
    # Insertar usuarios por defecto si no existen
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Usuario admin
        cursor.execute('''
            INSERT INTO users (email, password, nombre, rol)
            VALUES (?, ?, ?, ?)
        ''', (
            'admin@belgranoahorro.com',
            generate_password_hash('admin123'),
            'Administrador',
            'admin'
        ))
        
        # Usuario flota
        cursor.execute('''
            INSERT INTO users (email, password, nombre, rol)
            VALUES (?, ?, ?, ?)
        ''', (
            'repartidor1@belgranoahorro.com',
            generate_password_hash('flota123'),
            'Repartidor 1',
            'flota'
        ))
    
    conn.commit()
    conn.close()

# =============================
# FUNCIONES DE AUTENTICACIÓN
# =============================

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['email'], user_data['nombre'], user_data['rol'])
    return None

# =============================
# RUTAS PRINCIPALES
# =============================

@app.route('/')
def index():
    """Página principal - redirigir a login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND activo = 1', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['email'], user_data['nombre'], user_data['rol'])
            login_user(user)
            return redirect(url_for('tickets'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/tickets')
@login_required
def tickets():
    """Panel de tickets"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tickets 
        ORDER BY fecha_creacion DESC
    ''')
    tickets_data = cursor.fetchall()
    conn.close()
    
    # Convertir a lista de diccionarios
    tickets = []
    for ticket in tickets_data:
        tickets.append({
            'id': ticket['id'],
            'numero_pedido': ticket['numero_pedido'],
            'cliente': ticket['cliente'],
            'productos': json.loads(ticket['productos']) if ticket['productos'] else [],
            'total': ticket['total'],
            'direccion': ticket['direccion'],
            'telefono': ticket['telefono'],
            'email': ticket['email'],
            'metodo_pago': ticket['metodo_pago'],
            'notas': ticket['notas'],
            'estado': ticket['estado'],
            'prioridad': ticket['prioridad'],
            'repartidor': ticket['repartidor'],
            'fecha_creacion': ticket['fecha_creacion'],
            'fecha_entrega': ticket['fecha_entrega']
        })
    
    return render_template('tickets.html', tickets=tickets)

# =============================
# API ENDPOINTS
# =============================

@app.route('/api/tickets', methods=['POST'])
def api_crear_ticket():
    """API para crear tickets desde Belgrano Ahorro"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        required_fields = ['cliente', 'productos', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Validar tipos de datos
        if not isinstance(data['cliente'], str):
            return jsonify({'error': 'cliente debe ser string'}), 400
        
        if not isinstance(data['productos'], list):
            return jsonify({'error': 'productos debe ser lista'}), 400
        
        if not isinstance(data['total'], (int, float)):
            return jsonify({'error': 'total debe ser número'}), 400
        
        # Generar número de pedido si no viene
        if 'numero_pedido' not in data:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            data['numero_pedido'] = f"TICK-{timestamp}"
        
        # Guardar ticket en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (numero_pedido, cliente, productos, total, direccion, telefono, email, metodo_pago, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['numero_pedido'],
            data['cliente'],
            json.dumps(data['productos']),
            data['total'],
            data.get('direccion', ''),
            data.get('telefono', ''),
            data.get('email', ''),
            data.get('metodo_pago', 'efectivo'),
            data.get('notas', '')
        ))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'msg': 'ticket registrado',
            'ticket_id': ticket_id,
            'numero_pedido': data['numero_pedido']
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/api/tickets', methods=['GET'])
@login_required
def api_obtener_tickets():
    """API para obtener tickets (requiere autenticación)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets ORDER BY fecha_creacion DESC')
        tickets_data = cursor.fetchall()
        conn.close()
        
        tickets = []
        for ticket in tickets_data:
            tickets.append({
                'id': ticket['id'],
                'numero_pedido': ticket['numero_pedido'],
                'cliente': ticket['cliente'],
                'productos': json.loads(ticket['productos']) if ticket['productos'] else [],
                'total': ticket['total'],
                'direccion': ticket['direccion'],
                'telefono': ticket['telefono'],
                'email': ticket['email'],
                'metodo_pago': ticket['metodo_pago'],
                'notas': ticket['notas'],
                'estado': ticket['estado'],
                'prioridad': ticket['prioridad'],
                'repartidor': ticket['repartidor'],
                'fecha_creacion': ticket['fecha_creacion'],
                'fecha_entrega': ticket['fecha_entrega']
            })
        
        return jsonify({'tickets': tickets}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check para Render.com"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200

# =============================
# INICIALIZACIÓN
# =============================

if __name__ == '__main__':
    print("🎫 Iniciando Belgrano Tickets...")
    print("📱 Abre tu navegador en: http://localhost:5001")
    print("⏹️ Presiona Ctrl+C para detener")
    
    # Inicializar base de datos
    init_database()
    print("✅ Base de datos inicializada")
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=5001, debug=False)
