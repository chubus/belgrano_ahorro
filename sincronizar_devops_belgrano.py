#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de sincronización entre DevOps y Belgrano Ahorro
"""

import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, List, Any

def sincronizar_negocios():
    """Sincronizar negocios entre DevOps y Belgrano Ahorro"""
    print("🔄 Sincronizando negocios...")
    
    try:
        # Conectar a ambas bases de datos
        devops_db = sqlite3.connect('belgrano_ahorro.db')
        belgrano_db = sqlite3.connect('belgrano_ahorro.db')
        
        # Obtener negocios de DevOps
        devops_cursor = devops_db.cursor()
        devops_cursor.execute('SELECT * FROM negocios ORDER BY fecha_creacion DESC')
        devops_negocios = devops_cursor.fetchall()
        
        # Obtener negocios de Belgrano Ahorro
        belgrano_cursor = belgrano_db.cursor()
        belgrano_cursor.execute('SELECT * FROM negocios ORDER BY fecha_creacion DESC')
        belgrano_negocios = belgrano_cursor.fetchall()
        
        print(f"📊 DevOps: {len(devops_negocios)} negocios")
        print(f"📊 Belgrano Ahorro: {len(belgrano_negocios)} negocios")
        
        # Sincronizar cambios
        cambios = 0
        
        for devops_negocio in devops_negocios:
            negocio_id = devops_negocio[0]
            nombre = devops_negocio[1]
            
            # Verificar si existe en Belgrano Ahorro
            belgrano_cursor.execute('SELECT * FROM negocios WHERE id = ?', (negocio_id,))
            belgrano_negocio = belgrano_cursor.fetchone()
            
            if not belgrano_negocio:
                # Crear en Belgrano Ahorro
                belgrano_cursor.execute('''
                    INSERT INTO negocios (id, nombre, descripcion, direccion, telefono, email, activo, fecha_creacion, fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', devops_negocio)
                cambios += 1
                print(f"✅ Negocio sincronizado: {nombre}")
            else:
                # Verificar si hay cambios
                if belgrano_negocio != devops_negocio:
                    belgrano_cursor.execute('''
                        UPDATE negocios 
                        SET nombre = ?, descripcion = ?, direccion = ?, telefono = ?, email = ?, activo = ?, fecha_actualizacion = ?
                        WHERE id = ?
                    ''', devops_negocio[1:] + (negocio_id,))
                    cambios += 1
                    print(f"🔄 Negocio actualizado: {nombre}")
        
        belgrano_db.commit()
        print(f"✅ Sincronización de negocios completada: {cambios} cambios")
        
        devops_db.close()
        belgrano_db.close()
        
        return cambios
        
    except Exception as e:
        print(f"❌ Error sincronizando negocios: {e}")
        return 0

def sincronizar_productos():
    """Sincronizar productos entre DevOps y Belgrano Ahorro"""
    print("🔄 Sincronizando productos...")
    
    try:
        # Conectar a ambas bases de datos
        devops_db = sqlite3.connect('belgrano_ahorro.db')
        belgrano_db = sqlite3.connect('belgrano_ahorro.db')
        
        # Obtener productos de DevOps
        devops_cursor = devops_db.cursor()
        devops_cursor.execute('SELECT * FROM productos ORDER BY fecha_creacion DESC')
        devops_productos = devops_cursor.fetchall()
        
        # Obtener productos de Belgrano Ahorro
        belgrano_cursor = belgrano_db.cursor()
        belgrano_cursor.execute('SELECT * FROM productos ORDER BY fecha_creacion DESC')
        belgrano_productos = belgrano_cursor.fetchall()
        
        print(f"📊 DevOps: {len(devops_productos)} productos")
        print(f"📊 Belgrano Ahorro: {len(belgrano_productos)} productos")
        
        # Sincronizar cambios
        cambios = 0
        
        for devops_producto in devops_productos:
            producto_id = devops_producto[0]
            nombre = devops_producto[1]
            
            # Verificar si existe en Belgrano Ahorro
            belgrano_cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
            belgrano_producto = belgrano_cursor.fetchone()
            
            if not belgrano_producto:
                # Crear en Belgrano Ahorro
                belgrano_cursor.execute('''
                    INSERT INTO productos (id, nombre, descripcion, precio, categoria, stock, stock_minimo, negocio_id, activo, fecha_creacion, fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', devops_producto)
                cambios += 1
                print(f"✅ Producto sincronizado: {nombre}")
            else:
                # Verificar si hay cambios
                if belgrano_producto != devops_producto:
                    belgrano_cursor.execute('''
                        UPDATE productos 
                        SET nombre = ?, descripcion = ?, precio = ?, categoria = ?, stock = ?, stock_minimo = ?, negocio_id = ?, activo = ?, fecha_actualizacion = ?
                        WHERE id = ?
                    ''', devops_producto[1:] + (producto_id,))
                    cambios += 1
                    print(f"🔄 Producto actualizado: {nombre}")
        
        belgrano_db.commit()
        print(f"✅ Sincronización de productos completada: {cambios} cambios")
        
        devops_db.close()
        belgrano_db.close()
        
        return cambios
        
    except Exception as e:
        print(f"❌ Error sincronizando productos: {e}")
        return 0

def sincronizar_ofertas():
    """Sincronizar ofertas entre DevOps y Belgrano Ahorro"""
    print("🔄 Sincronizando ofertas...")
    
    try:
        # Conectar a ambas bases de datos
        devops_db = sqlite3.connect('belgrano_ahorro.db')
        belgrano_db = sqlite3.connect('belgrano_ahorro.db')
        
        # Obtener ofertas de DevOps
        devops_cursor = devops_db.cursor()
        devops_cursor.execute('SELECT * FROM ofertas ORDER BY fecha_creacion DESC')
        devops_ofertas = devops_cursor.fetchall()
        
        # Obtener ofertas de Belgrano Ahorro
        belgrano_cursor = belgrano_db.cursor()
        belgrano_cursor.execute('SELECT * FROM ofertas ORDER BY fecha_creacion DESC')
        belgrano_ofertas = belgrano_cursor.fetchall()
        
        print(f"📊 DevOps: {len(devops_ofertas)} ofertas")
        print(f"📊 Belgrano Ahorro: {len(belgrano_ofertas)} ofertas")
        
        # Sincronizar cambios
        cambios = 0
        
        for devops_oferta in devops_ofertas:
            oferta_id = devops_oferta[0]
            titulo = devops_oferta[1]
            
            # Verificar si existe en Belgrano Ahorro
            belgrano_cursor.execute('SELECT * FROM ofertas WHERE id = ?', (oferta_id,))
            belgrano_oferta = belgrano_cursor.fetchone()
            
            if not belgrano_oferta:
                # Crear en Belgrano Ahorro
                belgrano_cursor.execute('''
                    INSERT INTO ofertas (id, titulo, descripcion, productos, hasta_agotar_stock, activa, fecha_creacion, fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', devops_oferta)
                cambios += 1
                print(f"✅ Oferta sincronizada: {titulo}")
            else:
                # Verificar si hay cambios
                if belgrano_oferta != devops_oferta:
                    belgrano_cursor.execute('''
                        UPDATE ofertas 
                        SET titulo = ?, descripcion = ?, productos = ?, hasta_agotar_stock = ?, activa = ?, fecha_actualizacion = ?
                        WHERE id = ?
                    ''', devops_oferta[1:] + (oferta_id,))
                    cambios += 1
                    print(f"🔄 Oferta actualizada: {titulo}")
        
        belgrano_db.commit()
        print(f"✅ Sincronización de ofertas completada: {cambios} cambios")
        
        devops_db.close()
        belgrano_db.close()
        
        return cambios
        
    except Exception as e:
        print(f"❌ Error sincronizando ofertas: {e}")
        return 0

def sincronizar_completa():
    """Ejecutar sincronización completa"""
    print("🚀 INICIANDO SINCRONIZACIÓN COMPLETA DEVOPS ↔ BELGRANO AHORRO")
    print("=" * 70)
    
    # Verificar que existe la base de datos
    if not os.path.exists('belgrano_ahorro.db'):
        print("❌ No se encontró la base de datos belgrano_ahorro.db")
        return False
    
    total_cambios = 0
    
    # Sincronizar negocios
    cambios_negocios = sincronizar_negocios()
    total_cambios += cambios_negocios
    
    # Sincronizar productos
    cambios_productos = sincronizar_productos()
    total_cambios += cambios_productos
    
    # Sincronizar ofertas
    cambios_ofertas = sincronizar_ofertas()
    total_cambios += cambios_ofertas
    
    print("\n" + "=" * 70)
    print(f"🎉 SINCRONIZACIÓN COMPLETADA")
    print(f"📊 Total de cambios: {total_cambios}")
    print(f"   - Negocios: {cambios_negocios}")
    print(f"   - Productos: {cambios_productos}")
    print(f"   - Ofertas: {cambios_ofertas}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    return total_cambios > 0

if __name__ == "__main__":
    if sincronizar_completa():
        print("\n✅ La sincronización se ejecutó correctamente")
    else:
        print("\n⚠️ No se realizaron cambios en la sincronización")
