#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio completo para DevOps - Belgrano Ahorro
Configura variables de entorno y inicia todos los servicios
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DevOpsCompleteStarter:
    """Iniciador completo para DevOps - Belgrano Ahorro"""
    
    def __init__(self):
        self.services = {
            'belgrano_ahorro': {
                'port': 5000,
                'script': 'app_unificado.py',
                'name': 'Belgrano Ahorro'
            },
            'devops': {
                'port': 5002,
                'script': 'devops_routes.py',
                'name': 'DevOps'
            }
        }
        
        self.config = {
            'BELGRANO_AHORRO_URL': 'http://localhost:5000',
            'BELGRANO_AHORRO_API_KEY': 'devops_api_key_2025',
            'API_TIMEOUT_SECS': '30',
            'JWT_SECRET': 'devops_jwt_secret_2025',
            'DEVOPS_USERNAME': 'devops',
            'DEVOPS_PASSWORD': 'devops_2025',
            'FLASK_ENV': 'development',
            'DEBUG': 'True'
        }
    
    def setup_environment(self):
        """Configurar variables de entorno"""
        logger.info("🔧 CONFIGURANDO VARIABLES DE ENTORNO...")
        
        for key, value in self.config.items():
            os.environ[key] = value
            logger.info(f"   {key} = {value}")
        
        logger.info("✅ Variables de entorno configuradas")
    
    def check_dependencies(self):
        """Verificar dependencias"""
        logger.info("🔍 VERIFICANDO DEPENDENCIAS...")
        
        required_modules = [
            'flask',
            'requests',
            'jwt',
            'sqlite3'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"   ✅ {module}")
            except ImportError:
                missing_modules.append(module)
                logger.error(f"   ❌ {module}")
        
        if missing_modules:
            logger.error(f"❌ Módulos faltantes: {', '.join(missing_modules)}")
            logger.info("💡 Instale las dependencias con: pip install -r requirements.txt")
            return False
        
        logger.info("✅ Todas las dependencias están disponibles")
        return True
    
    def start_service(self, service_name, service_config):
        """Iniciar un servicio"""
        logger.info(f"🚀 INICIANDO {service_config['name']}...")
        
        try:
            # Configurar variables de entorno para el servicio
            env = os.environ.copy()
            
            # Iniciar el servicio
            process = subprocess.Popen(
                [sys.executable, service_config['script']],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Esperar un poco para que el servicio se inicie
            time.sleep(3)
            
            # Verificar si el proceso está ejecutándose
            if process.poll() is None:
                logger.info(f"✅ {service_config['name']} iniciado (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Error iniciando {service_config['name']}")
                logger.error(f"   stdout: {stdout.decode()}")
                logger.error(f"   stderr: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error iniciando {service_config['name']}: {e}")
            return None
    
    def test_connectivity(self):
        """Probar conectividad entre servicios"""
        logger.info("🔍 PROBANDO CONECTIVIDAD...")
        
        import requests
        
        # Probar Belgrano Ahorro
        try:
            response = requests.get("http://localhost:5000/healthz", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Belgrano Ahorro: OK")
            else:
                logger.warning(f"⚠️ Belgrano Ahorro: {response.status_code}")
        except:
            logger.warning("⚠️ Belgrano Ahorro: No disponible")
        
        # Probar DevOps
        try:
            response = requests.get("http://localhost:5002/devops/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ DevOps: OK")
            else:
                logger.warning(f"⚠️ DevOps: {response.status_code}")
        except:
            logger.warning("⚠️ DevOps: No disponible")
    
    def run_tests(self):
        """Ejecutar pruebas de conectividad"""
        logger.info("🧪 EJECUTANDO PRUEBAS DE CONECTIVIDAD...")
        
        try:
            # Importar y ejecutar el tester
            from test_devops_complete import DevOpsCompleteTester
            
            tester = DevOpsCompleteTester()
            results = tester.run_all_tests()
            
            if results['overall_status'] == 'success':
                logger.info("✅ Todas las pruebas pasaron")
            elif results['overall_status'] == 'partial':
                logger.info("⚠️ Algunas pruebas fallaron")
            else:
                logger.error("❌ Muchas pruebas fallaron")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando pruebas: {e}")
            return None
    
    def start_all_services(self):
        """Iniciar todos los servicios"""
        logger.info("🚀 INICIANDO TODOS LOS SERVICIOS...")
        
        processes = {}
        
        # Iniciar Belgrano Ahorro
        belgrano_process = self.start_service('belgrano_ahorro', self.services['belgrano_ahorro'])
        if belgrano_process:
            processes['belgrano_ahorro'] = belgrano_process
        
        # Esperar un poco para que Belgrano Ahorro se inicie
        time.sleep(5)
        
        # Iniciar DevOps
        devops_process = self.start_service('devops', self.services['devops'])
        if devops_process:
            processes['devops'] = devops_process
        
        return processes
    
    def run_complete_startup(self):
        """Ejecutar inicio completo"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO SISTEMA DEVOPS - BELGRANO AHORRO COMPLETO")
        logger.info("=" * 80)
        logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Configurar entorno
        self.setup_environment()
        
        # 2. Verificar dependencias
        if not self.check_dependencies():
            logger.error("❌ Dependencias faltantes - Abortando")
            return False
        
        # 3. Iniciar servicios
        processes = self.start_all_services()
        
        if not processes:
            logger.error("❌ No se pudieron iniciar los servicios")
            return False
        
        # 4. Esperar a que los servicios se estabilicen
        logger.info("⏳ Esperando a que los servicios se estabilicen...")
        time.sleep(10)
        
        # 5. Probar conectividad
        self.test_connectivity()
        
        # 6. Ejecutar pruebas
        results = self.run_tests()
        
        # 7. Mostrar resumen
        logger.info("=" * 80)
        logger.info("📋 RESUMEN DE INICIO")
        logger.info("=" * 80)
        
        if results and results['overall_status'] == 'success':
            logger.info("✅ SISTEMA COMPLETAMENTE FUNCIONAL")
            logger.info("🌐 URLs disponibles:")
            logger.info("   - Belgrano Ahorro: http://localhost:5000")
            logger.info("   - DevOps: http://localhost:5002")
            logger.info("   - API Docs: http://localhost:5000/api/docs")
        else:
            logger.warning("⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
            logger.info("🔧 Revise los logs para más detalles")
        
        logger.info("=" * 80)
        
        return True

if __name__ == "__main__":
    starter = DevOpsCompleteStarter()
    success = starter.run_complete_startup()
    
    if success:
        print("\n🎉 SISTEMA INICIADO EXITOSAMENTE")
        print("💡 Presione Ctrl+C para detener los servicios")
        
        try:
            # Mantener el script ejecutándose
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servicios...")
            print("✅ Servicios detenidos")
    else:
        print("\n❌ ERROR AL INICIAR EL SISTEMA")
        print("🔧 Revise los logs para más detalles")
        sys.exit(1)
