#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba completo para DevOps - Belgrano Ahorro
Verifica conectividad, funcionalidad y sincronización
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DevOpsCompleteTester:
    """Tester completo para DevOps - Belgrano Ahorro"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.devops_url = "http://localhost:5002"
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'unknown',
            'errors': [],
            'warnings': []
        }
    
    def test_devops_manager(self):
        """Probar gestor DevOps unificado"""
        logger.info("🧪 PROBANDO GESTOR DEVOPS UNIFICADO...")
        
        try:
            from devops_belgrano_manager_unified import devops_manager_unified
            
            # Probar inicialización
            if devops_manager_unified:
                logger.info("✅ Gestor DevOps unificado inicializado")
                
                # Probar conectividad
                connectivity = devops_manager_unified.test_connectivity()
                
                self.results['tests']['devops_manager'] = {
                    'status': 'success',
                    'connectivity': connectivity,
                    'fallback_mode': devops_manager_unified.fallback_mode
                }
                
                logger.info(f"📊 Conectividad: {connectivity['overall_status']}")
                return True
            else:
                logger.error("❌ Gestor DevOps no inicializado")
                self.results['tests']['devops_manager'] = {
                    'status': 'error',
                    'error': 'Gestor no inicializado'
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Error probando gestor DevOps: {e}")
            self.results['tests']['devops_manager'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def test_belgrano_ahorro_endpoints(self):
        """Probar endpoints de Belgrano Ahorro"""
        logger.info("🧪 PROBANDO ENDPOINTS DE BELGRANO AHORRO...")
        
        endpoints = [
            ('/healthz', 'Health Check'),
            ('/api/v1/negocios', 'Negocios'),
            ('/api/v1/productos', 'Productos'),
            ('/api/v1/sucursales', 'Sucursales'),
            ('/api/v1/ofertas', 'Ofertas'),
            ('/api/tickets', 'Tickets')
        ]
        
        results = {}
        successful = 0
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    results[endpoint] = {
                        'status': 'success',
                        'name': name,
                        'response_time': response.elapsed.total_seconds()
                    }
                    successful += 1
                    logger.info(f"✅ {name}: OK")
                elif response.status_code == 302:
                    results[endpoint] = {
                        'status': 'redirect',
                        'name': name,
                        'message': 'Redirigido a login'
                    }
                    logger.warning(f"⚠️ {name}: Redirigido (302)")
                else:
                    results[endpoint] = {
                        'status': 'error',
                        'name': name,
                        'status_code': response.status_code
                    }
                    logger.error(f"❌ {name}: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                results[endpoint] = {
                    'status': 'error',
                    'name': name,
                    'error': 'No se puede conectar'
                }
                logger.error(f"❌ {name}: No se puede conectar")
            except Exception as e:
                results[endpoint] = {
                    'status': 'error',
                    'name': name,
                    'error': str(e)
                }
                logger.error(f"❌ {name}: {e}")
        
        self.results['tests']['belgrano_endpoints'] = {
            'status': 'success' if successful > 0 else 'error',
            'successful': successful,
            'total': len(endpoints),
            'endpoints': results
        }
        
        return successful > 0
    
    def test_devops_routes(self):
        """Probar rutas de DevOps"""
        logger.info("🧪 PROBANDO RUTAS DE DEVOPS...")
        
        # Primero verificar si DevOps está ejecutándose
        try:
            response = requests.get(f"{self.devops_url}/devops/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ DevOps está ejecutándose")
            else:
                logger.warning(f"⚠️ DevOps responde con {response.status_code}")
        except:
            logger.warning("⚠️ DevOps no está ejecutándose - probando rutas locales")
            # Probar rutas locales si DevOps no está ejecutándose
            return self.test_local_devops_routes()
        
        # Probar rutas específicas de DevOps
        devops_routes = [
            ('/devops/health', 'Health Check'),
            ('/devops/status', 'Status'),
            ('/devops/system-status', 'System Status'),
            ('/devops/conectar-belgrano', 'Conectar Belgrano')
        ]
        
        results = {}
        successful = 0
        
        for route, name in devops_routes:
            try:
                response = requests.get(f"{self.devops_url}{route}", timeout=10)
                
                if response.status_code == 200:
                    results[route] = {
                        'status': 'success',
                        'name': name
                    }
                    successful += 1
                    logger.info(f"✅ {name}: OK")
                else:
                    results[route] = {
                        'status': 'error',
                        'name': name,
                        'status_code': response.status_code
                    }
                    logger.error(f"❌ {name}: {response.status_code}")
                    
            except Exception as e:
                results[route] = {
                    'status': 'error',
                    'name': name,
                    'error': str(e)
                }
                logger.error(f"❌ {name}: {e}")
        
        self.results['tests']['devops_routes'] = {
            'status': 'success' if successful > 0 else 'error',
            'successful': successful,
            'total': len(devops_routes),
            'routes': results
        }
        
        return successful > 0
    
    def test_local_devops_routes(self):
        """Probar rutas DevOps locales (importando directamente)"""
        logger.info("🧪 PROBANDO RUTAS DEVOPS LOCALES...")
        
        try:
            # Importar y probar el gestor directamente
            from devops_belgrano_manager_unified import devops_manager_unified
            
            # Probar operaciones CRUD
            test_data = {
                'nombre': 'Test Producto',
                'descripcion': 'Producto de prueba',
                'precio': 100.0,
                'activo': True
            }
            
            # Probar creación
            success, message = devops_manager_unified.create_producto(test_data)
            
            if success:
                logger.info("✅ Creación de producto: OK")
                self.results['tests']['local_devops'] = {
                    'status': 'success',
                    'create_test': 'passed',
                    'message': message
                }
                return True
            else:
                logger.error(f"❌ Creación de producto: {message}")
                self.results['tests']['local_devops'] = {
                    'status': 'error',
                    'create_test': 'failed',
                    'message': message
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Error probando DevOps local: {e}")
            self.results['tests']['local_devops'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def test_crud_operations(self):
        """Probar operaciones CRUD completas"""
        logger.info("🧪 PROBANDO OPERACIONES CRUD...")
        
        try:
            from devops_belgrano_manager_unified import devops_manager_unified
            
            # Datos de prueba
            test_negocio = {
                'nombre': 'Negocio Test',
                'descripcion': 'Negocio de prueba',
                'direccion': 'Calle Test 123',
                'telefono': '+54 11 1234-5678',
                'email': 'test@negocio.com',
                'activo': True
            }
            
            test_producto = {
                'nombre': 'Producto Test',
                'descripcion': 'Producto de prueba',
                'precio': 500.0,
                'categoria': 'Test',
                'negocio': 'Negocio Test',
                'activo': True
            }
            
            test_oferta = {
                'titulo': 'Oferta Test',
                'descripcion': 'Oferta de prueba',
                'descuento': 20,
                'fecha_inicio': '2025-01-19',
                'fecha_fin': '2025-01-31',
                'activa': True
            }
            
            # Probar operaciones
            operations = []
            
            # Crear negocio
            success, message = devops_manager_unified.create_negocio(test_negocio)
            operations.append(('create_negocio', success, message))
            
            # Crear producto
            success, message = devops_manager_unified.create_producto(test_producto)
            operations.append(('create_producto', success, message))
            
            # Crear oferta
            success, message = devops_manager_unified.create_oferta(test_oferta)
            operations.append(('create_oferta', success, message))
            
            # Obtener datos
            negocios = devops_manager_unified.get_negocios()
            productos = devops_manager_unified.get_productos()
            ofertas = devops_manager_unified.get_ofertas()
            
            operations.append(('get_negocios', len(negocios) > 0, f"{len(negocios)} negocios"))
            operations.append(('get_productos', len(productos) > 0, f"{len(productos)} productos"))
            operations.append(('get_ofertas', len(ofertas) > 0, f"{len(ofertas)} ofertas"))
            
            # Contar operaciones exitosas
            successful_ops = sum(1 for _, success, _ in operations if success)
            total_ops = len(operations)
            
            self.results['tests']['crud_operations'] = {
                'status': 'success' if successful_ops == total_ops else 'partial',
                'successful': successful_ops,
                'total': total_ops,
                'operations': operations
            }
            
            logger.info(f"📊 Operaciones CRUD: {successful_ops}/{total_ops} exitosas")
            return successful_ops == total_ops
            
        except Exception as e:
            logger.error(f"❌ Error probando operaciones CRUD: {e}")
            self.results['tests']['crud_operations'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def generate_report(self):
        """Generar reporte completo"""
        logger.info("📋 GENERANDO REPORTE COMPLETO...")
        
        # Determinar estado general
        test_results = [test.get('status') for test in self.results['tests'].values()]
        
        if all(status == 'success' for status in test_results):
            self.results['overall_status'] = 'success'
        elif any(status == 'success' for status in test_results):
            self.results['overall_status'] = 'partial'
        else:
            self.results['overall_status'] = 'error'
        
        # Generar reporte
        print("=" * 80)
        print("📋 REPORTE COMPLETO: DEVOPS - BELGRANO AHORRO")
        print("=" * 80)
        print(f"Fecha: {self.results['timestamp']}")
        print(f"Estado General: {self.results['overall_status'].upper()}")
        
        print("\n🔍 RESULTADOS DE PRUEBAS:")
        for test_name, test_result in self.results['tests'].items():
            status = test_result.get('status', 'unknown')
            status_icon = "✅" if status == 'success' else "⚠️" if status == 'partial' else "❌"
            print(f"   {status_icon} {test_name}: {status}")
        
        print("\n📊 RESUMEN:")
        total_tests = len(self.results['tests'])
        successful_tests = sum(1 for test in self.results['tests'].values() if test.get('status') == 'success')
        print(f"   Tests exitosos: {successful_tests}/{total_tests}")
        
        if self.results['overall_status'] == 'success':
            print("\n✅ SISTEMA COMPLETAMENTE FUNCIONAL")
        elif self.results['overall_status'] == 'partial':
            print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        else:
            print("\n❌ SISTEMA CON PROBLEMAS")
        
        print("\n" + "=" * 80)
        
        # Guardar reporte
        with open(f"reporte_devops_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return self.results
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        logger.info("🚀 INICIANDO PRUEBAS COMPLETAS DE DEVOPS...")
        
        # Ejecutar pruebas
        self.test_devops_manager()
        self.test_belgrano_ahorro_endpoints()
        self.test_devops_routes()
        self.test_crud_operations()
        
        # Generar reporte
        return self.generate_report()

if __name__ == "__main__":
    tester = DevOpsCompleteTester()
    results = tester.run_all_tests()
    
    # Mostrar resumen final
    if results['overall_status'] == 'success':
        print("\n🎉 TODAS LAS PRUEBAS PASARON - SISTEMA COMPLETAMENTE FUNCIONAL")
    elif results['overall_status'] == 'partial':
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON - SISTEMA PARCIALMENTE FUNCIONAL")
    else:
        print("\n❌ MUCHAS PRUEBAS FALLARON - SISTEMA REQUIERE ATENCIÓN")
