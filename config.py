#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración simple y segura para variables de entorno.
No detiene la app si faltan variables críticas; emite warnings y usa valores por defecto.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Valores por defecto seguros para desarrollo
BELGRANO_AHORRO_API_KEY = os.getenv("BELGRANO_AHORRO_API_KEY", "dev_key_placeholder")
DEVOPS_API_KEY = os.getenv("DEVOPS_API_KEY", "devops_key_placeholder")

BELGRANO_AHORRO_URL = os.getenv("BELGRANO_AHORRO_URL", "https://belgranoahorro-hp30.onrender.com")
DEVOPS_API_URL = os.getenv("DEVOPS_API_URL", os.getenv("TICKETERA_URL", "http://localhost:5002"))


def load_env_defaults() -> None:
    """Asegura que existan variables mínimas con valores por defecto y emite warnings.

    No levanta excepciones: la app debe poder iniciar en entornos de dev/test sin bloquearse.
    """
    defaults = {
        "BELGRANO_AHORRO_API_KEY": BELGRANO_AHORRO_API_KEY,
        "DEVOPS_API_KEY": DEVOPS_API_KEY,
        "BELGRANO_AHORRO_URL": BELGRANO_AHORRO_URL,
        "DEVOPS_API_URL": DEVOPS_API_URL,
    }

    for key, value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.warning(f"ENV {key} no configurada, usando valor por defecto: {value}")


def validate_env_non_blocking() -> None:
    """Valida variables críticas y emite warnings si faltan o parecen inválidas."""
    checks = [
        ("BELGRANO_AHORRO_URL", os.getenv("BELGRANO_AHORRO_URL")),
        ("BELGRANO_AHORRO_API_KEY", os.getenv("BELGRANO_AHORRO_API_KEY")),
        ("DEVOPS_API_URL", os.getenv("DEVOPS_API_URL")),
        ("DEVOPS_API_KEY", os.getenv("DEVOPS_API_KEY")),
    ]

    for name, val in checks:
        if not val or str(val).strip() == "":
            logger.warning(f"ENV {name} ausente; ciertas funciones externas podrían fallar")




