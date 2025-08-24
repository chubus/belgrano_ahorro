#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar credenciales de administrador en Belgrano Tickets
"""

import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash

def verificar_admin():
    """Verificar y mostrar información detallada sobre usuarios admin"""
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'belgrano_tickets.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 DIAGNÓSTICO DE ACCESO ADMIN - BELGRANO TICKETS")
    print("=" * 70)
    print()
    
    # Verificar estructura de la tabla
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    print("📋 ESTRUCTURA DE LA TABLA USER:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    print()
    
    # Obtener todos los usuarios
    cursor.execute('SELECT id, username, email, password, role, nombre FROM user')
    usuarios = cursor.fetchall()
    
    print(f"👥 TOTAL DE USUARIOS: {len(usuarios)}")
    print()
    
    # Filtrar usuarios admin
    admin_users = [u for u in usuarios if u[4] == 'admin']
    
    if not admin_users:
        print("❌ NO HAY USUARIOS ADMIN EN LA BASE DE DATOS")
        print()
        print("🔧 SOLUCIÓN: Crear usuario admin...")
        
        # Crear usuario admin
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO user (username, email, password, role, nombre) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@belgranoahorro.com', admin_password, 'admin', 'Administrador Principal'))
        
        conn.commit()
        print("✅ Usuario admin creado exitosamente")
        print("   Email: admin@belgranoahorro.com")
        print("   Password: admin123")
        print()
        
        # Verificar nuevamente
        cursor.execute('SELECT id, username, email, password, role, nombre FROM user WHERE role = "admin"')
        admin_users = cursor.fetchall()
    
    print("👨‍💼 USUARIOS ADMIN ENCONTRADOS:")
    print("-" * 50)
    
    for usuario in admin_users:
        print(f"   ID: {usuario[0]}")
        print(f"   Username: {usuario[1]}")
        print(f"   Email: {usuario[2]}")
        print(f"   Role: {usuario[4]}")
        print(f"   Nombre: {usuario[5]}")
        
        # Verificar si la contraseña es correcta
        test_password = 'admin123'
        if check_password_hash(usuario[3], test_password):
            print(f"   ✅ Password '{test_password}' es válido")
        else:
            print(f"   ❌ Password '{test_password}' NO es válido")
            print(f"   🔧 Hash actual: {usuario[3][:50]}...")
        
        print()
    
    # Mostrar instrucciones de acceso
    print("=" * 70)
    print("💡 INSTRUCCIONES DE ACCESO:")
    print("   1. Inicia la aplicación: python app.py")
    print("   2. Ve a: http://localhost:5001")
    print("   3. Usa las credenciales de admin mostradas arriba")
    print()
    print("🔐 CREDENCIALES ADMIN:")
    print("   Email: admin@belgranoahorro.com")
    print("   Password: admin123")
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    verificar_admin()
