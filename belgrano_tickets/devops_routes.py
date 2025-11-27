#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema DevOps Completo para Belgrano Tickets
Control total sobre el contenido de Belgrano Ahorro
"""

import os
import json
import requests
from functools import wraps
from datetime import datetime
import logging
from urllib.parse import urljoin
from flask import Blueprint, request, jsonify, redirect, url_for, session, make_response, render_template, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de API y credenciales DevOps
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
API_TIMEOUT_SECS = 10

# Credenciales de DevOps
DEVOPS_USERNAME = os.environ.get('DEVOPS_USERNAME', 'devops')
DEVOPS_PASSWORD_PLAIN = os.environ.get('DEVOPS_PASSWORD', 'DevOps2025!Secure')
DEVOPS_PASSWORD_HASH = generate_password_hash(DEVOPS_PASSWORD_PLAIN)

# Validar variables de entorno críticas
env_status = os.environ.get('FLASK_ENV', 'development')
if not BELGRANO_AHORRO_URL:
    if env_status != 'production':
        logger.info("ℹ️ BELGRANO_AHORRO_URL no configurada (normal en desarrollo)")
    else:
        logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_URL no está definida")

if not BELGRANO_AHORRO_API_KEY:
    if env_status != 'production':
        logger.info("ℹ️ BELGRANO_AHORRO_API_KEY no configurada (normal en desarrollo)")
    else:
        logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_API_KEY no está definida")

# Importar cliente API de forma robusta (soporta ejecución desde paquetes distintos)
devops_api_client = None
try:
    from belgrano_tickets.api_client import create_api_client, api_client as global_api_client
except Exception:
    try:
        from api_client import create_api_client, api_client as global_api_client  # type: ignore
    except Exception:
        try:
            from belgrano_client_gateway import BelgranoClientGateway as create_api_client  # type: ignore
        except Exception as e:
            logger.error(f"No se pudo inicializar el cliente API: {e}")
            create_api_client = None  # type: ignore

if create_api_client and BELGRANO_AHORRO_URL and BELGRANO_AHORRO_API_KEY:
    try:
        devops_api_client = create_api_client(BELGRANO_AHORRO_URL, BELGRANO_AHORRO_API_KEY)
        logger.info("Cliente API de Belgrano Ahorro inicializado para DevOps")
    except Exception as e:
        logger.error(f"Error creando cliente API de DevOps: {e}")
        devops_api_client = None
    else:
        if env_status == 'production':
            logger.warning("Variables de entorno no configuradas para cliente API de DevOps")
        else:
            logger.info("Cliente API de DevOps no inicializado (variables no configuradas)")

# Importar solo gestor DevOps unificado (evita errores por módulos antiguos)
try:
    from devops_belgrano_manager_unified import devops_manager_unified as devops_manager
    logger.info("✅ Gestor DevOps unificado inicializado")
except Exception as e:
    # Intento adicional ajustando sys.path a raíz del proyecto
    try:
                    logger.info(f"Producto creado desde DevOps: {nombre}")
                else:
                    logger.error(f"Error al crear producto en API: {message}")
                    # Fallback local
                    nuevo_id = _fallback_insert_producto(producto_data)
                    flash(f'API DevOps no disponible. Producto creado localmente (ID {nuevo_id}).', 'warning')
            else:
                logger.error("Gestor DevOps no disponible para crear producto")
                nuevo_id = _fallback_insert_producto(producto_data)
                flash(f'Gestor DevOps no disponible. Producto creado localmente (ID {nuevo_id}).', 'warning')
                
        except Exception as e:
            logger.error(f"Error creando producto desde DevOps: {e}")
            flash('Error interno al crear el producto', 'error')
        
        return redirect(url_for('devops.gestion_productos'))
    
    # Manejar requests AJAX/API
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Obtener datos reales usando el gestor DevOps o fallback DB
            if devops_manager:
                if getattr(devops_manager, 'fallback_mode', False):
                    productos = _fallback_get_productos()
                else:
                    productos = devops_manager.get_productos()
            else:
                productos = _fallback_get_productos()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'productos': productos,
                    'total': len(productos),
                    'timestamp': datetime.now().isoformat()
                },
                'source': 'api',
                'message': f'Productos obtenidos correctamente ({len(productos)} encontrados)'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo productos: {str(e)}',
                'data': [],
                'source': 'error'
            }), 500
    
    # Manejar requests desde navegador
    try:
        if not devops_manager:
            productos = _fallback_get_productos()
            negocios = _fallback_get_negocios()
            flash(f'Productos cargados desde base local: {len(productos)}', 'warning')
        else:
            productos = devops_manager.get_productos()
            negocios = devops_manager.get_negocios() if devops_manager else []
        categorias = []
        flash(f'Productos cargados: {len(productos)} encontrados', 'success')
    
    try:
        sync_results = {
            'timestamp': datetime.now().isoformat(),
            'ofertas': {'status': 'pending'},
            'negocios': {'status': 'pending'},
            'overall_status': 'running'
        }
        
        # Sincronizar ofertas
        try:
            if devops_manager:
                ofertas = devops_manager.get_ofertas()
                sync_results['ofertas'] = {
                    'status': 'success',
                    'count': len(ofertas),
                    'message': f'{len(ofertas)} ofertas obtenidas'
                }
            else:
                sync_results['ofertas'] = {'status': 'error', 'error': 'Gestor DevOps no disponible'}
        except Exception as e:
            sync_results['ofertas'] = {'status': 'error', 'error': str(e)}
        
        # Sincronizar negocios
        try:
            if devops_manager:
                negocios = devops_manager.get_negocios()
                sync_results['negocios'] = {
                    'status': 'success',
                    'count': len(negocios),
                    'message': f'{len(negocios)} negocios obtenidos'
                }
            else:
                sync_results['negocios'] = {'status': 'error', 'error': 'Gestor DevOps no disponible'}
        except Exception as e:
            sync_results['negocios'] = {'status': 'error', 'error': str(e)}
        
        # Determinar estado general
        if all(item['status'] == 'success' for item in [sync_results['ofertas'], sync_results['negocios']]):
            sync_results['overall_status'] = 'success'
        elif any(item['status'] == 'success' for item in [sync_results['ofertas'], sync_results['negocios']]):
            sync_results['overall_status'] = 'partial'
        else:
            sync_results['overall_status'] = 'error'
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'success',
                'message': 'Sincronización completada',
                'data': sync_results
            })
        else:
            flash('Sincronización completada', 'success')
            return render_template('devops/sync.html', 
                                 sync_results=sync_results,
                                 status='success')
        
    except Exception as e:
        logger.error(f"Error en sincronización manual: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {str(e)}'
            }), 500
        else:
            flash(f'Error en sincronización: {str(e)}', 'error')
            return render_template('devops/sync.html', 
                                 sync_results={},
                                 status='error')

@devops_bp.route('/system-status')
@devops_login_required
def system_status():
    """Estado completo del sistema DevOps"""
    try:
        if devops_manager:
            status = devops_manager.get_system_status()
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'success',
                    'data': status
                })
            else:
                flash('Estado del sistema obtenido', 'success')
                return render_template('devops/system_status.html', 
                                     status_data=status,
                                     status='success')
        else:
            fallback_data = {
                'timestamp': datetime.now().isoformat(),
                'fallback_mode': True,
                'api_configured': False
            }
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'error',
                    'message': 'Gestor DevOps no disponible',
                    'data': fallback_data
                }), 503
            else:
                flash('Gestor DevOps no disponible', 'error')
                return render_template('devops/system_status.html', 
                                     status_data=fallback_data,
                                     status='error')
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }), 500
        else:
            flash(f'Error interno: {str(e)}', 'error')
            return render_template('devops/system_status.html', 
                                 status_data={},
                                 status='error')

# =================================================================
# MANEJO DE ERRORES
# =================================================================

@devops_bp.errorhandler(404)
def devops_not_found(error):
    """Manejar errores 404 en DevOps"""
    error_data = {
        'message': 'Endpoint de DevOps no encontrado',
        'available_endpoints': [
            '/devops/',
            '/devops/health',
            '/devops/status',
            '/devops/info',
            '/devops/ofertas',
            '/devops/negocios',
            '/devops/sync',
            '/devops/system-status'
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'status': 'error',
            **error_data
        }), 404
    else:
        flash('Endpoint no encontrado', 'error')
        return render_template('devops/error.html', 
                             error_data=error_data,
                             status='404'), 404

@devops_bp.errorhandler(500)
def devops_internal_error(error):
    """Manejar errores 500 en DevOps"""
    error_data = {
        'message': 'Error interno del servidor DevOps',
        'timestamp': datetime.now().isoformat()
    }
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'status': 'error',
            **error_data
        }), 500
    else:
        flash('Error interno del servidor', 'error')
        return render_template('devops/error.html', 
                             error_data=error_data,
                             status='500'), 500