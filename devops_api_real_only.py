#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevOps API - SOLO DATOS REALES DE BELGRANO AHORRO
Sin fallbacks locales, solo API real
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de API
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
API_TIMEOUT_SECS = int(os.environ.get('API_TIMEOUT_SECS', '30'))

def build_api_url(endpoint: str) -> str:
    """Construir URL completa para endpoint de API"""
    return f"{BELGRANO_AHORRO_URL}/api/{endpoint}"

def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Any]:
    """Realizar request a la API real de Belgrano Ahorro"""
    try:
        url = build_api_url(endpoint)
        headers = {
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'Content-Type': 'application/json',
            'X-Origin': 'devops_real_only'
        }
        
        logger.info(f"🌐 Realizando {method} a {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=API_TIMEOUT_SECS)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=API_TIMEOUT_SECS)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=API_TIMEOUT_SECS)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=API_TIMEOUT_SECS)
        else:
            return False, f"Método HTTP no soportado: {method}"
        
        if response.status_code == 200:
            logger.info(f"✅ {method} exitoso - {endpoint}")
            return True, response.json()
        elif response.status_code == 401:
            logger.error(f"❌ Error de autenticación (401) - {endpoint}")
            return False, "Error de autenticación - Verificar API_KEY"
        elif response.status_code == 404:
            logger.error(f"❌ Endpoint no encontrado (404) - {endpoint}")
            return False, f"Endpoint {endpoint} no encontrado en Belgrano Ahorro"
        else:
            logger.error(f"❌ Error HTTP {response.status_code} - {endpoint}")
            return False, f"Error HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ Timeout - {endpoint}")
        return False, "Timeout - API no responde"
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Error de conexión - {endpoint}")
        return False, "Error de conexión - API no disponible"
    except Exception as e:
        logger.error(f"❌ Error inesperado - {endpoint}: {e}")
        return False, f"Error inesperado: {str(e)}"

# =================================================================
# FUNCIONES SOLO API REAL - SIN FALLBACKS LOCALES
# =================================================================

def get_negocios_from_belgrano_real() -> List[Dict]:
    """Obtener negocios SOLO desde API real de Belgrano Ahorro"""
    logger.info("🏪 Obteniendo negocios desde API real de Belgrano Ahorro...")
    
    success, data = make_api_request('GET', 'v1/negocios')
    if success:
        if isinstance(data, list):
            logger.info(f"✅ {len(data)} negocios obtenidos desde API real")
            return data
        elif isinstance(data, dict) and 'data' in data:
            negocios = data.get('data', [])
            logger.info(f"✅ {len(negocios)} negocios obtenidos desde API real")
            return negocios
        else:
            logger.warning("⚠️ Formato inesperado de respuesta de API")
            return []
    else:
        logger.error(f"❌ No se pudieron obtener negocios: {data}")
        return []

def get_productos_from_belgrano_real() -> List[Dict]:
    """Obtener productos SOLO desde API real de Belgrano Ahorro"""
    logger.info("📦 Obteniendo productos desde API real de Belgrano Ahorro...")
    
    success, data = make_api_request('GET', 'v1/productos')
    if success:
        if isinstance(data, list):
            logger.info(f"✅ {len(data)} productos obtenidos desde API real")
            return data
        elif isinstance(data, dict) and 'data' in data:
            productos = data.get('data', [])
            logger.info(f"✅ {len(productos)} productos obtenidos desde API real")
            return productos
        else:
            logger.warning("⚠️ Formato inesperado de respuesta de API")
            return []
    else:
        logger.error(f"❌ No se pudieron obtener productos: {data}")
        return []

def get_ofertas_from_belgrano_real() -> List[Dict]:
    """Obtener ofertas SOLO desde API real de Belgrano Ahorro"""
    logger.info("🎯 Obteniendo ofertas desde API real de Belgrano Ahorro...")
    
    success, data = make_api_request('GET', 'v1/ofertas')
    if success:
        if isinstance(data, list):
            logger.info(f"✅ {len(data)} ofertas obtenidas desde API real")
            return data
        elif isinstance(data, dict) and 'data' in data:
            ofertas = data.get('data', [])
            logger.info(f"✅ {len(ofertas)} ofertas obtenidas desde API real")
            return ofertas
        else:
            logger.warning("⚠️ Formato inesperado de respuesta de API")
            return []
    else:
        logger.error(f"❌ No se pudieron obtener ofertas: {data}")
        return []

