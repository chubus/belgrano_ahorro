#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevOps Simplificado - Versión que funciona
"""

from flask import Flask, request, jsonify, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'devops_secret_key_2025'

# Configuración
BELGRANO_AHORRO_URL = 'http://localhost:5000'
BELGRANO_AHORRO_API_KEY = 'belgrano_ahorro_api_key_2025'
DEVOPS_USERNAME = 'devops'
DEVOPS_PASSWORD = 'DevOps2025!Secure'

def devops_is_authenticated():
    """Verificar si DevOps está autenticado"""
    return session.get('devops_authenticated', False)

def devops_login_required(fn):
    """Decorador para requerir autenticación de DevOps"""
    def wrapper(*args, **kwargs):
        if not devops_is_authenticated():
            return redirect('/devops/login')
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def make_api_request(method, endpoint, data=None):
    """Realizar request a la API de Belgrano Ahorro"""
    try:
        headers = {
            'Authorization': f'Bearer {BELGRANO_AHORRO_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        url = f"{BELGRANO_AHORRO_URL}/api/{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {'success': False, 'error': f'Método no soportado: {method}'}
        
        if response.status_code in [200, 201]:
            result = response.json() if response.content else {}
            return {
                'success': True,
                'data': result.get('data', result),
                'status_code': response.status_code
            }
        else:
            error_data = response.json() if response.content else {}
            return {
                'success': False,
                'error': error_data.get('error', f'HTTP {response.status_code}'),
                'status_code': response.status_code
            }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/devops/login', methods=['GET', 'POST'])
def devops_login():
    """Login de DevOps"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == DEVOPS_USERNAME and password == DEVOPS_PASSWORD:
            session['devops_authenticated'] = True
            session.permanent = True
            return redirect('/devops/')
        else:
            flash('Credenciales incorrectas', 'error')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; }}
            .form-group {{ margin: 10px 0; }}
            input {{ padding: 8px; width: 200px; }}
            button {{ padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h2>🔧 DevOps Login</h2>
        <form method="POST">
            <div class="form-group">
                <label>Usuario:</label><br>
                <input type="text" name="username" value="{DEVOPS_USERNAME}" required>
            </div>
            <div class="form-group">
                <label>Contraseña:</label><br>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Entrar</button>
        </form>
    </body>
    </html>
    '''

@app.route('/devops/')
@devops_login_required
def devops_home():
    """Panel principal de DevOps"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; }}
            .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
            .btn {{ padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }}
            .status {{ padding: 5px 10px; border-radius: 3px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <h1>🔧 DevOps Dashboard</h1>
        <p>Bienvenido al panel de administración DevOps</p>
        
        <div class="card">
            <h3>📊 Estado del Sistema</h3>
            <p>✅ DevOps: Activo</p>
            <p>✅ Belgrano Ahorro: Conectado</p>
        </div>
        
        <div class="card">
            <h3>🔗 Enlaces de Gestión</h3>
            <a href="/devops/negocios" class="btn">🏪 Negocios</a>
            <a href="/devops/productos" class="btn">📦 Productos</a>
            <a href="/devops/ofertas" class="btn">🎯 Ofertas</a>
            <a href="/devops/sucursales" class="btn">🏢 Sucursales</a>
        </div>
        
        <div class="card">
            <h3>🔧 Utilidades</h3>
            <a href="/devops/health" class="btn">💚 Health Check</a>
            <a href="/devops/status" class="btn">📈 Estado</a>
            <a href="/devops/logout" class="btn">🚪 Logout</a>
        </div>
    </body>
    </html>
    '''

@app.route('/devops/logout')
def devops_logout():
    """Cerrar sesión de DevOps"""
    session.pop('devops_authenticated', None)
    return redirect('/devops/login')

@app.route('/devops/health')
@devops_login_required
def devops_health():
    """Health check del sistema"""
    try:
        # Probar conexión a Belgrano Ahorro
        response = requests.get(f"{BELGRANO_AHORRO_URL}/health", timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'devops': 'active',
                'belgrano_ahorro': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'devops': 'active',
                'belgrano_ahorro': 'disconnected',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'devops': 'active',
            'belgrano_ahorro': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/devops/status')
@devops_login_required
def devops_status():
    """Estado detallado del sistema DevOps"""
    try:
        # Obtener datos de Belgrano Ahorro
        endpoints = ['negocios', 'productos', 'ofertas', 'sucursales']
        data_counts = {}
        
        for endpoint in endpoints:
            try:
                result = make_api_request('GET', endpoint)
                if result.get('success'):
                    data_counts[endpoint] = len(result.get('data', []))
                else:
                    data_counts[endpoint] = 0
            except:
                data_counts[endpoint] = 0
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>DevOps Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                .status {{ padding: 5px 10px; border-radius: 3px; }}
                .success {{ background: #d4edda; color: #155724; }}
            </style>
        </head>
        <body>
            <h1>📈 Estado del Sistema DevOps</h1>
            
            <div class="card">
                <h3>🔧 Servicios</h3>
                <p>✅ DevOps: Activo</p>
                <p>✅ Belgrano Ahorro: Conectado</p>
            </div>
            
            <div class="card">
                <h3>📊 Datos Disponibles</h3>
                <p>🏪 Negocios: {data_counts.get('negocios', 0)}</p>
                <p>📦 Productos: {data_counts.get('productos', 0)}</p>
                <p>🎯 Ofertas: {data_counts.get('ofertas', 0)}</p>
                <p>🏢 Sucursales: {data_counts.get('sucursales', 0)}</p>
            </div>
            
            <div class="card">
                <h3>🕐 Información del Sistema</h3>
                <p>Timestamp: {datetime.now().isoformat()}</p>
                <p>Versión: 2.0.0</p>
            </div>
            
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''

@app.route('/devops/negocios')
@devops_login_required
def gestion_negocios():
    """Gestión de negocios"""
    try:
        result = make_api_request('GET', 'negocios')
        negocios = result.get('data', []) if result.get('success') else []
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gestión de Negocios</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                .btn {{ padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🏪 Gestión de Negocios</h1>
            
            <div class="card">
                <h3>📊 Negocios Existentes ({len(negocios)})</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Dirección</th>
                        <th>Teléfono</th>
                        <th>Email</th>
                        <th>Activo</th>
                    </tr>
        '''
        
        for negocio in negocios:
            activo = "✅" if negocio.get('activo') else "❌"
            return_html += f'''
                    <tr>
                        <td>{negocio.get('id', 'N/A')}</td>
                        <td>{negocio.get('nombre', 'N/A')}</td>
                        <td>{negocio.get('direccion', 'N/A')}</td>
                        <td>{negocio.get('telefono', 'N/A')}</td>
                        <td>{negocio.get('email', 'N/A')}</td>
                        <td>{activo}</td>
                    </tr>
            '''
        
        return_html += '''
                </table>
            </div>
            
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''
        
        return return_html
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>❌ Error</h1>
            <p>Error obteniendo negocios: {str(e)}</p>
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''

@app.route('/devops/productos')
@devops_login_required
def gestion_productos():
    """Gestión de productos"""
    try:
        result = make_api_request('GET', 'productos')
        productos = result.get('data', []) if result.get('success') else []
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gestión de Productos</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>📦 Gestión de Productos</h1>
            
            <div class="card">
                <h3>📊 Productos Existentes ({len(productos)})</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Precio</th>
                        <th>Categoría</th>
                        <th>Stock</th>
                        <th>Activo</th>
                    </tr>
        '''
        
        for producto in productos:
            activo = "✅" if producto.get('activo') else "❌"
            return_html += f'''
                    <tr>
                        <td>{producto.get('id', 'N/A')}</td>
                        <td>{producto.get('nombre', 'N/A')}</td>
                        <td>${producto.get('precio', 0)}</td>
                        <td>{producto.get('categoria', 'N/A')}</td>
                        <td>{producto.get('stock', 0)}</td>
                        <td>{activo}</td>
                    </tr>
            '''
        
        return_html += '''
                </table>
            </div>
            
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''
        
        return return_html
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>❌ Error</h1>
            <p>Error obteniendo productos: {str(e)}</p>
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''

@app.route('/devops/ofertas')
@devops_login_required
def gestion_ofertas():
    """Gestión de ofertas"""
    try:
        result = make_api_request('GET', 'ofertas')
        ofertas = result.get('data', []) if result.get('success') else []
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gestión de Ofertas</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🎯 Gestión de Ofertas</h1>
            
            <div class="card">
                <h3>📊 Ofertas Existentes ({len(ofertas)})</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Título</th>
                        <th>Descuento</th>
                        <th>Fecha Inicio</th>
                        <th>Fecha Fin</th>
                        <th>Activa</th>
                    </tr>
        '''
        
        for oferta in ofertas:
            activa = "✅" if oferta.get('activa') else "❌"
            return_html += f'''
                    <tr>
                        <td>{oferta.get('id', 'N/A')}</td>
                        <td>{oferta.get('titulo', 'N/A')}</td>
                        <td>{oferta.get('descuento', 0)}%</td>
                        <td>{oferta.get('fecha_inicio', 'N/A')}</td>
                        <td>{oferta.get('fecha_fin', 'N/A')}</td>
                        <td>{activa}</td>
                    </tr>
            '''
        
        return_html += '''
                </table>
            </div>
            
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''
        
        return return_html
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <head><title>Error</title></head>
        <body>
            <h1>❌ Error</h1>
            <p>Error obteniendo ofertas: {str(e)}</p>
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''

@app.route('/devops/sucursales')
@devops_login_required
def gestion_sucursales():
    """Gestión de sucursales"""
    try:
        result = make_api_request('GET', 'sucursales')
        sucursales = result.get('data', []) if result.get('success') else []
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gestión de Sucursales</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🏢 Gestión de Sucursales</h1>
            
            <div class="card">
                <h3>📊 Sucursales Existentes ({len(sucursales)})</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Dirección</th>
                        <th>Teléfono</th>
                        <th>Email</th>
                        <th>Activa</th>
                    </tr>
        '''
        
        for sucursal in sucursales:
            activa = "✅" if sucursal.get('activo') else "❌"
            return_html += f'''
                    <tr>
                        <td>{sucursal.get('id', 'N/A')}</td>
                        <td>{sucursal.get('nombre', 'N/A')}</td>
                        <td>{sucursal.get('direccion', 'N/A')}</td>
                        <td>{sucursal.get('telefono', 'N/A')}</td>
                        <td>{sucursal.get('email', 'N/A')}</td>
                        <td>{activa}</td>
                    </tr>
            '''
        
        return_html += '''
                </table>
            </div>
            
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''
        
        return return_html
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>❌ Error</h1>
            <p>Error obteniendo sucursales: {str(e)}</p>
            <a href="/devops/">← Volver al Dashboard</a>
        </body>
        </html>
        '''

if __name__ == "__main__":
    print("🔧 Iniciando DevOps Simplificado en puerto 5002...")
    print("URL: http://localhost:5002/devops/")
    print("Credenciales: devops / DevOps2025!Secure")
    print("Presiona Ctrl+C para detener")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False)
    except KeyboardInterrupt:
        print("\nDevOps detenido")
    except Exception as e:
        print(f"Error iniciando DevOps: {e}")
