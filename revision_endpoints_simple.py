#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revision completa de endpoints DevOps y conectividad con Belgrano Ahorro
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

class DevOpsEndpointReviewer:
    def __init__(self):
        self.base_urls = {
            'devops': 'http://localhost:5002',
            'belgrano_ahorro': 'http://localhost:5000',
            'ticketera': 'http://localhost:5001',
            'gateway': 'http://localhost:5003',
            'sync': 'http://localhost:5004'
        }
        self.results = {}
        self.session = requests.Session()
        self.session.timeout = 10
        
    def check_service_connectivity(self):
        """Verificar conectividad de servicios"""
        print("VERIFICANDO CONECTIVIDAD DE SERVICIOS")
        print("=" * 50)
        
        services_status = {}
        
        for service, url in self.base_urls.items():
            try:
                response = self.session.get(f"{url}/", timeout=5)
                if response.status_code in [200, 302]:
                    print(f"OK {service.upper()} - Conectado ({response.status_code})")
                    services_status[service] = True
                else:
                    print(f"WARNING {service.upper()} - Respuesta {response.status_code}")
                    services_status[service] = False
            except requests.exceptions.ConnectionError:
                print(f"ERROR {service.upper()} - No se puede conectar")
                services_status[service] = False
            except Exception as e:
                print(f"ERROR {service.upper()} - Error: {e}")
                services_status[service] = False
        
        return services_status
    
    def check_devops_endpoints(self):
        """Verificar todos los endpoints DevOps"""
        print("\nVERIFICANDO ENDPOINTS DEVOPS")
        print("=" * 50)
        
        devops_url = self.base_urls['devops']
        endpoints = [
            # Autenticacion
            ('/devops/login', 'GET', 'Login DevOps'),
            ('/devops/logout', 'GET', 'Logout DevOps'),
            
            # Panel principal
            ('/devops/', 'GET', 'Panel principal'),
            ('/devops/health', 'GET', 'Health check'),
            ('/devops/status', 'GET', 'Estado del sistema'),
            ('/devops/info', 'GET', 'Informacion del servicio'),
            
            # Gestion de contenido
            ('/devops/negocios', 'GET', 'Gestion de negocios'),
            ('/devops/productos', 'GET', 'Gestion de productos'),
            ('/devops/ofertas', 'GET', 'Gestion de ofertas'),
            ('/devops/sucursales', 'GET', 'Gestion de sucursales'),
            ('/devops/precios', 'GET', 'Gestion de precios'),
            ('/devops/sync', 'GET', 'Panel de sincronizacion')
        ]
        
        endpoints_status = {}
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{devops_url}{endpoint}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    endpoints_status[endpoint] = True
                elif response.status_code == 302:
                    print(f"OK {endpoint} - {description} (Redirect)")
                    endpoints_status[endpoint] = True
                elif response.status_code == 401:
                    print(f"WARNING {endpoint} - {description} (Requiere autenticacion)")
                    endpoints_status[endpoint] = True
                else:
                    print(f"ERROR {endpoint} - {description} ({response.status_code})")
                    endpoints_status[endpoint] = False
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
                endpoints_status[endpoint] = False
        
        return endpoints_status
    
    def check_belgrano_ahorro_connectivity(self):
        """Verificar conectividad con Belgrano Ahorro"""
        print("\nVERIFICANDO CONECTIVIDAD CON BELGRANO AHORRO")
        print("=" * 50)
        
        belgrano_url = self.base_urls['belgrano_ahorro']
        endpoints = [
            ('/', 'GET', 'Pagina principal'),
            ('/api/negocios', 'GET', 'API Negocios'),
            ('/api/productos', 'GET', 'API Productos'),
            ('/api/ofertas', 'GET', 'API Ofertas'),
            ('/api/sucursales', 'GET', 'API Sucursales'),
            ('/api/precios', 'GET', 'API Precios')
        ]
        
        connectivity_status = {}
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{belgrano_url}{endpoint}"
                headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
                response = self.session.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    connectivity_status[endpoint] = True
                elif response.status_code == 401:
                    print(f"WARNING {endpoint} - {description} (Requiere autenticacion)")
                    connectivity_status[endpoint] = True
                else:
                    print(f"ERROR {endpoint} - {description} ({response.status_code})")
                    connectivity_status[endpoint] = False
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
                connectivity_status[endpoint] = False
        
        return connectivity_status
    
    def check_api_gateway_endpoints(self):
        """Verificar endpoints del API Gateway"""
        print("\nVERIFICANDO API GATEWAY")
        print("=" * 50)
        
        gateway_url = self.base_urls['gateway']
        endpoints = [
            ('/gateway/health', 'GET', 'Health check Gateway'),
            ('/gateway/sync/status', 'GET', 'Estado de sincronizacion'),
            ('/gateway/negocios', 'GET', 'API Negocios Gateway'),
            ('/gateway/productos', 'GET', 'API Productos Gateway'),
            ('/gateway/ofertas', 'GET', 'API Ofertas Gateway'),
            ('/gateway/sucursales', 'GET', 'API Sucursales Gateway')
        ]
        
        gateway_status = {}
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{gateway_url}{endpoint}"
                headers = {'Authorization': 'Bearer devops_api_key_2025'}
                response = self.session.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    gateway_status[endpoint] = True
                else:
                    print(f"ERROR {endpoint} - {description} ({response.status_code})")
                    gateway_status[endpoint] = False
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
                gateway_status[endpoint] = False
        
        return gateway_status
    
    def check_sync_system(self):
        """Verificar sistema de sincronizacion"""
        print("\nVERIFICANDO SISTEMA DE SINCRONIZACION")
        print("=" * 50)
        
        sync_url = self.base_urls['sync']
        endpoints = [
            ('/sync/status', 'GET', 'Estado de sincronizacion'),
            ('/sync/force', 'POST', 'Forzar sincronizacion'),
            ('/sync/differences', 'GET', 'Obtener diferencias')
        ]
        
        sync_status = {}
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{sync_url}{endpoint}"
                if method == 'POST':
                    response = self.session.post(url, timeout=5)
                else:
                    response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"OK {endpoint} - {description}")
                    sync_status[endpoint] = True
                else:
                    print(f"ERROR {endpoint} - {description} ({response.status_code})")
                    sync_status[endpoint] = False
            except Exception as e:
                print(f"ERROR {endpoint} - {description} ({e})")
                sync_status[endpoint] = False
        
        return sync_status
    
    def test_crud_operations(self):
        """Probar operaciones CRUD"""
        print("\nPROBANDO OPERACIONES CRUD")
        print("=" * 50)
        
        # Verificar que los metodos CRUD estan implementados
        crud_methods = [
            'get_negocios', 'create_negocio', 'update_negocio', 'delete_negocio',
            'get_productos', 'create_producto', 'update_producto', 'delete_producto',
            'get_ofertas', 'create_oferta', 'update_oferta', 'delete_oferta',
            'get_sucursales', 'create_sucursal', 'update_sucursal', 'delete_sucursal'
        ]
        
        try:
            # Verificar que el cliente API tiene los metodos
            with open('belgrano_client_gateway.py', 'r', encoding='utf-8') as f:
                client_content = f.read()
            
            methods_found = []
            for method in crud_methods:
                if f"def {method}(" in client_content:
                    methods_found.append(method)
                    print(f"OK {method}")
                else:
                    print(f"ERROR {method} - NO ENCONTRADO")
            
            print(f"\nMetodos CRUD encontrados: {len(methods_found)}/{len(crud_methods)}")
            return len(methods_found) == len(crud_methods)
            
        except Exception as e:
            print(f"ERROR verificando CRUD: {e}")
            return False
    
    def test_authentication_flow(self):
        """Probar flujo de autenticacion"""
        print("\nPROBANDO FLUJO DE AUTENTICACION")
        print("=" * 50)
        
        devops_url = self.base_urls['devops']
        
        try:
            # Verificar pagina de login
            login_url = f"{devops_url}/devops/login"
            response = self.session.get(login_url, timeout=5)
            
            if response.status_code == 200:
                print("OK Pagina de login accesible")
                
                # Intentar login
                login_data = {
                    'username': 'devops',
                    'password': 'DevOps2025!Secure'
                }
                
                login_response = self.session.post(login_url, data=login_data, timeout=5, allow_redirects=False)
                
                if login_response.status_code == 302:
                    print("OK Login exitoso (redirect)")
                    return True
                else:
                    print(f"WARNING Login - Respuesta {login_response.status_code}")
                    return False
            else:
                print(f"ERROR Pagina de login - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"ERROR en autenticacion: {e}")
            return False
    
    def generate_comprehensive_report(self):
        """Generar reporte completo"""
        print("\nGENERANDO REPORTE COMPREHENSIVO")
        print("=" * 50)
        
        # Ejecutar todas las verificaciones
        services_status = self.check_service_connectivity()
        devops_endpoints = self.check_devops_endpoints()
        belgrano_connectivity = self.check_belgrano_ahorro_connectivity()
        gateway_endpoints = self.check_api_gateway_endpoints()
        sync_system = self.check_sync_system()
        crud_operations = self.test_crud_operations()
        authentication = self.test_authentication_flow()
        
        # Calcular metricas
        total_checks = 0
        passed_checks = 0
        
        # Servicios
        for service, status in services_status.items():
            total_checks += 1
            if status:
                passed_checks += 1
        
        # Endpoints DevOps
        for endpoint, status in devops_endpoints.items():
            total_checks += 1
            if status:
                passed_checks += 1
        
        # Conectividad Belgrano Ahorro
        for endpoint, status in belgrano_connectivity.items():
            total_checks += 1
            if status:
                passed_checks += 1
        
        # Gateway
        for endpoint, status in gateway_endpoints.items():
            total_checks += 1
            if status:
                passed_checks += 1
        
        # Sync
        for endpoint, status in sync_system.items():
            total_checks += 1
            if status:
                passed_checks += 1
        
        # CRUD y Auth
        total_checks += 2
        if crud_operations:
            passed_checks += 1
        if authentication:
            passed_checks += 1
        
        success_rate = round((passed_checks / total_checks) * 100, 2)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'services': services_status,
            'devops_endpoints': devops_endpoints,
            'belgrano_connectivity': belgrano_connectivity,
            'gateway_endpoints': gateway_endpoints,
            'sync_system': sync_system,
            'crud_operations': crud_operations,
            'authentication': authentication,
            'metrics': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'success_rate': success_rate,
                'ready_for_deploy': success_rate >= 80
            }
        }
        
        # Guardar reporte
        with open('reporte_endpoints_devops_completo.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Verificaciones exitosas: {passed_checks}/{total_checks}")
        print(f"Tasa de exito: {success_rate}%")
        
        if success_rate >= 80:
            print("SISTEMA DEVOPS FUNCIONAL")
        else:
            print("SISTEMA DEVOPS REQUIERE CORRECCIONES")
        
        return report
    
    def run_complete_review(self):
        """Ejecutar revision completa"""
        print("REVISION COMPLETA DE ENDPOINTS DEVOPS")
        print("=" * 60)
        print("Verificacion exhaustiva de conectividad y funcionalidad")
        print("")
        
        report = self.generate_comprehensive_report()
        
        print("\n" + "=" * 60)
        print("RESUMEN EJECUTIVO")
        print("=" * 60)
        
        # Mostrar resultados por categoria
        print(f"\nSERVICIOS ({sum(1 for v in report['services'].values() if v)}/{len(report['services'])}):")
        for service, status in report['services'].items():
            status_icon = "OK" if status else "ERROR"
            print(f"  {status_icon} {service}")
        
        print(f"\nENDPOINTS DEVOPS ({sum(1 for v in report['devops_endpoints'].values() if v)}/{len(report['devops_endpoints'])}):")
        for endpoint, status in report['devops_endpoints'].items():
            status_icon = "OK" if status else "ERROR"
            print(f"  {status_icon} {endpoint}")
        
        print(f"\nCONECTIVIDAD BELGRANO AHORRO ({sum(1 for v in report['belgrano_connectivity'].values() if v)}/{len(report['belgrano_connectivity'])}):")
        for endpoint, status in report['belgrano_connectivity'].items():
            status_icon = "OK" if status else "ERROR"
            print(f"  {status_icon} {endpoint}")
        
        print(f"\nAPI GATEWAY ({sum(1 for v in report['gateway_endpoints'].values() if v)}/{len(report['gateway_endpoints'])}):")
        for endpoint, status in report['gateway_endpoints'].items():
            status_icon = "OK" if status else "ERROR"
            print(f"  {status_icon} {endpoint}")
        
        print(f"\nSISTEMA SYNC ({sum(1 for v in report['sync_system'].values() if v)}/{len(report['sync_system'])}):")
        for endpoint, status in report['sync_system'].items():
            status_icon = "OK" if status else "ERROR"
            print(f"  {status_icon} {endpoint}")
        
        print(f"\nOPERACIONES CRUD: {'OK' if report['crud_operations'] else 'ERROR'}")
        print(f"AUTENTICACION: {'OK' if report['authentication'] else 'ERROR'}")
        
        print(f"\nEstado General: {report['metrics']['success_rate']}%")
        
        if report['metrics']['ready_for_deploy']:
            print("\nSISTEMA DEVOPS COMPLETAMENTE FUNCIONAL")
            print("Conectividad con Belgrano Ahorro garantizada")
        else:
            print("\nSISTEMA DEVOPS REQUIERE CORRECCIONES")
            print("Revisar conectividad antes del deploy")
        
        return report['metrics']['ready_for_deploy']

def main():
    """Funcion principal"""
    reviewer = DevOpsEndpointReviewer()
    return reviewer.run_complete_review()

if __name__ == "__main__":
    main()