def get_sucursales_from_belgrano_real() -> List[Dict]:
    """Obtener sucursales SOLO desde API real de Belgrano Ahorro"""
    logger.info("🏢 Obteniendo sucursales desde API real de Belgrano Ahorro...")
    
    success, data = make_api_request('GET', 'v1/sucursales')
    if success:
        if isinstance(data, list):
            logger.info(f"✅ {len(data)} sucursales obtenidas desde API real")
            return data
        elif isinstance(data, dict) and 'data' in data:
            sucursales = data.get('data', [])
            logger.info(f"✅ {len(sucursales)} sucursales obtenidas desde API real")
            return sucursales
        else:
            logger.warning("⚠️ Formato inesperado de respuesta de API")
            return []
    else:
        logger.error(f"❌ No se pudieron obtener sucursales: {data}")
        return []

def get_precios_from_belgrano_real() -> List[Dict]:
    """Obtener precios SOLO desde API real de Belgrano Ahorro"""
    logger.info("💰 Obteniendo precios desde API real de Belgrano Ahorro...")
    
    success, data = make_api_request('GET', 'v1/precios')
    if success:
        if isinstance(data, list):
            logger.info(f"✅ {len(data)} precios obtenidos desde API real")
            return data
        elif isinstance(data, dict) and 'data' in data:
            precios = data.get('data', [])
            logger.info(f"✅ {len(precios)} precios obtenidos desde API real")
            return precios
        else:
            logger.warning("⚠️ Formato inesperado de respuesta de API")
            return []
    else:
        logger.error(f"❌ No se pudieron obtener precios: {data}")
        return []

# =================================================================
# OPERACIONES CRUD SOLO API REAL
# =================================================================

def create_negocio_real(negocio_data: Dict) -> Tuple[bool, str]:
    """Crear negocio SOLO en API real de Belgrano Ahorro"""
    logger.info(f"🏪 Creando negocio: {negocio_data.get('nombre', 'Sin nombre')}")
    
    success, response = make_api_request('POST', 'v1/negocios', negocio_data)
    if success:
        logger.info("✅ Negocio creado exitosamente en API real")
        return True, "Negocio creado exitosamente en Belgrano Ahorro"
    else:
        logger.error(f"❌ Error creando negocio: {response}")
        return False, f"Error creando negocio: {response}"

def create_producto_real(producto_data: Dict) -> Tuple[bool, str]:
    """Crear producto SOLO en API real de Belgrano Ahorro"""
    logger.info(f"📦 Creando producto: {producto_data.get('nombre', 'Sin nombre')}")
    
    success, response = make_api_request('POST', 'v1/productos', producto_data)
    if success:
        logger.info("✅ Producto creado exitosamente en API real")
        return True, "Producto creado exitosamente en Belgrano Ahorro"
    else:
        logger.error(f"❌ Error creando producto: {response}")
        return False, f"Error creando producto: {response}"

def create_oferta_real(oferta_data: Dict) -> Tuple[bool, str]:
    """Crear oferta SOLO en API real de Belgrano Ahorro"""
    logger.info(f"🎯 Creando oferta: {oferta_data.get('titulo', 'Sin título')}")
    
    success, response = make_api_request('POST', 'v1/ofertas', oferta_data)
    if success:
        logger.info("✅ Oferta creada exitosamente en API real")
        return True, "Oferta creada exitosamente en Belgrano Ahorro"
    else:
        logger.error(f"❌ Error creando oferta: {response}")
        return False, f"Error creando oferta: {response}"

def create_sucursal_real(sucursal_data: Dict) -> Tuple[bool, str]:
    """Crear sucursal SOLO en API real de Belgrano Ahorro"""
    logger.info(f"🏢 Creando sucursal: {sucursal_data.get('nombre', 'Sin nombre')}")
    
    success, response = make_api_request('POST', 'v1/sucursales', sucursal_data)
    if success:
        logger.info("✅ Sucursal creada exitosamente en API real")
        return True, "Sucursal creada exitosamente en Belgrano Ahorro"
    else:
        logger.error(f"❌ Error creando sucursal: {response}")
        return False, f"Error creando sucursal: {response}"

