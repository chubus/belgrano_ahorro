#!/usr/bin/env python3
"""
Script de respaldo para inicialización de usuarios de flota
Corrige el error de indentación identificado en los logs
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def init_users():
    """Inicializar usuarios de flota"""
    try:
        # Importar después de configurar el path
        from werkzeug.security import generate_password_hash
        from belgrano_tickets.models import db, User
        from belgrano_tickets.app import app
        
        with app.app_context():
            # Verificar si ya existen usuarios
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"✅ Ya existen {existing_users} usuarios en la base de datos")
                return True
            
            print("🔧 Inicializando usuarios...")
            
            # Crear usuario admin
            admin = User(
                username='admin',
                email='admin@belgranoahorro.com',
                password=generate_password_hash('admin123'),
                role='admin',
                nombre='Administrador Principal',
                activo=True
            )
            db.session.add(admin)
            print("✅ Usuario admin creado")
            
            # Crear usuarios de flota
            flota_usuarios = [
                ('repartidor1', 'repartidor1@belgranoahorro.com', 'Repartidor 1'),
                ('repartidor2', 'repartidor2@belgranoahorro.com', 'Repartidor 2'),
                ('repartidor3', 'repartidor3@belgranoahorro.com', 'Repartidor 3'),
                ('repartidor4', 'repartidor4@belgranoahorro.com', 'Repartidor 4'),
                ('repartidor5', 'repartidor5@belgranoahorro.com', 'Repartidor 5')
            ]
            
            for username, email, nombre in flota_usuarios:
                flota = User(
                    username=username,
                    email=email,
                    password=generate_password_hash('flota123'),
                    role='flota',
                    nombre=nombre,
                    activo=True
                )
                db.session.add(flota)
                print(f"✅ Usuario {username} creado")
            
            db.session.commit()
            print("🎉 Todos los usuarios inicializados correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error inicializando usuarios: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Inicializando usuarios de flota...")
    success = init_users()
    if success:
        print("✅ Inicialización exitosa")
    else:
        print("❌ Error en la inicialización")
    sys.exit(0 if success else 1)