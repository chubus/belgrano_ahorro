#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir todas las credenciales de usuarios en Belgrano Tickets
"""

import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash

def verificar_y_corregir_usuarios():
    """Verificar y corregir todas las credenciales de usuarios"""
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'belgrano_tickets.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 VERIFICACIÓN Y CORRECCIÓN DE USUARIOS - BELGRANO TICKETS")
    print("=" * 70)
    print()
    
    # Obtener todos los usuarios
    cursor.execute('SELECT id, username, email, password, role, nombre FROM user')
    usuarios = cursor.fetchall()
    
    print(f"👥 TOTAL DE USUARIOS ENCONTRADOS: {len(usuarios)}")
    print()
    
    # Separar usuarios por rol
    admin_users = [u for u in usuarios if u[4] == 'admin']
    flota_users = [u for u in usuarios if u[4] == 'flota']
    
    print(f"👨‍💼 USUARIOS ADMIN: {len(admin_users)}")
    print(f"🚚 USUARIOS FLOTA: {len(flota_users)}")
    print()
    
    # Verificar y corregir usuarios admin
    print("🔧 VERIFICANDO USUARIOS ADMIN:")
    print("-" * 50)
    
    for usuario in admin_users:
        print(f"   ID: {usuario[0]}")
        print(f"   Email: {usuario[2]}")
        print(f"   Nombre: {usuario[5]}")
        
        # Verificar contraseña admin123
        if check_password_hash(usuario[3], 'admin123'):
            print(f"   ✅ Password 'admin123' es válido")
        else:
            print(f"   ❌ Password 'admin123' NO es válido - CORRIGIENDO...")
            new_password_hash = generate_password_hash('admin123')
            cursor.execute('UPDATE user SET password = ? WHERE id = ?', (new_password_hash, usuario[0]))
            print(f"   ✅ Password corregido a 'admin123'")
        
        print()
    
    # Verificar y corregir usuarios flota
    print("🔧 VERIFICANDO USUARIOS FLOTA:")
    print("-" * 50)
    
    for usuario in flota_users:
        print(f"   ID: {usuario[0]}")
        print(f"   Email: {usuario[2]}")
        print(f"   Nombre: {usuario[5]}")
        
        # Verificar contraseña flota123
        if check_password_hash(usuario[3], 'flota123'):
            print(f"   ✅ Password 'flota123' es válido")
        else:
            print(f"   ❌ Password 'flota123' NO es válido - CORRIGIENDO...")
            new_password_hash = generate_password_hash('flota123')
            cursor.execute('UPDATE user SET password = ? WHERE id = ?', (new_password_hash, usuario[0]))
            print(f"   ✅ Password corregido a 'flota123'")
        
        print()
    
    # Guardar cambios
    conn.commit()
    
    # Mostrar resumen final
    print("=" * 70)
    print("🎉 VERIFICACIÓN COMPLETADA")
    print()
    print("👨‍💼 CREDENCIALES ADMIN:")
    for usuario in admin_users:
        print(f"   Email: {usuario[2]}")
        print(f"   Password: admin123")
        print()
    
    print("🚚 CREDENCIALES FLOTA:")
    for usuario in flota_users:
        print(f"   Email: {usuario[2]}")
        print(f"   Password: flota123")
        print()
    
    print("=" * 70)
    print("💡 INSTRUCCIONES DE ACCESO:")
    print("   1. Inicia la ticketera: python app.py")
    print("   2. Ve a: http://localhost:5001")
    print("   3. Usa cualquiera de las credenciales mostradas arriba")
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    verificar_y_corregir_usuarios()
