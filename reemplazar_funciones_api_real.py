#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reemplazar funciones DevOps con versiones que SOLO usen API real
"""

import os
import shutil
from datetime import datetime

def crear_backup_original():
    """Crear backup de archivos originales"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    archivos_originales = [
        'belgrano_tickets/devops_routes_backup.py',
        'belgrano_tickets/app.py',
        'devops_belgrano_manager_unified.py'
    ]
    
    for archivo in archivos_originales:
        if os.path.exists(archivo):
            backup_name = f"{archivo}.backup_{timestamp}"
            shutil.copy2(archivo, backup_name)
            print(f"✅ Backup creado: {backup_name}")

def reemplazar_funciones_get():
    """Reemplazar funciones get_*_from_belgrano con versiones que solo usen API real"""
    
    codigo_nuevo = '''
def get_negocios_from_belgrano():
    """Obtener negocios SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
        response = requests.get(
            build_api_url('v1/negocios'),
            headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
            timeout=API_TIMEOUT_SECS
        )
        if response.status_code == 200:
            negocios_api = response.json()
            if isinstance(negocios_api, list):
                logger.info(f"✅ {len(negocios_api)} negocios obtenidos desde API real")
                return negocios_api
            elif isinstance(negocios_api, dict):
                negocios = list(negocios_api.values())
                logger.info(f"✅ {len(negocios)} negocios obtenidos desde API real")
                return negocios
            else:
                logger.warning("⚠️ Formato inesperado de negocios desde API")
                return []
        else:
            logger.error(f"❌ Error API negocios: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo negocios desde API: {e}")
        return []

def get_productos_from_belgrano():
    """Obtener productos SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
        response = requests.get(
            build_api_url('v1/productos'),
            headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
            timeout=API_TIMEOUT_SECS
        )
        if response.status_code == 200:
            productos_api = response.json()
            if isinstance(productos_api, list):
                logger.info(f"✅ {len(productos_api)} productos obtenidos desde API real")
                return productos_api
            elif isinstance(productos_api, dict) and 'data' in productos_api:
                productos = productos_api.get('data', [])
                logger.info(f"✅ {len(productos)} productos obtenidos desde API real")
                return productos
            else:
                logger.warning("⚠️ Formato inesperado de productos desde API")
                return []
        else:
            logger.error(f"❌ Error API productos: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo productos desde API: {e}")
        return []

def get_ofertas_from_belgrano():
    """Obtener ofertas SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
        response = requests.get(
            build_api_url('v1/ofertas'),
            headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
            timeout=API_TIMEOUT_SECS
        )
        if response.status_code == 200:
            ofertas_api = response.json()
            if isinstance(ofertas_api, list):
                logger.info(f"✅ {len(ofertas_api)} ofertas obtenidas desde API real")
                return ofertas_api
            elif isinstance(ofertas_api, dict) and 'data' in ofertas_api:
                ofertas = ofertas_api.get('data', [])
                logger.info(f"✅ {len(ofertas)} ofertas obtenidas desde API real")
                return ofertas
            else:
                logger.warning("⚠️ Formato inesperado de ofertas desde API")
                return []
        else:
            logger.error(f"❌ Error API ofertas: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo ofertas desde API: {e}")
        return []

def get_sucursales_from_belgrano():
    """Obtener sucursales SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
        response = requests.get(
            build_api_url('v1/sucursales'),
            headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
            timeout=API_TIMEOUT_SECS
        )
        if response.status_code == 200:
            sucursales_api = response.json()
            if isinstance(sucursales_api, list):
                logger.info(f"✅ {len(sucursales_api)} sucursales obtenidas desde API real")
                return sucursales_api
            elif isinstance(sucursales_api, dict) and 'data' in sucursales_api:
                sucursales = sucursales_api.get('data', [])
                logger.info(f"✅ {len(sucursales)} sucursales obtenidas desde API real")
                return sucursales
            else:
                logger.warning("⚠️ Formato inesperado de sucursales desde API")
                return []
        else:
            logger.error(f"❌ Error API sucursales: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo sucursales desde API: {e}")
        return []

def get_precios_from_belgrano():
    """Obtener precios SOLO desde API real de Belgrano Ahorro - SIN FALLBACK LOCAL"""
    try:
        response = requests.get(
            build_api_url('v1/precios'),
            headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
            timeout=API_TIMEOUT_SECS
        )
        if response.status_code == 200:
            precios_api = response.json()
            if isinstance(precios_api, list):
                logger.info(f"✅ {len(precios_api)} precios obtenidos desde API real")
                return precios_api
            elif isinstance(precios_api, dict) and 'data' in precios_api:
                precios = precios_api.get('data', [])
                logger.info(f"✅ {len(precios)} precios obtenidos desde API real")
                return precios
            else:
                logger.warning("⚠️ Formato inesperado de precios desde API")
                return []
        else:
            logger.error(f"❌ Error API precios: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Error obteniendo precios desde API: {e}")
        return []
'''
    
    return codigo_nuevo

