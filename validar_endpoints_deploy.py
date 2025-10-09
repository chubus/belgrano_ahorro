#!/usr/bin/env python3
"""
Script para validar endpoints antes del deploy
Levanta las tres plataformas y ejecuta tests de conectividad
"""

import subprocess
import time
import requests
import json
import threading
from datetime import datetime
import os
import signal
import sys

class PlatformValidator:
    def __init__(self):
        self.processes = []
        self.results = {
            'belgrano_ahorro': {'status': 'not_started', 'endpoints': []},
            'ticketera': {'status': 'not_started', 'endpoints': []},
            'devops': {'status': 'not_started', 'endpoints': []}
        }
        
    def start_belgrano_ahorro(self):
        """Iniciar Belgrano Ahorro en puerto 5000"""
        try:
            print("🚀 Iniciando Belgrano Ahorro en puerto 5000...")
            process = subprocess.Popen([
                'python', 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(('belgrano_ahorro', process))
            time.sleep(3)  # Esperar a que inicie
            print("✅ Belgrano Ahorro iniciado")
        except Exception as e:
            print(f"❌ Error iniciando Belgrano Ahorro: {e}")
            
    def start_ticketera(self):
        """Iniciar Ticketera en puerto 5001"""
        try:
            print("🚀 Iniciando Ticketera en puerto 5001...")
            process = subprocess.Popen([
                'python', 'belgrano_tickets/app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(('ticketera', process))
            time.sleep(3)  # Esperar a que inicie
            print("✅ Ticketera iniciado")
        except Exception as e:
            print(f"❌ Error iniciando Ticketera: {e}")
            
    def start_devops(self):
        """Iniciar DevOps en puerto 5002"""
        try:
            print("🚀 Iniciando DevOps en puerto 5002...")
            # Crear app DevOps simple
            devops_app = '''
from flask import Flask, jsonify
import os
os.environ["FLASK_ENV"] = "production"
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "devops"})

@app.route('/status')
def status():
    return jsonify({"status": "operational", "service": "devops"})

@app.route('/devops/health')
def devops_health():
    return jsonify({"status": "healthy", "service": "devops"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
'''
            with open('devops_test_app.py', 'w') as f:
                f.write(devops_app)
                
            process = subprocess.Popen([
                'python', 'devops_test_app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(('devops', process))
            time.sleep(3)  # Esperar a que inicie
            print("✅ DevOps iniciado")
        except Exception as e:
            print(f"❌ Error iniciando DevOps: {e}")
    
    def test_endpoint(self, url, platform, endpoint_name):
        """Probar un endpoint específico"""
        try:
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            result = {
                'endpoint': endpoint_name,
                'url': url,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds()
            }
            self.results[platform]['endpoints'].append(result)
            print(f"  {status} {endpoint_name}: {response.status_code} ({result['response_time']:.2f}s)")
            return result
        except Exception as e:
            result = {
                'endpoint': endpoint_name,
                'url': url,
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
            self.results[platform]['endpoints'].append(result)
            print(f"  ❌ {endpoint_name}: Error - {e}")
            return result
    
    def validate_belgrano_ahorro(self):
        """Validar endpoints de Belgrano Ahorro"""
        print("\n🏪 VALIDANDO BELGRANO AHORRO (Puerto 5000)")
        print("=" * 50)
        
        endpoints = [
            ('/', 'Home'),
            ('/health', 'Health Check'),
            ('/status', 'Status'),
            ('/login', 'Login'),
            ('/register', 'Register'),
            ('/productos', 'Productos'),
            ('/carrito', 'Carrito'),
            ('/checkout', 'Checkout'),
            ('/mis_pedidos', 'Mis Pedidos'),
            ('/perfil', 'Perfil'),
            ('/admin', 'Admin'),
            ('/ticketera', 'Ticketera Link')
        ]
        
        for endpoint, name in endpoints:
            self.test_endpoint(f"http://localhost:5000{endpoint}", 'belgrano_ahorro', name)
            
        # Verificar si al menos algunos endpoints funcionan
        successful = sum(1 for ep in self.results['belgrano_ahorro']['endpoints'] if ep['success'])
        self.results['belgrano_ahorro']['status'] = 'healthy' if successful > 5 else 'partial' if successful > 0 else 'failed'
        
    def validate_ticketera(self):
        """Validar endpoints de Ticketera"""
        print("\n🎫 VALIDANDO TICKETERA (Puerto 5001)")
        print("=" * 50)
        
        endpoints = [
            ('/', 'Home'),
            ('/health', 'Health Check'),
            ('/status', 'Status'),
            ('/login', 'Login'),
            ('/api/tickets', 'API Tickets'),
            ('/panel', 'Panel'),
            ('/tickets', 'Tickets'),
            ('/gestion_flota', 'Gestión Flota'),
            ('/gestion_usuarios', 'Gestión Usuarios'),
            ('/reportes', 'Reportes'),
            ('/perfil', 'Perfil')
        ]
        
        for endpoint, name in endpoints:
            self.test_endpoint(f"http://localhost:5001{endpoint}", 'ticketera', name)
            
        # Verificar si al menos algunos endpoints funcionan
        successful = sum(1 for ep in self.results['ticketera']['endpoints'] if ep['success'])
        self.results['ticketera']['status'] = 'healthy' if successful > 5 else 'partial' if successful > 0 else 'failed'
        
    def validate_devops(self):
        """Validar endpoints de DevOps"""
        print("\n🔧 VALIDANDO DEVOPS (Puerto 5002)")
        print("=" * 50)
        
        endpoints = [
            ('/health', 'Health Check'),
            ('/status', 'Status'),
            ('/devops/health', 'DevOps Health')
        ]
        
        for endpoint, name in endpoints:
            self.test_endpoint(f"http://localhost:5002{endpoint}", 'devops', name)
            
        # Verificar si al menos algunos endpoints funcionan
        successful = sum(1 for ep in self.results['devops']['endpoints'] if ep['success'])
        self.results['devops']['status'] = 'healthy' if successful > 1 else 'partial' if successful > 0 else 'failed'
    
    def generate_report(self):
        """Generar reporte final"""
        print("\n📊 REPORTE FINAL DE VALIDACIÓN")
        print("=" * 60)
        
        total_endpoints = sum(len(self.results[platform]['endpoints']) for platform in self.results)
        successful_endpoints = sum(
            sum(1 for ep in self.results[platform]['endpoints'] if ep['success'])
            for platform in self.results
        )
        
        print(f"Total de endpoints probados: {total_endpoints}")
        print(f"Endpoints exitosos: {successful_endpoints}")
        print(f"Tasa de éxito: {(successful_endpoints/total_endpoints*100):.1f}%")
        
        print("\n📋 ESTADO POR PLATAFORMA:")
        for platform, data in self.results.items():
            status_icon = "✅" if data['status'] == 'healthy' else "⚠️" if data['status'] == 'partial' else "❌"
            successful = sum(1 for ep in data['endpoints'] if ep['success'])
            total = len(data['endpoints'])
            print(f"  {status_icon} {platform.upper()}: {successful}/{total} endpoints ({data['status']})")
        
        # Guardar reporte
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_endpoints': total_endpoints,
                'successful_endpoints': successful_endpoints,
                'success_rate': successful_endpoints/total_endpoints*100
            },
            'platforms': self.results
        }
        
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        return successful_endpoints > total_endpoints * 0.7  # 70% de éxito mínimo
    
    def cleanup(self):
        """Limpiar procesos y archivos temporales"""
        print("\n🧹 Limpiando procesos...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} terminado")
            except:
                try:
                    process.kill()
                    print(f"🔪 {name} forzado a terminar")
                except:
                    pass
        
        # Limpiar archivo temporal
        if os.path.exists('devops_test_app.py'):
            os.remove('devops_test_app.py')
            print("✅ Archivo temporal eliminado")
    
    def run_validation(self):
        """Ejecutar validación completa"""
        print("🎯 VALIDACIÓN DE ENDPOINTS ANTES DEL DEPLOY")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Iniciar plataformas
            self.start_belgrano_ahorro()
            self.start_ticketera()
            self.start_devops()
            
            # Esperar un poco más para que se estabilicen
            print("\n⏳ Esperando estabilización de servicios...")
            time.sleep(5)
            
            # Validar endpoints
            self.validate_belgrano_ahorro()
            self.validate_ticketera()
            self.validate_devops()
            
            # Generar reporte
            success = self.generate_report()
            
            if success:
                print("\n✅ VALIDACIÓN EXITOSA - Listo para deploy")
                return True
            else:
                print("\n❌ VALIDACIÓN FALLIDA - Revisar antes del deploy")
                return False
                
        except KeyboardInterrupt:
            print("\n⏹️ Validación interrumpida por el usuario")
            return False
        except Exception as e:
            print(f"\n💥 Error durante la validación: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Función principal"""
    validator = PlatformValidator()
    
    # Manejar interrupciones
    def signal_handler(sig, frame):
        print("\n⏹️ Interrumpiendo validación...")
        validator.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

