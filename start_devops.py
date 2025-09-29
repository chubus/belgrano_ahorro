#!/usr/bin/env python3
"""
Script para iniciar DevOps correctamente
"""
import os
import sys
from flask import Flask

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = 'devops_secret_key_2025'

# Importar y registrar blueprint de DevOps
try:
    from devops_routes import devops_bp
    app.register_blueprint(devops_bp)
    print("✅ DevOps blueprint registrado correctamente")
except Exception as e:
    print(f"❌ Error registrando DevOps blueprint: {e}")
    # Intentar importar desde belgrano_tickets
    try:
        import sys
        sys.path.append('belgrano_tickets')
        from devops_routes import devops_bp as devops_bp_tickets
        app.register_blueprint(devops_bp_tickets)
        print("✅ DevOps blueprint registrado desde belgrano_tickets")
    except Exception as e2:
        print(f"❌ Error registrando DevOps blueprint desde belgrano_tickets: {e2}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Iniciando DevOps en puerto 5002...")
    print("📱 URL: http://localhost:5002/devops/")
    print("🔐 Credenciales: devops / DevOps2025!Secure")
    print("📝 Presiona Ctrl+C para detener")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False)
    except KeyboardInterrupt:
        print("\n⏹️ DevOps detenido")
    except Exception as e:
        print(f"❌ Error iniciando DevOps: {e}")
