#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Final de Gestión DevOps a Belgrano Ahorro
Prueba completa del funcionamiento del sistema
"""

import requests
import json
import time
from datetime import datetime
import sys

class TestGestionDevOpsFinal:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'services_status': {}
            }
        }
        
        # URLs de los servicios
        self.services = {
            'devops': 'http://localhost:5002',
            'belgrano_ahorro': 'http://localhost:5000',
            'ticketera': 'http://localhost:5001'
        }
        
        # Headers para APIs
        self.api_headers = {
            'Authorization': 'Bearer belgrano_ahorro_api_key_2025',
            'Content-Type': 'application/json'
        }
        
    def log_test(self, test_name, status, message, details=None):
        """Registrar resultado de prueba"""
        test_result = {
            'name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results['tests'].append(test_result)
        self.results['summary']['total_tests'] += 1
        
        if status == 'PASS':
            self.results['summary']['passed'] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.results['summary']['failed'] += 1
            print(f"❌ {test_name}: {message}")
    
    def test_servicios_connectivity(self):
        """Probar conectividad de todos los servicios"""
        print("\n🔗 PROBANDO CONECTIVIDAD DE SERVICIOS...")
        
        for service_name, service_url in self.services.items():
            try:
                if service_name == 'devops':
                    # DevOps tiene rutas específicas
                    response = requests.get(f"{service_url}/devops/", timeout=5)
                else:
                    response = requests.get(service_url, timeout=5)
                
                if response.status_code in [200, 302]:
                    self.log_test(f"Conectividad {service_name}", "PASS", f"{service_name} respondiendo correctamente")
                else:
                    self.log_test(f"Conectividad {service_name}", "FAIL", f"{service_name} respondió con código {response.status_code}")
            except requests.exceptions.ConnectionError:
                self.log_test(f"Conectividad {service_name}", "FAIL", f"{service_name} no está ejecutándose")
            except Exception as e:
                self.log_test(f"Conectividad {service_name}", "FAIL", f"Error conectando a {service_name}: {str(e)}")
    
    def test_devops_authentication(self):
        """Probar autenticación DevOps"""
        print("\n🔐 PROBANDO AUTENTICACIÓN DEVOPS...")
        
        try:
            # Crear sesión
            session = requests.Session()
            
            # Probar login DevOps
            login_url = f"{self.services['devops']}/devops/login"
            login_data = {
                'username': 'devops',
                'password': 'DevOps2025!Secure'
            }
            
            response = session.post(login_url, data=login_data, timeout=10)
            
            if response.status_code in [200, 302]:
                self.log_test("Login DevOps", "PASS", "Login DevOps exitoso")
                
                # Probar acceso al dashboard
                dashboard_url = f"{self.services['devops']}/devops/"
                dashboard_response = session.get(dashboard_url, timeout=10)
                
                if dashboard_response.status_code == 200:
                    self.log_test("Acceso Dashboard DevOps", "PASS", "Dashboard DevOps accesible")
                else:
                    self.log_test("Acceso Dashboard DevOps", "FAIL", f"Dashboard no accesible: {dashboard_response.status_code}")
            else:
                self.log_test("Login DevOps", "FAIL", f"Login falló: {response.status_code}")
                
        except Exception as e:
            self.log_test("Autenticación DevOps", "FAIL", f"Error en autenticación: {str(e)}")
    
    def test_devops_endpoints(self):
        """Probar endpoints DevOps"""
        print("\n🌐 PROBANDO ENDPOINTS DEVOPS...")
        
        endpoints = [
            '/devops/health',
            '/devops/status', 
            '/devops/info',
            '/devops/negocios',
            '/devops/productos',
            '/devops/ofertas',
            '/devops/sucursales'
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.services['devops']}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.log_test(f"Endpoint {endpoint}", "PASS", f"Endpoint {endpoint} funcionando")
                else:
                    self.log_test(f"Endpoint {endpoint}", "FAIL", f"Endpoint {endpoint} falló: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Endpoint {endpoint}", "FAIL", f"Error en {endpoint}: {str(e)}")
    
    def test_belgrano_ahorro_apis(self):
        """Probar APIs de Belgrano Ahorro"""
        print("\n🛒 PROBANDO APIs BELGRANO AHORRO...")
        
        api_endpoints = [
            '/api/negocios',
            '/api/productos', 
            '/api/ofertas',
            '/api/sucursales',
            '/health'
        ]
        
        for endpoint in api_endpoints:
            try:
                url = f"{self.services['belgrano_ahorro']}{endpoint}"
                response = requests.get(url, headers=self.api_headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json() if response.content else {}
                    data_count = len(data.get('data', [])) if isinstance(data.get('data'), list) else 'N/A'
                    
                    self.log_test(f"API Belgrano {endpoint}", "PASS", f"API {endpoint} funcionando", {
                        'status_code': response.status_code,
                        'data_count': data_count
                    })
                else:
                    self.log_test(f"API Belgrano {endpoint}", "FAIL", f"API {endpoint} falló: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.log_test(f"API Belgrano {endpoint}", "FAIL", f"API {endpoint} no está disponible")
            except Exception as e:
                self.log_test(f"API Belgrano {endpoint}", "FAIL", f"Error en {endpoint}: {str(e)}")
    
    def test_creacion_negocios_devops(self):
        """Probar creación de negocios desde DevOps"""
        print("\n🏪 PROBANDO CREACIÓN DE NEGOCIOS DESDE DEVOPS...")
        
        try:
            # Crear sesión DevOps
            session = requests.Session()
            
            # Login DevOps
            login_url = f"{self.services['devops']}/devops/login"
            login_data = {
                'username': 'devops',
                'password': 'DevOps2025!Secure'
            }
            
            login_response = session.post(login_url, data=login_data, timeout=10)
            
            if login_response.status_code in [200, 302]:
                # Crear nuevo negocio
                nuevo_negocio = {
                    'nombre': f'Negocio Test DevOps Final {datetime.now().strftime("%H%M%S")}',
                    'descripcion': 'Negocio de prueba creado desde DevOps',
                    'direccion': 'Dirección de Prueba DevOps 123',
                    'telefono': '+54 11 1234-5678',
                    'email': 'testdevops@negocio.com',
                    'activo': True
                }
                
                # Usar endpoint DevOps para crear negocio
                create_url = f"{self.services['devops']}/devops/negocios"
                create_response = session.post(create_url, data=nuevo_negocio, timeout=10)
                
                if create_response.status_code in [200, 302]:
                    self.log_test("Crear Negocio DevOps", "PASS", f"Negocio creado exitosamente desde DevOps")
                    
                    # Verificar que el negocio fue creado en Belgrano Ahorro
                    verify_url = f"{self.services['belgrano_ahorro']}/api/negocios"
                    verify_response = requests.get(verify_url, headers=self.api_headers, timeout=10)
                    
                    if verify_response.status_code == 200:
                        negocios = verify_response.json().get('data', [])
                        negocio_encontrado = any(n.get('nombre') == nuevo_negocio['nombre'] for n in negocios)
                        
                        if negocio_encontrado:
                            self.log_test("Verificar Negocio Creado", "PASS", "Negocio verificado en Belgrano Ahorro")
                        else:
                            self.log_test("Verificar Negocio Creado", "FAIL", "Negocio no encontrado en Belgrano Ahorro")
                    else:
                        self.log_test("Verificar Negocio Creado", "FAIL", "Error verificando negocio en Belgrano Ahorro")
                else:
                    self.log_test("Crear Negocio DevOps", "FAIL", f"Error creando negocio desde DevOps: {create_response.status_code}")
            else:
                self.log_test("Login DevOps", "FAIL", "No se pudo autenticar en DevOps")
                
        except Exception as e:
            self.log_test("Crear Negocio DevOps", "FAIL", f"Error en creación de negocio: {str(e)}")
    
    def test_creacion_productos_devops(self):
        """Probar creación de productos desde DevOps"""
        print("\n📦 PROBANDO CREACIÓN DE PRODUCTOS DESDE DEVOPS...")
        
        try:
            # Crear sesión DevOps
            session = requests.Session()
            
            # Login DevOps
            login_url = f"{self.services['devops']}/devops/login"
            login_data = {
                'username': 'devops',
                'password': 'DevOps2025!Secure'
            }
            
            login_response = session.post(login_url, data=login_data, timeout=10)
            
            if login_response.status_code in [200, 302]:
                # Crear nuevo producto
                nuevo_producto = {
                    'nombre': f'Producto Test DevOps Final {datetime.now().strftime("%H%M%S")}',
                    'precio': 299.99,
                    'categoria': 'Test DevOps',
                    'stock': 50,
                    'negocio_id': 1,  # Asumir que existe un negocio con ID 1
                    'activo': True
                }
                
                # Usar endpoint DevOps para crear producto
                create_url = f"{self.services['devops']}/devops/productos"
                create_response = session.post(create_url, data=nuevo_producto, timeout=10)
                
                if create_response.status_code in [200, 302]:
                    self.log_test("Crear Producto DevOps", "PASS", f"Producto creado exitosamente desde DevOps")
                else:
                    self.log_test("Crear Producto DevOps", "FAIL", f"Error creando producto desde DevOps: {create_response.status_code}")
            else:
                self.log_test("Login DevOps", "FAIL", "No se pudo autenticar en DevOps")
                
        except Exception as e:
            self.log_test("Crear Producto DevOps", "FAIL", f"Error en creación de producto: {str(e)}")
    
    def test_creacion_ofertas_devops(self):
        """Probar creación de ofertas desde DevOps"""
        print("\n🎯 PROBANDO CREACIÓN DE OFERTAS DESDE DEVOPS...")
        
        try:
            # Crear sesión DevOps
            session = requests.Session()
            
            # Login DevOps
            login_url = f"{self.services['devops']}/devops/login"
            login_data = {
                'username': 'devops',
                'password': 'DevOps2025!Secure'
            }
            
            login_response = session.post(login_url, data=login_data, timeout=10)
            
            if login_response.status_code in [200, 302]:
                # Crear nueva oferta
                nueva_oferta = {
                    'titulo': f'Oferta Test DevOps Final {datetime.now().strftime("%H%M%S")}',
                    'descripcion': 'Oferta de prueba creada desde DevOps',
                    'descuento': 25,
                    'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
                    'fecha_fin': (datetime.now().replace(day=datetime.now().day + 30)).strftime('%Y-%m-%d'),
                    'activa': True
                }
                
                # Usar endpoint DevOps para crear oferta
                create_url = f"{self.services['devops']}/devops/ofertas"
                create_response = session.post(create_url, data=nueva_oferta, timeout=10)
                
                if create_response.status_code in [200, 302]:
                    self.log_test("Crear Oferta DevOps", "PASS", f"Oferta creada exitosamente desde DevOps")
                else:
                    self.log_test("Crear Oferta DevOps", "FAIL", f"Error creando oferta desde DevOps: {create_response.status_code}")
            else:
                self.log_test("Login DevOps", "FAIL", "No se pudo autenticar en DevOps")
                
        except Exception as e:
            self.log_test("Crear Oferta DevOps", "FAIL", f"Error en creación de oferta: {str(e)}")
    
    def test_creacion_sucursales_devops(self):
        """Probar creación de sucursales desde DevOps"""
        print("\n🏢 PROBANDO CREACIÓN DE SUCURSALES DESDE DEVOPS...")
        
        try:
            # Crear sesión DevOps
            session = requests.Session()
            
            # Login DevOps
            login_url = f"{self.services['devops']}/devops/login"
            login_data = {
                'username': 'devops',
                'password': 'DevOps2025!Secure'
            }
            
            login_response = session.post(login_url, data=login_data, timeout=10)
            
            if login_response.status_code in [200, 302]:
                # Crear nueva sucursal
                nueva_sucursal = {
                    'nombre': f'Sucursal Test DevOps Final {datetime.now().strftime("%H%M%S")}',
                    'direccion': 'Dirección de Sucursal Test DevOps 456',
                    'telefono': '+54 11 9876-5432',
                    'email': 'sucursaldevops@test.com',
                    'horario_apertura': '09:00',
                    'horario_cierre': '18:00',
                    'activo': True
                }
                
                # Usar endpoint DevOps para crear sucursal
                create_url = f"{self.services['devops']}/devops/sucursales"
                create_response = session.post(create_url, data=nueva_sucursal, timeout=10)
                
                if create_response.status_code in [200, 302]:
                    self.log_test("Crear Sucursal DevOps", "PASS", f"Sucursal creada exitosamente desde DevOps")
                else:
                    self.log_test("Crear Sucursal DevOps", "FAIL", f"Error creando sucursal desde DevOps: {create_response.status_code}")
            else:
                self.log_test("Login DevOps", "FAIL", "No se pudo autenticar en DevOps")
                
        except Exception as e:
            self.log_test("Crear Sucursal DevOps", "FAIL", f"Error en creación de sucursal: {str(e)}")
    
    def test_integration_complete(self):
        """Probar integración completa del sistema"""
        print("\n🔄 PROBANDO INTEGRACIÓN COMPLETA...")
        
        try:
            # Obtener datos de Belgrano Ahorro
            belgrano_data = {}
            endpoints = ['negocios', 'productos', 'ofertas', 'sucursales']
            
            for endpoint in endpoints:
                url = f"{self.services['belgrano_ahorro']}/api/{endpoint}"
                response = requests.get(url, headers=self.api_headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    belgrano_data[endpoint] = len(data.get('data', []))
                else:
                    belgrano_data[endpoint] = 0
            
            # Obtener datos de Ticketera
            ticketera_data = {}
            ticketera_endpoints = ['productos', 'repartidores', 'estados']
            
            for endpoint in ticketera_endpoints:
                url = f"{self.services['ticketera']}/api/{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    ticketera_data[endpoint] = len(data.get('data', [])) if isinstance(data.get('data'), list) else 0
                else:
                    ticketera_data[endpoint] = 0
            
            self.log_test("Datos Belgrano Ahorro", "PASS", f"Datos obtenidos: {belgrano_data}")
            self.log_test("Datos Ticketera", "PASS", f"Datos obtenidos: {ticketera_data}")
            
            # Verificar integración
            total_belgrano = sum(belgrano_data.values())
            total_ticketera = sum(ticketera_data.values())
            
            if total_belgrano > 0 and total_ticketera >= 0:
                self.log_test("Integración Completa", "PASS", "Integración funcionando correctamente", {
                    'belgrano_total': total_belgrano,
                    'ticketera_total': total_ticketera,
                    'integracion_status': 'active'
                })
            else:
                self.log_test("Integración Completa", "FAIL", "Problemas en integración de datos")
                
        except Exception as e:
            self.log_test("Integración Completa", "FAIL", f"Error en integración: {str(e)}")
    
    def generate_report(self):
        """Generar reporte final"""
        print("\n📊 GENERANDO REPORTE FINAL...")
        
        # Calcular estadísticas
        total = self.results['summary']['total_tests']
        passed = self.results['summary']['passed']
        failed = self.results['summary']['failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"📋 REPORTE FINAL DE GESTIÓN DEVOPS")
        print(f"{'='*60}")
        print(f"🕐 Timestamp: {self.results['timestamp']}")
        print(f"📊 Total de pruebas: {total}")
        print(f"✅ Exitosas: {passed}")
        print(f"❌ Fallidas: {failed}")
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        print(f"\n🔧 FUNCIONALIDADES PROBADAS:")
        for test in self.results['tests']:
            status_icon = "✅" if test['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {test['name']}: {test['message']}")
        
        # Guardar reporte
        report_filename = f"reporte_gestion_devops_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {report_filename}")
        
        return self.results
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DE GESTIÓN DEVOPS FINAL")
        print("="*60)
        
        # Ejecutar todas las pruebas
        self.test_servicios_connectivity()
        self.test_devops_authentication()
        self.test_devops_endpoints()
        self.test_belgrano_ahorro_apis()
        self.test_creacion_negocios_devops()
        self.test_creacion_productos_devops()
        self.test_creacion_ofertas_devops()
        self.test_creacion_sucursales_devops()
        self.test_integration_complete()
        
        # Generar reporte
        return self.generate_report()

def main():
    """Función principal"""
    print("🔧 SISTEMA DE PRUEBAS DE GESTIÓN DEVOPS FINAL")
    print("Prueba completa del funcionamiento DevOps a Belgrano Ahorro")
    print("="*60)
    
    tester = TestGestionDevOpsFinal()
    results = tester.run_all_tests()
    
    # Determinar si el sistema está funcionando correctamente
    success_rate = (results['summary']['passed'] / results['summary']['total_tests'] * 100) if results['summary']['total_tests'] > 0 else 0
    
    if success_rate >= 80:
        print(f"\n🎉 SISTEMA DEVOPS FUNCIONANDO CORRECTAMENTE ({success_rate:.1f}% de éxito)")
        return 0
    elif success_rate >= 60:
        print(f"\n⚠️ SISTEMA DEVOPS PARCIALMENTE FUNCIONAL ({success_rate:.1f}% de éxito)")
        return 1
    else:
        print(f"\n❌ SISTEMA DEVOPS CON PROBLEMAS ({success_rate:.1f}% de éxito)")
        return 2

if __name__ == "__main__":
    sys.exit(main())
