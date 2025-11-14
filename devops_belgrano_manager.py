#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor DevOps para Belgrano Ahorro
Módulo de gestión segura para administrar ofertas, productos, negocios y precios
Compatibilidad: reexporta desde manager_unified
"""

# Importar desde manager_unified (manager.py fue eliminado)
try:
    from devops.manager_unified import DevOpsBelgranoManagerUnified as DevOpsBelgranoManager  # type: ignore
except ImportError:
    # Fallback si no se puede importar desde el paquete
    import sys
    import os
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _devops_dir = os.path.join(_current_dir, 'devops')
    if _devops_dir not in sys.path:
        sys.path.insert(0, _devops_dir)
    from manager_unified import DevOpsBelgranoManagerUnified as DevOpsBelgranoManager  # type: ignore
