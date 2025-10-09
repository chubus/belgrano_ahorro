#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Probar Ticketera de forma simple
"""

import subprocess
import time
import requests
import os

def probar_ticketera_simple():
    """Probar Ticketera de forma simple"""
    print("PROBANDO TICKETERA SIMPLE")
    print("=" * 50)
    
    try:
        # Configurar variables de entorno
        os.environ['PORT'] = '5001'
        os.environ['FLASK_ENV'] = 'development'
        
        # Iniciar Ticketera
        print("Iniciando Ticketera...")
        proceso = subprocess.Popen(['python', 'app_tickets.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Esperar más tiempo
        print("Esperando 15 segundos...")
        time.sleep(15)
        
        # Verificar si está corriendo
        if proceso.poll() is None:
            print("OK Proceso corriendo")
            
            # Probar conectividad
            try:
                response = requests.get('http://localhost:5001/', timeout=5)
                print(f"OK Ticketera conectado - Status: {response.status_code}")
                return True
            except requests.exceptions.ConnectionError:
                print("ERROR No se puede conectar")
                return False
            except Exception as e:
                print(f"ERROR {e}")
                return False
        else:
            stdout, stderr = proceso.communicate()
            print("ERROR Proceso terminado")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR General: {e}")
        return False
    finally:
        # Terminar proceso
        try:
            proceso.terminate()
        except:
            pass

def main():
    """Función principal"""
    print("PRUEBA SIMPLE DE TICKETERA")
    print("=" * 60)
    
    if probar_ticketera_simple():
        print("\nTICKETERA FUNCIONA CORRECTAMENTE")
        return True
    else:
        print("\nTICKETERA NO FUNCIONA")
        return False

if __name__ == "__main__":
    main()
<<<<<<< HEAD

=======
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
