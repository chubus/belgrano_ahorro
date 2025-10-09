#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la conectividad DevOps
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_devops_endpoints():
    """Probar todos los endpoints de DevOps"""
    
    base_url = "http://localhost:5000"  # Ajustar según tu configuración
    endpoints = [
        "/devops/health",
        "/devops/status", 
        "/devops/info",
        "/devops/system-status",
        "/devops/conectar-belgrano"
    ]
    
    print("🔧 Probando conectividad DevOps...")
    print("=" * 50)
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Probando: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ OK - {response.status_code}")
                    print(f"   📊 Status: {data.get('status', 'unknown')}")
                    if 'data' in data:
                        print(f"   📈 Datos: {len(str(data['data']))} caracteres")
                except:
                    print(f"   ✅ OK - {response.status_code} (HTML)")
            else:
                print(f"   ⚠️  {response.status_code}")
                
            results[endpoint] = {
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Error de conexión")
            results[endpoint] = {
                'status_code': 0,
                'success': False,
                'error': 'Connection error'
            }
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[endpoint] = {
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
        
        print()
    
    # Resumen
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print("=" * 50)
    print(f"📊 RESUMEN: {successful}/{total} endpoints funcionando")
    
    if successful == total:
        print("🎉 ¡Todos los endpoints funcionan correctamente!")
    elif successful > 0:
        print("⚠️  Algunos endpoints funcionan, otros tienen problemas")
    else:
        print("❌ Ningún endpoint funciona - revisar configuración")
    
    return results

def test_api_connectivity():
    """Probar conectividad con la API externa"""
    
    print("\n🌐 Probando conectividad con API externa...")
    print("=" * 50)
    
    # Verificar variables de entorno
    belgrano_url = os.environ.get('BELGRANO_AHORRO_URL')
    belgrano_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
    
    print(f"🔗 URL: {belgrano_url or 'No configurada'}")
    print(f"🔑 API Key: {'Configurada' if belgrano_key else 'No configurada'}")
    
    if not belgrano_url or not belgrano_key:
        print("⚠️  Variables de entorno no configuradas - modo fallback activado")
        return
    
    # Probar endpoints de la API
    api_endpoints = [
        "/api/tickets",
        "/api/v1/ofertas", 
        "/api/v1/negocios",
        "/api/v1/productos",
        "/api/v1/sucursales"
    ]
    
    headers = {
        'X-API-Key': belgrano_key,
        'Content-Type': 'application/json'
    }
    
    for endpoint in api_endpoints:
        try:
            url = f"{belgrano_url}{endpoint}"
            print(f"📡 Probando API: {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ OK - {response.status_code}")
            elif response.status_code == 302:
                print(f"   🔄 Redirigido - {response.status_code} (posible problema de autenticación)")
            elif response.status_code == 404:
                print(f"   ❌ No encontrado - {response.status_code}")
            elif response.status_code == 500:
                print(f"   💥 Error interno - {response.status_code}")
            else:
                print(f"   ⚠️  {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Error de conexión")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conectividad DevOps")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Probar endpoints DevOps
    devops_results = test_devops_endpoints()
    
    # Probar API externa
    test_api_connectivity()
    
    print("\n✅ Pruebas completadas")
    print("📝 Para más detalles, revisar los logs del sistema")
