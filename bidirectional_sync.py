# =================================================================
# SISTEMA DE SINCRONIZACIÓN BIDIRECCIONAL
# BELGRANO AHORRO ↔ BELGRANO TICKETERA
# =================================================================

import json
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
from sync_config import sync_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BidirectionalSync:
    """Sistema de sincronización bidireccional entre plataformas"""
    
    def __init__(self):
        self.config = sync_config
        self.last_sync: Dict[str, Optional[datetime]] = {
            'productos': None,
            'tickets': None,
            'estados': None
        }
        self.sync_stats: Dict[str, int | str] = {
            'productos_synced': 0,
            'tickets_synced': 0,
            'estados_synced': 0,
            'errors': 0,
            'last_error': ''
        }
        
        # Inicializar base de datos de sincronización
        self.init_sync_database()
    
    def init_sync_database(self):
        """Inicializar base de datos para tracking de sincronización"""
        try:
            conn = sqlite3.connect('sync_database.db')
            cursor = conn.cursor()
            
            # Tabla de productos sincronizados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id VARCHAR(50) UNIQUE NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    precio REAL NOT NULL,
                    categoria VARCHAR(100),
                    negocio VARCHAR(100),
                    sucursal VARCHAR(100),
                    stock INTEGER DEFAULT 0,
                    activo BOOLEAN DEFAULT 1,
                    ultima_sincronizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    origen VARCHAR(20) NOT NULL,
                    estado_sync VARCHAR(20) DEFAULT 'sincronizado'
                )
            """)
            
            # Tabla de tickets sincronizados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id VARCHAR(50) UNIQUE NOT NULL,
                    numero_pedido VARCHAR(50) NOT NULL,
                    cliente_nombre VARCHAR(255) NOT NULL,
                    cliente_email VARCHAR(255),
                    total REAL NOT NULL,
                    estado VARCHAR(50) DEFAULT 'pendiente',
                    productos TEXT NOT NULL,
                    fecha_creacion DATETIME,
                    ultima_sincronizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    origen VARCHAR(20) NOT NULL,
                    estado_sync VARCHAR(20) DEFAULT 'sincronizado'
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de sincronización inicializada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos de sincronización: {e}")
    
    def sync_productos_from_ticketera(self) -> Dict:
        """Sincronizar productos desde Ticketera hacia Ahorro"""
        start_time = time.time()
        logger.info("🔄 Iniciando sincronización de productos desde Ticketera...")
        
        try:
            # Obtener productos de Ticketera
            ticketera_url = f"{self.config.TICKETERA_URL}{self.config.TICKETERA_ENDPOINTS['productos']}"
            headers = self.config.get_ticketera_headers()
            
            response = requests.get(ticketera_url, headers=headers, timeout=self.config.API_TIMEOUT)
            
            if response.status_code != 200:
                error_msg = f"Error obteniendo productos de Ticketera: {response.status_code}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            productos_ticketera = response.json().get('productos', [])
            logger.info(f"📦 Obtenidos {len(productos_ticketera)} productos de Ticketera")
            
            # Sincronizar con Ahorro
            ahorro_url = f"{self.config.BELGRANO_AHORRO_URL}{self.config.AHORRO_ENDPOINTS['productos']}/sync"
            ahorro_headers = self.config.get_ahorro_headers()
            
            sync_data = {
                'productos': productos_ticketera,
                'origen': 'ticketera',
                'fecha_sync': datetime.now().isoformat()
            }
            
            sync_response = requests.post(
                ahorro_url, 
                json=sync_data, 
                headers=ahorro_headers, 
                timeout=self.config.API_TIMEOUT
            )
            
            if sync_response.status_code in (200, 201):
                resultado = sync_response.json()
                tiempo_ejecucion = time.time() - start_time
                
                logger.info(f"✅ Productos sincronizados exitosamente: {resultado.get('productos_sincronizados', 0)}")
                
                # Actualizar estadísticas
                self.sync_stats['productos_synced'] += resultado.get('productos_sincronizados', 0)
                self.last_sync['productos'] = datetime.now()
                
                return {
                    'success': True,
                    'productos_sincronizados': resultado.get('productos_sincronizados', 0),
                    'tiempo_ejecucion': tiempo_ejecucion
                }
            else:
                error_msg = f"Error sincronizando productos con Ahorro: {sync_response.status_code}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            tiempo_ejecucion = time.time() - start_time
            error_msg = f"Error en sincronización de productos: {str(e)}"
            logger.error(error_msg)
            self.sync_stats['errors'] += 1
            self.sync_stats['last_error'] = error_msg
            return {'success': False, 'error': error_msg}
    
    def sync_tickets_from_ahorro(self) -> Dict:
        """Sincronizar tickets desde Ahorro hacia Ticketera"""
        start_time = time.time()
        logger.info("🔄 Iniciando sincronización de tickets desde Ahorro...")
        
        try:
            # Obtener pedidos de Ahorro
            ahorro_url = f"{self.config.BELGRANO_AHORRO_URL}{self.config.AHORRO_ENDPOINTS['pedidos']}"
            headers = self.config.get_ahorro_headers()
            
            response = requests.get(ahorro_url, headers=headers, timeout=self.config.API_TIMEOUT)
            
            if response.status_code != 200:
                error_msg = f"Error obteniendo pedidos de Ahorro: {response.status_code}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            pedidos_ahorro = response.json().get('pedidos', [])
            logger.info(f"📋 Obtenidos {len(pedidos_ahorro)} pedidos de Ahorro")
            
            # Filtrar pedidos que no han sido sincronizados
            pedidos_pendientes = [
                p for p in pedidos_ahorro 
                if p.get('estado_sync') != 'sincronizado' and p.get('estado') != 'cancelado'
            ]
            
            if not pedidos_pendientes:
                logger.info("✅ No hay pedidos pendientes de sincronización")
                return {'success': True, 'tickets_sincronizados': 0}
            
            # Sincronizar con Ticketera
            ticketera_url = f"{self.config.TICKETERA_URL}{self.config.TICKETERA_ENDPOINTS['tickets']}/sync"
            ticketera_headers = self.config.get_ticketera_headers()
            
            tickets_creados = 0
            
            for pedido in pedidos_pendientes:
                try:
                    # Preparar datos del ticket
                    ticket_data = {
                        'numero': pedido.get('numero_pedido'),
                        'cliente_nombre': pedido.get('cliente_nombre'),
                        'cliente_email': pedido.get('cliente_email'),
                        'cliente_direccion': pedido.get('direccion_entrega'),
                        'cliente_telefono': pedido.get('cliente_telefono'),
                        'productos': pedido.get('productos', []),
                        'total': pedido.get('total'),
                        'metodo_pago': pedido.get('metodo_pago'),
                        'indicaciones': pedido.get('notas'),
                        'estado': 'pendiente',
                        'prioridad': 'normal',
                        'origen': 'ahorro'
                    }
                    
                    # Crear ticket en Ticketera
                    ticket_response = requests.post(
                        ticketera_url,
                        json=ticket_data,
                        headers=ticketera_headers,
                        timeout=self.config.API_TIMEOUT
                    )
                    
                    if ticket_response.status_code in (200, 201):
                        tickets_creados += 1
                        logger.info(f"✅ Ticket creado para pedido {pedido.get('numero_pedido')}")
                        
                        # Marcar pedido como sincronizado en Ahorro
                        self.mark_pedido_synced(pedido.get('id'))
                        
                    else:
                        logger.warning(f"⚠️ Error creando ticket para pedido {pedido.get('numero_pedido')}: {ticket_response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error procesando pedido {pedido.get('numero_pedido')}: {e}")
                    continue
            
            tiempo_ejecucion = time.time() - start_time
            
            if tickets_creados > 0:
                logger.info(f"✅ {tickets_creados} tickets sincronizados exitosamente")
                
                # Actualizar estadísticas
                self.sync_stats['tickets_synced'] += tickets_creados
                self.last_sync['tickets'] = datetime.now()
            
            return {
                'success': True,
                'tickets_sincronizados': tickets_creados,
                'tiempo_ejecucion': tiempo_ejecucion
            }
                
        except Exception as e:
            tiempo_ejecucion = time.time() - start_time
            error_msg = f"Error en sincronización de tickets: {str(e)}"
            logger.error(error_msg)
            self.sync_stats['errors'] += 1
            self.sync_stats['last_error'] = error_msg
            return {'success': False, 'error': error_msg}
    
    def mark_pedido_synced(self, pedido_id: str):
        """Marcar pedido como sincronizado en Ahorro"""
        try:
            ahorro_url = f"{self.config.BELGRANO_AHORRO_URL}{self.config.AHORRO_ENDPOINTS['pedidos']}/{pedido_id}/sync"
            headers = self.config.get_ahorro_headers()
            
            sync_data = {
                'estado_sync': 'sincronizado',
                'fecha_sync': datetime.now().isoformat()
            }
            
            response = requests.patch(ahorro_url, json=sync_data, headers=headers, timeout=self.config.API_TIMEOUT)
            
            if response.status_code == 200:
                logger.info(f"✅ Pedido {pedido_id} marcado como sincronizado")
            else:
                logger.warning(f"⚠️ Error marcando pedido {pedido_id} como sincronizado: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error marcando pedido {pedido_id} como sincronizado: {e}")

# Instancia global del sistema de sincronización
bidirectional_sync = BidirectionalSync()
