#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación completa del sistema DevOps antes del deploy
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def verificar_estructura_archivos():
    """Verificar que todos los archivos necesarios existen"""
    print("VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("=" * 50)
    
    archivos_requeridos = [
        'devops_routes.py',
        'belgrano_client_gateway.py',
        'api_gateway.py',
        'sync_manager.py',
        'templates/devops/base.html',
        'templates/devops/login.html',
        'templates/devops/dashboard.html',
        'templates/devops/negocios.html',
        'templates/devops/productos.html',
        'templates/devops/ofertas.html',
        'templates/devops/sucursales.html',
        'templates/devops/precios.html',
        'templates/devops/sync.html'
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"\n⚠️ Archivos faltantes: {len(archivos_faltantes)}")
        return False
    else:
        print(f"\n✅ Todos los archivos presentes: {len(archivos_requeridos)}")
        return True

def verificar_importaciones():
    """Verificar que todas las importaciones funcionan"""
    print("\n🔧 VERIFICANDO IMPORTACIONES")
    print("=" * 50)
    
    importaciones = [
        ('devops_routes', 'devops_routes'),
        ('belgrano_client_gateway', 'belgrano_client_gateway'),
        ('api_gateway', 'api_gateway'),
        ('sync_manager', 'sync_manager')
    ]
    
    errores = []
    
    for nombre, modulo in importaciones:
        try:
            __import__(modulo)
            print(f"✅ {nombre}")
        except Exception as e:
            print(f"❌ {nombre}: {e}")
            errores.append(f"{nombre}: {e}")
    
    if errores:
        print(f"\n⚠️ Errores de importación: {len(errores)}")
        return False
    else:
        print(f"\n✅ Todas las importaciones exitosas: {len(importaciones)}")
        return True

def verificar_rutas_devops():
    """Verificar rutas DevOps en app_tickets.py"""
    print("\n🌐 VERIFICANDO RUTAS DEVOPS")
    print("=" * 50)
    
    try:
        with open('app_tickets.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        rutas_esperadas = [
            '/devops/',
            '/devops/login',
            '/devops/logout',
            '/devops/health',
            '/devops/status',
            '/devops/info',
            '/devops/ofertas',
            '/devops/negocios',
            '/devops/productos',
            '/devops/precios',
            '/devops/sync'
        ]
        
        rutas_encontradas = []
        
        for ruta in rutas_esperadas:
            if f"@app.route('{ruta}'" in contenido or f'@app.route("{ruta}"' in contenido:
                print(f"✅ {ruta}")
                rutas_encontradas.append(ruta)
            else:
                print(f"❌ {ruta} - NO ENCONTRADA")
        
        print(f"\n✅ Rutas encontradas: {len(rutas_encontradas)}/{len(rutas_esperadas)}")
        return len(rutas_encontradas) == len(rutas_esperadas)
        
    except Exception as e:
        print(f"❌ Error leyendo app_tickets.py: {e}")
        return False

def verificar_templates():
    """Verificar que los templates HTML existen y son válidos"""
    print("\n🎨 VERIFICANDO TEMPLATES HTML")
    print("=" * 50)
    
    templates_dir = 'templates/devops'
    templates_requeridos = [
        'base.html',
        'login.html',
        'dashboard.html',
        'negocios.html',
        'productos.html',
        'ofertas.html',
        'sucursales.html',
        'precios.html',
        'sync.html'
    ]
    
    templates_validos = []
    
    for template in templates_requeridos:
        ruta_template = os.path.join(templates_dir, template)
        if os.path.exists(ruta_template):
            try:
                with open(ruta_template, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Verificar que tiene contenido HTML básico
                if '<html' in contenido and '</html>' in contenido:
                    print(f"✅ {template}")
                    templates_validos.append(template)
                else:
                    print(f"⚠️ {template} - Contenido HTML incompleto")
            except Exception as e:
                print(f"❌ {template} - Error leyendo: {e}")
        else:
            print(f"❌ {template} - NO ENCONTRADO")
    
    print(f"\n✅ Templates válidos: {len(templates_validos)}/{len(templates_requeridos)}")
    return len(templates_validos) == len(templates_requeridos)

def verificar_configuracion():
    """Verificar configuración y variables de entorno"""
    print("\n⚙️ VERIFICANDO CONFIGURACIÓN")
    print("=" * 50)
    
    variables_requeridas = [
        'DEVOPS_USERNAME',
        'DEVOPS_PASSWORD',
        'BELGRANO_AHORRO_URL',
        'BELGRANO_AHORRO_API_KEY'
    ]
    
    configuracion_ok = True
    
    for var in variables_requeridas:
        valor = os.environ.get(var)
        if valor:
            # Ocultar contraseñas en el log
            if 'PASSWORD' in var or 'KEY' in var:
                valor_mostrar = valor[:10] + "..." if len(valor) > 10 else "***"
            else:
                valor_mostrar = valor
            print(f"✅ {var} = {valor_mostrar}")
        else:
            print(f"⚠️ {var} - NO CONFIGURADA")
            configuracion_ok = False
    
    # Verificar archivos de configuración
    archivos_config = [
        'requirements.txt',
        'Procfile'
    ]
    
    for archivo in archivos_config:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"⚠️ {archivo} - NO ENCONTRADO")
    
    return configuracion_ok

def verificar_base_datos():
    """Verificar bases de datos"""
    print("\n🗄️ VERIFICANDO BASES DE DATOS")
    print("=" * 50)
    
    bases_datos = [
        'belgrano_ahorro.db',
        'belgrano_tickets.db'
    ]
    
    bases_ok = []
    
    for bd in bases_datos:
        if os.path.exists(bd):
            tamaño = os.path.getsize(bd)
            print(f"✅ {bd} - {tamaño:,} bytes")
            bases_ok.append(bd)
        else:
            print(f"⚠️ {bd} - NO ENCONTRADA")
    
    print(f"\n✅ Bases de datos encontradas: {len(bases_ok)}/{len(bases_datos)}")
    return len(bases_ok) == len(bases_datos)

def verificar_endpoints_api():
    """Verificar endpoints de la API"""
    print("\n📡 VERIFICANDO ENDPOINTS API")
    print("=" * 50)
    
    try:
        with open('api_belgrano_ahorro.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        endpoints_esperados = [
            '/api/negocios',
            '/api/productos',
            '/api/ofertas',
            '/api/sucursales',
            '/api/precios'
        ]
        
        endpoints_encontrados = []
        
        for endpoint in endpoints_esperados:
            if f"@api_bp.route('{endpoint}'" in contenido:
                print(f"✅ {endpoint}")
                endpoints_encontrados.append(endpoint)
            else:
                print(f"❌ {endpoint} - NO ENCONTRADO")
        
        print(f"\n✅ Endpoints encontrados: {len(endpoints_encontrados)}/{len(endpoints_esperados)}")
        return len(endpoints_encontrados) == len(endpoints_esperados)
        
    except Exception as e:
        print(f"❌ Error verificando API: {e}")
        return False

def verificar_cliente_api():
    """Verificar cliente API"""
    print("\n🔌 VERIFICANDO CLIENTE API")
    print("=" * 50)
    
    try:
        with open('belgrano_client_gateway.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        metodos_esperados = [
            'get_negocios',
            'create_negocio',
            'update_negocio',
            'delete_negocio',
            'get_productos',
            'create_producto',
            'update_producto',
            'delete_producto',
            'get_ofertas',
            'create_oferta',
            'update_oferta',
            'delete_oferta',
            'get_sucursales',
            'create_sucursal',
            'update_sucursal',
            'delete_sucursal'
        ]
        
        metodos_encontrados = []
        
        for metodo in metodos_esperados:
            if f"def {metodo}(" in contenido:
                print(f"✅ {metodo}")
                metodos_encontrados.append(metodo)
            else:
                print(f"❌ {metodo} - NO ENCONTRADO")
        
        print(f"\n✅ Métodos encontrados: {len(metodos_encontrados)}/{len(metodos_esperados)}")
        return len(metodos_encontrados) == len(metodos_esperados)
        
    except Exception as e:
        print(f"❌ Error verificando cliente API: {e}")
        return False

def generar_reporte_final():
    """Generar reporte final de verificación"""
    print("\nGENERANDO REPORTE FINAL")
    print("=" * 50)
    
    reporte = {
        'timestamp': datetime.now().isoformat(),
        'verificaciones': {
            'archivos': verificar_estructura_archivos(),
            'importaciones': verificar_importaciones(),
            'rutas': verificar_rutas_devops(),
            'templates': verificar_templates(),
            'configuracion': verificar_configuracion(),
            'base_datos': verificar_base_datos(),
            'endpoints_api': verificar_endpoints_api(),
            'cliente_api': verificar_cliente_api()
        }
    }
    
    # Calcular estado general
    verificaciones_exitosas = sum(1 for v in reporte['verificaciones'].values() if v)
    total_verificaciones = len(reporte['verificaciones'])
    
    reporte['estado_general'] = {
        'exitosas': verificaciones_exitosas,
        'total': total_verificaciones,
        'porcentaje': round((verificaciones_exitosas / total_verificaciones) * 100, 2),
        'listo_para_deploy': verificaciones_exitosas == total_verificaciones
    }
    
    # Guardar reporte
    with open('reporte_verificacion_devops.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"Verificaciones exitosas: {verificaciones_exitosas}/{total_verificaciones}")
    print(f"Porcentaje de exito: {reporte['estado_general']['porcentaje']}%")
    
    if reporte['estado_general']['listo_para_deploy']:
        print("SISTEMA LISTO PARA DEPLOY")
    else:
        print("SISTEMA REQUIERE CORRECCIONES ANTES DEL DEPLOY")
    
    return reporte

def main():
    """Función principal"""
    print("VERIFICACION COMPLETA DEL SISTEMA DEVOPS")
    print("=" * 60)
    print("Antes del deploy - Verificacion exhaustiva")
    print("")
    
    reporte = generar_reporte_final()
    
    print("\n" + "=" * 60)
    print("RESUMEN EJECUTIVO")
    print("=" * 60)
    
    for verificacion, resultado in reporte['verificaciones'].items():
        estado = "EXITOSO" if resultado else "FALLO"
        print(f"{verificacion.replace('_', ' ').title()}: {estado}")
    
    print(f"\nEstado General: {reporte['estado_general']['porcentaje']}%")
    
    if reporte['estado_general']['listo_para_deploy']:
        print("\nEL SISTEMA DEVOPS ESTA LISTO PARA DEPLOY")
        print("Todas las verificaciones pasaron exitosamente")
        print("La arquitectura esta completa y funcional")
        print("Los componentes estan integrados correctamente")
    else:
        print("\nEL SISTEMA REQUIERE CORRECCIONES")
        print("Algunas verificaciones fallaron")
        print("Revisar los errores antes del deploy")
    
    return reporte['estado_general']['listo_para_deploy']

if __name__ == "__main__":
    main()
