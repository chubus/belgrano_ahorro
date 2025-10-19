#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Corrección Automática - Problemas de Conectividad DevOps
Corrige automáticamente los problemas identificados en el chequeo de conectividad
"""

import os
import json
import requests
import sqlite3
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DevOpsConnectivityFixer:
    """Corrector automático de problemas de conectividad DevOps"""
    
    def __init__(self):
        self.belgrano_url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
        self.belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        self.headers = {
            'X-API-Key': self.belgrano_api_key,
            'Content-Type': 'application/json'
        }
        self.fixes_applied = []
        self.errors_found = []
    
    def create_env_file(self):
        """Crear archivo .env con variables de entorno"""
        logger.info("🔧 Creando archivo .env con variables de entorno...")
        
        env_content = """# Configuración DevOps - Variables de Entorno
# Archivo generado automáticamente

# Credenciales DevOps
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=DevOps2025!Secure

# API Belgrano Ahorro
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# API Gateway
GATEWAY_URL=http://localhost:5003/gateway
GATEWAY_API_KEY=devops_api_key_2025

# API Ticketera
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETERA_API_KEY=ticketera_api_key_2025

# Base de Datos
BELGRANO_AHORRO_DB_PATH=belgrano_ahorro.db
TICKETS_DB_PATH=belgrano_tickets.db

# Configuración de Seguridad
SECRET_KEY=devops_secret_key_2025

# Configuración de API
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3
API_RETRY_DELAY=1
CACHE_TTL=300

# Configuración de Sincronización
SYNC_INTERVAL=60

# Configuración de Logging
LOG_LEVEL=INFO
LOG_FILE=devops.log
"""
        
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            logger.info("✅ Archivo .env creado exitosamente")
            self.fixes_applied.append("Archivo .env creado con variables de entorno")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando archivo .env: {e}")
            self.errors_found.append(f"Error creando .env: {e}")
            return False
    
    def test_endpoints_manually(self):
        """Probar endpoints manualmente para identificar problemas específicos"""
        logger.info("🔍 Probando endpoints manualmente...")
        
        endpoints_to_test = [
            '/api/v1/ofertas',
            '/api/v1/sucursales', 
            '/api/v1/precios'
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{self.belgrano_url}{endpoint}"
                logger.info(f"   Probando: {url}")
                
                response = requests.get(url, headers=self.headers, timeout=30)
                
                results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'success': response.status_code == 200
                }
                
                if response.status_code == 200:
                    logger.info(f"   ✅ {endpoint}: OK")
                else:
                    logger.warning(f"   ❌ {endpoint}: Error {response.status_code}")
                    if response.status_code == 500:
                        logger.warning(f"      Error interno del servidor - Revisar logs")
                    elif response.status_code == 404:
                        logger.warning(f"      Endpoint no encontrado - Verificar implementación")
                
            except requests.exceptions.Timeout:
                logger.error(f"   ⏰ {endpoint}: Timeout")
                results[endpoint] = {'error': 'Timeout'}
            except Exception as e:
                logger.error(f"   💥 {endpoint}: Error - {e}")
                results[endpoint] = {'error': str(e)}
        
        return results
    
    def check_database_integrity(self):
        """Verificar integridad de la base de datos"""
        logger.info("🗄️ Verificando integridad de la base de datos...")
        
        db_path = 'belgrano_ahorro.db'
        
        try:
            if not os.path.exists(db_path):
                logger.error(f"❌ Base de datos no encontrada: {db_path}")
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tablas críticas
            critical_tables = ['productos', 'negocios', 'ofertas', 'sucursales']
            
            for table in critical_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"   📊 {table}: {count} registros")
                except Exception as e:
                    logger.warning(f"   ⚠️ Error en tabla {table}: {e}")
            
            # Verificar integridad de datos
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            if integrity_result == 'ok':
                logger.info("   ✅ Integridad de base de datos: OK")
            else:
                logger.warning(f"   ⚠️ Problemas de integridad: {integrity_result}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando base de datos: {e}")
            return False
    
    def create_monitoring_script(self):
        """Crear script de monitoreo continuo"""
        logger.info("📊 Creando script de monitoreo continuo...")
        
        monitoring_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script de Monitoreo Continuo - DevOps Belgrano Ahorro
Ejecutar periódicamente para verificar conectividad
'''

import os
import sys
import time
from datetime import datetime
import subprocess

def run_connectivity_check():
    \"\"\"Ejecutar chequeo de conectividad\"\"\"
    try:
        result = subprocess.run([sys.executable, 'chequeo_conectividad_devops_integral.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✅ Chequeo de conectividad exitoso")
            return True
        else:
            print(f"[{datetime.now()}] ❌ Chequeo de conectividad falló")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] ⏰ Timeout en chequeo de conectividad")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] 💥 Error ejecutando chequeo: {e}")
        return False

def main():
    \"\"\"Función principal de monitoreo\"\"\"
    print(f"[{datetime.now()}] 🔍 Iniciando monitoreo de conectividad DevOps...")
    
    success = run_connectivity_check()
    
    if success:
        print(f"[{datetime.now()}] ✅ Monitoreo completado exitosamente")
    else:
        print(f"[{datetime.now()}] ❌ Monitoreo detectó problemas")
        # Aquí se pueden agregar alertas (email, Slack, etc.)
    
    return success

if __name__ == "__main__":
    main()
"""
        
        try:
            with open('monitoreo_conectividad_devops.py', 'w', encoding='utf-8') as f:
                f.write(monitoring_script)
            
            # Hacer el script ejecutable
            os.chmod('monitoreo_conectividad_devops.py', 0o755)
            
            logger.info("✅ Script de monitoreo creado exitosamente")
            self.fixes_applied.append("Script de monitoreo continuo creado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando script de monitoreo: {e}")
            self.errors_found.append(f"Error creando monitoreo: {e}")
            return False
    
    def create_health_check_endpoint(self):
        """Crear endpoint de health check mejorado"""
        logger.info("🏥 Creando endpoint de health check mejorado...")
        
        health_check_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Health Check Endpoint Mejorado - DevOps Belgrano Ahorro
