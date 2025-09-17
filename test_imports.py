#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar imports
"""

import os
import sys

# Agregar directorios necesarios al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'belgrano_tickets'))
sys.path.insert(0, '.')

def test_imports():
    """Probar los imports necesarios"""
    print("🔧 Probando imports...")
    
    try:
        # Intentar importar desde belgrano_tickets primero
        try:
            from belgrano_tickets.models import db, User
            from belgrano_tickets.app import app
            print("✅ Import desde belgrano_tickets exitoso")
            return True
        except ImportError as e:
            print(f"❌ Error importando desde belgrano_tickets: {e}")
            
            # Si falla, intentar importar desde el directorio actual
            try:
                sys.path.append('belgrano_tickets')
                from models import db, User
                from app import app
                print("✅ Import desde directorio local exitoso")
                return True
            except ImportError as e2:
                print(f"❌ Error importando desde directorio local: {e2}")
                print("   Asegúrate de que belgrano_tickets/models.py y belgrano_tickets/app.py existan")
                return False
                
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("🎉 Todos los imports funcionan correctamente")
        sys.exit(0)
    else:
        print("❌ Hay problemas con los imports")
        sys.exit(1)
