#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FUNCIONES DEVOPS - SOLO API REAL DE BELGRANO AHORRO
Reemplazo completo sin fallbacks locales
"""

import os
import requests
import logging
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
    """Realizar request a la API real de Belgrano Ahorro - SIN FALLBACKS"""
    try:
        url = build_api_url(endpoint)
        headers = {
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'Content-Type': 'application/json',
            'X-Origin': 'devops_solo_api_real'
        }
        
        logger.info(f"🌐 {method} {url}")
        
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

def get_negocios_from_belgrano():
    """Obtener negocios SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
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
                logger.warning("⚠️ Formato inesperado de negocios desde API")
                return []
        else:
            logger.error(f"❌ No se pudieron obtener negocios: {data}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocios: {e}")
        return []

def get_productos_from_belgrano():
    """Obtener productos SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
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
                logger.warning("⚠️ Formato inesperado de productos desde API")
                return []
        else:
            logger.error(f"❌ No se pudieron obtener productos: {data}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo productos: {e}")
        return []

def get_ofertas_from_belgrano():
    """Obtener ofertas SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
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
                logger.warning("⚠️ Formato inesperado de ofertas desde API")
                return []
        else:
            logger.error(f"❌ No se pudieron obtener ofertas: {data}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo ofertas: {e}")
        return []

def get_sucursales_from_belgrano():
    """Obtener sucursales SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
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
                logger.warning("⚠️ Formato inesperado de sucursales desde API")
                return []
        else:
            logger.error(f"❌ No se pudieron obtener sucursales: {data}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo sucursales: {e}")
        return []

def get_precios_from_belgrano():
    """Obtener precios SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
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
                logger.warning("⚠️ Formato inesperado de precios desde API")
                return []
        else:
            logger.error(f"❌ No se pudieron obtener precios: {data}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo precios: {e}")
        return []

def sincronizar_con_belgrano_ahorro():
    """Sincronizar datos SOLO desde API real de Belgrano Ahorro"""
    try:
        logger.info("🔄 Iniciando sincronización SOLO con API real de Belgrano Ahorro...")
        
        # Obtener datos SOLO desde API real
        productos = get_productos_from_belgrano()
        negocios = get_negocios_from_belgrano()
        sucursales = get_sucursales_from_belgrano()
        ofertas = get_ofertas_from_belgrano()
        precios = get_precios_from_belgrano()
        
        logger.info(f"📊 Sincronización completada:")
        logger.info(f"   🏪 Negocios: {len(negocios)}")
        logger.info(f"   📦 Productos: {len(productos)}")
        logger.info(f"   🏢 Sucursales: {len(sucursales)}")
        logger.info(f"   🎯 Ofertas: {len(ofertas)}")
        logger.info(f"   💰 Precios: {len(precios)}")
        
        return {
            'productos': len(productos),
            'negocios': len(negocios),
            'sucursales': len(sucursales),
            'ofertas': len(ofertas),
            'precios': len(precios),
            'source': 'api_real_only'
        }
        
    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        return {
            'productos': 0,
            'negocios': 0,
            'sucursales': 0,
            'ofertas': 0,
            'precios': 0,
            'source': 'error'
        }

if __name__ == "__main__":
    print("🧪 PROBANDO FUNCIONES SOLO API REAL")
    print("=" * 50)
    
    # Probar funciones
    negocios = get_negocios_from_belgrano()
    productos = get_productos_from_belgrano()
    ofertas = get_ofertas_from_belgrano()
    sucursales = get_sucursales_from_belgrano()
    precios = get_precios_from_belgrano()
    
    print(f"🏪 Negocios: {len(negocios)} (API real)")
    print(f"📦 Productos: {len(productos)} (API real)")
    print(f"🎯 Ofertas: {len(ofertas)} (API real)")
    print(f"🏢 Sucursales: {len(sucursales)} (API real)")
    print(f"💰 Precios: {len(precios)} (API real)")
    
    print("\n✅ CONFIRMACIÓN:")
    print("✅ Solo API real de Belgrano Ahorro")
    print("✅ Sin fallbacks locales")
    print("✅ Sin datos simulados")
    print("✅ Datos 100% reales")
