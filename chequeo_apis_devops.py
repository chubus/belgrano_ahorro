#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chequeo completo de APIs DevOps
Verificación exhaustiva de todos los endpoints y servicios
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from urllib.parse import urljoin

class DevOpsAPIChecker:
    def __init__(self):
        self.base_urls = {
            'ticketera': 'http://localhost:5001',
            'devops': 'http://localhost:5002',
            'gateway': 'http://localhost:5003',
            'sync': 'http://localhost:5004',
            'belgrano_ahorro': 'http://localhost:5000'
        }
        self.results = {}
        self.session = requests.Session()
        self.session.timeout = 10
        
    def check_service_status(self, service_name, base_url):
        """Verificar estado de un servicio"""
        print(f"\nVERIFICANDO {service_name.upper()}")
        print("=" * 50)
        
        try:
            # Intentar conectar al servicio
            response = self.session.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print(f"OK {service_name} - Conectado (200)")
                return True
            else:
                print(f"WARNING {service_name} - Respuesta {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"ERROR {service_name} - No se puede conectar")
            return False
        except requests.exceptions.Timeout:
            print(f"ERROR {service_name} - Timeout")
            return False
        except Exception as e:
            print(f"ERROR {service_name} - {e}")
            return False
    
    def check_devops_endpoints(self):
        """Verificar endpoints DevOps"""
        print("\nVERIFICANDO ENDPOINTS DEVOPS")
        print("=" * 50)
        
        devops_url = self.base_urls['devops']
        endpoints = [
            ('/devops/', 'GET', 'Panel principal'),
            ('/devops/login', 'GET', 'Login DevOps'),
            ('/devops/health', 'GET', 'Health check'),
            ('/devops/status', 'GET', 'Estado del sistema'),
            ('/devops/info', 'GET', 'Información del servicio'),
            ('/devops/negocios', 'GET', 'Gestión de negocios'),
            ('/devops/productos', 'GET', 'Gestión de productos'),
            ('/devops/ofertas', 'GET', 'Gestión de ofertas'),
            ('/devops/sucursales', 'GET', 'Gestión de sucursales'),
            ('/devops/precios', 'GET', 'Gestión de precios'),
            ('/devops/sync', 'GET', 'Panel de sincronización')
        ]
        
        endpoints_ok = []
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{devops_url}{endpoint}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    endpoints_ok.append(endpoint)
                elif response.status_code == 302:  # Redirect (normal para login)
                    print(f"OK {endpoint} - {description} (Redirect)")
                    endpoints_ok.append(endpoint)
                else:
                    print(f"WARNING {endpoint} - {description} ({response.status_code})")
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
        
        print(f"\nEndpoints DevOps funcionando: {len(endpoints_ok)}/{len(endpoints)}")
        return len(endpoints_ok) == len(endpoints)
    
    def check_api_gateway(self):
        """Verificar API Gateway"""
        print("\nVERIFICANDO API GATEWAY")
        print("=" * 50)
        
        gateway_url = self.base_urls['gateway']
        endpoints = [
            ('/gateway/health', 'GET', 'Health check Gateway'),
            ('/gateway/sync/status', 'GET', 'Estado de sincronización'),
            ('/gateway/negocios', 'GET', 'API Negocios'),
            ('/gateway/productos', 'GET', 'API Productos'),
            ('/gateway/ofertas', 'GET', 'API Ofertas'),
            ('/gateway/sucursales', 'GET', 'API Sucursales')
        ]
        
        endpoints_ok = []
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{gateway_url}{endpoint}"
                headers = {'Authorization': 'Bearer devops_api_key_2025'}
                response = self.session.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    endpoints_ok.append(endpoint)
                else:
                    print(f"WARNING {endpoint} - {description} ({response.status_code})")
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
        
        print(f"\nEndpoints Gateway funcionando: {len(endpoints_ok)}/{len(endpoints)}")
        return len(endpoints_ok) == len(endpoints)
    
    def check_sync_manager(self):
        """Verificar Sistema de Sincronización"""
        print("\nVERIFICANDO SISTEMA DE SINCRONIZACION")
        print("=" * 50)
        
        sync_url = self.base_urls['sync']
        endpoints = [
            ('/sync/status', 'GET', 'Estado de sincronización'),
            ('/sync/force', 'POST', 'Forzar sincronización'),
            ('/sync/differences', 'GET', 'Obtener diferencias')
        ]
        
        endpoints_ok = []
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{sync_url}{endpoint}"
                if method == 'POST':
                    response = self.session.post(url, timeout=5)
                else:
                    response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    endpoints_ok.append(endpoint)
                else:
                    print(f"WARNING {endpoint} - {description} ({response.status_code})")
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
        
        print(f"\nEndpoints Sync funcionando: {len(endpoints_ok)}/{len(endpoints)}")
        return len(endpoints_ok) == len(endpoints)
    
    def check_belgrano_ahorro_api(self):
        """Verificar API de Belgrano Ahorro"""
        print("\nVERIFICANDO API BELGRANO AHORRO")
        print("=" * 50)
        
        api_url = self.base_urls['belgrano_ahorro']
        endpoints = [
            ('/api/negocios', 'GET', 'API Negocios'),
            ('/api/productos', 'GET', 'API Productos'),
            ('/api/ofertas', 'GET', 'API Ofertas'),
            ('/api/sucursales', 'GET', 'API Sucursales'),
            ('/api/precios', 'GET', 'API Precios')
        ]
        
        endpoints_ok = []
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{api_url}{endpoint}"
                headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
                response = self.session.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    endpoints_ok.append(endpoint)
                else:
                    print(f"WARNING {endpoint} - {description} ({response.status_code})")
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
        
        print(f"\nEndpoints Belgrano Ahorro funcionando: {len(endpoints_ok)}/{len(endpoints)}")
        return len(endpoints_ok) == len(endpoints)
    
    def check_authentication(self):
        """Verificar autenticación DevOps"""
        print("\nVERIFICANDO AUTENTICACION DEVOPS")
        print("=" * 50)
        
        devops_url = self.base_urls['devops']
        
        try:
            # Verificar página de login
            login_url = f"{devops_url}/devops/login"
            response = self.session.get(login_url, timeout=5)
            
            if response.status_code == 200:
                print("OK Login page - Accesible")
                
                # Intentar login
                login_data = {
                    'username': 'devops',
                    'password': 'DevOps2025!Secure'
                }
                
                login_response = self.session.post(login_url, data=login_data, timeout=5)
                
                if login_response.status_code == 302:  # Redirect después del login
                    print("OK Login - Autenticación exitosa")
                    return True
                else:
                    print(f"WARNING Login - Respuesta {login_response.status_code}")
                    return False
            else:
                print(f"ERROR Login page - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"ERROR Autenticación - {e}")
            return False
    
    def check_crud_operations(self):
        """Verificar operaciones CRUD"""
        print("\nVERIFICANDO OPERACIONES CRUD")
        print("=" * 50)
        
        # Verificar que los métodos CRUD están implementados
        crud_methods = [
            'get_negocios', 'create_negocio', 'update_negocio', 'delete_negocio',
            'get_productos', 'create_producto', 'update_producto', 'delete_producto',
            'get_ofertas', 'create_oferta', 'update_oferta', 'delete_oferta',
            'get_sucursales', 'create_sucursal', 'update_sucursal', 'delete_sucursal'
        ]
        
        try:
            # Verificar que el cliente API tiene los métodos
            with open('belgrano_client_gateway.py', 'r', encoding='utf-8') as f:
                client_content = f.read()
            
            methods_found = []
            for method in crud_methods:
                if f"def {method}(" in client_content:
                    methods_found.append(method)
                    print(f"OK {method}")
                else:
                    print(f"ERROR {method} - NO ENCONTRADO")
            
            print(f"\nMétodos CRUD encontrados: {len(methods_found)}/{len(crud_methods)}")
            return len(methods_found) == len(crud_methods)
            
        except Exception as e:
            print(f"ERROR verificando CRUD - {e}")
            return False
    
    def generate_report(self):
        """Generar reporte final"""
        print("\nGENERANDO REPORTE FINAL")
        print("=" * 50)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'endpoints': {},
            'authentication': {},
            'crud': {},
            'summary': {}
        }
        
        # Verificar servicios
        for service, url in self.base_urls.items():
            report['services'][service] = self.check_service_status(service, url)
        
        # Verificar endpoints
        report['endpoints']['devops'] = self.check_devops_endpoints()
        report['endpoints']['gateway'] = self.check_api_gateway()
        report['endpoints']['sync'] = self.check_sync_manager()
        report['endpoints']['belgrano_ahorro'] = self.check_belgrano_ahorro_api()
        
        # Verificar autenticación
        report['authentication']['devops'] = self.check_authentication()
        
        # Verificar CRUD
        report['crud']['methods'] = self.check_crud_operations()
        
        # Calcular resumen
        total_checks = 0
        passed_checks = 0
        
        for category, results in report.items():
            if isinstance(results, dict):
                for check, result in results.items():
                    if isinstance(result, bool):
                        total_checks += 1
                        if result:
                            passed_checks += 1
        
        report['summary'] = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'success_rate': round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0,
            'ready_for_deploy': passed_checks == total_checks
        }
        
        # Guardar reporte
        with open('reporte_apis_devops.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Verificaciones exitosas: {passed_checks}/{total_checks}")
        print(f"Tasa de éxito: {report['summary']['success_rate']}%")
        
        if report['summary']['ready_for_deploy']:
            print("APIS DEVOPS LISTAS PARA DEPLOY")
        else:
            print("APIS DEVOPS REQUIEREN CORRECCIONES")
        
        return report
    
    def run_full_check(self):
        """Ejecutar chequeo completo"""
        print("CHEQUEO COMPLETO DE APIS DEVOPS")
        print("=" * 60)
        print("Verificación exhaustiva de todos los servicios y endpoints")
        print("")
        
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("RESUMEN EJECUTIVO")
        print("=" * 60)
        
        # Mostrar resultados por categoría
        for category, results in report.items():
            if isinstance(results, dict) and category != 'summary':
                print(f"\n{category.upper()}:")
                for check, result in results.items():
                    status = "OK" if result else "ERROR"
                    print(f"  {status} {check}")
        
        print(f"\nEstado General: {report['summary']['success_rate']}%")
        
        if report['summary']['ready_for_deploy']:
            print("\nTODAS LAS APIS DEVOPS ESTAN FUNCIONANDO CORRECTAMENTE")
            print("Sistema listo para deploy")
        else:
            print("\nALGUNAS APIS REQUIEREN CORRECCIONES")
            print("Revisar errores antes del deploy")
        
        return report['summary']['ready_for_deploy']

def main():
    """Función principal"""
    checker = DevOpsAPIChecker()
    return checker.run_full_check()

if __name__ == "__main__":
    main()
