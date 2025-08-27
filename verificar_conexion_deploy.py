#!/usr/bin/env python3
"""
Script de verificación de conexión entre plataformas para deploy
Verifica que Belgrano Ahorro y Belgrano Tickets se comuniquen correctamente
"""

import requests
import time
import json
import os
from datetime import datetime

def verificar_conexion_entre_plataformas():
    """Verificar que ambas plataformas se comunican correctamente"""
    
    print("🔍 VERIFICACIÓN DE CONEXIÓN ENTRE PLATAFORMAS")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs de producción (configurables)
    ahorro_url = os.environ.get('AHORRO_URL', 'https://belgrano-ahorro.onrender.com')
    tickets_url = os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
    
    print(f"🌐 Belgrano Ahorro: {ahorro_url}")
    print(f"🎫 Belgrano Tickets: {tickets_url}")
    print()
    
    resultados = {
        'ahorro_status': False,
        'tickets_status': False,
        'api_integration': False,
        'errors': []
    }
    
    # 1. Verificar que Belgrano Ahorro responde
    print("1️⃣ Verificando Belgrano Ahorro...")
    try:
        response = requests.get(f"{ahorro_url}/test", timeout=10)
        if response.status_code == 200:
            print("   ✅ Belgrano Ahorro está funcionando")
            resultados['ahorro_status'] = True
        else:
            print(f"   ⚠️ Belgrano Ahorro responde con código: {response.status_code}")
            resultados['errors'].append(f"Ahorro status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar a Belgrano Ahorro")
        resultados['errors'].append("Connection error to Ahorro")
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout conectando a Belgrano Ahorro")
        resultados['errors'].append("Timeout connecting to Ahorro")
    except Exception as e:
        print(f"   ❌ Error conectando a Belgrano Ahorro: {e}")
        resultados['errors'].append(f"Error connecting to Ahorro: {e}")
    
    print()
    
    # 2. Verificar que Belgrano Tickets responde
    print("2️⃣ Verificando Belgrano Tickets...")
    try:
        response = requests.get(f"{tickets_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Belgrano Tickets está funcionando")
            resultados['tickets_status'] = True
            
            # Mostrar información del health check
            try:
                health_data = response.json()
                print(f"   📊 Estado: {health_data.get('status', 'N/A')}")
                print(f"   🗄️ Base de datos: {health_data.get('database', 'N/A')}")
                print(f"   🎫 Total tickets: {health_data.get('total_tickets', 'N/A')}")
            except:
                print("   📄 Respuesta de texto recibida")
        else:
            print(f"   ⚠️ Belgrano Tickets responde con código: {response.status_code}")
            resultados['errors'].append(f"Tickets status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar a Belgrano Tickets")
        resultados['errors'].append("Connection error to Tickets")
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout conectando a Belgrano Tickets")
        resultados['errors'].append("Timeout connecting to Tickets")
    except Exception as e:
        print(f"   ❌ Error conectando a Belgrano Tickets: {e}")
        resultados['errors'].append(f"Error connecting to Tickets: {e}")
    
    print()
    
    # 3. Verificar API de integración
    print("3️⃣ Verificando API de integración...")
    if resultados['tickets_status']:
        try:
            test_data = {
                "numero": f"TEST-{int(time.time())}",
                "cliente_nombre": "Cliente Test Deploy",
                "cliente_direccion": "Dirección Test Deploy",
                "cliente_telefono": "123456789",
                "cliente_email": "test-deploy@belgranoahorro.com",
                "productos": ["Producto Test Deploy x1"],
                "total": 100.0,
                "metodo_pago": "efectivo",
                "indicaciones": "Test de integración para deploy"
            }
            
            print(f"   📤 Enviando datos de prueba: {test_data['numero']}")
            
            response = requests.post(
                f"{tickets_url}/api/tickets",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 201:
                print("   ✅ API de integración funciona correctamente")
                resultados['api_integration'] = True
                
                try:
                    response_data = response.json()
                    print(f"   🎫 Ticket creado: {response_data.get('ticket_id', 'N/A')}")
                except:
                    print("   📄 Respuesta recibida")
            else:
                print(f"   ⚠️ API de integración responde con código: {response.status_code}")
                print(f"   📄 Respuesta: {response.text}")
                resultados['errors'].append(f"API integration status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ No se puede conectar a la API de integración")
            resultados['errors'].append("Connection error to API integration")
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout en API de integración")
            resultados['errors'].append("Timeout in API integration")
        except Exception as e:
            print(f"   ❌ Error en API de integración: {e}")
            resultados['errors'].append(f"Error in API integration: {e}")
    else:
        print("   ⏭️ Saltando verificación de API (Tickets no disponible)")
    
    print()
    
    # 4. Resumen de resultados
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 30)
    
    total_checks = 3
    passed_checks = sum([
        resultados['ahorro_status'],
        resultados['tickets_status'],
        resultados['api_integration']
    ])
    
    print(f"✅ Checks pasados: {passed_checks}/{total_checks}")
    print(f"❌ Checks fallidos: {total_checks - passed_checks}/{total_checks}")
    
    if resultados['ahorro_status']:
        print("   ✅ Belgrano Ahorro: FUNCIONANDO")
    else:
        print("   ❌ Belgrano Ahorro: FALLO")
    
    if resultados['tickets_status']:
        print("   ✅ Belgrano Tickets: FUNCIONANDO")
    else:
        print("   ❌ Belgrano Tickets: FALLO")
    
    if resultados['api_integration']:
        print("   ✅ API de Integración: FUNCIONANDO")
    else:
        print("   ❌ API de Integración: FALLO")
    
    if resultados['errors']:
        print()
        print("🚨 ERRORES DETECTADOS:")
        for i, error in enumerate(resultados['errors'], 1):
            print(f"   {i}. {error}")
    
    print()
    
    # 5. Recomendaciones
    print("💡 RECOMENDACIONES")
    print("=" * 20)
    
    if passed_checks == total_checks:
        print("🎉 ¡Sistema completamente funcional!")
        print("   - Todas las plataformas están operativas")
        print("   - La integración funciona correctamente")
        print("   - El sistema está listo para producción")
    elif passed_checks >= 2:
        print("⚠️ Sistema parcialmente funcional")
        print("   - Algunas funciones pueden no estar disponibles")
        print("   - Revisar los errores listados arriba")
        print("   - Verificar configuración de URLs")
    else:
        print("🚨 Sistema con problemas críticos")
        print("   - Revisar configuración de deploy")
        print("   - Verificar que las aplicaciones estén ejecutándose")
        print("   - Comprobar variables de entorno")
    
    return resultados

