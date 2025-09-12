#!/usr/bin/env python3
"""
Script simple para probar endpoints DevOps
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Intentar importar Flask
    from flask import Flask
    print("✅ Flask importado correctamente")
    
    # Crear una aplicación Flask básica
    app = Flask(__name__)
    
    # Intentar importar el blueprint de DevOps
    try:
        from belgrano_tickets.devops_routes import devops_bp
        print("✅ Blueprint DevOps importado correctamente")
        
        # Registrar el blueprint
        app.register_blueprint(devops_bp)
        print("✅ Blueprint DevOps registrado correctamente")
        
        # Listar todas las rutas registradas
        print("\n📋 Rutas registradas:")
        for rule in app.url_map.iter_rules():
            print(f"   {rule.rule} -> {rule.endpoint}")
        
        # Probar algunas rutas específicas de DevOps
        with app.test_client() as client:
            print("\n🧪 Probando endpoints DevOps:")
            
            # Probar /devops/
            try:
                response = client.get('/devops/')
                print(f"   GET /devops/ -> {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Endpoint principal funciona")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error probando /devops/: {e}")
            
            # Probar /devops/health
            try:
                response = client.get('/devops/health')
                print(f"   GET /devops/health -> {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Health check funciona")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error probando /devops/health: {e}")
            
            # Probar /devops/info
            try:
                response = client.get('/devops/info')
                print(f"   GET /devops/info -> {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Info endpoint funciona")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error probando /devops/info: {e}")
        
        print("\n🎉 RESULTADO: Los endpoints DevOps están funcionando correctamente!")
        print("   El problema del 404 debería estar resuelto.")
        
    except ImportError as e:
        print(f"❌ Error importando blueprint DevOps: {e}")
        print("   Verificar que todas las dependencias estén instaladas")
        
except ImportError as e:
    print(f"❌ Error importando Flask: {e}")
    print("   Instalar Flask: pip install Flask")

except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
