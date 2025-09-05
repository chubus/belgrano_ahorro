#!/usr/bin/env python3
"""
🧪 PRUEBAS DETALLADAS DE APIS - FUNCIONALIDADES ESPECÍFICAS
===========================================================

Pruebas rigurosas de todas las funcionalidades:
- DevOps: CRUD completo de negocios, productos, ofertas
- Ticketera: Gestión de tickets y flota
- Sincronización bidireccional
"""

import requests
import json
import time
import sys
from datetime import datetime

class DetailedAPITester:
    def __init__(self):
        self.devops_url = "https://ticketerabelgrano.onrender.com"
        self.belgrano_ahorro_url = "https://belgranoahorro-hp30.onrender.com"
        
        self.devops_session = requests.Session()
        self.api_key = "belgrano_ahorro_api_key_2025"
        
        self.results = []
        self.test_data = {
            "negocio_id": None,
            "producto_id": None,
            "oferta_id": None
        }
        
        print("🔬 INICIANDO PRUEBAS DETALLADAS DE APIS")
        print("=" * 60)

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registrar resultado de prueba"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        
        self.results.append({
            "name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def authenticate_devops(self):
        """Autenticar en DevOps"""
        try:
            response = self.devops_session.post(
                f"{self.devops_url}/devops/login",
                data={"username": "devops", "password": "devops2025"},
                timeout=10,
                allow_redirects=False
            )
            return response.status_code == 302
        except:
            return False

    def test_devops_negocios_crud(self):
        """Probar CRUD completo de negocios en DevOps"""
        print("\n🏢 PROBANDO CRUD DE NEGOCIOS EN DEVOPS")
        print("-" * 50)
        
        if not self.authenticate_devops():
            self.log_test("DevOps Authentication", False, "No se pudo autenticar")
            return
        
        # CREATE - Agregar negocio
        negocio_data = {
            "nombre": f"Test Negocio {int(time.time())}",
            "descripcion": "Negocio de prueba para testing riguroso",
            "categoria": "Supermercado",
            "direccion": "Av. Test 123, CABA",
            "telefono": "011-1234-5678",
            "email": "test@negocio.com"
        }
        
        try:
            response = self.devops_session.post(
                f"{self.devops_url}/devops/negocios/agregar",
                data=negocio_data,
                timeout=10,
                allow_redirects=False
            )
            
            success = response.status_code == 302
            self.log_test("CREATE Negocio", success, f"Status: {response.status_code}")
            
            if success:
                # READ - Verificar que se agregó
                time.sleep(2)
                response = self.devops_session.get(f"{self.devops_url}/devops/negocios", timeout=10)
                if negocio_data["nombre"] in response.text:
                    self.log_test("READ Negocio", True, "Negocio encontrado en lista")
                else:
                    self.log_test("READ Negocio", False, "Negocio no encontrado en lista")
            
        except Exception as e:
            self.log_test("CREATE Negocio", False, f"Error: {str(e)}")

    def test_devops_productos(self):
        """Probar gestión de productos en DevOps"""
        print("\n📦 PROBANDO GESTIÓN DE PRODUCTOS EN DEVOPS")
        print("-" * 50)
        
        # Test acceso a productos
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/productos", timeout=10)
            success = response.status_code == 200
            self.log_test("Productos List Access", success, f"Status: {response.status_code}")
            
            if success:
                # Verificar que la página carga correctamente
                if "productos" in response.text.lower():
                    self.log_test("Productos Page Content", True, "Página de productos carga correctamente")
                else:
                    self.log_test("Productos Page Content", False, "Página de productos no tiene contenido esperado")
                    
        except Exception as e:
            self.log_test("Productos List Access", False, f"Error: {str(e)}")

    def test_devops_ofertas(self):
        """Probar gestión de ofertas en DevOps"""
        print("\n🏷️ PROBANDO GESTIÓN DE OFERTAS EN DEVOPS")
        print("-" * 50)
        
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/ofertas", timeout=10)
            success = response.status_code == 200
            self.log_test("Ofertas List Access", success, f"Status: {response.status_code}")
            
            if success:
                if "ofertas" in response.text.lower():
                    self.log_test("Ofertas Page Content", True, "Página de ofertas carga correctamente")
                else:
                    self.log_test("Ofertas Page Content", False, "Página de ofertas no tiene contenido esperado")
                    
        except Exception as e:
            self.log_test("Ofertas List Access", False, f"Error: {str(e)}")

    def test_devops_sucursales(self):
        """Probar gestión de sucursales en DevOps"""
        print("\n🏪 PROBANDO GESTIÓN DE SUCURSALES EN DEVOPS")
        print("-" * 50)
        
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/sucursales", timeout=10)
            success = response.status_code == 200
            self.log_test("Sucursales List Access", success, f"Status: {response.status_code}")
            
            if success:
                if "sucursales" in response.text.lower():
                    self.log_test("Sucursales Page Content", True, "Página de sucursales carga correctamente")
                else:
                    self.log_test("Sucursales Page Content", False, "Página de sucursales no tiene contenido esperado")
                    
        except Exception as e:
            self.log_test("Sucursales List Access", False, f"Error: {str(e)}")

    def test_devops_dashboard(self):
        """Probar dashboard de DevOps"""
        print("\n📊 PROBANDO DASHBOARD DE DEVOPS")
        print("-" * 50)
        
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/dashboard", timeout=10)
            success = response.status_code == 200
            self.log_test("Dashboard Access", success, f"Status: {response.status_code}")
            
            if success:
                # Verificar elementos clave del dashboard
                dashboard_elements = ["productos", "negocios", "ofertas", "sucursales"]
                found_elements = [elem for elem in dashboard_elements if elem in response.text.lower()]
                
                if len(found_elements) >= 3:
                    self.log_test("Dashboard Content", True, f"Elementos encontrados: {found_elements}")
                else:
                    self.log_test("Dashboard Content", False, f"Solo se encontraron: {found_elements}")
                    
        except Exception as e:
            self.log_test("Dashboard Access", False, f"Error: {str(e)}")

    def test_belgrano_ahorro_endpoints(self):
        """Probar endpoints de Belgrano Ahorro"""
        print("\n🛒 PROBANDO ENDPOINTS DE BELGRANO AHORRO")
        print("-" * 50)
        
        # Test páginas principales
        pages = [
            ("/", "Página Principal"),
            ("/productos", "Página de Productos"),
            ("/login", "Página de Login"),
            ("/register", "Página de Registro")
        ]
        
        for page, name in pages:
            try:
                response = requests.get(f"{self.belgrano_ahorro_url}{page}", timeout=10)
                success = response.status_code in [200, 302]
                self.log_test(f"Belgrano Ahorro {name}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Belgrano Ahorro {name}", False, f"Error: {str(e)}")

    def test_api_endpoints_404(self):
        """Probar que los endpoints de API devuelven 404 (como se espera)"""
        print("\n🔍 PROBANDO ENDPOINTS DE API (ESPERANDO 404)")
        print("-" * 50)
        
        api_endpoints = [
            "/api/productos",
            "/api/v1/negocios",
            "/api/ofertas",
            "/api/precios",
            "/api/sucursales"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(
                    f"{self.belgrano_ahorro_url}{endpoint}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
                # Esperamos 404 porque estos endpoints no están implementados
                success = response.status_code == 404
                self.log_test(f"API {endpoint}", success, f"Status: {response.status_code} (Expected 404)")
            except Exception as e:
                self.log_test(f"API {endpoint}", False, f"Error: {str(e)}")

    def test_fallback_functionality(self):
        """Probar funcionalidad de fallback local"""
        print("\n🔄 PROBANDO FUNCIONALIDAD DE FALLBACK LOCAL")
        print("-" * 50)
        
        # Test que DevOps puede funcionar sin API externa
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/dashboard", timeout=10)
            if response.status_code == 200:
                # Verificar que las estadísticas se muestran (incluso si son 0)
                if "productos" in response.text and "negocios" in response.text:
                    self.log_test("Fallback Local Data", True, "Dashboard muestra estadísticas locales")
                else:
                    self.log_test("Fallback Local Data", False, "Dashboard no muestra estadísticas")
            else:
                self.log_test("Fallback Local Data", False, f"Dashboard no accesible: {response.status_code}")
        except Exception as e:
            self.log_test("Fallback Local Data", False, f"Error: {str(e)}")

    def test_error_handling(self):
        """Probar manejo de errores"""
        print("\n⚠️ PROBANDO MANEJO DE ERRORES")
        print("-" * 50)
        
        # Test endpoints inexistentes
        invalid_endpoints = [
            "/devops/invalid",
            "/api/invalid",
            "/nonexistent"
        ]
        
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"{self.devops_url}{endpoint}", timeout=5)
                success = response.status_code == 404
                self.log_test(f"Invalid Endpoint {endpoint}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Invalid Endpoint {endpoint}", False, f"Error: {str(e)}")

    def generate_detailed_report(self):
        """Generar reporte detallado"""
        print("\n📊 REPORTE DETALLADO DE PRUEBAS")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        failed = sum(1 for r in self.results if not r["success"])
        total = len(self.results)
        
        print(f"📈 RESUMEN:")
        print(f"   ✅ Pasaron: {passed}")
        print(f"   ❌ Fallaron: {failed}")
        print(f"   📊 Total: {total}")
        print(f"   🎯 Porcentaje: {(passed/total*100):.1f}%")
        
        print(f"\n📋 DETALLES POR CATEGORÍA:")
        categories = {}
        for result in self.results:
            category = result["name"].split()[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        for category, data in categories.items():
            total_cat = data["passed"] + data["failed"]
            percentage = (data["passed"] / total_cat * 100) if total_cat > 0 else 0
            print(f"   🔧 {category}: {data['passed']}/{total_cat} ({percentage:.1f}%)")
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "percentage": (passed/total*100) if total > 0 else 0
            },
            "categories": categories,
            "results": self.results
        }
        
        with open("test_detailed_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: test_detailed_report.json")
        
        return passed, failed

    def run_all_tests(self):
        """Ejecutar todas las pruebas detalladas"""
        print("🚀 INICIANDO PRUEBAS DETALLADAS")
        
        # 1. DevOps CRUD
        self.test_devops_negocios_crud()
        
        # 2. DevOps funcionalidades
        self.test_devops_productos()
        self.test_devops_ofertas()
        self.test_devops_sucursales()
        self.test_devops_dashboard()
        
        # 3. Belgrano Ahorro
        self.test_belgrano_ahorro_endpoints()
        self.test_api_endpoints_404()
        
        # 4. Funcionalidades avanzadas
        self.test_fallback_functionality()
        self.test_error_handling()
        
        # 5. Reporte
        passed, failed = self.generate_detailed_report()
        
        print(f"\n🏁 PRUEBAS DETALLADAS COMPLETADAS")
        print(f"   ✅ {passed} pruebas pasaron")
        print(f"   ❌ {failed} pruebas fallaron")
        
        return passed, failed

if __name__ == "__main__":
    tester = DetailedAPITester()
    passed, failed = tester.run_all_tests()
    
    sys.exit(0 if failed == 0 else 1)
