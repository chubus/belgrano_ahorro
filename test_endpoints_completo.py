#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba completa de endpoints DevOps → Belgrano Ahorro
Verifica creación real y visibilidad de datos
"""

import requests
import sqlite3
import time
import json
from urllib.parse import urljoin

# Configuración de servicios
SERVICIOS = {
    'belgrano_ahorro': 'http://localhost:5000',
    'ticketera': 'http://localhost:5001', 
    'devops': 'http://localhost:5002'
}

def verificar_servicio(url, nombre):
    """Verificar si un servicio está disponible"""
    try:
        r = requests.get(url, timeout=5)
        print(f"✅ {nombre}: {r.status_code}")
        return True
    except Exception as e:
        print(f"❌ {nombre}: {e}")
        return False

def test_devops_login():
    """Probar login en DevOps"""
    print("\n🔐 PROBANDO LOGIN DEVOPS...")
    
    devops_url = SERVICIOS['devops']
    session = requests.Session()
    
    # Obtener formulario de login
    login_url = urljoin(devops_url, '/devops/login')
    try:
        r = session.get(login_url, timeout=5)
        print(f"GET /devops/login: {r.status_code}")
    except Exception as e:
        print(f"Error obteniendo login: {e}")
        return None
    
    # Hacer login
    login_data = {
        'username': 'devops',
        'password': 'DevOps2025!Secure'
    }
    
    try:
        r = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"POST /devops/login: {r.status_code}")
        if r.status_code in [302, 200]:
            print("✅ Login exitoso")
            return session
        else:
            print(f"❌ Login falló: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def test_crear_negocio(session):
    """Probar creación de negocio"""
    print("\n🏢 PROBANDO CREACIÓN DE NEGOCIO...")
    
    devops_url = SERVICIOS['devops']
    negocio_nombre = f'Test Negocio DevOps {int(time.time())}'
    
    negocio_data = {
        'nombre': negocio_nombre,
        'descripcion': 'Negocio creado desde prueba DevOps',
        'direccion': 'Calle Test 123',
        'telefono': '123456789',
        'email': 'test@devops.com'
    }
    
    try:
        r = session.post(
            urljoin(devops_url, '/devops/negocios'),
            data=negocio_data,
            allow_redirects=False
        )
        print(f"POST /devops/negocios: {r.status_code}")
        
        if r.status_code in [200, 302]:
            print("✅ Negocio creado exitosamente")
            return negocio_nombre
        else:
            print(f"❌ Error creando negocio: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Error creando negocio: {e}")
        return None

def test_crear_producto(session):
    """Probar creación de producto"""
    print("\n📦 PROBANDO CREACIÓN DE PRODUCTO...")
    
    devops_url = SERVICIOS['devops']
    producto_nombre = f'Test Producto DevOps {int(time.time())}'
    
    # Obtener ID de negocio existente
    conn = sqlite3.connect('belgrano_ahorro.db')
    c = conn.cursor()
    negocio_id = c.execute('SELECT id FROM negocios ORDER BY id DESC LIMIT 1').fetchone()
    negocio_id = negocio_id[0] if negocio_id else 1
    conn.close()
    
    producto_data = {
        'nombre': producto_nombre,
        'precio': '99.99',
        'categoria': 'Test',
        'negocio': str(negocio_id),
        'descripcion': 'Producto creado desde prueba DevOps',
        'imagen': ''
    }
    
    try:
        r = session.post(
            urljoin(devops_url, '/devops/productos'),
            data=producto_data,
            allow_redirects=False
        )
        print(f"POST /devops/productos: {r.status_code}")
        
        if r.status_code in [200, 302]:
            print("✅ Producto creado exitosamente")
            return producto_nombre
        else:
            print(f"❌ Error creando producto: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Error creando producto: {e}")
        return None

def verificar_base_datos():
    """Verificar que los datos se guardaron en la base"""
    print("\n🗄️ VERIFICANDO BASE DE DATOS...")
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar registros
        negocios_count = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        productos_count = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        print(f"📊 Negocios en DB: {negocios_count}")
        print(f"📊 Productos en DB: {productos_count}")
        
        # Mostrar últimos registros
        print("\n🏢 Últimos negocios:")
        for row in c.execute('SELECT id, nombre, activo FROM negocios ORDER BY id DESC LIMIT 3').fetchall():
            print(f"   ID: {row[0]}, Nombre: {row[1]}, Activo: {row[2]}")
        
        print("\n📦 Últimos productos:")
        for row in c.execute('SELECT id, nombre, precio, store, negocio_id FROM productos ORDER BY id DESC LIMIT 3').fetchall():
            print(f"   ID: {row[0]}, Nombre: {row[1]}, Precio: {row[2]}, Store: {row[3]}, Negocio: {row[4]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base: {e}")
        return False

def test_visibilidad_ahorro():
    """Probar que los datos son visibles en Belgrano Ahorro"""
    print("\n👁️ VERIFICANDO VISIBILIDAD EN BELGRANO AHORRO...")
    
    ahorro_url = SERVICIOS['belgrano_ahorro']
    
    try:
        # Probar endpoint de productos
        r = requests.get(urljoin(ahorro_url, '/api/v1/productos'), timeout=5)
        print(f"GET /api/v1/productos: {r.status_code}")
        
        if r.status_code == 200:
            productos = r.json().get('productos', [])
            print(f"✅ Productos visibles en Ahorro: {len(productos)}")
            
            # Mostrar algunos productos
            for prod in productos[:3]:
                print(f"   - {prod.get('nombre', 'N/A')} (${prod.get('precio', 'N/A')})")
        else:
            print(f"❌ Error obteniendo productos: {r.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error verificando visibilidad: {e}")

def main():
    """Función principal de prueba"""
    print("=" * 60)
    print("🧪 PRUEBA COMPLETA DEVOPS → BELGRANO AHORRO")
    print("=" * 60)
    
    # 1. Verificar servicios
    print("\n1️⃣ VERIFICANDO SERVICIOS...")
    servicios_ok = True
    for nombre, url in SERVICIOS.items():
        if not verificar_servicio(url, nombre):
            servicios_ok = False
    
    if not servicios_ok:
        print("\n❌ Algunos servicios no están disponibles")
        print("💡 Ejecuta: python start_servicios_separados.py")
        return
    
    # 2. Login DevOps
    session = test_devops_login()
    if not session:
        print("\n❌ No se pudo hacer login en DevOps")
        return
    
    # 3. Crear negocio
    negocio_nombre = test_crear_negocio(session)
    if not negocio_nombre:
        print("\n❌ No se pudo crear negocio")
        return
    
    # 4. Crear producto
    producto_nombre = test_crear_producto(session)
    if not producto_nombre:
        print("\n❌ No se pudo crear producto")
        return
    
    # 5. Verificar base de datos
    verificar_base_datos()
    
    # 6. Verificar visibilidad en Ahorro
    test_visibilidad_ahorro()
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
