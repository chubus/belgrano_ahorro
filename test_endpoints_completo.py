#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para testear todos los endpoints y encontrar errores
"""

import requests
import json
import time
import sys
from datetime import datetime

class EndpointTester:
    def __init__(self):
        self.base_url_ahorro = "http://localhost:5000"
        self.base_url_ticketera = "http://localhost:5001"
        self.results = []
        
    def log_result(self, endpoint, method, status_code, response_text, error=None):
        """Registrar resultado de la prueba"""
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response': response_text[:200] + "..." if len(response_text) > 200 else response_text,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Mostrar resultado inmediato
        if error:
            print(f"❌ {method} {endpoint} - Error: {error}")
        elif status_code >= 400:
            print(f"⚠️ {method} {endpoint} - Status: {status_code}")
        else:
            print(f"✅ {method} {endpoint} - Status: {status_code}")
    
    def test_get(self, url, description=""):
        """Probar endpoint GET"""
        try:
            response = requests.get(url, timeout=10)
            self.log_result(url, "GET", response.status_code, response.text)
            return response.status_code < 400
        except Exception as e:
            self.log_result(url, "GET", 0, "", str(e))
            return False
    
    def test_post(self, url, data=None, description=""):
        """Probar endpoint POST"""
        try:
            headers = {'Content-Type': 'application/json'} if data else {}
            response = requests.post(url, json=data, headers=headers, timeout=10)
            self.log_result(url, "POST", response.status_code, response.text)
            return response.status_code < 400
        except Exception as e:
            self.log_result(url, "POST", 0, "", str(e))
            return False
    
    def test_belgrano_ahorro_endpoints(self):
        """Testear endpoints de Belgrano Ahorro"""
        print("\n🛒 TESTEANDO ENDPOINTS DE BELGRANO AHORRO")
        print("=" * 50)
        
        endpoints = [
            "/",  # Página principal
            "/login",  # Login
            "/register",  # Registro
            "/productos",  # Productos
            "/carrito",  # Carrito
            "/checkout",  # Checkout
            "/mis_pedidos",  # Mis pedidos
            "/perfil",  # Perfil
            "/admin",  # Admin (redirige a ticketera)
            "/ticketera",  # Ticketera (redirige)
        ]
        
        for endpoint in endpoints:
            self.test_get(f"{self.base_url_ahorro}{endpoint}")
    
    def test_ticketera_endpoints(self):
        """Testear endpoints de Ticketera"""
        print("\n🎫 TESTEANDO ENDPOINTS DE TICKETERA")
        print("=" * 50)
        
        # Endpoints públicos
        public_endpoints = [
            "/",  # Página principal
            "/login",  # Login
            "/health",  # Health check
            "/api/tickets",  # API tickets (GET)
        ]
        
        for endpoint in public_endpoints:
            self.test_get(f"{self.base_url_ticketera}{endpoint}")
        
        # Testear API POST con datos de prueba
        test_ticket_data = {
            "cliente": "Test Cliente",
            "productos": ["Producto Test"],
            "total": 1000,
            "numero_pedido": f"TEST-{int(time.time())}",
            "direccion": "Dirección Test",
            "telefono": "1234567890",
            "email": "test@test.com",
            "metodo_pago": "efectivo",
            "notas": "Prueba de endpoint"
        }
        
        self.test_post(f"{self.base_url_ticketera}/api/tickets", test_ticket_data)
    
    def test_protected_endpoints(self):
        """Testear endpoints protegidos (sin autenticación)"""
        print("\n🔒 TESTEANDO ENDPOINTS PROTEGIDOS (sin auth)")
        print("=" * 50)
        
        protected_endpoints = [
            "/panel",  # Panel admin
            "/tickets",  # Lista tickets
            "/gestion_flota",  # Gestión flota
            "/gestion_usuarios",  # Gestión usuarios
            "/reportes",  # Reportes
            "/perfil",  # Perfil
        ]
        
        for endpoint in protected_endpoints:
            self.test_get(f"{self.base_url_ticketera}{endpoint}")
    
    def test_api_endpoints(self):
        """Testear endpoints de API específicos"""
        print("\n📡 TESTEANDO ENDPOINTS DE API")
        print("=" * 50)
        
        # Testear diferentes formatos de datos
        test_cases = [
            {
                "name": "Datos completos válidos",
                "data": {
                    "cliente": "Juan Pérez",
                    "productos": ["Arroz", "Aceite"],
                    "total": 3500,
                    "numero_pedido": f"TEST-COMPLETO-{int(time.time())}",
                    "direccion": "Av. Belgrano 123",
                    "telefono": "1234567890",
                    "email": "juan@test.com",
                    "metodo_pago": "efectivo",
                    "notas": "Prueba completa"
                }
            },
            {
                "name": "Datos mínimos",
                "data": {
                    "cliente": "Cliente Mínimo",
                    "productos": ["Producto"],
                    "total": 100
                }
            },
            {
                "name": "Datos inválidos (sin cliente)",
                "data": {
                    "productos": ["Producto"],
                    "total": 100
                }
            },
            {
                "name": "Datos inválidos (sin productos)",
                "data": {
                    "cliente": "Cliente",
                    "total": 100
                }
            },
            {
                "name": "Datos inválidos (sin total)",
                "data": {
                    "cliente": "Cliente",
                    "productos": ["Producto"]
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🧪 Probando: {test_case['name']}")
            self.test_post(f"{self.base_url_ticketera}/api/tickets", test_case['data'])
    
    def test_error_scenarios(self):
        """Testear escenarios de error"""
        print("\n🚨 TESTEANDO ESCENARIOS DE ERROR")
        print("=" * 50)
        
        # Endpoints que no existen
        non_existent = [
            "/endpoint-que-no-existe",
            "/api/endpoint-inexistente",
            "/admin/panel-inexistente",
            "/tickets/999999",  # Ticket que no existe
        ]
        
        for endpoint in non_existent:
            self.test_get(f"{self.base_url_ticketera}{endpoint}")
        
        # Datos malformados
        malformed_data = [
            None,  # Sin datos
            "datos_invalidos",  # String en lugar de JSON
            {"cliente": None},  # Cliente null
            {"cliente": "", "productos": [], "total": -1},  # Datos vacíos y negativos
        ]
        
        for i, data in enumerate(malformed_data):
            print(f"\n🧪 Probando datos malformados #{i+1}")
            self.test_post(f"{self.base_url_ticketera}/api/tickets", data)
    
    def test_health_and_status(self):
        """Testear health checks y status"""
        print("\n🏥 TESTEANDO HEALTH CHECKS")
        print("=" * 50)
        
        health_endpoints = [
            "/health",
            "/status",
            "/ping",
            "/api/health",
        ]
        
        for endpoint in health_endpoints:
            self.test_get(f"{self.base_url_ticketera}{endpoint}")
            self.test_get(f"{self.base_url_ahorro}{endpoint}")
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DE ENDPOINTS")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Belgrano Ahorro: {self.base_url_ahorro}")
        print(f"Ticketera: {self.base_url_ticketera}")
        print("=" * 60)
        
        # Ejecutar todas las pruebas
        self.test_health_and_status()
        self.test_belgrano_ahorro_endpoints()
        self.test_ticketera_endpoints()
        self.test_protected_endpoints()
        self.test_api_endpoints()
        self.test_error_scenarios()
        
        # Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Generar reporte de resultados"""
        print("\n📊 REPORTE DE RESULTADOS")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful = len([r for r in self.results if r['status_code'] < 400 and not r['error']])
        failed = total_tests - successful
        
        print(f"Total de pruebas: {total_tests}")
        print(f"✅ Exitosas: {successful}")
        print(f"❌ Fallidas: {failed}")
        print(f"📈 Tasa de éxito: {(successful/total_tests)*100:.1f}%")
        
        # Mostrar errores encontrados
        if failed > 0:
            print(f"\n🚨 ERRORES ENCONTRADOS ({failed}):")
            print("-" * 40)
            
            for result in self.results:
                if result['error'] or result['status_code'] >= 400:
                    print(f"❌ {result['method']} {result['endpoint']}")
                    if result['error']:
                        print(f"   Error: {result['error']}")
                    else:
                        print(f"   Status: {result['status_code']}")
                        print(f"   Response: {result['response'][:100]}...")
                    print()
        
        # Guardar reporte en archivo
        report_file = f"endpoint_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        # Recomendaciones
        if failed > 0:
            print(f"\n💡 RECOMENDACIONES:")
            print("- Verificar que ambas aplicaciones estén ejecutándose")
            print("- Revisar logs de error en las aplicaciones")
            print("- Verificar configuración de base de datos")
            print("- Comprobar que los templates existan")
        else:
            print(f"\n🎉 ¡TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")

def main():
    """Función principal"""
    tester = EndpointTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
