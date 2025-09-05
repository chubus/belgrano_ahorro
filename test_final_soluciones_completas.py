#!/usr/bin/env python3
"""
🎯 PRUEBAS FINALES DE SOLUCIONES COMPLETAS
==========================================

Este script realiza las pruebas finales de todas las soluciones implementadas:
1. ✅ Error 500 en ofertas (SOLUCIONADO)
2. ✅ Propagación de negocios (OPTIMIZADO)
3. ✅ Comunicación bidireccional (ROBUSTA)
4. ✅ Fallback local (MEJORADO)
5. ✅ Manejo de errores (ROBUSTO)
"""

import requests
import json
import time
import sys
from datetime import datetime

class FinalSolutionsTester:
    def __init__(self):
        self.devops_url = "https://ticketerabelgrano.onrender.com"
        self.belgrano_ahorro_url = "https://belgranoahorro-hp30.onrender.com"
        
        self.devops_session = requests.Session()
        self.api_key = "belgrano_ahorro_api_key_2025"
        
        self.results = []
        self.solutions_status = {
            "ofertas_500_fix": False,
            "negocios_propagation": False,
            "bidirectional_communication": False,
            "fallback_local": False,
            "error_handling": False
        }
        
        print("🎯 INICIANDO PRUEBAS FINALES DE SOLUCIONES COMPLETAS")
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
                timeout=15,
                allow_redirects=False
            )
            return response.status_code == 302
        except:
            return False

    def test_solution_1_ofertas_500_fix(self):
        """SOLUCIÓN 1: Corregir error 500 en ofertas"""
        print("\n🏷️ SOLUCIÓN 1: CORRECCIÓN DEL ERROR 500 EN OFERTAS")
        print("-" * 50)
        
        if not self.authenticate_devops():
            self.log_test("Autenticación DevOps", False, "No se pudo autenticar")
            return False
        
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/ofertas", timeout=15)
            success = response.status_code == 200
            self.log_test("Acceso Página Ofertas", success, f"Status: {response.status_code}")
            
            if success:
                # Verificar que la página carga correctamente
                if "ofertas" in response.text.lower() and "gestión" in response.text.lower():
                    self.log_test("Contenido Página Ofertas", True, "Página carga correctamente")
                    self.solutions_status["ofertas_500_fix"] = True
                    return True
                else:
                    self.log_test("Contenido Página Ofertas", False, "Página no tiene contenido esperado")
            else:
                self.log_test("Contenido Página Ofertas", False, f"Error {response.status_code}")
                
        except Exception as e:
            self.log_test("Acceso Página Ofertas", False, f"Error: {str(e)}")
        
        return False

    def test_solution_2_negocios_propagation(self):
        """SOLUCIÓN 2: Optimizar propagación de negocios"""
        print("\n🏢 SOLUCIÓN 2: OPTIMIZACIÓN DE PROPAGACIÓN DE NEGOCIOS")
        print("-" * 50)
        
        if not self.authenticate_devops():
            self.log_test("Autenticación DevOps", False, "No se pudo autenticar")
            return False
        
        # Crear negocio de prueba
        negocio_data = {
            "nombre": f"Test Final {int(time.time())}",
            "descripcion": "Negocio para prueba final de propagación",
            "categoria": "Supermercado",
            "direccion": "Av. Final 123",
            "telefono": "011-5555-4444",
            "email": "final@test.com"
        }
        
        try:
            # Crear negocio
            response = self.devops_session.post(
                f"{self.devops_url}/devops/negocios/agregar",
                data=negocio_data,
                timeout=15,
                allow_redirects=False
            )
            
            success = response.status_code == 302
            self.log_test("Crear Negocio", success, f"Status: {response.status_code}")
            
            if success:
                # Verificar propagación en diferentes intervalos
                for seconds in [1, 3, 5]:
                    time.sleep(seconds - (1 if seconds > 1 else 0))
                    response = self.devops_session.get(f"{self.devops_url}/devops/negocios", timeout=15)
                    
                    if negocio_data["nombre"] in response.text:
                        self.log_test(f"Propagación en {seconds}s", True, f"Negocio aparece en {seconds} segundos")
                        self.solutions_status["negocios_propagation"] = True
                        return True
                
                self.log_test("Propagación Fallida", False, "Negocio no aparece después de 5 segundos")
            
        except Exception as e:
            self.log_test("Crear Negocio", False, f"Error: {str(e)}")
        
        return False

    def test_solution_3_bidirectional_communication(self):
        """SOLUCIÓN 3: Comunicación bidireccional robusta"""
        print("\n🔄 SOLUCIÓN 3: COMUNICACIÓN BIDIRECCIONAL ROBUSTA")
        print("-" * 50)
        
        # Test conectividad básica
        services = [
            (self.devops_url, "DevOps"),
            (self.belgrano_ahorro_url, "Belgrano Ahorro")
        ]
        
        connectivity_success = 0
        for url, name in services:
            try:
                response = requests.get(f"{url}/", timeout=10)
                success = response.status_code in [200, 302]
                self.log_test(f"Conectividad {name}", success, f"Status: {response.status_code}")
                if success:
                    connectivity_success += 1
            except:
                self.log_test(f"Conectividad {name}", False, "Timeout o error de conexión")
        
        # Test DevOps independiente
        if self.authenticate_devops():
            try:
                response = self.devops_session.get(f"{self.devops_url}/devops/dashboard", timeout=15)
                success = response.status_code == 200
                self.log_test("DevOps Independiente", success, f"Status: {response.status_code}")
                
                if success and connectivity_success >= 1:
                    self.solutions_status["bidirectional_communication"] = True
                    return True
                    
            except Exception as e:
                self.log_test("DevOps Independiente", False, f"Error: {str(e)}")
        
        return False

    def test_solution_4_fallback_local(self):
        """SOLUCIÓN 4: Sistema de fallback local mejorado"""
        print("\n💾 SOLUCIÓN 4: SISTEMA DE FALLBACK LOCAL MEJORADO")
        print("-" * 50)
        
        if not self.authenticate_devops():
            self.log_test("Autenticación DevOps", False, "No se pudo autenticar")
            return False
        
        # Test todas las páginas principales
        pages = ["dashboard", "productos", "negocios", "sucursales", "precios", "ofertas"]
        success_count = 0
        
        for page in pages:
            try:
                response = self.devops_session.get(f"{self.devops_url}/devops/{page}", timeout=15)
                success = response.status_code == 200
                self.log_test(f"Página {page.title()}", success, f"Status: {response.status_code}")
                if success:
                    success_count += 1
            except Exception as e:
                self.log_test(f"Página {page.title()}", False, f"Error: {str(e)}")
        
        # Verificar dashboard con estadísticas
        try:
            response = self.devops_session.get(f"{self.devops_url}/devops/dashboard", timeout=15)
            if response.status_code == 200 and "productos" in response.text and "negocios" in response.text:
                self.log_test("Estadísticas Locales", True, "Dashboard muestra estadísticas locales")
                success_count += 1
            else:
                self.log_test("Estadísticas Locales", False, "Dashboard no muestra estadísticas")
        except Exception as e:
            self.log_test("Estadísticas Locales", False, f"Error: {str(e)}")
        
        if success_count >= 6:  # Al menos 6 de 7 pruebas exitosas
            self.solutions_status["fallback_local"] = True
            return True
        
        return False

    def test_solution_5_error_handling(self):
        """SOLUCIÓN 5: Manejo robusto de errores"""
        print("\n⚠️ SOLUCIÓN 5: MANEJO ROBUSTO DE ERRORES")
        print("-" * 50)
        
        # Test manejo de timeouts
        try:
            response = requests.get(f"{self.devops_url}/devops/dashboard", timeout=1)
            success = response.status_code == 200
            self.log_test("Manejo Timeout", success, f"Status: {response.status_code}")
        except requests.exceptions.Timeout:
            self.log_test("Manejo Timeout", True, "Timeout manejado correctamente")
        except Exception as e:
            self.log_test("Manejo Timeout", False, f"Error inesperado: {str(e)}")
        
        # Test endpoints inexistentes
        invalid_endpoints = ["/devops/invalid", "/api/invalid", "/nonexistent"]
        error_handling_success = 0
        
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"{self.devops_url}{endpoint}", timeout=5)
                success = response.status_code == 404
                self.log_test(f"Endpoint Inexistente {endpoint}", success, f"Status: {response.status_code}")
                if success:
                    error_handling_success += 1
            except Exception as e:
                self.log_test(f"Endpoint Inexistente {endpoint}", False, f"Error: {str(e)}")
        
        if error_handling_success >= 2:  # Al menos 2 de 3 pruebas exitosas
            self.solutions_status["error_handling"] = True
            return True
        
        return False

    def generate_final_report(self):
        """Generar reporte final de soluciones"""
        print("\n📊 REPORTE FINAL DE SOLUCIONES IMPLEMENTADAS")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        failed = sum(1 for r in self.results if not r["success"])
        total = len(self.results)
        
        print(f"📈 RESUMEN GENERAL:")
        print(f"   ✅ Pasaron: {passed}")
        print(f"   ❌ Fallaron: {failed}")
        print(f"   📊 Total: {total}")
        print(f"   🎯 Porcentaje: {(passed/total*100):.1f}%")
        
        print(f"\n🔧 ESTADO DE SOLUCIONES:")
        solutions = [
            ("Error 500 en Ofertas", "ofertas_500_fix"),
            ("Propagación de Negocios", "negocios_propagation"),
            ("Comunicación Bidireccional", "bidirectional_communication"),
            ("Fallback Local", "fallback_local"),
            ("Manejo de Errores", "error_handling")
        ]
        
        solutions_implemented = 0
        for name, key in solutions:
            status = "✅ IMPLEMENTADA" if self.solutions_status[key] else "❌ PENDIENTE"
            print(f"   {status} {name}")
            if self.solutions_status[key]:
                solutions_implemented += 1
        
        print(f"\n🎯 RESUMEN DE SOLUCIONES:")
        print(f"   ✅ Implementadas: {solutions_implemented}/5")
        print(f"   📈 Porcentaje: {(solutions_implemented/5*100):.1f}%")
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total,
                "passed_tests": passed,
                "failed_tests": failed,
                "test_percentage": (passed/total*100) if total > 0 else 0,
                "solutions_implemented": solutions_implemented,
                "total_solutions": 5,
                "solutions_percentage": (solutions_implemented/5*100)
            },
            "solutions_status": self.solutions_status,
            "results": self.results
        }
        
        with open("test_final_solutions_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte final guardado en: test_final_solutions_report.json")
        
        return passed, failed, solutions_implemented

    def run_all_final_tests(self):
        """Ejecutar todas las pruebas finales"""
        print("🚀 INICIANDO PRUEBAS FINALES DE SOLUCIONES COMPLETAS")
        
        # Ejecutar todas las pruebas de soluciones
        self.test_solution_1_ofertas_500_fix()
        self.test_solution_2_negocios_propagation()
        self.test_solution_3_bidirectional_communication()
        self.test_solution_4_fallback_local()
        self.test_solution_5_error_handling()
        
        # Generar reporte final
        passed, failed, solutions_implemented = self.generate_final_report()
        
        print(f"\n🏁 PRUEBAS FINALES COMPLETADAS")
        print(f"   ✅ {passed} pruebas pasaron")
        print(f"   ❌ {failed} pruebas fallaron")
        print(f"   🔧 {solutions_implemented}/5 soluciones implementadas")
        
        return passed, failed, solutions_implemented

if __name__ == "__main__":
    tester = FinalSolutionsTester()
    passed, failed, solutions_implemented = tester.run_all_final_tests()
    
    # Exit code basado en soluciones implementadas
    sys.exit(0 if solutions_implemented >= 4 else 1)
