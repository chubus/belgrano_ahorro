#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chequeo Integral de Conectividad DevOps - Belgrano Ahorro
Script completo para verificar conectividad, configuración y estado del sistema
"""

import requests
import json
import os
import sys
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DevOpsConnectivityChecker:
    """Verificador integral de conectividad DevOps"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {},
            'configuration': {},
            'recommendations': []
        }
        
        # URLs y configuración
        self.belgrano_url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
        self.belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        self.devops_url = os.environ.get('DEVOPS_URL', 'http://localhost:5002')
        self.ticketera_url = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com')
        
        # Headers para autenticación
        self.headers = {
            'X-API-Key': self.belgrano_api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'DevOps-Connectivity-Checker/1.0'
        }
        
        # Timeouts
        self.timeout = 30
        
    def test_belgrano_ahorro_health(self) -> Dict[str, Any]:
        """Probar salud de Belgrano Ahorro"""
        test_name = "Belgrano Ahorro Health Check"
        logger.info(f"🔍 Probando: {test_name}")
        
        try:
            health_url = f"{self.belgrano_url}/healthz"
            response = requests.get(health_url, timeout=self.timeout)
            
            result = {
                'name': test_name,
                'url': health_url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'success': response.status_code == 200
            }
            
            if result['success']:
                logger.info(f"✅ {test_name}: OK ({result['response_time']:.2f}s)")
                result['message'] = "Servicio respondiendo correctamente"
            else:
                logger.warning(f"❌ {test_name}: Error {response.status_code}")
                result['message'] = f"Error HTTP {response.status_code}"
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"⏰ {test_name}: Timeout")
            return {
                'name': test_name,
                'url': health_url,
                'success': False,
                'error': 'Timeout de conexión',
                'message': 'Servicio no responde en tiempo esperado'
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 {test_name}: Error de conexión")
            return {
                'name': test_name,
                'url': health_url,
                'success': False,
                'error': 'Error de conexión',
                'message': 'No se puede conectar al servicio'
            }
        except Exception as e:
            logger.error(f"💥 {test_name}: Error inesperado - {e}")
            return {
                'name': test_name,
                'url': health_url,
                'success': False,
                'error': str(e),
                'message': 'Error inesperado'
            }
    
    def test_belgrano_ahorro_endpoints(self) -> Dict[str, Any]:
        """Probar endpoints de Belgrano Ahorro"""
        test_name = "Belgrano Ahorro API Endpoints"
        logger.info(f"🔍 Probando: {test_name}")
        
        endpoints = [
            ('/api/v1/productos', 'Productos'),
            ('/api/v1/negocios', 'Negocios'),
            ('/api/v1/ofertas', 'Ofertas'),
            ('/api/v1/sucursales', 'Sucursales'),
            ('/api/v1/precios', 'Precios')
        ]
        
        results = []
        successful = 0
        
        for endpoint, name in endpoints:
            try:
                url = f"{self.belgrano_url}{endpoint}"
                start_time = time.time()
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                response_time = time.time() - start_time
                
                endpoint_result = {
                    'endpoint': endpoint,
                    'name': name,
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200
                }
                
                if endpoint_result['success']:
                    # Intentar obtener datos
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            endpoint_result['data_count'] = len(data)
                        elif isinstance(data, dict) and 'data' in data:
                            endpoint_result['data_count'] = len(data.get('data', []))
                        else:
                            endpoint_result['data_count'] = 0
                    except:
                        endpoint_result['data_count'] = 0
                    
                    successful += 1
                    logger.info(f"✅ {name}: OK ({response_time:.2f}s) - {endpoint_result['data_count']} items")
                else:
                    logger.warning(f"❌ {name}: Error {response.status_code}")
                    endpoint_result['error'] = f"HTTP {response.status_code}"
                
                results.append(endpoint_result)
                
            except requests.exceptions.Timeout:
                logger.error(f"⏰ {name}: Timeout")
                results.append({
                    'endpoint': endpoint,
                    'name': name,
                    'url': url,
                    'success': False,
                    'error': 'Timeout'
                })
            except requests.exceptions.ConnectionError:
                logger.error(f"🔌 {name}: Error de conexión")
                results.append({
                    'endpoint': endpoint,
                    'name': name,
                    'url': url,
                    'success': False,
                    'error': 'Connection Error'
                })
            except Exception as e:
                logger.error(f"💥 {name}: Error - {e}")
                results.append({
                    'endpoint': endpoint,
                    'name': name,
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'name': test_name,
            'success': successful == len(endpoints),
            'successful_endpoints': successful,
            'total_endpoints': len(endpoints),
            'success_rate': f"{successful}/{len(endpoints)}",
            'endpoints': results,
            'message': f"{successful}/{len(endpoints)} endpoints funcionando correctamente"
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Probar conectividad a base de datos"""
        test_name = "Base de Datos Belgrano Ahorro"
        logger.info(f"🔍 Probando: {test_name}")
        
        db_path = 'belgrano_ahorro.db'
        
        try:
            if not os.path.exists(db_path):
                return {
                    'name': test_name,
                    'success': False,
                    'error': 'Archivo de base de datos no encontrado',
                    'message': f'Base de datos no existe: {db_path}'
                }
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener información de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Contar registros en cada tabla
            table_counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except Exception as e:
                    table_counts[table] = f"Error: {e}"
            
            conn.close()
            
            logger.info(f"✅ {test_name}: Base de datos accesible")
            for table, count in table_counts.items():
                logger.info(f"   📊 {table}: {count} registros")
            
            return {
                'name': test_name,
                'success': True,
                'database_path': db_path,
                'tables': tables,
                'table_counts': table_counts,
                'message': f"Base de datos accesible con {len(tables)} tablas"
            }
            
        except Exception as e:
            logger.error(f"❌ {test_name}: Error - {e}")
            return {
                'name': test_name,
                'success': False,
                'error': str(e),
                'message': 'Error accediendo a base de datos'
            }
    
    def test_devops_configuration(self) -> Dict[str, Any]:
        """Probar configuración de DevOps"""
        test_name = "Configuración DevOps"
        logger.info(f"🔍 Probando: {test_name}")
        
        # Verificar archivos de configuración
        config_files = [
            'config_devops.py',
            'devops_routes.py',
            'devops_belgrano_manager_unified.py',
            'config_devops.env'
        ]
        
        existing_files = []
        for file in config_files:
            if os.path.exists(file):
                existing_files.append(file)
        
        # Verificar variables de entorno
        env_vars = [
            'BELGRANO_AHORRO_URL',
            'BELGRANO_AHORRO_API_KEY',
            'DEVOPS_USERNAME',
            'DEVOPS_PASSWORD'
        ]
        
        configured_vars = []
        for var in env_vars:
            if os.environ.get(var):
                configured_vars.append(var)
        
        # Verificar configuración actual
        config_status = {
            'belgrano_url': self.belgrano_url,
            'belgrano_api_key': '***' if self.belgrano_api_key else 'No configurada',
            'devops_url': self.devops_url,
            'ticketera_url': self.ticketera_url
        }
        
        success = len(existing_files) >= 3 and len(configured_vars) >= 2
        
        logger.info(f"✅ {test_name}: {'OK' if success else 'Parcial'}")
        logger.info(f"   📁 Archivos: {len(existing_files)}/{len(config_files)}")
        logger.info(f"   🔧 Variables: {len(configured_vars)}/{len(env_vars)}")
        
        return {
            'name': test_name,
            'success': success,
            'config_files_found': len(existing_files),
            'config_files_total': len(config_files),
            'env_vars_configured': len(configured_vars),
            'env_vars_total': len(env_vars),
            'existing_files': existing_files,
            'configured_vars': configured_vars,
            'current_config': config_status,
            'message': f"Configuración {'completa' if success else 'parcial'}"
        }
    
    def test_api_communication(self) -> Dict[str, Any]:
        """Probar comunicación entre APIs"""
        test_name = "Comunicación API DevOps-Belgrano"
        logger.info(f"🔍 Probando: {test_name}")
        
        try:
            # Probar endpoint de productos (más confiable)
            url = f"{self.belgrano_url}/api/v1/productos"
            start_time = time.time()
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        productos = data
                    elif isinstance(data, dict) and 'data' in data:
                        productos = data.get('data', [])
                    else:
                        productos = []
                    
                    logger.info(f"✅ {test_name}: Comunicación exitosa")
                    logger.info(f"   📦 Productos disponibles: {len(productos)}")
                    logger.info(f"   ⏱️ Tiempo de respuesta: {response_time:.2f}s")
                    
                    return {
                        'name': test_name,
                        'success': True,
                        'url': url,
                        'response_time': response_time,
                        'productos_count': len(productos),
                        'status_code': response.status_code,
                        'message': f"Comunicación exitosa - {len(productos)} productos disponibles"
                    }
                except Exception as e:
                    logger.warning(f"⚠️ {test_name}: Error procesando respuesta - {e}")
                    return {
                        'name': test_name,
                        'success': False,
                        'url': url,
                        'error': f"Error procesando respuesta: {e}",
                        'message': "Comunicación establecida pero error en datos"
                    }
            else:
                logger.error(f"❌ {test_name}: Error HTTP {response.status_code}")
                return {
                    'name': test_name,
                    'success': False,
                    'url': url,
                    'status_code': response.status_code,
                    'error': f"HTTP {response.status_code}",
                    'message': f"Error en comunicación: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ {test_name}: Timeout")
            return {
                'name': test_name,
                'success': False,
                'error': 'Timeout',
                'message': 'Timeout en comunicación API'
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 {test_name}: Error de conexión")
            return {
                'name': test_name,
                'success': False,
                'error': 'Connection Error',
                'message': 'Error de conexión con API'
            }
        except Exception as e:
            logger.error(f"💥 {test_name}: Error inesperado - {e}")
            return {
                'name': test_name,
                'success': False,
                'error': str(e),
                'message': 'Error inesperado en comunicación'
            }
    
    def test_ticketera_connectivity(self) -> Dict[str, Any]:
        """Probar conectividad con Ticketera"""
        test_name = "Ticketera Connectivity"
        logger.info(f"🔍 Probando: {test_name}")
        
        try:
            # Probar endpoint de salud de ticketera
            health_url = f"{self.ticketera_url}/health"
            response = requests.get(health_url, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info(f"✅ {test_name}: Ticketera accesible")
                return {
                    'name': test_name,
                    'success': True,
                    'url': health_url,
                    'status_code': response.status_code,
                    'message': 'Ticketera accesible'
                }
            else:
                logger.warning(f"⚠️ {test_name}: Ticketera responde con código {response.status_code}")
                return {
                    'name': test_name,
                    'success': False,
                    'url': health_url,
                    'status_code': response.status_code,
                    'message': f'Ticketera responde con código {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ {test_name}: Timeout - Ticketera no disponible")
            return {
                'name': test_name,
                'success': False,
                'error': 'Timeout',
                'message': 'Ticketera no responde (timeout)'
            }
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 {test_name}: Error de conexión - Ticketera no disponible")
            return {
                'name': test_name,
                'success': False,
                'error': 'Connection Error',
                'message': 'Ticketera no disponible'
            }
        except Exception as e:
            logger.warning(f"⚠️ {test_name}: Error - {e}")
            return {
                'name': test_name,
                'success': False,
                'error': str(e),
                'message': f'Error accediendo a Ticketera: {e}'
            }
    
    def generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Analizar resultados
        failed_tests = [test for test in self.results['tests'] if not test.get('success', False)]
        partial_tests = [test for test in self.results['tests'] if test.get('success') is None]
        
        if failed_tests:
            recommendations.append("🔧 Revisar servicios con fallos de conectividad")
        
        # Verificar configuración
        config_test = next((test for test in self.results['tests'] if test['name'] == 'Configuración DevOps'), None)
        if config_test and config_test.get('env_vars_configured', 0) < 2:
            recommendations.append("⚙️ Configurar variables de entorno para producción")
        
        # Verificar endpoints
        endpoints_test = next((test for test in self.results['tests'] if test['name'] == 'Belgrano Ahorro API Endpoints'), None)
        if endpoints_test and endpoints_test.get('successful_endpoints', 0) < endpoints_test.get('total_endpoints', 1):
            recommendations.append("🔍 Revisar endpoints con errores en Belgrano Ahorro")
        
        # Verificar base de datos
        db_test = next((test for test in self.results['tests'] if test['name'] == 'Base de Datos Belgrano Ahorro'), None)
        if not db_test or not db_test.get('success', False):
            recommendations.append("🗄️ Verificar integridad de la base de datos")
        
        # Recomendaciones generales
        recommendations.extend([
            "📊 Implementar monitoreo continuo de conectividad",
            "🔒 Revisar y rotar credenciales periódicamente",
            "📝 Documentar procedimientos de recuperación",
            "🚨 Configurar alertas para fallos de conectividad"
        ])
        
        return recommendations
    
    def run_all_tests(self) -> str:
        """Ejecutar todos los tests de conectividad"""
        print("=" * 80)
        print("🔗 CHEQUEO INTEGRAL DE CONECTIVIDAD DEVOPS - BELGRANO AHORRO")
        print("=" * 80)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Belgrano Ahorro: {self.belgrano_url}")
        print(f"🔧 DevOps: {self.devops_url}")
        print(f"🎫 Ticketera: {self.ticketera_url}")
        print()
        
        # Ejecutar tests
        tests = [
            self.test_belgrano_ahorro_health,
            self.test_belgrano_ahorro_endpoints,
            self.test_database_connectivity,
            self.test_devops_configuration,
            self.test_api_communication,
            self.test_ticketera_connectivity
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                result = test_func()
                self.results['tests'].append(result)
                
                if result.get('success', False):
                    passed += 1
                    
            except Exception as e:
                logger.error(f"💥 Error ejecutando test: {e}")
                self.results['tests'].append({
                    'name': test_func.__name__,
                    'success': False,
                    'error': str(e),
                    'message': 'Error ejecutando test'
                })
            print()
        
        # Generar resumen
        success_rate = (passed / total) * 100
        
        self.results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': success_rate,
            'status': self._determine_status(success_rate)
        }
        
        # Generar recomendaciones
        self.results['recommendations'] = self.generate_recommendations()
        
        # Mostrar resumen
        print("=" * 80)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 80)
        print(f"🧪 Tests ejecutados: {total}")
        print(f"✅ Tests exitosos: {passed}")
        print(f"❌ Tests fallidos: {total - passed}")
        print(f"📈 Porcentaje de éxito: {success_rate:.1f}%")
        print(f"🎯 Estado general: {self.results['summary']['status']}")
        
        if self.results['recommendations']:
            print("\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        return self.results['summary']['status']
    
    def _determine_status(self, success_rate: float) -> str:
        """Determinar estado basado en porcentaje de éxito"""
        if success_rate >= 90:
            return "EXCELENTE"
        elif success_rate >= 80:
            return "BUENO"
        elif success_rate >= 60:
            return "ACEPTABLE"
        elif success_rate >= 40:
            return "PROBLEMÁTICO"
        else:
            return "CRÍTICO"
    
    def save_report(self) -> str:
        """Guardar reporte detallado"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reporte_conectividad_integral_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Reporte guardado en: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Error guardando reporte: {e}")
            return ""

def main():
    """Función principal"""
    try:
        checker = DevOpsConnectivityChecker()
        status = checker.run_all_tests()
        report_file = checker.save_report()
        
        print(f"\n📄 Reporte detallado guardado en: {report_file}")
        
        # Código de salida basado en el estado
        if status in ["EXCELENTE", "BUENO"]:
            return 0
        elif status == "ACEPTABLE":
            return 1
        else:
            return 2
            
    except Exception as e:
        logger.error(f"💥 Error ejecutando chequeo: {e}")
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

