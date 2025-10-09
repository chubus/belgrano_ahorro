#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Rápido del Sistema
Verificación rápida de todos los servicios
"""

import requests
import time
from datetime import datetime

def test_servicio(nombre, url, timeout=5):
    """Test rápido de un servicio"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code in [200, 302]:
            return f"✅ {nombre}: FUNCIONANDO"
        else:
            return f"⚠️ {nombre}: Status {response.status_code}"
    except requests.exceptions.Timeout:
        return f"⏰ {nombre}: TIMEOUT"
    except requests.exceptions.ConnectionError:
        return f"❌ {nombre}: NO CONECTADO"
    except Exception as e:
        return f"❌ {nombre}: ERROR - {str(e)[:50]}"

def main():
    """Test rápido del sistema"""
    print("🚀 TEST RÁPIDO DEL SISTEMA")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Servicios a testear
    servicios = [
        ("Belgrano Ahorro", "http://localhost:5000"),
        ("Belgrano Ahorro Health", "http://localhost:5000/health"),
        ("Ticketera", "http://localhost:5001"),
        ("Ticketera Health", "http://localhost:5001/health"),
        ("DevOps", "http://localhost:5002/devops/"),
        ("DevOps Health", "http://localhost:5002/devops/health")
    ]
    
    resultados = []
    
    for nombre, url in servicios:
        resultado = test_servicio(nombre, url)
        print(resultado)
        resultados.append(resultado)
    
    # Test APIs de Belgrano Ahorro
    print("\n🛒 TESTEANDO APIs DE BELGRANO AHORRO...")
    try:
        headers = {'Authorization': 'Bearer belgrano_ahorro_api_key_2025'}
        endpoints = ['negocios', 'productos', 'ofertas', 'sucursales']
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:5000/api/{endpoint}", 
                                      headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ GET /api/{endpoint}: OK")
                else:
                    print(f"⚠️ GET /api/{endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ GET /api/{endpoint}: ERROR - {str(e)[:50]}")
    except Exception as e:
        print(f"❌ Error testeando APIs: {str(e)[:50]}")
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    
    funcionando = sum(1 for r in resultados if "✅" in r)
    total = len(resultados)
    
    print(f"🔗 Servicios funcionando: {funcionando}/{total}")
    
    if funcionando >= 3:
        print("🎉 ¡SISTEMA FUNCIONAL!")
    elif funcionando > 0:
        print("⚠️ Sistema parcialmente funcional")
    else:
        print("❌ Sistema no funcional")
    
    print(f"⏰ Test completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
