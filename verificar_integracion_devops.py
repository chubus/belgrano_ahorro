#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación de Integración DevOps
Verifica que todos los componentes estén funcionando correctamente
"""

import os
import sys
import json
import requests
import sqlite3
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsIntegrationChecker:
    """Verificador de integración DevOps"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system': 'DevOps Integration Check',
            'version': '1.0.0',
            'checks': {},
            'summary': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
        # Configuración
        self.config = {
            'devops_url': 'http://localhost:5000',
            'api_url': 'https://belgranoahorro-aliq.onrender.com',
            'api_key': 'belgrano_ahorro_api_key_2025',
            'db_path': 'belgrano_ahorro.db'
        }
    
    def check_files_exist(self):
        """Verificar que todos los archivos necesarios existan"""
        logger.info("🔍 Verificando archivos del sistema...")
        
        required_files = [
            'devops_routes.py',
            'api_belgrano_ahorro.py', 
            'belgrano_client.py',
            'README_INTEGRACION.md',
            'templates/devops/base.html',
            'templates/devops/login.html',
            'templates/devops/dashboard.html',
            'templates/devops/negocios.html',
            'templates/devops/sucursales.html',
            'templates/devops/productos.html',
            'templates/devops/ofertas.html',
            'templates/devops/precios.html'
        ]
        
        file_checks = {}
        for file_path in required_files:
            exists = os.path.exists(file_path)
            file_checks[file_path] = {
                'status': 'ok' if exists else 'error',
                'exists': exists
            }
        
        self.results['checks']['files'] = file_checks
        return file_checks
    
    def check_database_structure(self):
        """Verificar estructura de base de datos"""
        logger.info("🔍 Verificando estructura de base de datos...")
        
        db_checks = {}
        
        try:
            if os.path.exists(self.config['db_path']):
                conn = sqlite3.connect(self.config['db_path'])
                cursor = conn.cursor()
                
                # Verificar tablas requeridas
                required_tables = ['negocios', 'sucursales', 'productos', 'ofertas', 'precios_historial']
                
                for table in required_tables:
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    exists = cursor.fetchone() is not None
                    
                    db_checks[table] = {
                        'status': 'ok' if exists else 'error',
                        'exists': exists
                    }
                
                conn.close()
            else:
                for table in ['negocios', 'sucursales', 'productos', 'ofertas', 'precios_historial']:
                    db_checks[table] = {
                        'status': 'error',
                        'exists': False,
                        'error': 'Database file not found'
                    }
        
        except Exception as e:
            logger.error(f"Error checking database: {e}")
            db_checks['error'] = str(e)
        
        self.results['checks']['database'] = db_checks
        return db_checks
    
    def check_api_endpoints(self):
        """Verificar endpoints de API"""
        logger.info("🔍 Verificando endpoints de API...")
        
        endpoints_to_check = [
            '/api/health',
            '/api/status',
            '/api/negocios',
            '/api/sucursales',
            '/api/productos',
            '/api/ofertas',
            '/api/precios'
        ]
        
        endpoint_checks = {}
        
        for endpoint in endpoints_to_check:
            try:
                url = f"{self.config['api_url']}{endpoint}"
                headers = {'Authorization': f'Bearer {self.config['api_key']}'}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                endpoint_checks[endpoint] = {
                    'status': 'ok' if response.status_code == 200 else 'warning',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
                
            except requests.exceptions.ConnectionError:
                endpoint_checks[endpoint] = {
                    'status': 'error',
                    'error': 'Connection failed'
                }
            except requests.exceptions.Timeout:
                endpoint_checks[endpoint] = {
                    'status': 'warning',
                    'error': 'Timeout'
                }
            except Exception as e:
                endpoint_checks[endpoint] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.results['checks']['api_endpoints'] = endpoint_checks
        return endpoint_checks
    
    def check_devops_routes(self):
        """Verificar rutas de DevOps"""
        logger.info("🔍 Verificando rutas de DevOps...")
        
        devops_routes = [
            '/devops/',
            '/devops/login',
            '/devops/negocios',
            '/devops/sucursales',
            '/devops/productos',
            '/devops/ofertas',
            '/devops/precios'
        ]
        
        route_checks = {}
        
        for route in devops_routes:
            try:
                url = f"{self.config['devops_url']}{route}"
                response = requests.get(url, timeout=5)
                
                route_checks[route] = {
                    'status': 'ok' if response.status_code == 200 else 'warning',
                    'status_code': response.status_code
                }
                
            except requests.exceptions.ConnectionError:
                route_checks[route] = {
                    'status': 'error',
                    'error': 'DevOps server not running'
                }
            except Exception as e:
                route_checks[route] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.results['checks']['devops_routes'] = route_checks
        return route_checks
    
    def check_templates(self):
        """Verificar templates HTML"""
        logger.info("🔍 Verificando templates HTML...")
        
        template_files = [
            'templates/devops/base.html',
            'templates/devops/login.html',
            'templates/devops/dashboard.html',
            'templates/devops/negocios.html',
            'templates/devops/sucursales.html',
            'templates/devops/productos.html',
            'templates/devops/ofertas.html',
            'templates/devops/precios.html'
        ]
        
        template_checks = {}
        
        for template in template_files:
            try:
                if os.path.exists(template):
                    with open(template, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar elementos básicos
                    has_doctype = '<!DOCTYPE html>' in content
                    has_title = '<title>' in content
                    has_bootstrap = 'bootstrap' in content.lower()
                    
                    template_checks[template] = {
                        'status': 'ok' if has_doctype and has_title else 'warning',
                        'has_doctype': has_doctype,
                        'has_title': has_title,
                        'has_bootstrap': has_bootstrap,
                        'size_bytes': len(content)
                    }
                else:
                    template_checks[template] = {
                        'status': 'error',
                        'exists': False
                    }
            except Exception as e:
                template_checks[template] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.results['checks']['templates'] = template_checks
        return template_checks
    
    def check_client_functionality(self):
        """Verificar funcionalidad del cliente"""
        logger.info("🔍 Verificando funcionalidad del cliente...")
        
        try:
            from belgrano_client import BelgranoAhorroClient, test_connection
            
            # Verificar que el cliente se puede instanciar
            client = BelgranoAhorroClient()
            
            # Verificar métodos disponibles
            methods = [
                'get_negocios', 'create_negocio', 'update_negocio', 'delete_negocio',
                'get_sucursales', 'create_sucursal', 'update_sucursal', 'delete_sucursal',
                'get_productos', 'create_producto', 'update_producto', 'delete_producto',
                'get_ofertas', 'create_oferta', 'update_oferta', 'delete_oferta',
                'get_precios', 'update_precio', 'health_check', 'get_status'
            ]
            
            method_checks = {}
            for method in methods:
                has_method = hasattr(client, method)
                method_checks[method] = {
                    'status': 'ok' if has_method else 'error',
                    'exists': has_method
                }
            
            # Test de conexión
            connection_test = test_connection()
            
            client_checks = {
                'methods': method_checks,
                'connection_test': {
                    'status': 'ok' if connection_test else 'warning',
                    'success': connection_test
                }
            }
            
        except Exception as e:
            client_checks = {
                'status': 'error',
                'error': str(e)
            }
        
        self.results['checks']['client'] = client_checks
        return client_checks
    
    def calculate_summary(self):
        """Calcular resumen de verificaciones"""
        total_checks = 0
        passed = 0
        failed = 0
        warnings = 0
        
        for category, checks in self.results['checks'].items():
            if isinstance(checks, dict):
                for check_name, check_result in checks.items():
                    if isinstance(check_result, dict) and 'status' in check_result:
                        total_checks += 1
                        status = check_result['status']
                        
                        if status == 'ok':
                            passed += 1
                        elif status == 'warning':
                            warnings += 1
                        else:
                            failed += 1
        
        self.results['summary'] = {
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'success_rate': round((passed / total_checks * 100) if total_checks > 0 else 0, 2)
        }
    
    def generate_report(self):
        """Generar reporte completo"""
        logger.info("📊 Generando reporte de integración...")
        
        # Ejecutar todas las verificaciones
        self.check_files_exist()
        self.check_database_structure()
        self.check_api_endpoints()
        self.check_devops_routes()
        self.check_templates()
        self.check_client_functionality()
        
        # Calcular resumen
        self.calculate_summary()
        
        return self.results
    
    def print_summary(self):
        """Imprimir resumen en consola"""
        print("\n" + "="*70)
        print("🔧 VERIFICACIÓN DE INTEGRACIÓN DEVOPS - BELGRANO TICKETS")
        print("="*70)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Sistema: {self.results['system']} v{self.results['version']}")
        print(f"📊 Verificaciones: {self.results['summary']['total_checks']}")
        print(f"✅ Exitosas: {self.results['summary']['passed']}")
        print(f"⚠️  Advertencias: {self.results['summary']['warnings']}")
        print(f"❌ Fallidas: {self.results['summary']['failed']}")
        print(f"📈 Tasa de éxito: {self.results['summary']['success_rate']}%")
        print("="*70)
        
        # Mostrar detalles por categoría
        for category, checks in self.results['checks'].items():
            print(f"\n📋 {category.upper().replace('_', ' ')}:")
            if isinstance(checks, dict):
                for check_name, check_result in checks.items():
                    if isinstance(check_result, dict) and 'status' in check_result:
                        status_icon = "✅" if check_result['status'] == 'ok' else "⚠️" if check_result['status'] == 'warning' else "❌"
                        print(f"  {status_icon} {check_name}: {check_result['status']}")
                        if 'error' in check_result:
                            print(f"    Error: {check_result['error']}")

def main():
    """Función principal"""
    print("🚀 Iniciando verificación de integración DevOps...")
    
    checker = DevOpsIntegrationChecker()
    results = checker.generate_report()
    
    # Imprimir resumen
    checker.print_summary()
    
    # Guardar reporte en archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reporte_integracion_devops_{timestamp}.json'
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Reporte guardado en: {report_file}")
    except Exception as e:
        print(f"⚠️  Error guardando reporte: {e}")
    
    # Determinar estado general
    success_rate = results['summary']['success_rate']
    if success_rate >= 90:
        print("\n🎉 ¡Integración DevOps funcionando correctamente!")
        return 0
    elif success_rate >= 70:
        print("\n⚠️  Integración DevOps con algunas advertencias")
        return 1
    else:
        print("\n❌ Integración DevOps con problemas críticos")
        return 2

if __name__ == "__main__":
    sys.exit(main())
