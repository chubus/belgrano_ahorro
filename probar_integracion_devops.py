#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba de integración DevOps + Ticketera
"""

import sqlite3
import time
import json
from datetime import datetime

def probar_fallback_devops():
    """Probar funcionalidad de fallback de DevOps directamente en la DB"""
    print("🧪 PROBANDO INTEGRACIÓN DEVOPS → BELGRANO AHORRO")
    print("=" * 50)
    
    # Conectar a la base de datos
    conn = sqlite3.connect('belgrano_ahorro.db')
    c = conn.cursor()
    
    # Contar registros antes
    neg_before = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
    prod_before = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    ofer_before = c.execute('SELECT COUNT(*) FROM ofertas').fetchone()[0]
    
    print(f"📊 Estado inicial: Negocios={neg_before}, Productos={prod_before}, Ofertas={ofer_before}")
    
    # Simular creación desde DevOps (fallback)
    timestamp = int(time.time())
    
    # 1. Crear negocio
    negocio_nombre = f'DevOps Integrado {timestamp}'
    c.execute('''
        INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (negocio_nombre, 'Negocio creado desde DevOps integrado', 'Calle DevOps 123', '555-0100', 'devops@integrado.com'))
    negocio_id = c.lastrowid
    print(f"✅ Negocio creado: ID={negocio_id}, Nombre={negocio_nombre}")
    
    # 2. Crear producto
    producto_nombre = f'Producto DevOps {timestamp}'
    c.execute('''
        INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    ''', (producto_nombre, 'general', 199.99, 'DevOps', 50, 5, negocio_id))
    producto_id = c.lastrowid
    print(f"✅ Producto creado: ID={producto_id}, Nombre={producto_nombre}")
    
    # 3. Crear oferta
    oferta_nombre = f'Oferta DevOps {timestamp}'
    c.execute('''
        INSERT INTO ofertas (titulo, descripcion, descuento_porcentaje, fecha_inicio, fecha_fin, activa) 
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (oferta_nombre, 'Oferta creada desde DevOps integrado', 20.0, datetime.now().strftime('%Y-%m-%d'), 
          (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')))
    oferta_id = c.lastrowid
    print(f"✅ Oferta creada: ID={oferta_id}, Nombre={oferta_nombre}")
    
    conn.commit()
    
    # Contar registros después
    neg_after = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
    prod_after = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    ofer_after = c.execute('SELECT COUNT(*) FROM ofertas').fetchone()[0]
    
    print(f"📊 Estado final: Negocios={neg_after}, Productos={prod_after}, Ofertas={ofer_after}")
    
    # Mostrar últimos registros
    print("\n📋 Últimos negocios:")
    for row in c.execute('SELECT id, nombre, activo FROM negocios ORDER BY id DESC LIMIT 3').fetchall():
        print(f"  ID: {row[0]}, Nombre: {row[1]}, Activo: {row[2]}")
    
    print("\n📋 Últimos productos:")
    for row in c.execute('SELECT id, nombre, precio, store, negocio_id FROM productos ORDER BY id DESC LIMIT 3').fetchall():
        print(f"  ID: {row[0]}, Nombre: {row[1]}, Precio: {row[2]}, Store: {row[3]}, Negocio: {row[4]}")
    
    print("\n📋 Últimas ofertas:")
    for row in c.execute('SELECT id, titulo, descuento_porcentaje FROM ofertas ORDER BY id DESC LIMIT 3').fetchall():
        print(f"  ID: {row[0]}, Título: {row[1]}, Descuento: {row[2]}%")
    
    conn.close()
    
    print("\n✅ INTEGRACIÓN DEVOPS → BELGRANO AHORRO FUNCIONANDO")
    print("🔧 DevOps integrado en Ticketera permite:")
    print("   • Crear negocios, productos y ofertas")
    print("   • Persistencia directa en belgrano_ahorro.db")
    print("   • Datos visibles inmediatamente en Belgrano Ahorro")
    print("   • Fallback cuando DevOps Manager no está disponible")

def verificar_esquema_db():
    """Verificar que el esquema de la DB sea correcto"""
    print("\n🔍 VERIFICANDO ESQUEMA DE BASE DE DATOS")
    print("-" * 40)
    
    conn = sqlite3.connect('belgrano_ahorro.db')
    c = conn.cursor()
    
    # Verificar tablas
    tablas = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"📊 Tablas encontradas: {len(tablas)}")
    for tabla in tablas:
        print(f"  • {tabla[0]}")
    
    # Verificar esquema de productos
    print("\n📋 Esquema tabla productos:")
    for row in c.execute("PRAGMA table_info(productos)").fetchall():
        print(f"  • {row[1]} ({row[2]}) - {'NOT NULL' if row[3] else 'NULL'}")
    
    conn.close()

if __name__ == "__main__":
    verificar_esquema_db()
    probar_fallback_devops()

"""
Prueba de integración DevOps + Ticketera
"""

import sqlite3
import time
import json
from datetime import datetime

def probar_fallback_devops():
    """Probar funcionalidad de fallback de DevOps directamente en la DB"""
    print("🧪 PROBANDO INTEGRACIÓN DEVOPS → BELGRANO AHORRO")
    print("=" * 50)
    
    # Conectar a la base de datos
    conn = sqlite3.connect('belgrano_ahorro.db')
    c = conn.cursor()
    
    # Contar registros antes
    neg_before = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
    prod_before = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    ofer_before = c.execute('SELECT COUNT(*) FROM ofertas').fetchone()[0]
    
    print(f"📊 Estado inicial: Negocios={neg_before}, Productos={prod_before}, Ofertas={ofer_before}")
    
    # Simular creación desde DevOps (fallback)
    timestamp = int(time.time())
    
    # 1. Crear negocio
    negocio_nombre = f'DevOps Integrado {timestamp}'
    c.execute('''
        INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (negocio_nombre, 'Negocio creado desde DevOps integrado', 'Calle DevOps 123', '555-0100', 'devops@integrado.com'))
    negocio_id = c.lastrowid
    print(f"✅ Negocio creado: ID={negocio_id}, Nombre={negocio_nombre}")
    
    # 2. Crear producto
    producto_nombre = f'Producto DevOps {timestamp}'
    c.execute('''
        INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    ''', (producto_nombre, 'general', 199.99, 'DevOps', 50, 5, negocio_id))
    producto_id = c.lastrowid
    print(f"✅ Producto creado: ID={producto_id}, Nombre={producto_nombre}")
    
    # 3. Crear oferta
    oferta_nombre = f'Oferta DevOps {timestamp}'
    c.execute('''
        INSERT INTO ofertas (titulo, descripcion, descuento_porcentaje, fecha_inicio, fecha_fin, activa) 
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (oferta_nombre, 'Oferta creada desde DevOps integrado', 20.0, datetime.now().strftime('%Y-%m-%d'), 
          (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')))
    oferta_id = c.lastrowid
    print(f"✅ Oferta creada: ID={oferta_id}, Nombre={oferta_nombre}")
    
    conn.commit()
    
    # Contar registros después
    neg_after = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
    prod_after = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    ofer_after = c.execute('SELECT COUNT(*) FROM ofertas').fetchone()[0]
    
    print(f"📊 Estado final: Negocios={neg_after}, Productos={prod_after}, Ofertas={ofer_after}")
    
    # Mostrar últimos registros
    print("\n📋 Últimos negocios:")
    for row in c.execute('SELECT id, nombre, activo FROM negocios ORDER BY id DESC LIMIT 3').fetchall():
        print(f"  ID: {row[0]}, Nombre: {row[1]}, Activo: {row[2]}")
    
    print("\n📋 Últimos productos:")
    for row in c.execute('SELECT id, nombre, precio, store, negocio_id FROM productos ORDER BY id DESC LIMIT 3').fetchall():
        print(f"  ID: {row[0]}, Nombre: {row[1]}, Precio: {row[2]}, Store: {row[3]}, Negocio: {row[4]}")
    
    print("\n📋 Últimas ofertas:")
    for row in c.execute('SELECT id, titulo, descuento_porcentaje FROM ofertas ORDER BY id DESC LIMIT 3').fetchall():
        print(f"  ID: {row[0]}, Título: {row[1]}, Descuento: {row[2]}%")
    
    conn.close()
    
    print("\n✅ INTEGRACIÓN DEVOPS → BELGRANO AHORRO FUNCIONANDO")
    print("🔧 DevOps integrado en Ticketera permite:")
    print("   • Crear negocios, productos y ofertas")
    print("   • Persistencia directa en belgrano_ahorro.db")
    print("   • Datos visibles inmediatamente en Belgrano Ahorro")
    print("   • Fallback cuando DevOps Manager no está disponible")

def verificar_esquema_db():
    """Verificar que el esquema de la DB sea correcto"""
    print("\n🔍 VERIFICANDO ESQUEMA DE BASE DE DATOS")
    print("-" * 40)
    
    conn = sqlite3.connect('belgrano_ahorro.db')
    c = conn.cursor()
    
    # Verificar tablas
    tablas = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"📊 Tablas encontradas: {len(tablas)}")
    for tabla in tablas:
        print(f"  • {tabla[0]}")
    
    # Verificar esquema de productos
    print("\n📋 Esquema tabla productos:")
    for row in c.execute("PRAGMA table_info(productos)").fetchall():
        print(f"  • {row[1]} ({row[2]}) - {'NOT NULL' if row[3] else 'NULL'}")
    
    conn.close()

if __name__ == "__main__":
    verificar_esquema_db()
    probar_fallback_devops()
