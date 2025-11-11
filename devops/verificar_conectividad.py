#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo de verificación de conectividad entre APIs
Verifica: Belgrano Ahorro, Ticketera y DevOps
"""

import os
import sys
import requests
from datetime import datetime
from urllib.parse import urljoin

# Agregar ruta del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_paths = [
        os.path.join(current_dir, '.env'),
        os.path.join(current_dir, 'env', '.env'),
        os.path.join(parent_dir, '.env'),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ Variables cargadas desde: {env_path}")
            break
except ImportError:
    print("⚠️  python-dotenv no instalado, usando variables del sistema")

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_endpoint(url, headers=None, timeout=10, description=""):
    """Probar un endpoint HTTP"""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        status = response.status_code
        if 200 <= status < 300:
            return True, f"OK ({status})", response
        elif status == 401:
            return False, f"Unauthorized ({status}) - API Key inválida", response
        elif status == 404:
            return False, f"Not Found ({status}) - Endpoint no existe", response
        elif status == 502:
            return False, f"Bad Gateway ({status}) - Servidor no disponible", response
        else:
            return False, f"Error ({status})", response
    except requests.exceptions.Timeout:
        return False, "Timeout - Servidor no responde", None
    except requests.exceptions.ConnectionError:
        return False, "Connection Error - No se puede conectar", None
    except Exception as e:
        return False, f"Error: {str(e)}", None

def main():
    print_header("🔍 VERIFICACIÓN DE CONECTIVIDAD - APIs Belgrano Ahorro")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ============================================================
    # 1. VERIFICAR CONFIGURACIÓN DE VARIABLES
    # ============================================================
    print_header("1. CONFIGURACIÓN DE VARIABLES DE ENTORNO")
    
    belgrano_url = os.getenv('BELGRANO_AHORRO_URL', '').rstrip('/')
    belgrano_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '')
    ticketera_url = (
        os.getenv('TICKETS_API_URL') or 
        os.getenv('TICKETERA_URL') or 
        os.getenv('DEVOPS_API_URL') or ''
    ).rstrip('/')
    ticketera_api_key = (
        os.getenv('TICKETS_API_KEY') or 
        os.getenv('TICKETERA_API_KEY') or 
        os.getenv('DEVOPS_API_KEY') or ''
    )
    
    config_ok = True
    
    print("📋 Variables de Entorno:")
    if belgrano_url:
        print_success(f"BELGRANO_AHORRO_URL: {belgrano_url}")
    else:
        print_error("BELGRANO_AHORRO_URL: NO CONFIGURADA")
        config_ok = False
    
    if belgrano_api_key:
        masked_key = '*' * min(len(belgrano_api_key), 10) + '...' if len(belgrano_api_key) > 10 else '*' * len(belgrano_api_key)
        print_success(f"BELGRANO_AHORRO_API_KEY: {masked_key}")
    else:
        print_error("BELGRANO_AHORRO_API_KEY: NO CONFIGURADA")
        config_ok = False
    
    if ticketera_url:
        print_success(f"TICKETERA_URL: {ticketera_url}")
    else:
        print_warning("TICKETERA_URL: NO CONFIGURADA (opcional)")
    
    if ticketera_api_key:
        masked_key = '*' * min(len(ticketera_api_key), 10) + '...' if len(ticketera_api_key) > 10 else '*' * len(ticketera_api_key)
        print_success(f"TICKETERA_API_KEY: {masked_key}")
    else:
        print_warning("TICKETERA_API_KEY: NO CONFIGURADA (opcional)")
    
    if not config_ok:
        print_error("\n⚠️  Configuración incompleta. Algunas pruebas fallarán.")
        print_info("Ejecuta: python devops/configurar_env.py")
    
    # ============================================================
    # 2. VERIFICAR BELGRANO AHORRO
    # ============================================================
    print_header("2. CONECTIVIDAD CON BELGRANO AHORRO")
    
    if not belgrano_url:
        print_error("No se puede probar: BELGRANO_AHORRO_URL no configurada")
    else:
        headers = {}
        if belgrano_api_key:
            headers = {
                'Authorization': f'Bearer {belgrano_api_key}',
                'X-API-Key': belgrano_api_key,
                'Content-Type': 'application/json'
            }
        
        # Probar health endpoint
        health_url = urljoin(belgrano_url, '/api/health')
        print(f"Probando: {health_url}")
        success, message, response = test_endpoint(health_url, headers, timeout=15, description="Health Check")
        if success:
            print_success(f"Health Check: {message}")
            if response:
                try:
                    data = response.json()
                    print_info(f"Respuesta: {data}")
                except:
                    print_info(f"Respuesta: {response.text[:100]}")
        else:
            print_error(f"Health Check: {message}")
        
        # Probar endpoint de negocios
        negocios_url = urljoin(belgrano_url, '/api/negocios')
        print(f"\nProbando: {negocios_url}")
        success, message, response = test_endpoint(negocios_url, headers, timeout=15, description="Negocios")
        if success:
            print_success(f"Negocios: {message}")
            if response:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'data' in data:
                        count = len(data['data']) if isinstance(data['data'], list) else 'N/A'
                        print_info(f"Negocios encontrados: {count}")
                    else:
                        count = len(data) if isinstance(data, list) else 'N/A'
                        print_info(f"Negocios encontrados: {count}")
                except:
                    print_info(f"Respuesta recibida (no JSON)")
        else:
            print_error(f"Negocios: {message}")
        
        # Probar endpoint de productos
        productos_url = urljoin(belgrano_url, '/api/productos')
        print(f"\nProbando: {productos_url}")
        success, message, response = test_endpoint(productos_url, headers, timeout=15, description="Productos")
        if success:
            print_success(f"Productos: {message}")
        else:
            print_error(f"Productos: {message}")
        
        # Probar endpoint de ofertas
        ofertas_url = urljoin(belgrano_url, '/api/ofertas')
        print(f"\nProbando: {ofertas_url}")
        success, message, response = test_endpoint(ofertas_url, headers, timeout=15, description="Ofertas")
        if success:
            print_success(f"Ofertas: {message}")
        else:
            print_error(f"Ofertas: {message}")
    
    # ============================================================
    # 3. VERIFICAR TICKETERA
    # ============================================================
    print_header("3. CONECTIVIDAD CON TICKETERA")
    
    if not ticketera_url:
        print_warning("No se puede probar: TICKETERA_URL no configurada")
    else:
        headers = {}
        if ticketera_api_key:
            headers = {
                'Authorization': f'Bearer {ticketera_api_key}',
                'X-API-Key': ticketera_api_key,
                'Content-Type': 'application/json'
            }
        
        # Probar diferentes rutas de health
        health_paths = ['/api/health', '/health', '/status', '/api/status']
        health_ok = False
        for path in health_paths:
            health_url = urljoin(ticketera_url, path)
            print(f"Probando: {health_url}")
            success, message, response = test_endpoint(health_url, headers, timeout=15)
            if success:
                print_success(f"Health Check ({path}): {message}")
                health_ok = True
                if response:
                    try:
                        data = response.json()
                        print_info(f"Respuesta: {data}")
                    except:
                        print_info(f"Respuesta: {response.text[:100]}")
                break
            else:
                print_warning(f"Health Check ({path}): {message}")
        
        if not health_ok:
            print_error("No se pudo conectar con Ticketera en ninguna ruta de health")
        
        # Probar endpoint de tickets (si existe)
        tickets_url = urljoin(ticketera_url, '/api/tickets')
        print(f"\nProbando: {tickets_url}")
        success, message, response = test_endpoint(tickets_url, headers, timeout=15, description="Tickets")
        if success:
            print_success(f"Tickets: {message}")
        else:
            print_warning(f"Tickets: {message} (puede no existir este endpoint)")
    
    # ============================================================
    # 4. VERIFICAR INTEGRACIÓN DEVOPS
    # ============================================================
    print_header("4. VERIFICACIÓN DE INTEGRACIÓN DEVOPS")
    
    try:
        from devops.manager_unified import (
            devops_manager_unified,
            devops_ticketera_manager,
            devops_sync_manager
        )
        
        # Verificar manager de Belgrano Ahorro
        print("\n📦 Manager DevOps - Belgrano Ahorro:")
        if devops_manager_unified.is_configured():
            print_success("Manager configurado correctamente")
            print_info(f"URL: {devops_manager_unified.belgrano_url}")
            
            # Probar conectividad
            print("\nProbando conectividad...")
            connectivity = devops_manager_unified.test_connectivity()
            if connectivity.get('overall_status') == 'success':
                print_success("Conectividad: OK")
            else:
                print_error(f"Conectividad: {connectivity.get('overall_status', 'error')}")
                print_info(f"Detalles: {connectivity.get('details', 'N/A')}")
        else:
            print_error("Manager NO configurado - Falta API Key")
        
        # Verificar manager de Ticketera
        print("\n📦 Manager DevOps - Ticketera:")
        if ticketera_url:
            print_success("Manager configurado")
            print_info(f"URL: {devops_ticketera_manager.ticketera_url if hasattr(devops_ticketera_manager, 'ticketera_url') else 'N/A'}")
        else:
            print_warning("Manager NO configurado - TICKETERA_URL no configurada")
        
        # Verificar sync manager
        print("\n📦 Manager DevOps - Sincronización:")
        try:
            sync_status = devops_sync_manager.get_sync_status()
            print_success("Sync Manager disponible")
            print_info(f"Belgrano Ahorro conectado: {sync_status.get('belgrano_ahorro', {}).get('connected', False)}")
            print_info(f"Ticketera conectada: {sync_status.get('ticketera', {}).get('connected', False)}")
            print_info(f"Sync listo: {sync_status.get('sync_ready', False)}")
        except Exception as e:
            print_error(f"Error verificando sync manager: {e}")
            
    except ImportError as e:
        print_error(f"No se pudo importar managers de DevOps: {e}")
    except Exception as e:
        print_error(f"Error verificando integración DevOps: {e}")
    
    # ============================================================
    # 5. RESUMEN FINAL
    # ============================================================
    print_header("5. RESUMEN FINAL")
    
    print("\n📊 Estado de las Conexiones:")
    print(f"   Belgrano Ahorro: {'✅ Configurado' if belgrano_url and belgrano_api_key else '❌ No configurado'}")
    print(f"   Ticketera: {'✅ Configurado' if ticketera_url else '⚠️  Opcional'}")
    print(f"   DevOps Manager: {'✅ Disponible' if config_ok else '❌ No disponible'}")
    
    print("\n💡 Recomendaciones:")
    if not belgrano_url or not belgrano_api_key:
        print("   1. Configura BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY")
        print("   2. Ejecuta: python devops/configurar_env.py")
    if not ticketera_url:
        print("   3. (Opcional) Configura TICKETERA_URL para integración completa")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

