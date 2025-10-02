#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chequeo de Conectividad DevOps - Belgrano Ahorro
Script para verificar la conectividad entre servicios
"""

import requests
import json
import os
import sys
from datetime import datetime
import sqlite3

class ConectividadChecker:
    """Verificador de conectividad entre DevOps y Belgrano Ahorro"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {}
        }
        
        # URLs de configuración
        self.belgrano_ahorro_url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
        self.belgrano_ahorro_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        self.devops_url = os.environ.get('DEVOPS_URL', 'http://localhost:5002')
        
        # Headers para autenticación
        self.headers = {
            'X-API-Key': self.belgrano_ahorro_api_key,
            'Content-Type': 'application/json'
        }
    
    def test_belgrano_ahorro_health(self):
        """Probar salud de Belgrano Ahorro"""
        test_name = "Belgrano Ahorro Health Check"
        print(f"Probando: {test_name}")
        
        try:
            # Probar endpoint de salud
            health_url = f"{self.belgrano_ahorro_url}/healthz"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                print(f"  [OK] Belgrano Ahorro responde correctamente")
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'success',
                    'response_code': response.status_code,
                    'url': health_url
                })
                return True
            else:
                print(f"  [ERROR] Belgrano Ahorro responde con código {response.status_code}")
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'error',
                    'response_code': response.status_code,
                    'url': health_url
                })
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Error conectando a Belgrano Ahorro: {e}")
            self.results['tests'].append({
                'name': test_name,
                'status': 'error',
                'error': str(e),
                'url': health_url
            })
            return False
    
    def test_belgrano_ahorro_api(self):
        """Probar API de Belgrano Ahorro"""
        test_name = "Belgrano Ahorro API Endpoints"
        print(f"Probando: {test_name}")
        
        endpoints_to_test = [
            '/api/v1/productos',
            '/api/v1/ofertas',
            '/api/v1/negocios'
        ]
        
        success_count = 0
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{self.belgrano_ahorro_url}{endpoint}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"  [OK] {endpoint} - OK")
                    success_count += 1
                else:
                    print(f"  [ERROR] {endpoint} - Código {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  [ERROR] {endpoint} - Error: {e}")
        
        success = success_count == len(endpoints_to_test)
        self.results['tests'].append({
            'name': test_name,
            'status': 'success' if success else 'partial',
            'endpoints_tested': len(endpoints_to_test),
            'endpoints_success': success_count
        })
        
        return success
    
    def test_database_connection(self):
        """Probar conexión a base de datos"""
        test_name = "Base de Datos Belgrano Ahorro"
        print(f"Probando: {test_name}")
        
        db_path = 'belgrano_ahorro.db'
        
        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Probar consultas básicas
                cursor.execute("SELECT COUNT(*) FROM productos")
                productos_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM ofertas")
                ofertas_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM negocios")
                negocios_count = cursor.fetchone()[0]
                
                conn.close()
                
                print(f"  [OK] Base de datos accesible")
                print(f"    - Productos: {productos_count}")
                print(f"    - Ofertas: {ofertas_count}")
                print(f"    - Negocios: {negocios_count}")
                
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'success',
                    'productos': productos_count,
                    'ofertas': ofertas_count,
                    'negocios': negocios_count
                })
                return True
            else:
                print(f"  [ERROR] Base de datos no encontrada: {db_path}")
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'error',
                    'error': 'Database file not found'
                })
                return False
                
        except Exception as e:
            print(f"  [ERROR] Error accediendo a base de datos: {e}")
            self.results['tests'].append({
                'name': test_name,
                'status': 'error',
                'error': str(e)
            })
            return False
    
    def test_devops_configuration(self):
        """Probar configuración de DevOps"""
        test_name = "Configuración DevOps"
        print(f"Probando: {test_name}")
        
        try:
            # Verificar archivos de configuración
            config_files = [
                'config_devops.py',
                'devops_routes.py',
                'devops.env.example'
            ]
            
            existing_files = []
            for file in config_files:
                if os.path.exists(file):
                    existing_files.append(file)
            
            print(f"  [OK] Archivos de configuración encontrados: {len(existing_files)}/{len(config_files)}")
            for file in existing_files:
                print(f"    - {file}")
            
            # Verificar variables de entorno
            env_vars = [
                'BELGRANO_AHORRO_URL',
                'BELGRANO_AHORRO_API_KEY'
            ]
            
            configured_vars = []
            for var in env_vars:
                if os.environ.get(var):
                    configured_vars.append(var)
            
            print(f"  [OK] Variables de entorno configuradas: {len(configured_vars)}/{len(env_vars)}")
            
            self.results['tests'].append({
                'name': test_name,
                'status': 'success',
                'config_files': len(existing_files),
                'env_vars': len(configured_vars)
            })
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error verificando configuración: {e}")
            self.results['tests'].append({
                'name': test_name,
                'status': 'error',
                'error': str(e)
            })
            return False
    
    def test_api_communication(self):
        """Probar comunicación entre APIs"""
        test_name = "Comunicación API DevOps-Belgrano"
        print(f"Probando: {test_name}")
        
        try:
            # Simular petición que haría DevOps a Belgrano Ahorro
            test_data = {
                'test': True,
                'timestamp': datetime.now().isoformat()
            }
            
            # Probar endpoint de productos (que DevOps usaría)
            url = f"{self.belgrano_ahorro_url}/api/v1/productos"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Comunicación API exitosa")
                
                # Manejar diferentes formatos de respuesta
                if isinstance(data, dict):
                    productos = data.get('productos', [])
                elif isinstance(data, list):
                    productos = data
                else:
                    productos = []
                
                print(f"    - Productos disponibles: {len(productos)}")
                
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'success',
                    'response_code': response.status_code,
                    'productos_count': len(productos)
                })
                return True
            else:
                print(f"  [ERROR] Error en comunicación API: {response.status_code}")
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'error',
                    'response_code': response.status_code
                })
                return False
                
        except Exception as e:
            print(f"  [ERROR] Error en comunicación API: {e}")
            self.results['tests'].append({
                'name': test_name,
                'status': 'error',
                'error': str(e)
            })
            return False
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("=" * 60)
        print("CHEQUEO DE CONECTIVIDAD DEVOPS - BELGRANO AHORRO")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            self.test_belgrano_ahorro_health,
            self.test_belgrano_ahorro_api,
            self.test_database_connection,
            self.test_devops_configuration,
            self.test_api_communication
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"  [ERROR] Error ejecutando test: {e}")
            print()
        
        # Resumen
        print("=" * 60)
        print("RESUMEN DE RESULTADOS")
        print("=" * 60)
        print(f"Tests ejecutados: {total}")
        print(f"Tests exitosos: {passed}")
        print(f"Tests fallidos: {total - passed}")
        print(f"Porcentaje de éxito: {(passed/total)*100:.1f}%")
        
        # Estado general
        if passed == total:
            print("\n[SUCCESS] TODOS LOS TESTS PASARON - CONECTIVIDAD OPTIMA")
            status = "OPTIMA"
        elif passed >= total * 0.8:
            print("\n[WARNING] ALGUNOS TESTS FALLARON - CONECTIVIDAD ACEPTABLE")
            status = "ACEPTABLE"
        else:
            print("\n[ERROR] MUCHOS TESTS FALLARON - CONECTIVIDAD PROBLEMATICA")
            status = "PROBLEMATICA"
        
        self.results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': (passed/total)*100,
            'status': status
        }
        
        return status
    
    def save_report(self):
        """Guardar reporte en archivo"""
        report_file = f"reporte_conectividad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\nReporte guardado en: {report_file}")
        return report_file

def main():
    """Función principal"""
    checker = ConectividadChecker()
    
    try:
        status = checker.run_all_tests()
        report_file = checker.save_report()
        
        print(f"\nReporte detallado guardado en: {report_file}")
        
        return status == "OPTIMA"
        
    except Exception as e:
        print(f"Error ejecutando chequeo: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
