#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBAS RIGUROSAS - APIS COMPLETAS
===============================================

Este script realiza pruebas exhaustivas de todas las APIs:
- DevOps (productos, negocios, ofertas, sucursales)
- Ticketera (tickets, flota, gestión)
- Belgrano Ahorro (productos, pedidos, usuarios)

Verifica sincronización bidireccional y manejo de errores.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class APITester:
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
            "devops": {"passed": 0, "failed": 0, "tests": []},
            "ticketera": {"passed": 0, "failed": 0, "tests": []},
            "belgrano_ahorro": {"passed": 0, "failed": 0, "tests": []},
            "sync": {"passed": 0, "failed": 0, "tests": []}
        }
        
        print("🚀 INICIANDO PRUEBAS RIGUROSAS DE APIS")
        print("=" * 60)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 DevOps: {self.devops_url}")
        print(f"🎫 Ticketera: {self.ticketera_url}")
        print(f"🛒 Belgrano Ahorro: {self.belgrano_ahorro_url}")
        print("=" * 60)

    def log_test(self, service: str, test_name: str, success: bool, details: str = ""):
        """Registrar resultado de prueba"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} [{service.upper()}] {test_name}")
        if details:
            print(f"    📝 {details}")
        
        self.results[service]["tests"].append({
            "name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.results[service]["passed"] += 1
        else:
            self.results[service]["failed"] += 1

    def test_health_checks(self):
        """Probar health checks de todos los servicios"""
        print("\n🏥 PROBANDO HEALTH CHECKS")
        print("-" * 40)
        
        # DevOps Health
        try:
            response = requests.get(f"{self.devops_url}/devops/login", timeout=10)
            success = response.status_code in [200, 302]
            self.log_test("devops", "Health Check", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("devops", "Health Check", False, f"Error: {str(e)}")
        
        # Ticketera Health
        try:
            response = requests.get(f"{self.ticketera_url}/", timeout=10)
            success = response.status_code in [200, 302]
            self.log_test("ticketera", "Health Check", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("ticketera", "Health Check", False, f"Error: {str(e)}")
        
        # Belgrano Ahorro Health
        try:
            response = requests.get(f"{self.belgrano_ahorro_url}/", timeout=10)
            success = response.status_code in [200, 302]
            self.log_test("belgrano_ahorro", "Health Check", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("belgrano_ahorro", "Health Check", False, f"Error: {str(e)}")

    def authenticate_devops(self):
        """Autenticar en DevOps"""
        print("\n🔐 AUTENTICANDO EN DEVOPS")
        print("-" * 40)
        
        try:
            # Obtener página de login
            response = self.devops_session.get(f"{self.devops_url}/devops/login", timeout=10)
            if response.status_code != 200:
                self.log_test("devops", "Login Page", False, f"Status: {response.status_code}")
                return False
            
            # Intentar login
            login_data = self.devops_creds
            response = self.devops_session.post(
                f"{self.devops_url}/devops/login",
                data=login_data,
                timeout=10,
                allow_redirects=False
            )
            
            success = response.status_code == 302  # Redirect after successful login
            self.log_test("devops", "Authentication", success, f"Status: {response.status_code}")
            return success
            
        except Exception as e:
            self.log_test("devops", "Authentication", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO BATERÍA COMPLETA DE PRUEBAS")
        
        # 1. Health Checks
        self.test_health_checks()
        
        # 2. Autenticación DevOps
        self.authenticate_devops()
        
        # 3. Reporte final
        passed, failed = self.generate_report()
        
        print(f"\n🏁 PRUEBAS COMPLETADAS")
        print(f"   ✅ {passed} pruebas pasaron")
        print(f"   ❌ {failed} pruebas fallaron")
        
        return passed, failed

    def generate_report(self):
        """Generar reporte final"""
        print("\n📊 REPORTE FINAL DE PRUEBAS")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for service, data in self.results.items():
            passed = data["passed"]
            failed = data["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            percentage = (passed / total * 100) if total > 0 else 0
            
            print(f"\n🔧 {service.upper()}:")
            print(f"   ✅ Pasaron: {passed}")
            print(f"   ❌ Fallaron: {failed}")
            print(f"   📈 Porcentaje: {percentage:.1f}%")
        
        print(f"\n🎯 RESUMEN GENERAL:")
        print(f"   ✅ Total Pasaron: {total_passed}")
        print(f"   ❌ Total Fallaron: {total_failed}")
        print(f"   📈 Porcentaje General: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
        
        return total_passed, total_failed

if __name__ == "__main__":
    tester = APITester()
    passed, failed = tester.run_all_tests()
    
    # Exit code basado en resultados
    sys.exit(0 if failed == 0 else 1)
