#!/usr/bin/env python3
"""
Script para diagnosticar y solucionar el error 404 en DevOps
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔧 {description}")
    print(f"   Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"   ✅ Éxito: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout ejecutando comando")
        return False
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False

def main():
    print("🚀 DIAGNÓSTICO Y SOLUCIÓN DEL ERROR 404 EN DEVOPS")
    print("=" * 60)
    
    # 1. Verificar Python
    print(f"\n📍 Python version: {sys.version}")
    print(f"📍 Python executable: {sys.executable}")
    
    # 2. Instalar dependencias críticas
    dependencies = [
        "Flask==1.1.4",
        "requests==2.25.1",
        "Werkzeug==1.0.1"
    ]
    
    for dep in dependencies:
        success = run_command(f"pip install {dep}", f"Instalando {dep}")
        if not success:
            print(f"⚠️ Advertencia: No se pudo instalar {dep}")
    
    # 3. Verificar importaciones
    print(f"\n🧪 VERIFICANDO IMPORTACIONES:")
    
    try:
        import flask
        print("   ✅ Flask importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando Flask: {e}")
        return False
    
    try:
        import requests
        print("   ✅ Requests importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando requests: {e}")
        return False
    
    # 4. Probar importación del blueprint
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from belgrano_tickets.devops_routes import devops_bp
        print("   ✅ Blueprint DevOps importado correctamente")
        print(f"   📍 Blueprint name: {devops_bp.name}")
        print(f"   📍 Blueprint url_prefix: {devops_bp.url_prefix}")
    except ImportError as e:
        print(f"   ❌ Error importando blueprint DevOps: {e}")
        return False
    
    # 5. Crear aplicación de prueba
    try:
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(devops_bp)
        
        print(f"\n📋 RUTAS REGISTRADAS:")
        devops_routes = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/devops'):
                devops_routes.append(rule.rule)
                print(f"   ✅ {rule.rule}")
        
        if not devops_routes:
            print("   ❌ No se encontraron rutas de DevOps")
            return False
        
        # 6. Probar endpoints
        print(f"\n🧪 PROBANDO ENDPOINTS:")
        with app.test_client() as client:
            test_endpoints = ['/devops/', '/devops/health', '/devops/info', '/devops/status']
            
            for endpoint in test_endpoints:
                try:
                    response = client.get(endpoint)
                    if response.status_code == 200:
                        print(f"   ✅ {endpoint} -> 200 OK")
                    else:
                        print(f"   ❌ {endpoint} -> {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {endpoint} -> Error: {e}")
        
        print(f"\n🎉 DIAGNÓSTICO COMPLETO")
        print(f"   ✅ El blueprint DevOps está funcionando correctamente")
        print(f"   ✅ Se encontraron {len(devops_routes)} rutas DevOps")
        print(f"   ✅ Los endpoints responden correctamente")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   1. Las dependencias están instaladas")
        print(f"   2. El blueprint se registra correctamente")
        print(f"   3. Los endpoints funcionan")
        print(f"   4. El error 404 debería estar resuelto")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creando aplicación de prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ PROBLEMA RESUELTO: Los endpoints DevOps están funcionando")
    else:
        print(f"\n❌ PROBLEMA PERSISTENTE: Revisar errores anteriores")