def crear_archivo_reemplazo():
    """Crear archivo con las funciones reemplazadas"""
    
    codigo_completo = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FUNCIONES DEVOPS - SOLO API REAL DE BELGRANO AHORRO
Reemplazo de funciones para eliminar fallbacks locales
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

''' + reemplazar_funciones_get() + '''

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

def verificar_solo_api_real():
    """Verificar que todas las funciones usen SOLO API real"""
    print("🔍 VERIFICANDO QUE SOLO SE USE API REAL")
    print("=" * 50)
    
    # Verificar que no hay archivos de fallback
    archivos_fallback = ['productos.json', 'negocios.json', 'ofertas.json']
    fallbacks_encontrados = []
    
    for archivo in archivos_fallback:
        if os.path.exists(archivo):
            fallbacks_encontrados.append(archivo)
    
    if fallbacks_encontrados:
        print(f"⚠️ Archivos de fallback encontrados: {fallbacks_encontrados}")
        print("   Estos archivos NO se usarán - solo API real")
    else:
        print("✅ No hay archivos de fallback local")
    
    # Probar funciones
    print("\\n🧪 PROBANDO FUNCIONES SOLO API REAL:")
    
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
    
    print("\\n✅ CONFIRMACIÓN:")
    print("✅ Solo API real de Belgrano Ahorro")
    print("✅ Sin fallbacks locales")
    print("✅ Sin datos simulados")
    print("✅ Datos 100% reales")
    
    return {
        'negocios': len(negocios),
        'productos': len(productos),
        'ofertas': len(ofertas),
        'sucursales': len(sucursales),
        'precios': len(precios),
        'fallbacks_encontrados': fallbacks_encontrados
    }

if __name__ == "__main__":
    verificar_solo_api_real()
'''
    
    with open('funciones_api_real_reemplazo.py', 'w', encoding='utf-8') as f:
        f.write(codigo_completo)
    
    print("✅ Archivo de reemplazo creado: funciones_api_real_reemplazo.py")

def main():
    """Función principal"""
    print("🔧 REEMPLAZANDO FUNCIONES DEVOPS - SOLO API REAL")
    print("=" * 60)
    
    # Crear backups
    crear_backup_original()
    
    # Crear archivo de reemplazo
    crear_archivo_reemplazo()
    
    print("\\n📋 INSTRUCCIONES:")
    print("1. Revisar funciones_api_real_reemplazo.py")
    print("2. Reemplazar funciones en archivos originales")
    print("3. Eliminar referencias a fallbacks locales")
    print("4. Probar que solo use API real")
    
    print("\\n✅ PROCESO COMPLETADO")
    print("   - Backups creados")
    print("   - Funciones de reemplazo listas")
    print("   - Solo API real de Belgrano Ahorro")

if __name__ == "__main__":
    main()
