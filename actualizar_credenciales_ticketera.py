#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar las credenciales de la ticketera con las nuevas credenciales seguras
"""

import os
import sys
import sqlite3
import hashlib
import secrets

def generate_password_hash(password):
    """Generar hash de contraseña usando PBKDF2"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f'pbkdf2:sha256:100000${salt}${hash_obj.hex()}'

def actualizar_credenciales_ticketera():
    """Actualizar credenciales de la ticketera con las nuevas credenciales seguras"""
    print("🔄 Actualizando credenciales de la ticketera...")
    
    # Leer las credenciales generadas
    try:
        with open('credenciales_render.txt', 'r') as f:
            contenido = f.read()
        
        # Extraer la contraseña del admin
        admin_password = None
        for linea in contenido.split('\n'):
            if linea.startswith('Admin Password:'):
                admin_password = linea.split(': ')[1].strip()
                break
        
        if not admin_password:
            print("❌ No se pudo encontrar la contraseña del admin en credenciales_render.txt")
            return False
            
    except FileNotFoundError:
        print("❌ Archivo credenciales_render.txt no encontrado. Ejecuta primero generar_credenciales_seguras.py")
        return False
    
    # Ruta de la base de datos
    db_path = os.path.join('belgrano_tickets', 'belgrano_tickets.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en {db_path}")
        return False
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Actualizar contraseña del admin
    admin_password_hash = generate_password_hash(admin_password)
    
    cursor.execute('''
        UPDATE user 
        SET password = ? 
        WHERE email = 'admin@belgranoahorro.com'
    ''', (admin_password_hash,))
    
    if cursor.rowcount > 0:
        print("✅ Contraseña del admin actualizada")
    else:
        print("⚠️ No se encontró el usuario admin para actualizar")
    
    # Generar nueva contraseña para usuarios flota
    flota_password = "Flota2025!" + secrets.token_hex(4)
    flota_password_hash = generate_password_hash(flota_password)
    
    # Actualizar contraseñas de usuarios flota
    cursor.execute('''
        UPDATE user 
        SET password = ? 
        WHERE role = 'flota'
    ''', (flota_password_hash,))
    
    if cursor.rowcount > 0:
        print(f"✅ Contraseñas de usuarios flota actualizadas: {flota_password}")
    else:
        print("⚠️ No se encontraron usuarios flota para actualizar")
    
    # Guardar cambios
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🔑 NUEVAS CREDENCIALES DE LA TICKETERA:")
    print("=" * 60)
    print(f"👑 Admin: admin@belgranoahorro.com / {admin_password}")
    print(f"🚚 Flota: repartidor1@belgranoahorro.com / {flota_password}")
    print(f"🚚 Flota: repartidor2@belgranoahorro.com / {flota_password}")
    print(f"🚚 Flota: repartidor3@belgranoahorro.com / {flota_password}")
    print(f"🚚 Flota: repartidor4@belgranoahorro.com / {flota_password}")
    print(f"🚚 Flota: repartidor5@belgranoahorro.com / {flota_password}")
    print(f"🚚 Flota: repartidor6@belgranoahorro.com / {flota_password}")
    print(f"🚚 Flota: repartidor7@belgranoahorro.com / {flota_password}")
    
    # Guardar en archivo
    with open('credenciales_ticketera.txt', 'w') as f:
        f.write("CREDENCIALES ACTUALIZADAS DE LA TICKETERA\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Admin: admin@belgranoahorro.com / {admin_password}\n")
        f.write(f"Flota: repartidor1@belgranoahorro.com / {flota_password}\n")
        f.write(f"Flota: repartidor2@belgranoahorro.com / {flota_password}\n")
        f.write(f"Flota: repartidor3@belgranoahorro.com / {flota_password}\n")
        f.write(f"Flota: repartidor4@belgranoahorro.com / {flota_password}\n")
        f.write(f"Flota: repartidor5@belgranoahorro.com / {flota_password}\n")
        f.write(f"Flota: repartidor6@belgranoahorro.com / {flota_password}\n")
        f.write(f"Flota: repartidor7@belgranoahorro.com / {flota_password}\n")
    
    print(f"\n💾 Credenciales de la ticketera guardadas en: credenciales_ticketera.txt")
    print("\n✅ Credenciales actualizadas exitosamente!")
    
    return True

if __name__ == "__main__":
    actualizar_credenciales_ticketera()
