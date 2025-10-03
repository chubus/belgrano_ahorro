#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Chequeo de Conectividad DevOps - Belgrano Tickets
Verifica la conectividad y estado de todos los componentes DevOps
"""

import os
import sys
import json
import requests
import sqlite3
import time
from datetime import datetime
from urllib.parse import urljoin
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DevOpsConnectivityChecker:
    """Verificador de conectividad DevOps para Belgrano Tickets"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system': 'DevOps Belgrano Tickets',
            'version': '2.0.0',
            'checks': {},
            'summary': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
        # Configuración DevOps
        self.devops_config = {
            'username': os.environ.get('DEVOPS_USERNAME', 'devops'),
            'password': os.environ.get('DEVOPS_PASSWORD', 'DevOps2025!Secure'),
            'belgrano_ahorro_url': os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com'),
            'api_key': os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025'),
            'tickets_db': os.environ.get('TICKETS_DB_PATH', 'belgrano_tickets.db'),
            'ahorro_db': os.environ.get('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        }
        
        # URLs de prueba
        self.test_urls = {
            'devops_login': 'http://localhost:5000/devops/login',
            'devops_panel': 'http://localhost:5000/devops/',
            'devops_health': 'http://localhost:5000/devops/health',
            'devops_status': 'http://localhost:5000/devops/status',
            'devops_test': 'http://localhost:5000/devops/test',
            'belgrano_ahorro': self.devops_config['belgrano_ahorro_url']
        }
    
    def check_database_connectivity(self):
        """Verificar conectividad de bases de datos"""
        logger.info("🔍 Verificando conectividad de bases de datos...")
        
        db_checks = {
            'tickets_db': {'status': 'unknown', 'details': {}},
            'ahorro_db': {'status': 'unknown', 'details': {}}
        }
        
        # Verificar base de datos de tickets
        try:
            if os.path.exists(self.devops_config['tickets_db']):
                conn = sqlite3.connect(self.devops_config['tickets_db'])
                cursor = conn.cursor()
                
                # Verificar tablas principales
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Verificar tabla ticket
                if 'ticket' in tables:
                    cursor.execute("SELECT COUNT(*) FROM ticket")
                    ticket_count = cursor.fetchone()[0]
                    db_checks['tickets_db'] = {
                        'status': 'connected',
                        'details': {
                            'tables': tables,
                            'ticket_count': ticket_count,
                            'file_size': os.path.getsize(self.devops_config['tickets_db'])
                        }
                    }
                else:
                    db_checks['tickets_db'] = {
                        'status': 'warning',
                        'details': {'error': 'Tabla ticket no encontrada'}
                    }
                
                conn.close()
            else:
                db_checks['tickets_db'] = {
                    'status': 'error',
                    'details': {'error': 'Archivo de base de datos no encontrado'}
                }
        except Exception as e:
            db_checks['tickets_db'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
        
        # Verificar base de datos de ahorro
        try:
            if os.path.exists(self.devops_config['ahorro_db']):
                conn = sqlite3.connect(self.devops_config['ahorro_db'])
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                db_checks['ahorro_db'] = {
                    'status': 'connected',
                    'details': {
                        'tables': tables,
                        'file_size': os.path.getsize(self.devops_config['ahorro_db'])
                    }
                }
                
                conn.close()
            else:
                db_checks['ahorro_db'] = {
                    'status': 'warning',
                    'details': {'error': 'Archivo de base de datos no encontrado'}
                }
        except Exception as e:
            db_checks['ahorro_db'] = {
                'status': 'error',
                'details': {'error': str(e)}
            }
        
        self.results['checks']['database'] = db_checks
        return db_checks
    
    def check_devops_endpoints(self):
        """Verificar endpoints de DevOps"""
        logger.info("🔍 Verificando endpoints de DevOps...")
        
        endpoint_checks = {}
        
        for name, url in self.test_urls.items():
            if 'localhost' in url:
                try:
                    response = requests.get(url, timeout=10)
                    endpoint_checks[name] = {
                        'status': 'connected' if response.status_code == 200 else 'warning',
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds(),
                        'url': url
                    }
                except requests.exceptions.ConnectionError:
                    endpoint_checks[name] = {
                        'status': 'error',
                        'error': 'No se puede conectar al servidor',
                        'url': url
                    }
                except requests.exceptions.Timeout:
                    endpoint_checks[name] = {
                        'status': 'warning',
                        'error': 'Timeout de conexión',
                        'url': url
                    }
                except Exception as e:
                    endpoint_checks[name] = {
                        'status': 'error',
                        'error': str(e),
                        'url': url
                    }
            else:
                # Para URLs externas, solo verificar conectividad básica
                try:
                    response = requests.get(url, timeout=5)
                    endpoint_checks[name] = {
                        'status': 'connected' if response.status_code == 200 else 'warning',
                        'status_code': response.status_code,
                        'url': url
                    }
                except Exception as e:
                    endpoint_checks[name] = {
                        'status': 'error',
                        'error': str(e),
                        'url': url
                    }
        
        self.results['checks']['endpoints'] = endpoint_checks
        return endpoint_checks
    
    def check_devops_authentication(self):
        """Verificar autenticación DevOps"""
        logger.info("🔍 Verificando autenticación DevOps...")
        
        auth_checks = {
            'login_page': {'status': 'unknown'},
            'credentials': {'status': 'unknown'},
            'session': {'status': 'unknown'}
        }
        
        try:
            # Verificar página de login
            login_url = self.test_urls['devops_login']
            response = requests.get(login_url, timeout=10)
            
            if response.status_code == 200:
                auth_checks['login_page'] = {
                    'status': 'connected',
                    'status_code': response.status_code
                }
                
                # Verificar que contiene formulario de login
                if 'username' in response.text and 'password' in response.text:
                    auth_checks['credentials'] = {
                        'status': 'configured',
                        'username': self.devops_config['username']
                    }
                else:
                    auth_checks['credentials'] = {
                        'status': 'warning',
                        'error': 'Formulario de login no encontrado'
                    }
            else:
                auth_checks['login_page'] = {
                    'status': 'error',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            auth_checks['login_page'] = {
                'status': 'error',
                'error': str(e)
            }
        
        self.results['checks']['authentication'] = auth_checks
        return auth_checks
    
    def check_api_connectivity(self):
        """Verificar conectividad con API externa"""
        logger.info("🔍 Verificando conectividad con API externa...")
        
        api_checks = {
            'belgrano_ahorro': {'status': 'unknown'},
            'api_key': {'status': 'unknown'},
            'endpoints': {'status': 'unknown'}
        }
        
        # Verificar API de Belgrano Ahorro
        try:
            api_url = self.devops_config['belgrano_ahorro_url']
            headers = {'X-API-Key': self.devops_config['api_key']}
            
            # Probar endpoint de health
            health_url = urljoin(api_url, '/api/health')
            response = requests.get(health_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                api_checks['belgrano_ahorro'] = {
                    'status': 'connected',
                    'response_time': response.elapsed.total_seconds()
                }
                api_checks['api_key'] = {'status': 'valid'}
            else:
                api_checks['belgrano_ahorro'] = {
                    'status': 'warning',
                    'status_code': response.status_code
                }
                api_checks['api_key'] = {'status': 'invalid'}
                
        except requests.exceptions.ConnectionError:
            api_checks['belgrano_ahorro'] = {
                'status': 'error',
                'error': 'No se puede conectar a la API'
            }
        except Exception as e:
            api_checks['belgrano_ahorro'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Verificar endpoints específicos
        try:
            endpoints_to_check = ['/api/businesses', '/api/products', '/api/offers']
            endpoint_results = {}
            
            for endpoint in endpoints_to_check:
                try:
                    url = urljoin(self.devops_config['belgrano_ahorro_url'], endpoint)
                    response = requests.get(url, headers=headers, timeout=5)
                    endpoint_results[endpoint] = {
                        'status': 'connected' if response.status_code == 200 else 'warning',
                        'status_code': response.status_code
                    }
                except Exception as e:
                    endpoint_results[endpoint] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            api_checks['endpoints'] = {
                'status': 'checked',
                'results': endpoint_results
            }
            
        except Exception as e:
            api_checks['endpoints'] = {
                'status': 'error',
                'error': str(e)
            }
        
        self.results['checks']['api_connectivity'] = api_checks
        return api_checks
    
    def check_system_resources(self):
        """Verificar recursos del sistema"""
        logger.info("🔍 Verificando recursos del sistema...")
        
        resource_checks = {
            'disk_space': {'status': 'unknown'},
            'memory': {'status': 'unknown'},
            'python_version': {'status': 'unknown'},
            'dependencies': {'status': 'unknown'}
        }
        
        # Verificar espacio en disco
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free // (1024**3)
            
            if free_gb > 1:
                resource_checks['disk_space'] = {
                    'status': 'ok',
                    'free_gb': free_gb,
                    'total_gb': total // (1024**3)
                }
            else:
                resource_checks['disk_space'] = {
                    'status': 'warning',
                    'free_gb': free_gb,
                    'message': 'Poco espacio en disco'
                }
        except Exception as e:
            resource_checks['disk_space'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Verificar versión de Python
        try:
            python_version = sys.version
            resource_checks['python_version'] = {
                'status': 'ok',
                'version': python_version
            }
        except Exception as e:
            resource_checks['python_version'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Verificar dependencias críticas
        critical_deps = ['flask', 'requests', 'sqlite3', 'werkzeug']
        dep_status = {}
        
        for dep in critical_deps:
            try:
                if dep == 'sqlite3':
                    import sqlite3
                elif dep == 'flask':
                    import flask
                elif dep == 'requests':
                    import requests
                elif dep == 'werkzeug':
                    import werkzeug
                
                dep_status[dep] = {'status': 'available'}
            except ImportError:
                dep_status[dep] = {'status': 'missing'}
        
        resource_checks['dependencies'] = {
            'status': 'ok' if all(dep['status'] == 'available' for dep in dep_status.values()) else 'warning',
            'details': dep_status
        }
        
        self.results['checks']['system_resources'] = resource_checks
        return resource_checks
    
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
                        
                        if status in ['connected', 'ok', 'configured', 'valid']:
                            passed += 1
                        elif status in ['warning', 'timeout']:
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
        logger.info("📊 Generando reporte de conectividad...")
        
        # Ejecutar todas las verificaciones
        self.check_database_connectivity()
        self.check_devops_endpoints()
        self.check_devops_authentication()
        self.check_api_connectivity()
        self.check_system_resources()
        
        # Calcular resumen
        self.calculate_summary()
        
        return self.results
    
    def print_summary(self):
        """Imprimir resumen en consola"""
        print("\n" + "="*60)
        print("CHEQUEO DE CONECTIVIDAD DEVOPS - BELGRANO TICKETS")
        print("="*60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sistema: {self.results['system']} v{self.results['version']}")
        print(f"Verificaciones: {self.results['summary']['total_checks']}")
        print(f"Exitosas: {self.results['summary']['passed']}")
        print(f"Advertencias: {self.results['summary']['warnings']}")
        print(f"Fallidas: {self.results['summary']['failed']}")
        print(f"Tasa de exito: {self.results['summary']['success_rate']}%")
        print("="*60)
        
        # Mostrar detalles por categoría
        for category, checks in self.results['checks'].items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            if isinstance(checks, dict):
                for check_name, check_result in checks.items():
                    if isinstance(check_result, dict) and 'status' in check_result:
                        status_icon = "[OK]" if check_result['status'] in ['connected', 'ok', 'configured', 'valid'] else "[WARN]" if check_result['status'] in ['warning', 'timeout'] else "[ERROR]"
                        print(f"  {status_icon} {check_name}: {check_result['status']}")
                        if 'error' in check_result:
                            print(f"    Error: {check_result['error']}")

def main():
    """Función principal"""
    print("Iniciando chequeo de conectividad DevOps...")
    
    checker = DevOpsConnectivityChecker()
    results = checker.generate_report()
    
    # Imprimir resumen
    checker.print_summary()
    
    # Guardar reporte en archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reporte_conectividad_devops_{timestamp}.json'
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nReporte guardado en: {report_file}")
    except Exception as e:
        print(f"Error guardando reporte: {e}")
    
    # Determinar estado general
    success_rate = results['summary']['success_rate']
    if success_rate >= 90:
        print("\nSistema DevOps funcionando correctamente!")
        return 0
    elif success_rate >= 70:
        print("\nSistema DevOps con algunas advertencias")
        return 1
    else:
        print("\nSistema DevOps con problemas criticos")
        return 2

if __name__ == "__main__":
    sys.exit(main())