#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas
"""

import sys
import os

def diagnosticar():
    print("🔍 Diagnóstico de la aplicación...")
    
    # 1. Verificar archivos
    print("\n1. Verificando archivos:")
    archivos_necesarios = [
        'app.py',
        'database.py', 
        'productos.json',
        'templates/base.html',
        'templates/perfil.html'
    ]
    
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO EXISTE")
    
    # 2. Verificar importaciones
    print("\n2. Verificando importaciones:")
    try:
        import flask
        print("   ✅ Flask")
    except ImportError:
        print("   ❌ Flask - NO INSTALADO")
    
    try:
        import werkzeug
        print("   ✅ Werkzeug")
    except ImportError:
        print("   ❌ Werkzeug - NO INSTALADO")
    
    try:
        import db as database
        print("   ✅ database.py")
    except ImportError as e:
        print(f"   ❌ database.py - Error: {e}")
    
    # 3. Verificar base de datos
    print("\n3. Verificando base de datos:")
    if os.path.exists('belgrano_ahorro.db'):
        print("   ✅ Base de datos existe")
        size = os.path.getsize('belgrano_ahorro.db')
        print(f"   📊 Tamaño: {size} bytes")
    else:
        print("   ❌ Base de datos NO EXISTE")
    
    # 4. Verificar rutas en app.py
    print("\n4. Verificando rutas en app.py:")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        rutas_esperadas = [
            '@app.route("/perfil")',
            '@app.route("/registro"',
            '@app.route("/login"',
            '@app.route("/contacto"',
            '@app.route("/sobre-nosotros")'
        ]
        
        for ruta in rutas_esperadas:
            if ruta in contenido:
                print(f"   ✅ {ruta}")
            else:
                print(f"   ❌ {ruta} - NO ENCONTRADA")
                
    except Exception as e:
        print(f"   ❌ Error leyendo app.py: {e}")
    
    # 5. Verificar templates
    print("\n5. Verificando templates:")
    templates_necesarios = [
        'templates/perfil.html',
        'templates/login.html',
        'templates/registro.html',
        'templates/contacto.html',
        'templates/sobre_nosotros.html'
    ]
    
    for template in templates_necesarios:
        if os.path.exists(template):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - NO EXISTE")
    
    print("\n🎯 Diagnóstico completado!")

if __name__ == "__main__":
    diagnosticar() 