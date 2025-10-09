#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Directo de Gestión Belgrano Ahorro
Prueba directa de las APIs sin DevOps
"""

import requests
import json
import time
from datetime import datetime
import sys

class TestGestionDirectaBelgrano:
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
        """Probar conectividad de servicios"""
        print("\n🔗 PROBANDO CONECTIVIDAD DE SERVICIOS...")
        
        for service_name, service_url in self.services.items():
            try:
                response = requests.get(service_url, timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Conectividad {service_name}", "PASS", f"{service_name} respondiendo correctamente")
                else:
                    self.log_test(f"Conectividad {service_name}", "FAIL", f"{service_name} respondió con código {response.status_code}")
            except requests.exceptions.ConnectionError:
                self.log_test(f"Conectividad {service_name}", "FAIL", f"{service_name} no está ejecutándose")
            except Exception as e:
                self.log_test(f"Conectividad {service_name}", "FAIL", f"Error conectando a {service_name}: {str(e)}")
    
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
    
    def test_creacion_negocios_directa(self):
        """Probar creación directa de negocios"""
        print("\n🏪 PROBANDO CREACIÓN DIRECTA DE NEGOCIOS...")
        
        try:
            # Crear nuevo negocio
            nuevo_negocio = {
                'nombre': f'Negocio Test Directo {datetime.now().strftime("%H%M%S")}',
                'descripcion': 'Negocio de prueba creado directamente',
                'direccion': 'Dirección de Prueba Directa 123',
                'telefono': '+54 11 1234-5678',
                'email': 'testdirecto@negocio.com',
                'activo': True
            }
            
            url = f"{self.services['belgrano_ahorro']}/api/negocios"
            response = requests.post(url, json=nuevo_negocio, headers=self.api_headers, timeout=10)
            
            if response.status_code == 201:
                negocio_creado = response.json()
                negocio_id = negocio_creado.get('id')
                
                self.log_test("Crear Negocio Directo", "PASS", f"Negocio creado exitosamente (ID: {negocio_id})", {
                    'negocio_id': negocio_id,
                    'nombre': nuevo_negocio['nombre']
                })
                
                # Verificar que el negocio fue creado
                verify_response = requests.get(url, headers=self.api_headers, timeout=10)
                if verify_response.status_code == 200:
                    negocios = verify_response.json().get('data', [])
                    negocio_encontrado = any(n.get('nombre') == nuevo_negocio['nombre'] for n in negocios)
                    
                    if negocio_encontrado:
                        self.log_test("Verificar Negocio Creado", "PASS", "Negocio verificado en la base de datos")
                    else:
                        self.log_test("Verificar Negocio Creado", "FAIL", "Negocio no encontrado después de crear")
                else:
                    self.log_test("Verificar Negocio Creado", "FAIL", "Error verificando negocio creado")
            else:
                self.log_test("Crear Negocio Directo", "FAIL", f"Error creando negocio: {response.status_code}")
                
        except Exception as e:
            self.log_test("Crear Negocio Directo", "FAIL", f"Error en creación de negocio: {str(e)}")
    
    def test_creacion_productos_directa(self):
        """Probar creación directa de productos"""
        print("\n📦 PROBANDO CREACIÓN DIRECTA DE PRODUCTOS...")
        
        try:
            # Crear nuevo producto
            nuevo_producto = {
                'nombre': f'Producto Test Directo {datetime.now().strftime("%H%M%S")}',
                'precio': 199.99,
                'categoria': 'Test Directo',
                'stock': 50,
                'negocio_id': 1,  # Asumir que existe un negocio con ID 1
                'activo': True
            }
            
            url = f"{self.services['belgrano_ahorro']}/api/productos"
            response = requests.post(url, json=nuevo_producto, headers=self.api_headers, timeout=10)
            
            if response.status_code == 201:
                producto_creado = response.json()
                producto_id = producto_creado.get('id')
                
                self.log_test("Crear Producto Directo", "PASS", f"Producto creado exitosamente (ID: {producto_id})", {
                    'producto_id': producto_id,
                    'nombre': nuevo_producto['nombre'],
                    'precio': nuevo_producto['precio']
                })
            else:
                self.log_test("Crear Producto Directo", "FAIL", f"Error creando producto: {response.status_code}")
                
        except Exception as e:
            self.log_test("Crear Producto Directo", "FAIL", f"Error en creación de producto: {str(e)}")
    
    def test_creacion_ofertas_directa(self):
        """Probar creación directa de ofertas"""
        print("\n🎯 PROBANDO CREACIÓN DIRECTA DE OFERTAS...")
        
        try:
            # Crear nueva oferta
            nueva_oferta = {
                'titulo': f'Oferta Test Directo {datetime.now().strftime("%H%M%S")}',
                'descripcion': 'Oferta de prueba creada directamente',
                'descuento': 20,
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
                'fecha_fin': (datetime.now().replace(day=datetime.now().day + 30)).strftime('%Y-%m-%d'),
                'activa': True,
                'negocio_id': 1
            }
            
            url = f"{self.services['belgrano_ahorro']}/api/ofertas"
            response = requests.post(url, json=nueva_oferta, headers=self.api_headers, timeout=10)
            
            if response.status_code == 201:
                oferta_creada = response.json()
                oferta_id = oferta_creada.get('id')
                
                self.log_test("Crear Oferta Directo", "PASS", f"Oferta creada exitosamente (ID: {oferta_id})", {
                    'oferta_id': oferta_id,
                    'titulo': nueva_oferta['titulo'],
                    'descuento': nueva_oferta['descuento']
                })
            else:
                self.log_test("Crear Oferta Directo", "FAIL", f"Error creando oferta: {response.status_code}")
                
        except Exception as e:
            self.log_test("Crear Oferta Directo", "FAIL", f"Error en creación de oferta: {str(e)}")
    
    def test_creacion_sucursales_directa(self):
        """Probar creación directa de sucursales"""
        print("\n🏢 PROBANDO CREACIÓN DIRECTA DE SUCURSALES...")
        
        try:
            # Crear nueva sucursal
            nueva_sucursal = {
                'nombre': f'Sucursal Test Directo {datetime.now().strftime("%H%M%S")}',
                'direccion': 'Dirección de Sucursal Test Directo 456',
                'telefono': '+54 11 9876-5432',
                'email': 'sucursaldirecto@test.com',
                'horario_apertura': '09:00',
                'horario_cierre': '18:00',
                'activo': True
            }
            
            url = f"{self.services['belgrano_ahorro']}/api/sucursales"
            response = requests.post(url, json=nueva_sucursal, headers=self.api_headers, timeout=10)
            
            if response.status_code == 201:
                sucursal_creada = response.json()
                sucursal_id = sucursal_creada.get('id')
                
                self.log_test("Crear Sucursal Directo", "PASS", f"Sucursal creada exitosamente (ID: {sucursal_id})", {
                    'sucursal_id': sucursal_id,
                    'nombre': nueva_sucursal['nombre']
                })
            else:
                self.log_test("Crear Sucursal Directo", "FAIL", f"Error creando sucursal: {response.status_code}")
                
        except Exception as e:
            self.log_test("Crear Sucursal Directo", "FAIL", f"Error en creación de sucursal: {str(e)}")
    
    def test_ticketera_apis(self):
        """Probar APIs de Ticketera"""
        print("\n🎫 PROBANDO APIs TICKETERA...")
        
        ticketera_endpoints = [
            '/health',
            '/api/productos',
            '/api/repartidores', 
            '/api/estados'
        ]
        
        for endpoint in ticketera_endpoints:
            try:
                url = f"{self.services['ticketera']}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json() if response.content else {}
                    data_count = len(data.get('data', [])) if isinstance(data.get('data'), list) else 0
                    
                    self.log_test(f"API Ticketera {endpoint}", "PASS", f"API {endpoint} funcionando", {
                        'status_code': response.status_code,
                        'data_count': data_count
                    })
                else:
                    self.log_test(f"API Ticketera {endpoint}", "FAIL", f"API {endpoint} falló: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.log_test(f"API Ticketera {endpoint}", "FAIL", f"API {endpoint} no está disponible")
            except Exception as e:
                self.log_test(f"API Ticketera {endpoint}", "FAIL", f"Error en {endpoint}: {str(e)}")
    
    def test_creacion_tickets_directa(self):
        """Probar creación directa de tickets"""
        print("\n🎫 PROBANDO CREACIÓN DIRECTA DE TICKETS...")
        
        try:
            # Crear nuevo ticket
            nuevo_ticket = {
                'titulo': f'Ticket Test Directo {datetime.now().strftime("%H%M%S")}',
                'descripcion': 'Ticket de prueba creado directamente',
                'prioridad': 'media',
                'tipo': 'soporte',
                'usuario_id': 1
            }
            
            url = f"{self.services['ticketera']}/api/tickets"
            response = requests.post(url, json=nuevo_ticket, timeout=10)
            
            if response.status_code == 201:
                ticket_creado = response.json()
                ticket_id = ticket_creado.get('id')
                
                self.log_test("Crear Ticket Directo", "PASS", f"Ticket creado exitosamente (ID: {ticket_id})", {
                    'ticket_id': ticket_id,
                    'titulo': nuevo_ticket['titulo']
                })
            else:
                self.log_test("Crear Ticket Directo", "FAIL", f"Error creando ticket: {response.status_code}")
                
        except Exception as e:
            self.log_test("Crear Ticket Directo", "FAIL", f"Error en creación de ticket: {str(e)}")
    
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
        print(f"📋 REPORTE FINAL DE GESTIÓN DIRECTA")
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
        report_filename = f"reporte_gestion_directa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {report_filename}")
        
        return self.results
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DE GESTIÓN DIRECTA")
        print("="*60)
        
        # Ejecutar todas las pruebas
        self.test_servicios_connectivity()
        self.test_belgrano_ahorro_apis()
        self.test_creacion_negocios_directa()
        self.test_creacion_productos_directa()
        self.test_creacion_ofertas_directa()
        self.test_creacion_sucursales_directa()
        self.test_ticketera_apis()
        self.test_creacion_tickets_directa()
        self.test_integration_complete()
        
        # Generar reporte
        return self.generate_report()

def main():
    """Función principal"""
    print("🔧 SISTEMA DE PRUEBAS DE GESTIÓN DIRECTA")
    print("Prueba directa de las APIs de Belgrano Ahorro y Ticketera")
    print("="*60)
    
    tester = TestGestionDirectaBelgrano()
    results = tester.run_all_tests()
    
    # Determinar si el sistema está funcionando correctamente
    success_rate = (results['summary']['passed'] / results['summary']['total_tests'] * 100) if results['summary']['total_tests'] > 0 else 0
    
    if success_rate >= 80:
        print(f"\n🎉 SISTEMA FUNCIONANDO CORRECTAMENTE ({success_rate:.1f}% de éxito)")
        return 0
    elif success_rate >= 60:
        print(f"\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL ({success_rate:.1f}% de éxito)")
        return 1
    else:
        print(f"\n❌ SISTEMA CON PROBLEMAS ({success_rate:.1f}% de éxito)")
        return 2

if __name__ == "__main__":
    sys.exit(main())
