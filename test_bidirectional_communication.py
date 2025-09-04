#!/usr/bin/env python3
"""
Script de prueba para verificar la comunicación bidireccional entre DevOps y Belgrano Ahorro
Prueba la creación de negocios desde DevOps y su sincronización con Belgrano Ahorro
"""

import requests
import json
import time
import sys
from datetime import datetime
import uuid

# Configuración
DEVOPS_BASE_URL = "http://127.0.0.1:10000"  # URL base de DevOps
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"  # URL de Belgrano Ahorro
API_KEY = "belgrano_ahorro_api_key_2025"

# Headers para las peticiones
DEVOPS_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

BELGRANO_HEADERS = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
    'X-Origin': 'test_script'
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="INFO"):
    """Imprimir mensaje con colores según el estado"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "SUCCESS":
        print(f"{Colors.GREEN}✅ [{timestamp}] {message}{Colors.ENDC}")
    elif status == "ERROR":
        print(f"{Colors.RED}❌ [{timestamp}] {message}{Colors.ENDC}")
    elif status == "WARNING":
        print(f"{Colors.YELLOW}⚠️  [{timestamp}] {message}{Colors.ENDC}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ️  [{timestamp}] {message}{Colors.ENDC}")
    else:
        print(f"[{timestamp}] {message}")

def test_devops_health():
    """Probar que DevOps esté funcionando"""
    print_status("Probando salud de DevOps...", "INFO")
    try:
        response = requests.get(f"{DEVOPS_BASE_URL}/devops/health", timeout=10)
        if response.status_code == 200:
            print_status("DevOps está funcionando correctamente", "SUCCESS")
            return True
        else:
            print_status(f"DevOps respondió con código {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Error conectando con DevOps: {e}", "ERROR")
        return False

def test_belgrano_ahorro_health():
    """Probar que Belgrano Ahorro esté funcionando"""
    print_status("Probando salud de Belgrano Ahorro...", "INFO")
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/healthz", headers=BELGRANO_HEADERS, timeout=10)
        if response.status_code == 200:
            print_status("Belgrano Ahorro está funcionando correctamente", "SUCCESS")
            return True
        else:
            print_status(f"Belgrano Ahorro respondió con código {response.status_code}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Error conectando con Belgrano Ahorro: {e}", "WARNING")
        return False

def get_negocios_from_belgrano():
    """Obtener lista de negocios desde Belgrano Ahorro"""
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/v1/negocios", headers=BELGRANO_HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print_status(f"Error obteniendo negocios desde Belgrano Ahorro: {response.status_code}", "WARNING")
            return []
    except Exception as e:
        print_status(f"Error conectando con Belgrano Ahorro: {e}", "WARNING")
        return []

def get_negocios_from_devops():
    """Obtener lista de negocios desde DevOps"""
    try:
        response = requests.get(f"{DEVOPS_BASE_URL}/devops/negocios", headers=DEVOPS_HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print_status(f"Error obteniendo negocios desde DevOps: {response.status_code}", "WARNING")
            return []
    except Exception as e:
        print_status(f"Error conectando con DevOps: {e}", "WARNING")
        return []

def create_negocio_from_devops():
    """Crear un negocio desde DevOps"""
    negocio_id = str(uuid.uuid4())[:8]
    negocio_data = {
        "nombre": f"Negocio Test {negocio_id}",
        "descripcion": f"Descripción del negocio de prueba {negocio_id}",
        "categoria": "Pruebas",
        "direccion": "Dirección de prueba 123",
        "telefono": "+54 11 1234-5678",
        "email": f"test{negocio_id}@ejemplo.com"
    }
    
    print_status(f"Creando negocio desde DevOps: {negocio_data['nombre']}", "INFO")
    
    try:
        response = requests.post(
            f"{DEVOPS_BASE_URL}/devops/agregar_negocio",
            headers=DEVOPS_HEADERS,
            json=negocio_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print_status(f"Negocio creado exitosamente desde DevOps", "SUCCESS")
                return negocio_data, True
            else:
                print_status(f"Error en respuesta de DevOps: {result.get('message', 'Error desconocido')}", "ERROR")
                return negocio_data, False
        else:
            print_status(f"Error HTTP {response.status_code}: {response.text}", "ERROR")
            return negocio_data, False
            
    except Exception as e:
        print_status(f"Error creando negocio desde DevOps: {e}", "ERROR")
        return negocio_data, False

def verify_negocio_in_belgrano(negocio_data, max_attempts=5, delay=2):
    """Verificar que el negocio aparezca en Belgrano Ahorro"""
    print_status("Verificando sincronización con Belgrano Ahorro...", "INFO")
    
    for attempt in range(max_attempts):
        time.sleep(delay)
        negocios = get_negocios_from_belgrano()
        
        # Buscar el negocio por nombre
        for negocio in negocios:
            if negocio.get('nombre') == negocio_data['nombre']:
                print_status(f"✅ Negocio encontrado en Belgrano Ahorro: {negocio['nombre']}", "SUCCESS")
                return True, negocio
        
        print_status(f"Intento {attempt + 1}/{max_attempts}: Negocio no encontrado aún...", "WARNING")
    
    print_status("❌ Negocio no se sincronizó con Belgrano Ahorro después de varios intentos", "ERROR")
    return False, None

def test_bidirectional_sync():
    """Probar sincronización bidireccional completa"""
    print_status("=" * 60, "INFO")
    print_status("INICIANDO PRUEBA DE COMUNICACIÓN BIDIRECCIONAL", "INFO")
    print_status("=" * 60, "INFO")
    
    # 1. Verificar salud de los servicios
    print_status("\n1. Verificando salud de los servicios...", "INFO")
    devops_ok = test_devops_health()
    belgrano_ok = test_belgrano_ahorro_health()
    
    if not devops_ok:
        print_status("❌ DevOps no está disponible. Abortando prueba.", "ERROR")
        return False
    
    # 2. Obtener estado inicial
    print_status("\n2. Obteniendo estado inicial de negocios...", "INFO")
    negocios_belgrano_inicial = get_negocios_from_belgrano()
    negocios_devops_inicial = get_negocios_from_devops()
    
    print_status(f"Negocios en Belgrano Ahorro (inicial): {len(negocios_belgrano_inicial)}", "INFO")
    print_status(f"Negocios en DevOps (inicial): {len(negocios_devops_inicial)}", "INFO")
    
    # 3. Crear negocio desde DevOps
    print_status("\n3. Creando negocio desde DevOps...", "INFO")
    negocio_data, created = create_negocio_from_devops()
    
    if not created:
        print_status("❌ No se pudo crear el negocio desde DevOps", "ERROR")
        return False
    
    # 4. Verificar sincronización con Belgrano Ahorro
    print_status("\n4. Verificando sincronización con Belgrano Ahorro...", "INFO")
    synced, negocio_synced = verify_negocio_in_belgrano(negocio_data)
    
    if not synced:
        print_status("❌ La sincronización falló", "ERROR")
        return False
    
    # 5. Verificar que DevOps puede leer el negocio sincronizado
    print_status("\n5. Verificando lectura desde DevOps...", "INFO")
    negocios_devops_final = get_negocios_from_devops()
    
    # Buscar el negocio en la lista de DevOps
    negocio_encontrado = False
    for negocio in negocios_devops_final:
        if negocio.get('nombre') == negocio_data['nombre']:
            negocio_encontrado = True
            print_status(f"✅ Negocio encontrado en DevOps: {negocio['nombre']}", "SUCCESS")
            break
    
    if not negocio_encontrado:
        print_status("⚠️  Negocio no encontrado en la lista de DevOps", "WARNING")
    
    # 6. Resumen final
    print_status("\n" + "=" * 60, "INFO")
    print_status("RESUMEN DE LA PRUEBA", "INFO")
    print_status("=" * 60, "INFO")
    
    print_status(f"✅ DevOps funcionando: {'Sí' if devops_ok else 'No'}", "SUCCESS" if devops_ok else "ERROR")
    print_status(f"✅ Belgrano Ahorro funcionando: {'Sí' if belgrano_ok else 'No'}", "SUCCESS" if belgrano_ok else "WARNING")
    print_status(f"✅ Negocio creado desde DevOps: {'Sí' if created else 'No'}", "SUCCESS" if created else "ERROR")
    print_status(f"✅ Sincronización con Belgrano Ahorro: {'Sí' if synced else 'No'}", "SUCCESS" if synced else "ERROR")
    print_status(f"✅ Lectura desde DevOps: {'Sí' if negocio_encontrado else 'No'}", "SUCCESS" if negocio_encontrado else "WARNING")
    
    # Determinar resultado general
    if created and synced:
        print_status("\n🎉 PRUEBA EXITOSA: Comunicación bidireccional funcionando", "SUCCESS")
        return True
    else:
        print_status("\n❌ PRUEBA FALLIDA: Hay problemas en la comunicación bidireccional", "ERROR")
        return False

def main():
    """Función principal"""
    print_status("Script de prueba de comunicación bidireccional DevOps ↔ Belgrano Ahorro", "INFO")
    print_status("Versión: 1.0.0", "INFO")
    print_status(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    
    try:
        success = test_bidirectional_sync()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\nPrueba interrumpida por el usuario", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error inesperado: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