def verificar_endpoints_detallado():
    """Verificación detallada de endpoints específicos"""
    
    print("\n🔍 VERIFICACIÓN DETALLADA DE ENDPOINTS")
    print("=" * 40)
    
    ahorro_url = os.environ.get('AHORRO_URL', 'https://belgrano-ahorro.onrender.com')
    tickets_url = os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
    
    endpoints_ahorro = [
        ('/', 'Página principal'),
        ('/test', 'Test de funcionamiento'),
        ('/login', 'Página de login'),
        ('/register', 'Página de registro')
    ]
    
    endpoints_tickets = [
        ('/', 'Página principal'),
        ('/health', 'Health check'),
        ('/login', 'Login admin'),
        ('/admin', 'Panel admin')
    ]
    
    print("🌐 Endpoints Belgrano Ahorro:")
    for endpoint, desc in endpoints_ahorro:
        try:
            response = requests.get(f"{ahorro_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code < 400 else "⚠️"
            print(f"   {status} {endpoint} - {desc} ({response.status_code})")
        except:
            print(f"   ❌ {endpoint} - {desc} (Error de conexión)")
    
    print("\n🎫 Endpoints Belgrano Tickets:")
    for endpoint, desc in endpoints_tickets:
        try:
            response = requests.get(f"{tickets_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code < 400 else "⚠️"
            print(f"   {status} {endpoint} - {desc} ({response.status_code})")
        except:
            print(f"   ❌ {endpoint} - {desc} (Error de conexión)")

def generar_reporte(resultados):
    """Generar reporte en formato JSON"""
    
    reporte = {
        'fecha_verificacion': datetime.now().isoformat(),
        'resultados': resultados,
        'configuracion': {
            'ahorro_url': os.environ.get('AHORRO_URL', 'https://belgrano-ahorro.onrender.com'),
            'tickets_url': os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
        }
    }
    
    # Guardar reporte
    with open('reporte_verificacion_deploy.json', 'w') as f:
        json.dump(reporte, f, indent=2)
    
    print("\n📄 Reporte guardado en: reporte_verificacion_deploy.json")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE DEPLOY")
    print("=" * 40)
    
    # Verificación principal
    resultados = verificar_conexion_entre_plataformas()
    
    # Verificación detallada
    verificar_endpoints_detallado()
    
    # Generar reporte
    generar_reporte(resultados)
    
    print("\n🏁 Verificación completada")
    print("=" * 25)
