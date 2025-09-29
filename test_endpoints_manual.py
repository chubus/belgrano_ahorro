#!/usr/bin/env python3
"""
Script para probar endpoints manualmente
"""

import requests
import time

def test_endpoint(url, name):
    """Probar un endpoint específico"""
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"  {status} {name}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 PROBANDO ENDPOINTS MANUALMENTE")
    print("=" * 50)
    
    # Probar Belgrano Ahorro (puerto 5000)
    print("\n🏪 BELGRANO AHORRO (Puerto 5000)")
    print("-" * 30)
    
    belgrano_endpoints = [
        ('http://localhost:5000/', 'Home'),
        ('http://localhost:5000/health', 'Health Check'),
        ('http://localhost:5000/login', 'Login'),
        ('http://localhost:5000/register', 'Register'),
        ('http://localhost:5000/productos', 'Productos'),
        ('http://localhost:5000/carrito', 'Carrito'),
        ('http://localhost:5000/checkout', 'Checkout'),
        ('http://localhost:5000/mis_pedidos', 'Mis Pedidos'),
        ('http://localhost:5000/perfil', 'Perfil'),
        ('http://localhost:5000/admin', 'Admin')
    ]
    
    belgrano_success = 0
    for url, name in belgrano_endpoints:
        if test_endpoint(url, name):
            belgrano_success += 1
    
    # Probar Ticketera (puerto 5001)
    print("\n🎫 TICKETERA (Puerto 5001)")
    print("-" * 30)
    
    ticketera_endpoints = [
        ('http://localhost:5001/', 'Home'),
        ('http://localhost:5001/health', 'Health Check'),
        ('http://localhost:5001/login', 'Login'),
        ('http://localhost:5001/api/tickets', 'API Tickets'),
        ('http://localhost:5001/panel', 'Panel')
    ]
    
    ticketera_success = 0
    for url, name in ticketera_endpoints:
        if test_endpoint(url, name):
            ticketera_success += 1
    
    # Probar DevOps (puerto 5002)
    print("\n🔧 DEVOPS (Puerto 5002)")
    print("-" * 30)
    
    devops_endpoints = [
        ('http://localhost:5002/health', 'Health Check'),
        ('http://localhost:5002/devops/health', 'DevOps Health')
    ]
    
    devops_success = 0
    for url, name in devops_endpoints:
        if test_endpoint(url, name):
            devops_success += 1
    
    # Resumen
    print("\n📊 RESUMEN DE RESULTADOS")
    print("=" * 50)
    print(f"Belgrano Ahorro: {belgrano_success}/{len(belgrano_endpoints)} endpoints funcionando")
    print(f"Ticketera: {ticketera_success}/{len(ticketera_endpoints)} endpoints funcionando")
    print(f"DevOps: {devops_success}/{len(devops_endpoints)} endpoints funcionando")
    
    total_success = belgrano_success + ticketera_success + devops_success
    total_endpoints = len(belgrano_endpoints) + len(ticketera_endpoints) + len(devops_endpoints)
    
    print(f"\nTotal: {total_success}/{total_endpoints} endpoints funcionando")
    print(f"Tasa de éxito: {(total_success/total_endpoints*100):.1f}%")
    
    if total_success > total_endpoints * 0.5:
        print("\n✅ VALIDACIÓN EXITOSA - Listo para deploy")
    else:
        print("\n❌ VALIDACIÓN FALLIDA - Revisar aplicaciones")

if __name__ == "__main__":
    main()

