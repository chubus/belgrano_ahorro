import os
import json
from flask import Flask, render_template

print("=== DIAGNÓSTICO DE LA APLICACIÓN ===")

# Verificar estructura de directorios
print("\n1. Verificando estructura de directorios:")
print(f"Directorio actual: {os.getcwd()}")
print(f"Archivos en el directorio: {os.listdir('.')}")

if os.path.exists('templates'):
    print(f"Directorio templates existe: {os.listdir('templates')}")
else:
    print("❌ ERROR: Directorio templates no existe")

if os.path.exists('static'):
    print(f"Directorio static existe: {os.listdir('static')}")
else:
    print("❌ ERROR: Directorio static no existe")

# Verificar archivos críticos
print("\n2. Verificando archivos críticos:")
critical_files = ['app.py', 'productos.json', 'templates/base.html', 'templates/index.html', 'static/style.css']

for file in critical_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"✅ {file} existe ({size} bytes)")
    else:
        print(f"❌ {file} NO existe")

# Verificar contenido de productos.json
print("\n3. Verificando productos.json:")
try:
    with open('productos.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"✅ JSON válido: {len(data['productos'])} productos")
        for i, producto in enumerate(data['productos']):
            print(f"   Producto {i+1}: {producto['nombre']} - ${producto['precio']}")
except Exception as e:
    print(f"❌ Error al leer productos.json: {e}")

# Verificar contenido de templates
print("\n4. Verificando templates:")
try:
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"✅ index.html: {len(content)} caracteres")
        if '{% for producto in productos' in content:
            print("   ✅ Contiene bucle de productos")
        else:
            print("   ❌ NO contiene bucle de productos")
except Exception as e:
    print(f"❌ Error al leer index.html: {e}")

try:
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"✅ base.html: {len(content)} caracteres")
        if '{% block content %}' in content:
            print("   ✅ Contiene bloque content")
        else:
            print("   ❌ NO contiene bloque content")
except Exception as e:
    print(f"❌ Error al leer base.html: {e}")

print("\n=== FIN DEL DIAGNÓSTICO ===") 