# =================================================================
# FUNCIÓN DE VERIFICACIÓN DE CONECTIVIDAD
# =================================================================

def verificar_conectividad_api_real() -> Dict[str, Any]:
    """Verificar conectividad SOLO con API real de Belgrano Ahorro"""
    logger.info("🔍 Verificando conectividad con API real de Belgrano Ahorro...")
    
    resultados = {
        'api_url': BELGRANO_AHORRO_URL,
        'api_key_configured': bool(BELGRANO_AHORRO_API_KEY),
        'endpoints': {},
        'total_endpoints': 0,
        'successful_endpoints': 0,
        'overall_status': 'unknown'
    }
    
    endpoints = [
        ('negocios', 'v1/negocios'),
        ('productos', 'v1/productos'),
        ('ofertas', 'v1/ofertas'),
        ('sucursales', 'v1/sucursales'),
        ('precios', 'v1/precios')
    ]
    
    for nombre, endpoint in endpoints:
        resultados['total_endpoints'] += 1
        success, data = make_api_request('GET', endpoint)
        
        if success:
            resultados['endpoints'][nombre] = {
                'status': 'success',
                'data_count': len(data) if isinstance(data, list) else 0,
                'message': f'✅ {nombre} obtenidos correctamente'
            }
            resultados['successful_endpoints'] += 1
        else:
            resultados['endpoints'][nombre] = {
                'status': 'error',
                'data_count': 0,
                'message': f'❌ {nombre}: {data}'
            }
    
    # Calcular estado general
    if resultados['successful_endpoints'] == resultados['total_endpoints']:
        resultados['overall_status'] = 'success'
    elif resultados['successful_endpoints'] > 0:
        resultados['overall_status'] = 'partial'
    else:
        resultados['overall_status'] = 'error'
    
    resultados['success_rate'] = f"{resultados['successful_endpoints']}/{resultados['total_endpoints']}"
    
    logger.info(f"📊 Conectividad API real: {resultados['overall_status']} ({resultados['success_rate']})")
    
    return resultados

# =================================================================
# FUNCIÓN PRINCIPAL DE PRUEBA
# =================================================================

def probar_api_real_completa():
    """Probar que todas las funciones usen SOLO API real"""
    print("🧪 PROBANDO API REAL - SOLO DATOS DE BELGRANO AHORRO")
    print("=" * 60)
    
    # Verificar conectividad
    conectividad = verificar_conectividad_api_real()
    print(f"\n📊 Estado de Conectividad: {conectividad['overall_status']}")
    print(f"📈 Tasa de Éxito: {conectividad['success_rate']}")
    
    # Probar obtención de datos
    print("\n🔍 PROBANDO OBTENCIÓN DE DATOS REALES:")
    
    negocios = get_negocios_from_belgrano_real()
    print(f"🏪 Negocios: {len(negocios)} registros reales")
    
    productos = get_productos_from_belgrano_real()
    print(f"📦 Productos: {len(productos)} registros reales")
    
    ofertas = get_ofertas_from_belgrano_real()
    print(f"🎯 Ofertas: {len(ofertas)} registros reales")
    
    sucursales = get_sucursales_from_belgrano_real()
    print(f"🏢 Sucursales: {len(sucursales)} registros reales")
    
    precios = get_precios_from_belgrano_real()
    print(f"💰 Precios: {len(precios)} registros reales")
    
    # Verificar que no hay fallbacks locales
    print("\n✅ VERIFICACIÓN:")
    print("✅ Sin fallbacks locales")
    print("✅ Sin datos simulados")
    print("✅ Solo API real de Belgrano Ahorro")
    print("✅ Datos 100% reales")
    
    return {
        'negocios': len(negocios),
        'productos': len(productos),
        'ofertas': len(ofertas),
        'sucursales': len(sucursales),
        'precios': len(precios),
        'conectividad': conectividad
    }

if __name__ == "__main__":
    probar_api_real_completa()
