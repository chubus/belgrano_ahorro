#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar automáticamente el sistema DevOps
"""

import os
import sys

def configurar_variables_entorno():
    """Configurar variables de entorno para DevOps"""
    print("CONFIGURANDO VARIABLES DE ENTORNO DEVOPS")
    print("=" * 50)
    
    # Variables de configuración
    configuracion = {
        'DEVOPS_USERNAME': 'devops',
        'DEVOPS_PASSWORD': 'DevOps2025!Secure',
        'BELGRANO_AHORRO_URL': 'https://belgranoahorro-aliq.onrender.com',
        'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025',
        'GATEWAY_URL': 'http://localhost:5003/gateway',
        'GATEWAY_API_KEY': 'belgrano_ahorro_api_key_2025',
        'TICKETERA_URL': 'http://localhost:5001',
        'TICKETERA_API_KEY': 'ticketera_api_key_2025',
        'SECRET_KEY': 'devops_secret_key_2025',
        'API_TIMEOUT': '30',
        'API_RETRY_ATTEMPTS': '3',
        'API_RETRY_DELAY': '1',
        'CACHE_TTL': '300',
        'SYNC_INTERVAL': '60'
    }
    
    configuradas = 0
    
    for variable, valor in configuracion.items():
        os.environ[variable] = valor
        print(f"OK {variable} = {valor[:10]}..." if len(valor) > 10 else f"OK {variable} = {valor}")
        configuradas += 1
    
    print(f"\nVariables configuradas: {configuradas}/{len(configuracion)}")
    return configuradas == len(configuracion)

def verificar_dependencias():
    """Verificar que las dependencias están instaladas"""
    print("\nVERIFICANDO DEPENDENCIAS")
    print("=" * 50)
    
    dependencias = [
        'flask',
        'requests',
        'werkzeug',
        'sqlite3'
    ]
    
    dependencias_ok = []
    
    for dep in dependencias:
        try:
            if dep == 'sqlite3':
                import sqlite3
            else:
                __import__(dep)
            print(f"OK {dep}")
            dependencias_ok.append(dep)
        except ImportError:
            print(f"ERROR {dep} - NO INSTALADA")
    
    print(f"\nDependencias instaladas: {len(dependencias_ok)}/{len(dependencias)}")
    return len(dependencias_ok) == len(dependencias)

def verificar_archivos_criticos():
    """Verificar que los archivos críticos existen"""
    print("\nVERIFICANDO ARCHIVOS CRITICOS")
    print("=" * 50)
    
    archivos_criticos = [
        'devops_routes.py',
        'belgrano_client_gateway.py',
        'api_gateway.py',
        'sync_manager.py',
        'api_belgrano_ahorro.py',
        'app_tickets.py',
        'templates/devops/base.html',
        'templates/devops/login.html',
        'templates/devops/dashboard.html',
        'belgrano_ahorro.db',
        'belgrano_tickets.db'
    ]
    
    archivos_ok = []
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"OK {archivo}")
            archivos_ok.append(archivo)
        else:
            print(f"ERROR {archivo} - NO ENCONTRADO")
    
    print(f"\nArchivos encontrados: {len(archivos_ok)}/{len(archivos_criticos)}")
    return len(archivos_ok) == len(archivos_criticos)

def crear_script_inicio():
    """Crear script de inicio para DevOps"""
    print("\nCREANDO SCRIPT DE INICIO")
    print("=" * 50)
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio para DevOps
"""

import os
import sys
import subprocess
import time

def iniciar_devops():
    """Iniciar sistema DevOps"""
    print("INICIANDO SISTEMA DEVOPS")
    print("=" * 40)
    
    # Cargar configuración
    from configurar_devops import configurar_variables_entorno
    configurar_variables_entorno()
    
    # Iniciar servicios
    servicios = [
        ('Belgrano Ahorro', 'python app.py'),
        ('Ticketera', 'python app_tickets.py'),
        ('DevOps', 'python devops_routes.py'),
        ('API Gateway', 'python api_gateway.py'),
        ('Sync Manager', 'python sync_manager.py')
    ]
    
    procesos = []
    
    for nombre, comando in servicios:
        try:
            print(f"Iniciando {nombre}...")
            proceso = subprocess.Popen(comando, shell=True)
            procesos.append((nombre, proceso))
            time.sleep(2)
            print(f"✅ {nombre} iniciado")
        except Exception as e:
            print(f"❌ Error iniciando {nombre}: {e}")
    
    print("\\nSistema DevOps iniciado correctamente")
    print("Presiona Ctrl+C para detener todos los servicios")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\nDeteniendo servicios...")
        for nombre, proceso in procesos:
            try:
                proceso.terminate()
                print(f"✅ {nombre} detenido")
            except:
                print(f"⚠️ Error deteniendo {nombre}")

if __name__ == "__main__":
    iniciar_devops()
'''
    
    with open('iniciar_devops.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("OK Script de inicio creado: iniciar_devops.py")
    return True

def main():
    """Función principal"""
    print("CONFIGURACION AUTOMATICA DEL SISTEMA DEVOPS")
    print("=" * 60)
    
    # Configurar variables de entorno
    config_ok = configurar_variables_entorno()
    
    # Verificar dependencias
    deps_ok = verificar_dependencias()
    
    # Verificar archivos críticos
    archivos_ok = verificar_archivos_criticos()
    
    # Crear script de inicio
    script_ok = crear_script_inicio()
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE CONFIGURACION")
    print("=" * 60)
    
    print(f"Variables de entorno: {'OK' if config_ok else 'ERROR'}")
    print(f"Dependencias: {'OK' if deps_ok else 'ERROR'}")
    print(f"Archivos críticos: {'OK' if archivos_ok else 'ERROR'}")
    print(f"Script de inicio: {'OK' if script_ok else 'ERROR'}")
    
    if config_ok and deps_ok and archivos_ok and script_ok:
        print("\nSISTEMA DEVOPS CONFIGURADO CORRECTAMENTE")
        print("Listo para deploy")
        print("\nPara iniciar el sistema:")
        print("python iniciar_devops.py")
    else:
        print("\nSISTEMA REQUIERE CORRECCIONES")
        print("Revisar errores antes del deploy")
    
    return config_ok and deps_ok and archivos_ok and script_ok

if __name__ == "__main__":
    main()
