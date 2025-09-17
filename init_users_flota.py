#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicialización de usuarios de flota
Versión de respaldo en directorio raíz
"""

import os
import sys

# Agregar directorios necesarios al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'belgrano_tickets'))
sys.path.insert(0, '.')

def initialize_database():
    """Inicializar la base de datos y usuarios"""
    try:
        print("🔧 Inicializando base de datos...")
        
        # Importar módulos necesarios
        from werkzeug.security import generate_password_hash
        
        # Intentar importar desde belgrano_tickets primero
        try:
            from belgrano_tickets.models import db, User
            from belgrano_tickets.app import app
        except ImportError:
            # Si falla, intentar importar desde el directorio actual
            try:
                import sys
                sys.path.append('belgrano_tickets')
                from models import db, User
                from app import app
            except ImportError:
                print("❌ Error: No se pueden importar los módulos necesarios")
                print("   Asegúrate de que belgrano_tickets/models.py y belgrano_tickets/app.py existan")
                raise
        
        # Crear contexto de aplicación
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas de base de datos creadas")
            
            # Verificar si ya existen usuarios
            user_count = User.query.count()
            if user_count > 0:
                print(f"✅ Ya existen {user_count} usuarios en la base de datos")
                return True
            
            print("🔧 Creando usuarios iniciales...")
            
            # Crear usuario administrador
            admin_user = User(
                username='admin',
                email='admin@belgranoahorro.com',
                password=generate_password_hash('admin123'),
                role='admin',
                nombre='Administrador Principal',
                activo=True
            )
            db.session.add(admin_user)
            print("✅ Usuario administrador creado")
            
            # Lista de usuarios de flota
            fleet_users = [
                ('repartidor1', 'repartidor1@belgranoahorro.com', 'Repartidor 1'),
                ('repartidor2', 'repartidor2@belgranoahorro.com', 'Repartidor 2'),
                ('repartidor3', 'repartidor3@belgranoahorro.com', 'Repartidor 3'),
                ('repartidor4', 'repartidor4@belgranoahorro.com', 'Repartidor 4'),
                ('repartidor5', 'repartidor5@belgranoahorro.com', 'Repartidor 5')
            ]
            
            # Crear usuarios de flota
            for username, email, nombre in fleet_users:
                fleet_user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash('flota123'),
                    role='flota',
                    nombre=nombre,
                    activo=True
                )
                db.session.add(fleet_user)
                print(f"✅ Usuario de flota creado: {username}")
            
            # Confirmar cambios en la base de datos
            db.session.commit()
            print("🎉 Todos los usuarios creados exitosamente")
            
            # Verificar creación
            final_count = User.query.count()
            print(f"📊 Total de usuarios en base de datos: {final_count}")
            
            return True
            
    except Exception as error:
        print(f"❌ Error inicializando base de datos: {error}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando script de inicialización de usuarios...")
    print("=" * 50)
    
    try:
        success = initialize_database()
        
        if success:
            print("✅ Inicialización completada exitosamente")
            return 0
        else:
            print("❌ Error en la inicialización")
            return 1
            
    except Exception as error:
        print(f"❌ Error general: {error}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
