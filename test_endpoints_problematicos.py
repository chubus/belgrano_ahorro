#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testear específicamente los endpoints problemáticos identificados
"""

import requests
import json
import time
from datetime import datetime

class ProblematicEndpointsTester:
    def __init__(self):
        self.base_url_ahorro = "http://localhost:5000"
        self.base_url_ticketera = "http://localhost:5001"
        self.results = []
        
    def test_endpoint(self, url, method="GET", data=None, expected_status=None):
        """Testear un endpoint específico"""
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                print(f"❌ Método {method} no soportado")
                return False
            
            status_ok = response.status_code < 400
            if expected_status:
                status_ok = response.status_code == expected_status
            
            if status_ok:
                print(f"✅ {method} {url} - {response.status_code}")
            else:
                print(f"❌ {method} {url} - {response.status_code} (esperado: {expected_status})")
            
            return status_ok
            
        except requests.exceptions.ConnectionError:
            print(f"❌ {method} {url} - Connection Error (servicio no disponible)")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ {method} {url} - Timeout")
            return False
        except Exception as e:
            print(f"❌ {method} {url} - Error: {e}")
            return False
    
    def test_duplicate_endpoints(self):
        """Testear endpoints duplicados identificados"""
        print("\n🔄 TESTEANDO ENDPOINTS DUPLICADOS")
        print("=" * 50)
        
        # Endpoints duplicados encontrados
        duplicate_endpoints = [
            # /api/tickets aparece en múltiples archivos
            (f"{self.base_url_ahorro}/api/tickets", "GET"),
            (f"{self.base_url_ahorro}/api/tickets", "POST"),
            (f"{self.base_url_ticketera}/api/tickets", "GET"),
            (f"{self.base_url_ticketera}/api/tickets", "POST"),
        ]
        
        for url, method in duplicate_endpoints:
            if method == "POST":
                self.test_endpoint(url, method, {"test": "data"})
            else:
                self.test_endpoint(url, method)
    
    def test_security_endpoints(self):
        """Testear endpoints con problemas de seguridad"""
        print("\n🔒 TESTEANDO ENDPOINTS DE SEGURIDAD")
        print("=" * 50)
        
        # Endpoints sensibles que deberían requerir autenticación
        security_endpoints = [
            (f"{self.base_url_ahorro}/admin", "GET"),
            (f"{self.base_url_ahorro}/gestion_flota", "GET"),
            (f"{self.base_url_ticketera}/debug", "GET"),
            (f"{self.base_url_ticketera}/reinicializar", "GET"),
            (f"{self.base_url_ticketera}/crear_admin_emergencia", "GET"),
        ]
        
        for url, method in security_endpoints:
            # Estos endpoints deberían devolver 401 o 403 si no están autenticados
            self.test_endpoint(url, method, expected_status=401)
    
    def test_validation_endpoints(self):
        """Testear endpoints con problemas de validación"""
        print("\n📝 TESTEANDO VALIDACIÓN DE INPUTS")
        print("=" * 50)
        
        # Datos inválidos para probar validación
        invalid_data_sets = [
            None,
            {},
            {"invalid": "data"},
            {"email": "invalid-email"},
            {"password": ""},
            {"email": "", "password": ""},
            {"email": "test@test.com", "password": "123"},  # Contraseña muy corta
        ]
        
        # Endpoints que deberían validar inputs
        validation_endpoints = [
            (f"{self.base_url_ahorro}/login", "POST"),
            (f"{self.base_url_ahorro}/register", "POST"),
            (f"{self.base_url_ticketera}/login", "POST"),
        ]
        
        for url, method in validation_endpoints:
            print(f"\n🔍 Probando {url}:")
            for data in invalid_data_sets:
                if data is None:
                    print(f"   Probando con datos None...")
                else:
                    print(f"   Probando con {data}...")
                self.test_endpoint(url, method, data, expected_status=400)
    
    def test_debug_endpoints(self):
        """Testear endpoints de debug que no deberían estar en producción"""
        print("\n🛠️ TESTEANDO ENDPOINTS DE DEBUG")
        print("=" * 50)
        
        debug_endpoints = [
            (f"{self.base_url_ticketera}/debug", "GET"),
            (f"{self.base_url_ticketera}/debug/reparar_credenciales", "POST"),
            (f"{self.base_url_ticketera}/reinicializar", "GET"),
            (f"{self.base_url_ticketera}/crear_admin_emergencia", "GET"),
            (f"{self.base_url_ticketera}/crear_flota_emergencia", "GET"),
            (f"{self.base_url_ticketera}/crear_usuarios_directo", "GET"),
        ]
        
        for url, method in debug_endpoints:
            if method == "POST":
                self.test_endpoint(url, method, {"test": "data"})
            else:
                self.test_endpoint(url, method)
    
    def test_parameter_validation(self):
        """Testear validación de parámetros en URLs"""
        print("\n🔗 TESTEANDO VALIDACIÓN DE PARÁMETROS")
        print("=" * 50)
        
        # URLs con parámetros inválidos
        invalid_parameters = [
            (f"{self.base_url_ahorro}/negocio/invalid", "GET"),
            (f"{self.base_url_ahorro}/categoria/", "GET"),
            (f"{self.base_url_ahorro}/ver_pedido/abc", "GET"),  # Debería ser int
            (f"{self.base_url_ahorro}/repetir_pedido/xyz", "GET"),  # Debería ser int
            (f"{self.base_url_ticketera}/ticket/abc/estado", "POST"),  # Debería ser int
        ]
        
        for url, method in invalid_parameters:
            if method == "POST":
                self.test_endpoint(url, method, {"estado": "test"})
            else:
                self.test_endpoint(url, method)
    
    def test_missing_endpoints(self):
        """Testear endpoints que podrían no existir"""
        print("\n❓ TESTEANDO ENDPOINTS INEXISTENTES")
        print("=" * 50)
        
        # Endpoints que probablemente no existan
        missing_endpoints = [
            (f"{self.base_url_ahorro}/endpoint_inexistente", "GET"),
            (f"{self.base_url_ahorro}/api/error", "GET"),
            (f"{self.base_url_ticketera}/endpoint_inexistente", "GET"),
            (f"{self.base_url_ticketera}/api/error", "GET"),
        ]
        
        for url, method in missing_endpoints:
            # Estos deberían devolver 404
            self.test_endpoint(url, method, expected_status=404)
    
    def test_http_methods(self):
        """Testear métodos HTTP no soportados"""
        print("\n🚫 TESTEANDO MÉTODOS HTTP NO SOPORTADOS")
        print("=" * 50)
        
        # Endpoints que no deberían soportar PUT/DELETE
        unsupported_methods = [
            (f"{self.base_url_ahorro}/", "PUT"),
            (f"{self.base_url_ahorro}/", "DELETE"),
            (f"{self.base_url_ticketera}/", "PUT"),
            (f"{self.base_url_ticketera}/", "DELETE"),
        ]
        
        for url, method in unsupported_methods:
            # Estos deberían devolver 405 Method Not Allowed
            self.test_endpoint(url, method, expected_status=405)
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas de endpoints problemáticos"""
        print("🧪 TESTEANDO ENDPOINTS PROBLEMÁTICOS")
        print("=" * 60)
        print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Verificar que al menos un servicio esté disponible
            print("\n🔍 Verificando servicios...")
            health_ahorro = self.test_endpoint(f"{self.base_url_ahorro}/health", "GET")
            health_ticketera = self.test_endpoint(f"{self.base_url_ticketera}/health", "GET")
            
            if not health_ahorro and not health_ticketera:
                print("❌ No se pueden conectar a ningún servicio.")
                print("💡 Asegúrate de que al menos uno de los servicios esté corriendo:")
                print("   - Belgrano Ahorro: python app.py")
                print("   - Ticketera: python belgrano_tickets/app.py")
                return False
            
            # Ejecutar todas las pruebas
            self.test_duplicate_endpoints()
            self.test_security_endpoints()
            self.test_validation_endpoints()
            self.test_debug_endpoints()
            self.test_parameter_validation()
            self.test_missing_endpoints()
            self.test_http_methods()
            
            print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n✅ Pruebas de endpoints problemáticos completadas")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ Pruebas interrumpidas por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ Error durante las pruebas: {e}")
            return False

def main():
    """Función principal"""
    tester = ProblematicEndpointsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Análisis completado. Revisa los resultados arriba.")
    else:
        print("\n⚠️ Análisis incompleto. Revisa los errores arriba.")
    
    return success

if __name__ == "__main__":
    main()
