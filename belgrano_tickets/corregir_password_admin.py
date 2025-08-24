#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la contraseña del administrador en Belgrano Tickets
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def corregir_password_admin():
    """Corregir la contraseña del administrador"""
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'belgrano_tickets.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 CORRECCIÓN DE PASSWORD ADMIN - BELGRANO TICKETS")
    print("=" * 70)
    print()
    
    # Buscar usuario admin
    cursor.execute('SELECT id, username, email, role, nombre FROM user WHERE role = "admin"')
    admin_users = cursor.fetchall()
    
    if not admin_users:
        print("❌ No se encontraron usuarios admin")
        return
    
    for admin in admin_users:
        print(f"👨‍💼 Usuario admin encontrado:")
        print(f"   ID: {admin[0]}")
        print(f"   Username: {admin[1]}")
        print(f"   Email: {admin[2]}")
        print(f"   Nombre: {admin[4]}")
        print()
        
        # Generar nuevo hash para admin123
        new_password_hash = generate_password_hash('admin123')
        
        # Actualizar contraseña
        cursor.execute('UPDATE user SET password = ? WHERE id = ?', (new_password_hash, admin[0]))
        
        print(f"✅ Contraseña actualizada exitosamente")
        print(f"   Nueva contraseña: admin123")
        print()
    
    conn.commit()
    conn.close()
    
    print("=" * 70)
    print("🎉 CORRECCIÓN COMPLETADA")
    print("   Ahora puedes acceder con:")
    print("   Email: admin@belgranoahorro.com")
    print("   Password: admin123")
    print("=" * 70)

if __name__ == "__main__":
    corregir_password_admin()