Endpoint para verificar estado de todos los servicios
'''

from flask import Flask, jsonify
import requests
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

def check_belgrano_ahorro():
    \"\"\"Verificar estado de Belgrano Ahorro\"\"\"
    try:
        url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
        response = requests.get(f"{url}/healthz", timeout=10)
        return {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response.elapsed.total_seconds(),
            'status_code': response.status_code
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_database():
    \"\"\"Verificar estado de la base de datos\"\"\"
    try:
        db_path = os.environ.get('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        count = cursor.fetchone()[0]
        conn.close()
        return {'status': 'healthy', 'productos_count': count}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@app.route('/health')
def health_check():
    \"\"\"Endpoint de health check\"\"\"
    belgrano_status = check_belgrano_ahorro()
    db_status = check_database()
    
    overall_status = 'healthy'
    if belgrano_status['status'] != 'healthy' or db_status['status'] != 'healthy':
        overall_status = 'unhealthy'
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'overall_status': overall_status,
        'services': {
            'belgrano_ahorro': belgrano_status,
            'database': db_status
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
        
        try:
            with open('health_check_devops.py', 'w', encoding='utf-8') as f:
                f.write(health_check_script)
            
            logger.info("✅ Endpoint de health check creado exitosamente")
            self.fixes_applied.append("Endpoint de health check mejorado creado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando health check: {e}")
            self.errors_found.append(f"Error creando health check: {e}")
            return False
    
    def generate_fix_report(self):
        """Generar reporte de correcciones aplicadas"""
        logger.info("📄 Generando reporte de correcciones...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': self.fixes_applied,
            'errors_found': self.errors_found,
            'recommendations': [
                "Configurar variables de entorno en el sistema",
                "Ejecutar script de monitoreo periódicamente",
                "Revisar logs de Belgrano Ahorro para errores 500",
                "Implementar endpoints faltantes en la API",
                "Configurar alertas para fallos de conectividad"
            ]
        }
        
        try:
            with open('reporte_correcciones_devops.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Reporte de correcciones generado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return False
    
    def run_all_fixes(self):
        """Ejecutar todas las correcciones"""
        logger.info("🔧 Iniciando correcciones automáticas...")
        
        print("=" * 80)
        print("🔧 CORRECCIÓN AUTOMÁTICA DE PROBLEMAS DEVOPS")
        print("=" * 80)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Ejecutar correcciones
        fixes = [
            ("Crear archivo .env", self.create_env_file),
            ("Probar endpoints manualmente", self.test_endpoints_manually),
            ("Verificar base de datos", self.check_database_integrity),
            ("Crear script de monitoreo", self.create_monitoring_script),
            ("Crear health check", self.create_health_check_endpoint)
        ]
        
        for fix_name, fix_func in fixes:
            try:
                logger.info(f"🔧 Ejecutando: {fix_name}")
                result = fix_func()
                if result:
                    logger.info(f"✅ {fix_name}: Completado")
                else:
                    logger.warning(f"⚠️ {fix_name}: Parcialmente completado")
            except Exception as e:
                logger.error(f"❌ {fix_name}: Error - {e}")
                self.errors_found.append(f"{fix_name}: {e}")
        
        # Generar reporte final
        self.generate_fix_report()
        
        # Mostrar resumen
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE CORRECCIONES")
        print("=" * 80)
        print(f"✅ Correcciones aplicadas: {len(self.fixes_applied)}")
        print(f"❌ Errores encontrados: {len(self.errors_found)}")
        
        if self.fixes_applied:
            print("\n🔧 CORRECCIONES APLICADAS:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        if self.errors_found:
            print("\n⚠️ ERRORES ENCONTRADOS:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"   {i}. {error}")
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Configurar variables de entorno en el sistema")
        print("   2. Ejecutar script de monitoreo periódicamente")
        print("   3. Revisar logs de Belgrano Ahorro para errores 500")
        print("   4. Implementar endpoints faltantes en la API")
        print("   5. Configurar alertas para fallos de conectividad")
        
        return len(self.fixes_applied) > 0

def main():
    """Función principal"""
    try:
        fixer = DevOpsConnectivityFixer()
        success = fixer.run_all_fixes()
        
        if success:
            print("\n🎉 Correcciones aplicadas exitosamente")
            return 0
        else:
            print("\n⚠️ Algunas correcciones fallaron")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Error ejecutando correcciones: {e}")
        return 2

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

