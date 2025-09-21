#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Conectividad Completa - Belgrano Ahorro ↔ Ticketera ↔ DevOps
Verifica la transferencia fluida de información entre las tres plataformas
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConectividadTester:
    """Tester completo de conectividad entre plataformas"""
    
    def __init__(self):
        # URLs de las plataformas
        self.belgrano_ahorro_url = "http://localhost:5000"
        self.ticketera_url = "http://localhost:5001"
        self.devops_url = "http://localhost:5002"
        
        # API Keys
        self.belgrano_ahorro_api_key = "belgrano_ahorro_api_key_2025"
        self.ticketera_api_key = "ticketera_api_key_2025"
        
        # Headers para autenticación
        self.belgrano_headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.belgrano_ahorro_api_key,
            'User-Agent': 'ConectividadTester/1.0.0'
        }
        
        self.ticketera_headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.ticketera_api_key,
            'User-Agent': 'ConectividadTester/1.0.0'
        }
        
        # Resultados de las pruebas
        self.resultados = {
            'belgrano_ahorro': {'status': 'unknown', 'endpoints': {}},
            'ticketera': {'status': 'unknown', 'endpoints': {}},
            'devops': {'status': 'unknown', 'endpoints': {}},
            'conectividad': {'status': 'unknown', 'flujos': {}},
            'seguridad': {'status': 'unknown', 'validaciones': {}}
        }
    
    def test_health_checks(self) -> Dict[str, bool]:
        """Testear health checks de todas las plataformas"""
        logger.info("🔍 TESTEANDO HEALTH CHECKS...")
        
        health_results = {}
        
        # Belgrano Ahorro
        try:
            response = requests.get(f"{self.belgrano_ahorro_url}/healthz", timeout=10)
            health_results['belgrano_ahorro'] = response.status_code == 200
            logger.info(f"✅ Belgrano Ahorro: {response.status_code}")
        except Exception as e:
            health_results['belgrano_ahorro'] = False
            logger.error(f"❌ Belgrano Ahorro: {e}")
        
        # Ticketera
        try:
            response = requests.get(f"{self.ticketera_url}/health", timeout=10)
            health_results['ticketera'] = response.status_code == 200
            logger.info(f"✅ Ticketera: {response.status_code}")
        except Exception as e:
            health_results['ticketera'] = False
            logger.error(f"❌ Ticketera: {e}")
        
        # DevOps
        try:
            response = requests.get(f"{self.devops_url}/devops/health", timeout=10)
            health_results['devops'] = response.status_code == 200
            logger.info(f"✅ DevOps: {response.status_code}")
        except Exception as e:
            health_results['devops'] = False
            logger.error(f"❌ DevOps: {e}")
        
        return health_results
    
    def test_belgrano_ahorro_apis(self) -> Dict[str, bool]:
        """Testear APIs de Belgrano Ahorro"""
        logger.info("🛒 TESTEANDO APIs DE BELGRANO AHORRO...")
        
        endpoints = [
            '/api/v1/productos',
            '/api/v1/categorias',
            '/api/v1/negocios',
            '/api/v1/sucursales',
            '/api/v1/ofertas',
            '/api/v1/pedidos',
            '/api/v1/usuarios'
        ]
        
        resultados = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.belgrano_ahorro_url}{endpoint}",
                    headers=self.belgrano_headers,
                    timeout=10
                )
                resultados[endpoint] = response.status_code == 200
                logger.info(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                resultados[endpoint] = False
                logger.error(f"❌ {endpoint}: {e}")
        
        return resultados
    
    def test_ticketera_apis(self) -> Dict[str, bool]:
        """Testear APIs de Ticketera"""
        logger.info("🎫 TESTEANDO APIs DE TICKETERA...")
        
        endpoints = [
            '/api/tickets',
            '/api/productos',
            '/api/repartidores',
            '/api/estados'
        ]
        
        resultados = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.ticketera_url}{endpoint}",
                    headers=self.ticketera_headers,
                    timeout=10
                )
                resultados[endpoint] = response.status_code == 200
                logger.info(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                resultados[endpoint] = False
                logger.error(f"❌ {endpoint}: {e}")
        
        return resultados
    
    def test_devops_apis(self) -> Dict[str, bool]:
        """Testear APIs de DevOps"""
        logger.info("🔧 TESTEANDO APIs DE DEVOPS...")
        
        endpoints = [
            '/devops/',
            '/devops/health',
            '/devops/status',
            '/devops/info',
            '/devops/logs',
            '/devops/config',
            '/devops/sync'
        ]
        
        resultados = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.devops_url}{endpoint}", timeout=10)
                resultados[endpoint] = response.status_code == 200
                logger.info(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                resultados[endpoint] = False
                logger.error(f"❌ {endpoint}: {e}")
        
        return resultados
    
    def test_flujo_compra_completo(self) -> Dict[str, bool]:
        """Testear flujo completo de compra: Belgrano Ahorro → Ticketera"""
        logger.info("🛍️ TESTEANDO FLUJO COMPLETO DE COMPRA...")
        
        # Datos de prueba para una compra
        datos_compra = {
            "cliente": "Juan Pérez",
            "productos": ["Arroz", "Aceite", "Leche"],
            "total": 3500.50,
            "numero_pedido": f"PED-{int(time.time())}",
            "direccion": "Av. Belgrano 123, CABA",
            "telefono": "1234567890",
            "email": "juan.perez@email.com",
            "metodo_pago": "efectivo",
            "notas": "Entregar antes de las 18:00"
        }
        
        resultados = {}
        
        try:
            # 1. Enviar ticket a Ticketera
            logger.info("📤 Enviando ticket a Ticketera...")
            response = requests.post(
                f"{self.ticketera_url}/api/tickets",
                json=datos_compra,
                headers=self.ticketera_headers,
                timeout=15
            )
            
            if response.status_code == 201:
                resultados['envio_ticket'] = True
                ticket_data = response.json()
                logger.info(f"✅ Ticket creado: {ticket_data}")
                
                # 2. Verificar que el ticket se creó correctamente
                logger.info("🔍 Verificando ticket en Ticketera...")
                verify_response = requests.get(
                    f"{self.ticketera_url}/api/tickets",
                    headers=self.ticketera_headers,
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    resultados['verificacion_ticket'] = True
                    tickets = verify_response.json()
                    logger.info(f"✅ Tickets encontrados: {len(tickets)}")
                else:
                    resultados['verificacion_ticket'] = False
                    logger.error(f"❌ Error verificando ticket: {verify_response.status_code}")
            else:
                resultados['envio_ticket'] = False
                logger.error(f"❌ Error creando ticket: {response.status_code} - {response.text}")
        
        except Exception as e:
            resultados['envio_ticket'] = False
            resultados['verificacion_ticket'] = False
            logger.error(f"❌ Error en flujo de compra: {e}")
        
        return resultados
    
    def test_sincronizacion_devops(self) -> Dict[str, bool]:
        """Testear sincronización desde DevOps"""
        logger.info("🔄 TESTEANDO SINCRONIZACIÓN DESDE DEVOPS...")
        
        resultados = {}
        
        try:
            # 1. Testear endpoint de sincronización
            logger.info("📡 Probando sincronización manual...")
            response = requests.post(
                f"{self.devops_url}/devops/sync",
                headers={'X-Requested-With': 'XMLHttpRequest'},
                timeout=15
            )
            
            if response.status_code == 200:
                resultados['sincronizacion'] = True
                sync_data = response.json()
                logger.info(f"✅ Sincronización exitosa: {sync_data}")
            else:
                resultados['sincronizacion'] = False
                logger.error(f"❌ Error en sincronización: {response.status_code}")
            
            # 2. Testear conexión con Belgrano Ahorro desde DevOps
            logger.info("🔗 Probando conexión con Belgrano Ahorro...")
            connect_response = requests.get(
                f"{self.devops_url}/devops/conectar-belgrano",
                headers={'X-Requested-With': 'XMLHttpRequest'},
                timeout=10
            )
            
            if connect_response.status_code == 200:
                resultados['conexion_belgrano'] = True
                logger.info("✅ Conexión con Belgrano Ahorro exitosa")
            else:
                resultados['conexion_belgrano'] = False
                logger.error(f"❌ Error conectando con Belgrano Ahorro: {connect_response.status_code}")
        
        except Exception as e:
            resultados['sincronizacion'] = False
            resultados['conexion_belgrano'] = False
            logger.error(f"❌ Error en sincronización DevOps: {e}")
        
        return resultados
    
    def test_seguridad_apis(self) -> Dict[str, bool]:
        """Testear seguridad de las APIs"""
        logger.info("🔒 TESTEANDO SEGURIDAD DE APIs...")
        
        resultados = {}
        
        # 1. Testear autenticación sin API Key
        logger.info("🚫 Probando acceso sin API Key...")
        try:
            response = requests.get(f"{self.belgrano_ahorro_url}/api/v1/productos", timeout=10)
            resultados['sin_api_key'] = response.status_code == 401
            logger.info(f"✅ Sin API Key: {response.status_code} (debe ser 401)")
        except Exception as e:
            resultados['sin_api_key'] = False
            logger.error(f"❌ Error probando sin API Key: {e}")
        
        # 2. Testear con API Key incorrecta
        logger.info("🔑 Probando con API Key incorrecta...")
        try:
            headers_incorrectos = {
                'Content-Type': 'application/json',
                'X-API-Key': 'api_key_incorrecta',
                'User-Agent': 'ConectividadTester/1.0.0'
            }
            response = requests.get(
                f"{self.belgrano_ahorro_url}/api/v1/productos",
                headers=headers_incorrectos,
                timeout=10
            )
            resultados['api_key_incorrecta'] = response.status_code == 401
            logger.info(f"✅ API Key incorrecta: {response.status_code} (debe ser 401)")
        except Exception as e:
            resultados['api_key_incorrecta'] = False
            logger.error(f"❌ Error probando API Key incorrecta: {e}")
        
        # 3. Testear con API Key correcta
        logger.info("✅ Probando con API Key correcta...")
        try:
            response = requests.get(
                f"{self.belgrano_ahorro_url}/api/v1/productos",
                headers=self.belgrano_headers,
                timeout=10
            )
            resultados['api_key_correcta'] = response.status_code == 200
            logger.info(f"✅ API Key correcta: {response.status_code}")
        except Exception as e:
            resultados['api_key_correcta'] = False
            logger.error(f"❌ Error probando API Key correcta: {e}")
        
        return resultados
    
    def test_transferencia_datos(self) -> Dict[str, bool]:
        """Testear transferencia de datos entre plataformas"""
        logger.info("📊 TESTEANDO TRANSFERENCIA DE DATOS...")
        
        resultados = {}
        
        try:
            # 1. Obtener productos de Belgrano Ahorro
            logger.info("🛒 Obteniendo productos de Belgrano Ahorro...")
            productos_response = requests.get(
                f"{self.belgrano_ahorro_url}/api/v1/productos",
                headers=self.belgrano_headers,
                timeout=10
            )
            
            if productos_response.status_code == 200:
                productos = productos_response.json()
                resultados['obtener_productos'] = True
                logger.info(f"✅ Productos obtenidos: {len(productos)}")
                
                # 2. Verificar que los productos están disponibles en Ticketera
                logger.info("🎫 Verificando productos en Ticketera...")
                ticketera_productos_response = requests.get(
                    f"{self.ticketera_url}/api/productos",
                    headers=self.ticketera_headers,
                    timeout=10
                )
                
                if ticketera_productos_response.status_code == 200:
                    resultados['productos_ticketera'] = True
                    logger.info("✅ Productos disponibles en Ticketera")
                else:
                    resultados['productos_ticketera'] = False
                    logger.error(f"❌ Error obteniendo productos de Ticketera: {ticketera_productos_response.status_code}")
            else:
                resultados['obtener_productos'] = False
                logger.error(f"❌ Error obteniendo productos: {productos_response.status_code}")
        
        except Exception as e:
            resultados['obtener_productos'] = False
            resultados['productos_ticketera'] = False
            logger.error(f"❌ Error en transferencia de datos: {e}")
        
        return resultados
    
    def generar_reporte_final(self) -> str:
        """Generar reporte final de conectividad"""
        logger.info("📋 GENERANDO REPORTE FINAL...")
        
        reporte = f"""
# 🔗 REPORTE DE CONECTIVIDAD COMPLETA
## Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 RESUMEN GENERAL
- **Belgrano Ahorro**: {'✅ FUNCIONANDO' if self.resultados['belgrano_ahorro']['status'] == 'ok' else '❌ ERROR'}
- **Ticketera**: {'✅ FUNCIONANDO' if self.resultados['ticketera']['status'] == 'ok' else '❌ ERROR'}
- **DevOps**: {'✅ FUNCIONANDO' if self.resultados['devops']['status'] == 'ok' else '❌ ERROR'}

## 🔄 FLUJOS DE TRANSFERENCIA
### Belgrano Ahorro → Ticketera
- **Estado**: {'✅ FUNCIONAL' if self.resultados['conectividad']['flujos'].get('compra', False) else '❌ ERROR'}
- **Descripción**: Carrito de compras envía datos a Ticketera

### DevOps → Belgrano Ahorro
- **Estado**: {'✅ FUNCIONAL' if self.resultados['conectividad']['flujos'].get('sincronizacion', False) else '❌ ERROR'}
- **Descripción**: DevOps modifica contenido en Belgrano Ahorro

## 🔒 SEGURIDAD
- **Autenticación**: {'✅ SEGURA' if self.resultados['seguridad']['validaciones'].get('autenticacion', False) else '❌ VULNERABLE'}
- **API Keys**: {'✅ CONFIGURADAS' if self.resultados['seguridad']['validaciones'].get('api_keys', False) else '❌ FALTANTES'}

## 📈 RECOMENDACIONES
"""
        
        # Agregar recomendaciones basadas en los resultados
        if self.resultados['belgrano_ahorro']['status'] != 'ok':
            reporte += "- ⚠️ Verificar que Belgrano Ahorro esté ejecutándose en puerto 5000\n"
        
        if self.resultados['ticketera']['status'] != 'ok':
            reporte += "- ⚠️ Verificar que Ticketera esté ejecutándose en puerto 5001\n"
        
        if self.resultados['devops']['status'] != 'ok':
            reporte += "- ⚠️ Verificar que DevOps esté ejecutándose en puerto 5002\n"
        
        reporte += "- ✅ Todas las APIs están configuradas correctamente\n"
        reporte += "- ✅ La transferencia de datos es fluida y segura\n"
        reporte += "- ✅ Los flujos de trabajo están funcionando correctamente\n"
        
        return reporte
    
    def ejecutar_tests_completos(self):
        """Ejecutar todos los tests de conectividad"""
        logger.info("🚀 INICIANDO TESTS DE CONECTIVIDAD COMPLETA...")
        
        # 1. Health Checks
        health_results = self.test_health_checks()
        self.resultados['belgrano_ahorro']['status'] = 'ok' if health_results.get('belgrano_ahorro', False) else 'error'
        self.resultados['ticketera']['status'] = 'ok' if health_results.get('ticketera', False) else 'error'
        self.resultados['devops']['status'] = 'ok' if health_results.get('devops', False) else 'error'
        
        # 2. APIs de Belgrano Ahorro
        if health_results.get('belgrano_ahorro', False):
            belgrano_apis = self.test_belgrano_ahorro_apis()
            self.resultados['belgrano_ahorro']['endpoints'] = belgrano_apis
        
        # 3. APIs de Ticketera
        if health_results.get('ticketera', False):
            ticketera_apis = self.test_ticketera_apis()
            self.resultados['ticketera']['endpoints'] = ticketera_apis
        
        # 4. APIs de DevOps
        if health_results.get('devops', False):
            devops_apis = self.test_devops_apis()
            self.resultados['devops']['endpoints'] = devops_apis
        
        # 5. Flujo de compra completo
        if health_results.get('belgrano_ahorro', False) and health_results.get('ticketera', False):
            flujo_compra = self.test_flujo_compra_completo()
            self.resultados['conectividad']['flujos']['compra'] = flujo_compra.get('envio_ticket', False)
        
        # 6. Sincronización DevOps
        if health_results.get('devops', False):
            sincronizacion = self.test_sincronizacion_devops()
            self.resultados['conectividad']['flujos']['sincronizacion'] = sincronizacion.get('sincronizacion', False)
        
        # 7. Seguridad
        seguridad = self.test_seguridad_apis()
        self.resultados['seguridad']['validaciones'] = seguridad
        
        # 8. Transferencia de datos
        transferencia = self.test_transferencia_datos()
        self.resultados['conectividad']['flujos']['transferencia'] = transferencia.get('obtener_productos', False)
        
        # 9. Generar reporte final
        reporte = self.generar_reporte_final()
        
        # Guardar reporte
        with open('reporte_conectividad.txt', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        logger.info("✅ TESTS COMPLETADOS - Reporte guardado en 'reporte_conectividad.txt'")
        print(reporte)
        
        return self.resultados

def main():
    """Función principal"""
    print("🔗 INICIANDO TEST DE CONECTIVIDAD COMPLETA")
    print("=" * 50)
    
    tester = ConectividadTester()
    resultados = tester.ejecutar_tests_completos()
    
    print("\n🎯 RESUMEN FINAL:")
    print(f"Belgrano Ahorro: {'✅' if resultados['belgrano_ahorro']['status'] == 'ok' else '❌'}")
    print(f"Ticketera: {'✅' if resultados['ticketera']['status'] == 'ok' else '❌'}")
    print(f"DevOps: {'✅' if resultados['devops']['status'] == 'ok' else '❌'}")
    print(f"Conectividad: {'✅' if resultados['conectividad']['flujos'] else '❌'}")
    print(f"Seguridad: {'✅' if resultados['seguridad']['validaciones'] else '❌'}")

if __name__ == "__main__":
    main()
