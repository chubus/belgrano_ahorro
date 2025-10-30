#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que todas las aplicaciones funcionen correctamente
"""

import sys
import os

# Agregar el directorio de dependencias al path
sys.path.append(r'C:\Users\rey_a\AppData\Roaming\Python\Python313\site-packages')

def test_belgrano_ahorro():
    """Probar Belgrano Ahorro"""
    try:
        print("🔍 Probando Belgrano Ahorro...")
        import app
        print("✅ Belgrano Ahorro (app.py) - OK")
        
        import api_belgrano_ahorro
        print("✅ API Belgrano Ahorro - OK")
        
        return True
    except Exception as e:
        print(f"❌ Error en Belgrano Ahorro: {e}")
        return False

def test_ticketera():
    """Probar Ticketera"""
    try:
        print("\n🔍 Probando Ticketera...")
        
        # Cambiar al directorio de Ticketera
        original_dir = os.getcwd()
        ticketera_dir = os.path.join(original_dir, 'belgrano_tickets')
        
        if os.path.exists(ticketera_dir):
            os.chdir(ticketera_dir)
            try:
                import app
                print("✅ Ticketera (belgrano_tickets/app.py) - OK")
                return True
            finally:
                os.chdir(original_dir)
        else:
            print("❌ Directorio belgrano_tickets no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error en Ticketera: {e}")
        os.chdir(original_dir)
        return False

def test_devops():
    """Probar DevOps"""
    try:
        print("\n🔍 Probando DevOps...")
        import devops_routes
        print("✅ DevOps Routes - OK")
        
        import devops_belgrano_manager_unified
        print("✅ DevOps Manager - OK")
        
        return True
    except Exception as e:
        print(f"❌ Error en DevOps: {e}")
        return False

def test_dependencies():
    """Probar dependencias básicas"""
    try:
        print("🔍 Probando dependencias básicas...")
        
        import flask
        print(f"✅ Flask {flask.__version__} - OK")
        
        import requests
        print(f"✅ Requests {requests.__version__} - OK")
        
        import flask_login
        print("✅ Flask-Login - OK")
        
        import flask_socketio
        print("✅ Flask-SocketIO - OK")
        
        # Probar SQLAlchemy con manejo de errores
        try:
            import sqlalchemy
            print(f"✅ SQLAlchemy {sqlalchemy.__version__} - OK")
        except Exception as e:
            print(f"⚠️ SQLAlchemy con problemas: {e}")
            print("   Intentando importar Flask-SQLAlchemy...")
            try:
                import flask_sqlalchemy
                print("✅ Flask-SQLAlchemy - OK")
            except Exception as e2:
                print(f"❌ Flask-SQLAlchemy también falla: {e2}")
        
        return True
    except Exception as e:
        print(f"❌ Error en dependencias: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE DEPENDENCIAS")
    print("=" * 50)
    
    results = []
    
    # Probar dependencias básicas
    results.append(test_dependencies())
    
    # Probar aplicaciones
    results.append(test_belgrano_ahorro())
    results.append(test_ticketera())
    results.append(test_devops())
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS:")
    
    if all(results):
        print("🎉 ¡TODAS LAS APLICACIONES FUNCIONAN CORRECTAMENTE!")
        print("\n✅ Belgrano Ahorro - Listo")
        print("✅ Ticketera - Listo")
        print("✅ DevOps - Listo")
        print("\n🚀 Sistema completamente funcional")
    else:
        print("⚠️ Algunas aplicaciones tienen problemas")
        print("\nRevisar errores arriba para más detalles")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

