"""
Script de Verificación del Sistema de Ticketera
Verifica que:
1. Los usuarios de flota existen y están activos
2. Los tickets se asignan correctamente
3. El campo total está presente en los tickets
"""

import os
import sys

# Agregar el directorio de belgrano_tickets al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'belgrano_tickets'))

from belgrano_tickets.app import app, db
from belgrano_tickets.models import User, Ticket

def verificar_usuarios_flota():
    """Verifica que existan usuarios de flota activos"""
    print("\n" + "="*60)
    print("🔍 VERIFICANDO USUARIOS DE FLOTA")
    print("="*60)
    
    with app.app_context():
        usuarios_flota = User.query.filter_by(role='flota', activo=True).all()
        
        if not usuarios_flota:
            print("❌ ERROR: No hay usuarios de flota activos en la base de datos")
            print("   Ejecuta el script de inicialización para crear usuarios de flota")
            return False
        
        print(f"✅ Se encontraron {len(usuarios_flota)} usuarios de flota activos:\n")
        
        for idx, usuario in enumerate(usuarios_flota, 1):
            # Contar tickets asignados
            tickets_asignados = Ticket.query.filter_by(asignado_a=usuario.id).count()
            tickets_alta_prioridad = Ticket.query.filter_by(
                asignado_a=usuario.id, 
                prioridad='alta'
            ).count()
            
            print(f"   {idx}. {usuario.nombre}")
            print(f"      - ID: {usuario.id}")
            print(f"      - Email: {usuario.email}")
            print(f"      - Username: {usuario.username}")
            print(f"      - Tickets asignados: {tickets_asignados}")
            print(f"      - Tickets alta prioridad: {tickets_alta_prioridad}")
            print()
        
        return True

def verificar_tickets():
    """Verifica los tickets existentes y sus campos"""
    print("\n" + "="*60)
    print("🎫 VERIFICANDO TICKETS")
    print("="*60)
    
    with app.app_context():
        total_tickets = Ticket.query.count()
        
        if total_tickets == 0:
            print("ℹ️ No hay tickets en la base de datos")
            print("   Esto es normal si es una instalación nueva")
            return True
        
        print(f"📊 Total de tickets en la base de datos: {total_tickets}\n")
        
        # Verificar tickets asignados
        tickets_asignados = Ticket.query.filter(Ticket.asignado_a.isnot(None)).count()
        tickets_sin_asignar = Ticket.query.filter(Ticket.asignado_a.is_(None)).count()
        
        print(f"   ✅ Tickets asignados: {tickets_asignados}")
        print(f"   ⏳ Tickets sin asignar: {tickets_sin_asignar}")
        
        # Verificar campo total
        print("\n🔍 Verificando campo 'total' en tickets:")
        tickets_con_total = Ticket.query.filter(Ticket.total > 0).count()
        tickets_sin_total = Ticket.query.filter(Ticket.total == 0).count()
        
        print(f"   ✅ Tickets con total > 0: {tickets_con_total}")
        print(f"   ⚠️ Tickets con total = 0: {tickets_sin_total}")
        
        # Mostrar últimos 5 tickets
        print("\n📋 Últimos 5 tickets:")
        ultimos_tickets = Ticket.query.order_by(Ticket.fecha_creacion.desc()).limit(5).all()
        
        for idx, ticket in enumerate(ultimos_tickets, 1):
            repartidor = "Sin asignar"
            if ticket.asignado_a:
                usuario = User.query.get(ticket.asignado_a)
                if usuario:
                    repartidor = f"{usuario.nombre} (ID: {usuario.id})"
            
            print(f"\n   {idx}. Ticket #{ticket.numero}")
            print(f"      - Cliente: {ticket.cliente_nombre}")
            print(f"      - Total: ${ticket.total:.2f}")
            print(f"      - Estado: {ticket.estado}")
            print(f"      - Prioridad: {ticket.prioridad}")
            print(f"      - Asignado a: {repartidor}")
            print(f"      - Fecha: {ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
        
        return True

def verificar_asignacion_funciona():
    """Verifica que la función de asignación automática funcione"""
    print("\n" + "="*60)
    print("🎯 VERIFICANDO FUNCIÓN DE ASIGNACIÓN AUTOMÁTICA")
    print("="*60)
    
    with app.app_context():
        from belgrano_tickets.app import asignar_repartidor_automatico
        from belgrano_tickets.models import Ticket
        
        # Crear un ticket de prueba (sin guardarlo en BD)
        ticket_prueba = Ticket(
            numero="TEST-VERIFICACION",
            cliente_nombre="Cliente de Prueba",
            cliente_direccion="Dirección de Prueba",
            cliente_telefono="123456789",
            cliente_email="test@test.com",
            productos='[]',
            total=100.0,
            estado='pendiente',
            prioridad='normal'
        )
        
        print("\n🧪 Probando asignación automática...")
        repartidor_nombre, repartidor_id = asignar_repartidor_automatico(ticket_prueba)
        
        if repartidor_nombre and repartidor_id:
            print(f"✅ Asignación exitosa:")
            print(f"   - Repartidor: {repartidor_nombre}")
            print(f"   - ID: {repartidor_id}")
            
            # Verificar que el usuario existe
            usuario = User.query.get(repartidor_id)
            if usuario:
                print(f"   - Email: {usuario.email}")
                print(f"   - Role: {usuario.role}")
                print(f"   - Activo: {usuario.activo}")
            
            return True
        else:
            print("❌ ERROR: No se pudo asignar repartidor")
            print("   Verifica que existan usuarios de flota activos")
            return False

def main():
    """Función principal de verificación"""
    print("\n" + "="*60)
    print("🚀 INICIANDO VERIFICACIÓN DEL SISTEMA DE TICKETERA")
    print("="*60)
    
    resultados = []
    
    # Verificar usuarios de flota
    resultados.append(("Usuarios de Flota", verificar_usuarios_flota()))
    
    # Verificar tickets
    resultados.append(("Tickets", verificar_tickets()))
    
    # Verificar asignación automática
    resultados.append(("Asignación Automática", verificar_asignacion_funciona()))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60 + "\n")
    
    todas_ok = True
    for nombre, resultado in resultados:
        estado = "✅ CORRECTO" if resultado else "❌ ERROR"
        print(f"   {nombre}: {estado}")
        if not resultado:
            todas_ok = False
    
    print("\n" + "="*60)
    if todas_ok:
        print("✅ TODAS LAS VERIFICACIONES PASARON CORRECTAMENTE")
        print("="*60)
        print("\n🎉 El sistema está funcionando correctamente!")
        print("\nPróximos pasos:")
        print("   1. Probar creando un ticket desde Belgrano Ahorro")
        print("   2. Verificar que el repartidor lo vea en su panel")
        print("   3. Confirmar que el total se muestre correctamente")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("="*60)
        print("\n⚠️ Revisa los errores anteriores y corrige los problemas")
    
    print()

if __name__ == "__main__":
    main()
