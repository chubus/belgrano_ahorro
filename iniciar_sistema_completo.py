#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar el sistema completo: Belgrano Ahorro + Belgrano Tickets
"""

import subprocess
import time
import sys
import os
import signal
import threading
from datetime import datetime

class SistemaCompleto:
    def __init__(self):
        self.procesos = []
        self.detener = False
        
    def iniciar_belgrano_ahorro(self):
        """Iniciar aplicación principal de Belgrano Ahorro"""
        print("🚀 Iniciando Belgrano Ahorro...")
        try:
            proceso = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.procesos.append(("Belgrano Ahorro", proceso))
            print("✅ Belgrano Ahorro iniciado en puerto 5000")
            return True
        except Exception as e:
            print(f"❌ Error iniciando Belgrano Ahorro: {e}")
            return False
    
    def iniciar_belgrano_tickets(self):
        """Iniciar aplicación de Belgrano Tickets"""
        print("🚀 Iniciando Belgrano Tickets...")
        try:
            # Cambiar al directorio de belgrano_tickets
            os.chdir("belgrano_tickets")
            
            proceso = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.procesos.append(("Belgrano Tickets", proceso))
            print("✅ Belgrano Tickets iniciado en puerto 5001")
            
            # Volver al directorio original
            os.chdir("..")
            return True
        except Exception as e:
            print(f"❌ Error iniciando Belgrano Tickets: {e}")
            # Volver al directorio original en caso de error
            os.chdir("..")
            return False
    
    def monitorear_procesos(self):
        """Monitorear los procesos en segundo plano"""
        while not self.detener:
            for nombre, proceso in self.procesos:
                if proceso.poll() is not None:
                    print(f"⚠️ {nombre} se detuvo inesperadamente")
                    # Intentar reiniciar
                    if nombre == "Belgrano Ahorro":
                        self.iniciar_belgrano_ahorro()
                    elif nombre == "Belgrano Tickets":
                        self.iniciar_belgrano_tickets()
            time.sleep(5)
    
    def detener_procesos(self):
        """Detener todos los procesos"""
        print("\n🛑 Deteniendo procesos...")
        self.detener = True
        
        for nombre, proceso in self.procesos:
            try:
                print(f"   Deteniendo {nombre}...")
                proceso.terminate()
                proceso.wait(timeout=5)
                print(f"   ✅ {nombre} detenido")
            except subprocess.TimeoutExpired:
                print(f"   ⚠️ {nombre} no respondió, forzando cierre...")
                proceso.kill()
            except Exception as e:
                print(f"   ❌ Error deteniendo {nombre}: {e}")
    
    def iniciar_sistema(self):
        """Iniciar el sistema completo"""
        print("🎯 INICIANDO SISTEMA COMPLETO - BELGRANO AHORRO + TICKETS")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Iniciar aplicaciones
        if not self.iniciar_belgrano_ahorro():
            print("❌ No se pudo iniciar Belgrano Ahorro")
            return False
        
        time.sleep(2)  # Esperar un poco entre aplicaciones
        
        if not self.iniciar_belgrano_tickets():
            print("❌ No se pudo iniciar Belgrano Tickets")
            self.detener_procesos()
            return False
        
        # Iniciar monitoreo en segundo plano
        monitor_thread = threading.Thread(target=self.monitorear_procesos, daemon=True)
        monitor_thread.start()
        
        print()
        print("🎉 SISTEMA INICIADO EXITOSAMENTE")
        print("=" * 40)
        print("📱 URLs disponibles:")
        print("   • Belgrano Ahorro: http://localhost:5000")
        print("   • Belgrano Tickets: http://localhost:5001")
        print()
        print("🔐 Credenciales Belgrano Tickets:")
        print("   • Admin: admin@belgranoahorro.com / admin123")
        print("   • Flota: repartidor1@belgranoahorro.com / flota123")
        print()
        print("🔄 Integración automática activada:")
        print("   • Los pedidos de Belgrano Ahorro se envían automáticamente a Belgrano Tickets")
        print("   • Los tickets se crean con prioridad alta para comerciantes")
        print("   • Asignación automática de repartidores")
        print()
        print("⏹️  Presiona Ctrl+C para detener el sistema")
        print("=" * 60)
        
        try:
            # Mantener el script ejecutándose
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Señal de interrupción recibida")
            self.detener_procesos()
            print("✅ Sistema detenido correctamente")
            return True

def main():
    """Función principal"""
    sistema = SistemaCompleto()
    
    # Configurar manejo de señales
    def signal_handler(signum, frame):
        print("\n🛑 Señal recibida, deteniendo sistema...")
        sistema.detener_procesos()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar sistema
    try:
        sistema.iniciar_sistema()
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")
        sistema.detener_procesos()
        return False

if __name__ == "__main__":
    main()
