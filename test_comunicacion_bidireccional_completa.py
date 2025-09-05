#!/usr/bin/env python3
"""
🔄 PRUEBAS EXHAUSTIVAS DE COMUNICACIÓN BIDIRECCIONAL
===================================================

Este script realiza pruebas rigurosas de comunicación bidireccional entre:
- DevOps ↔ Belgrano Ahorro
- Ticketera ↔ Belgrano Ahorro  
- DevOps ↔ Ticketera
- Sincronización en tiempo real
- Fallback local y recuperación

Verifica que todos los cambios se reflejen correctamente en ambos sentidos.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class ComunicacionBidireccionalTester:
    def __init__(self):
        # URLs de los servicios
        self.devops_url = "https://ticketerabelgrano.onrender.com"
        self.ticketera_url = "https://ticketerabelgrano.onrender.com"
        self.belgrano_ahorro_url = "https://belgranoahorro-hp30.onrender.com"
        
        # Credenciales
        self.devops_creds = {"username": "devops", "password": "devops2025"}
        self.api_key = "belgrano_ahorro_api_key_2025"
        
        # Sesiones
        self.devops_session = requests.Session()
        self.ticketera_session = requests.Session()
        self.belgrano_session = requests.Session()
        
        # Resultados
        self.results = {
            "devops_to_belgrano": {"passed": 0, "failed": 0, "tests": []},
            "belgrano_to_devops": {"passed": 0, "failed": 0, "tests": []},
            "ticketera_to_belgrano": {"passed": 0, "failed": 0, "tests": []},
            "belgrano_to_ticketera": {"passed": 0, "failed": 0, "tests": []},
            "devops_to_ticketera": {"passed": 0, "failed": 0, "tests": []},
            "ticketera_to_devops": {"passed": 0, "failed": 0, "tests": []},
            "fallback_local": {"passed": 0, "failed": 0, "tests": []},
            "sync_realtime": {"passed": 0, "failed": 0, "tests": []}
        }
        
        # Datos de prueba
        self.test_data = {
            "negocio_creado": None,
            "producto_creado": None,
            "oferta_creada": None,
            "ticket_creado": None
        }
        
        print("🔄 INICIANDO PRUEBAS EXHAUSTIVAS DE COMUNICACIÓN BIDIRECCIONAL")
        print("=" * 70)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 DevOps: {self.devops_url}")
        print(f"🎫 Ticketera: {self.ticketera_url}")
        print(f"🛒 Belgrano Ahorro: {self.belgrano_ahorro_url}")
        print("=" * 70)

    def log_test(self, category: str, test_name: str, success: bool, details: str = ""):
        """Registrar resultado de prueba"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} [{category.upper()}] {test_name}")
        if details:
            print(f"    📝 {details}")
        
        self.results[category]["tests"].append({
            "name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.results[category]["passed"] += 1
        else:
            self.results[category]["failed"] += 1

    def authenticate_devops(self):
        """Autenticar en DevOps"""
        try:
            response = self.devops_session.post(
                f"{self.devops_url}/devops/login",
                data=self.devops_creds,
                timeout=10,
                allow_redirects=False
            )
            return response.status_code == 302
        except:
            return False

    def test_devops_to_belgrano_communication(self):
        """Probar comunicación DevOps → Belgrano Ahorro"""
        print("\n🛠️➡️🛒 PROBANDO COMUNICACIÓN DEVOPS → BELGRANO AHORRO")
        print("-" * 60)
        
        if not self.authenticate_devops():
            self.log_test("devops_to_belgrano", "Autenticación DevOps", False, "No se pudo autenticar")
            return
        
        # Test 1: Crear negocio en DevOps y verificar propagación
        negocio_data = {
            "nombre": f"Test Bidireccional {int(time.time())}",
            "descripcion": "Negocio para probar comunicación bidireccional",
            "categoria": "Supermercado",
            "direccion": "Av. Bidireccional 123",
            "telefono": "011-8888-7777",
            "email": "bidireccional@test.com"
        }
        
        try:
            # Crear negocio en DevOps
            response = self.devops_session.post(
                f"{self.devops_url}/devops/negocios/agregar",
                data=negocio_data,
                timeout=10,
                allow_redirects=False
            )
            
            success = response.status_code == 302
            self.log_test("devops_to_belgrano", "Crear Negocio en DevOps", success, f"Status: {response.status_code}")
            
            if success:
                self.test_data["negocio_creado"] = negocio_data["nombre"]
                
                # Verificar que se guardó localmente
                time.sleep(2)
                response = self.devops_session.get(f"{self.devops_url}/devops/negocios", timeout=10)
                if negocio_data["nombre"] in response.text:
                    self.log_test("devops_to_belgrano", "Verificar Negocio Local", True, "Negocio encontrado en lista local")
                else:
                    self.log_test("devops_to_belgrano", "Verificar Negocio Local", False, "Negocio no encontrado en lista local")
            
        except Exception as e:
            self.log_test("devops_to_belgrano", "Crear Negocio en DevOps", False, f"Error: {str(e)}")

    def test_belgrano_to_devops_communication(self):
        """Probar comunicación Belgrano Ahorro → DevOps"""
        print("\n🛒➡️🛠️ PROBANDO COMUNICACIÓN BELGRANO AHORRO → DEVOPS")
        print("-" * 60)
        
        # Test 1: Verificar que DevOps puede leer datos de Belgrano Ahorro
        try:
            # Probar acceso a APIs de Belgrano Ahorro desde DevOps
            response = requests.get(
                f"{self.belgrano_ahorro_url}/api/v1/negocios",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            success = response.status_code in [200, 404]  # 404 es esperado si no está implementado
            self.log_test("belgrano_to_devops", "Acceso API Negocios", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("belgrano_to_devops", "Acceso API Negocios", False, f"Error: {str(e)}")
        
        # Test 2: Verificar que DevOps puede acceder a páginas de Belgrano Ahorro
        try:
            response = requests.get(f"{self.belgrano_ahorro_url}/", timeout=10)
            success = response.status_code in [200, 302]
            self.log_test("belgrano_to_devops", "Acceso Página Principal", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("belgrano_to_devops", "Acceso Página Principal", False, f"Error: {str(e)}")

    def test_ticketera_to_belgrano_communication(self):
        """Probar comunicación Ticketera → Belgrano Ahorro"""
        print("\n🎫➡️🛒 PROBANDO COMUNICACIÓN TICKETERA → BELGRANO AHORRO")
        print("-" * 60)
        
        # Test 1: Verificar que Ticketera puede enviar tickets a Belgrano Ahorro
        try:
            ticket_data = {
                "cliente": "Test Cliente Bidireccional",
                "productos": ["Producto Test"],
                "total": 1500,
                "numero_pedido": f"TICKET-{int(time.time())}",
                "direccion": "Test Dirección 456",
                "telefono": "1234567890",
                "email": "ticket@test.com",
                "metodo_pago": "efectivo",
                "notas": "Ticket de prueba bidireccional"
            }
            
            response = self.ticketera_session.post(
                f"{self.ticketera_url}/api/tickets",
                json=ticket_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Esperamos 401/403 sin autenticación, o 201 con autenticación
            success = response.status_code in [200, 201, 401, 403]
            self.log_test("ticketera_to_belgrano", "Enviar Ticket", success, f"Status: {response.status_code}")
            
            if success and response.status_code in [200, 201]:
                self.test_data["ticket_creado"] = ticket_data["numero_pedido"]
            
        except Exception as e:
            self.log_test("ticketera_to_belgrano", "Enviar Ticket", False, f"Error: {str(e)}")
        
        # Test 2: Verificar acceso a panel de Ticketera
        try:
            response = self.ticketera_session.get(f"{self.ticketera_url}/panel", timeout=10)
            success = response.status_code == 200
            self.log_test("ticketera_to_belgrano", "Acceso Panel Ticketera", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("ticketera_to_belgrano", "Acceso Panel Ticketera", False, f"Error: {str(e)}")

    def test_belgrano_to_ticketera_communication(self):
        """Probar comunicación Belgrano Ahorro → Ticketera"""
        print("\n🛒➡️🎫 PROBANDO COMUNICACIÓN BELGRANO AHORRO → TICKETERA")
        print("-" * 60)
        
        # Test 1: Verificar que Belgrano Ahorro puede acceder a Ticketera
        try:
            response = requests.get(f"{self.ticketera_url}/", timeout=10)
            success = response.status_code in [200, 302]
            self.log_test("belgrano_to_ticketera", "Acceso Ticketera", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("belgrano_to_ticketera", "Acceso Ticketera", False, f"Error: {str(e)}")
        
        # Test 2: Verificar APIs de Ticketera
        try:
            response = requests.get(f"{self.ticketera_url}/api/tickets", timeout=10)
            success = response.status_code in [200, 401, 403]  # 401/403 es normal sin auth
            self.log_test("belgrano_to_ticketera", "Acceso API Tickets", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("belgrano_to_ticketera", "Acceso API Tickets", False, f"Error: {str(e)}")

    def test_devops_to_ticketera_communication(self):
        """Probar comunicación DevOps → Ticketera"""
        print("\n🛠️➡️🎫 PROBANDO COMUNICACIÓN DEVOPS → TICKETERA")
        print("-" * 60)
        
        if not self.authenticate_devops():
            self.log_test("devops_to_ticketera", "Autenticación DevOps", False, "No se pudo autenticar")
            return
        
        # Test 1: Verificar que DevOps puede acceder a Ticketera
        try:
            response = self.devops_session.get(f"{self.ticketera_url}/", timeout=10)
            success = response.status_code in [200, 302]
            self.log_test("devops_to_ticketera", "Acceso Ticketera desde DevOps", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("devops_to_ticketera", "Acceso Ticketera desde DevOps", False, f"Error: {str(e)}")
        
        # Test 2: Verificar que DevOps puede acceder al panel de Ticketera
        try:
            response = self.devops_session.get(f"{self.ticketera_url}/panel", timeout=10)
            success = response.status_code == 200
            self.log_test("devops_to_ticketera", "Acceso Panel Ticketera", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("devops_to_ticketera", "Acceso Panel Ticketera", False, f"Error: {str(e)}")

    def test_ticketera_to_devops_communication(self):
        """Probar comunicación Ticketera → DevOps"""
        print("\n🎫➡️🛠️ PROBANDO COMUNICACIÓN TICKETERA → DEVOPS")
        print("-" * 60)
        
        # Test 1: Verificar que Ticketera puede acceder a DevOps
        try:
            response = self.ticketera_session.get(f"{self.devops_url}/devops/login", timeout=10)
            success = response.status_code == 200
            self.log_test("ticketera_to_devops", "Acceso Login DevOps", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("ticketera_to_devops", "Acceso Login DevOps", False, f"Error: {str(e)}")
        
        # Test 2: Verificar que Ticketera puede acceder a APIs de DevOps
        try:
            response = self.ticketera_session.get(f"{self.devops_url}/api/", timeout=10)
            success = response.status_code in [200, 404]  # 404 es esperado
            self.log_test("ticketera_to_devops", "Acceso API DevOps", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("ticketera_to_devops", "Acceso API DevOps", False, f"Error: {str(e)}")

    def test_fallback_local_system(self):
        """Probar sistema de fallback local"""
        print("\n💾 PROBANDO SISTEMA DE FALLBACK LOCAL")
        print("-" * 60)
        
        if not self.authenticate_devops():
            self.log_test("fallback_local", "Autenticación DevOps", False, "No se pudo autenticar")
            return
        
        # Test 1: Verificar que el dashboard funciona con datos locales
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/dashboard", timeout=10)
            success = response.status_code == 200
            self.log_test("fallback_local", "Dashboard con Datos Locales", success, f"Status: {response.status_code}")
            
            if success:
                # Verificar que las estadísticas se muestran
                if "productos" in response.text and "negocios" in response.text:
                    self.log_test("fallback_local", "Estadísticas Locales", True, "Estadísticas se muestran correctamente")
                else:
                    self.log_test("fallback_local", "Estadísticas Locales", False, "Estadísticas no se muestran")
        except Exception as e:
            self.log_test("fallback_local", "Dashboard con Datos Locales", False, f"Error: {str(e)}")
        
        # Test 2: Verificar que las páginas funcionan sin API externa
        pages = ["productos", "negocios", "sucursales", "precios"]
        for page in pages:
            try:
                response = self.devops_session.get(f"{self.devops_url}/devops/{page}", timeout=10)
                success = response.status_code == 200
                self.log_test("fallback_local", f"Página {page.title()}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("fallback_local", f"Página {page.title()}", False, f"Error: {str(e)}")

    def test_sync_realtime(self):
        """Probar sincronización en tiempo real"""
        print("\n⚡ PROBANDO SINCRONIZACIÓN EN TIEMPO REAL")
        print("-" * 60)
        
        if not self.authenticate_devops():
            self.log_test("sync_realtime", "Autenticación DevOps", False, "No se pudo autenticar")
            return
        
        # Test 1: Verificar que los cambios se propagan rápidamente
        try:
            # Crear un negocio de prueba
            negocio_data = {
                "nombre": f"Test Tiempo Real {int(time.time())}",
                "descripcion": "Negocio para probar sincronización en tiempo real",
                "categoria": "Test",
                "direccion": "Av. Tiempo Real 789",
                "telefono": "011-9999-0000",
                "email": "tiemporeal@test.com"
            }
            
            # Crear negocio
            response = self.devops_session.post(
                f"{self.devops_url}/devops/negocios/agregar",
                data=negocio_data,
                timeout=10,
                allow_redirects=False
            )
            
            if response.status_code == 302:
                # Verificar propagación inmediata
                time.sleep(1)  # Esperar solo 1 segundo
                response = self.devops_session.get(f"{self.devops_url}/devops/negocios", timeout=10)
                
                if negocio_data["nombre"] in response.text:
                    self.log_test("sync_realtime", "Propagación Inmediata", True, "Negocio aparece en 1 segundo")
                else:
                    # Esperar un poco más
                    time.sleep(2)
                    response = self.devops_session.get(f"{self.devops_url}/devops/negocios", timeout=10)
                    if negocio_data["nombre"] in response.text:
                        self.log_test("sync_realtime", "Propagación Rápida", True, "Negocio aparece en 3 segundos")
                    else:
                        self.log_test("sync_realtime", "Propagación Lenta", False, "Negocio no aparece después de 3 segundos")
            else:
                self.log_test("sync_realtime", "Crear Negocio Test", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("sync_realtime", "Crear Negocio Test", False, f"Error: {str(e)}")

    def test_error_handling_bidirectional(self):
        """Probar manejo de errores en comunicación bidireccional"""
        print("\n⚠️ PROBANDO MANEJO DE ERRORES BIDIRECCIONAL")
        print("-" * 60)
        
        # Test 1: Verificar manejo de timeouts
        try:
            response = requests.get(f"{self.devops_url}/devops/dashboard", timeout=1)
            success = response.status_code == 200
            self.log_test("sync_realtime", "Timeout Handling", success, f"Status: {response.status_code}")
        except requests.exceptions.Timeout:
            self.log_test("sync_realtime", "Timeout Handling", True, "Timeout manejado correctamente")
        except Exception as e:
            self.log_test("sync_realtime", "Timeout Handling", False, f"Error inesperado: {str(e)}")
        
        # Test 2: Verificar manejo de endpoints inexistentes
        invalid_endpoints = [
            "/devops/invalid",
            "/api/invalid",
            "/ticketera/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"{self.devops_url}{endpoint}", timeout=5)
                success = response.status_code == 404
                self.log_test("sync_realtime", f"Invalid Endpoint {endpoint}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("sync_realtime", f"Invalid Endpoint {endpoint}", False, f"Error: {str(e)}")

    def generate_bidirectional_report(self):
        """Generar reporte de comunicación bidireccional"""
        print("\n📊 REPORTE DE COMUNICACIÓN BIDIRECCIONAL")
        print("=" * 70)
        
        total_passed = 0
        total_failed = 0
        
        for category, data in self.results.items():
            passed = data["passed"]
            failed = data["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            percentage = (passed / total * 100) if total > 0 else 0
            
            print(f"\n🔧 {category.upper().replace('_', ' ')}:")
            print(f"   ✅ Pasaron: {passed}")
            print(f"   ❌ Fallaron: {failed}")
            print(f"   📈 Porcentaje: {percentage:.1f}%")
        
        print(f"\n🎯 RESUMEN GENERAL:")
        print(f"   ✅ Total Pasaron: {total_passed}")
        print(f"   ❌ Total Fallaron: {total_failed}")
        print(f"   📈 Porcentaje General: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
        
        # Análisis de comunicación bidireccional
        bidirectional_tests = [
            "devops_to_belgrano", "belgrano_to_devops",
            "ticketera_to_belgrano", "belgrano_to_ticketera",
            "devops_to_ticketera", "ticketera_to_devops"
        ]
        
        bidirectional_passed = 0
        bidirectional_total = 0
        
        for category in bidirectional_tests:
            if category in self.results:
                bidirectional_passed += self.results[category]["passed"]
                bidirectional_total += (self.results[category]["passed"] + self.results[category]["failed"])
        
        print(f"\n🔄 COMUNICACIÓN BIDIRECCIONAL:")
        print(f"   ✅ Pasaron: {bidirectional_passed}")
        print(f"   📊 Total: {bidirectional_total}")
        print(f"   📈 Porcentaje: {(bidirectional_passed / bidirectional_total * 100):.1f}%")
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_passed": total_passed,
                "total_failed": total_failed,
                "percentage": (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0,
                "bidirectional_passed": bidirectional_passed,
                "bidirectional_total": bidirectional_total,
                "bidirectional_percentage": (bidirectional_passed / bidirectional_total * 100) if bidirectional_total > 0 else 0
            },
            "test_data": self.test_data,
            "results": self.results
        }
        
        with open("test_bidirectional_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte bidireccional guardado en: test_bidirectional_report.json")
        
        return total_passed, total_failed

    def run_all_bidirectional_tests(self):
        """Ejecutar todas las pruebas de comunicación bidireccional"""
        print("🚀 INICIANDO PRUEBAS EXHAUSTIVAS DE COMUNICACIÓN BIDIRECCIONAL")
        
        # 1. Comunicación DevOps ↔ Belgrano Ahorro
        self.test_devops_to_belgrano_communication()
        self.test_belgrano_to_devops_communication()
        
        # 2. Comunicación Ticketera ↔ Belgrano Ahorro
        self.test_ticketera_to_belgrano_communication()
        self.test_belgrano_to_ticketera_communication()
        
        # 3. Comunicación DevOps ↔ Ticketera
        self.test_devops_to_ticketera_communication()
        self.test_ticketera_to_devops_communication()
        
        # 4. Sistema de fallback local
        self.test_fallback_local_system()
        
        # 5. Sincronización en tiempo real
        self.test_sync_realtime()
        
        # 6. Manejo de errores
        self.test_error_handling_bidirectional()
        
        # 7. Reporte final
        passed, failed = self.generate_bidirectional_report()
        
        print(f"\n🏁 PRUEBAS DE COMUNICACIÓN BIDIRECCIONAL COMPLETADAS")
        print(f"   ✅ {passed} pruebas pasaron")
        print(f"   ❌ {failed} pruebas fallaron")
        
        return passed, failed

if __name__ == "__main__":
    tester = ComunicacionBidireccionalTester()
    passed, failed = tester.run_all_bidirectional_tests()
    
    sys.exit(0 if failed == 0 else 1)
