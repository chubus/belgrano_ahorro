#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio para Belgrano Ahorro
Maneja la inicialización y configuración del sistema
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar el entorno de la aplicación"""
    
    # Configurar variables de entorno por defecto
    default_env_vars = {
        'FLASK_ENV': 'production',
        'PYTHONPATH': '.',
        'PORT': '10000'
    }
    
    for key, value in default_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            logger.info(f"Configurando {key}={value}")

def verify_app_structure():
    """Verificar que la estructura de la aplicación sea correcta"""
    
    required_files = [
        'app_unificado.py',
        'requirements.txt',
        'belgrano_tickets/app.py',
        'belgrano_tickets/models.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Archivos faltantes: {missing_files}")
        return False
    
    logger.info("✅ Estructura de archivos verificada")
    return True

def start_application():
    """Iniciar la aplicación"""
    try:
        # Configurar entorno
        setup_environment()
        
        # Verificar estructura
        if not verify_app_structure():
            logger.error("❌ Error en la estructura de archivos")
            return False
        
        # Importar la aplicación principal
        logger.info("🚀 Iniciando Belgrano Ahorro...")
        from app_unificado import app
        
        # Configurar puerto
        port = int(os.environ.get('PORT', 10000))
        
        # Iniciar aplicación
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error iniciando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = start_application()
    sys.exit(0 if success else 1)
