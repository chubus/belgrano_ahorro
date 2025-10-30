#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente HTTP resiliente para APIs externas (Belgrano Ahorro y DevOps).
Incluye manejo de errores no bloqueante y función de health-check.
"""

import os
import logging
from typing import Any, Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    def request(self, method: str, path: str, **kwargs) -> Tuple[bool, Any, int]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
            status = response.status_code
            try:
                data = response.json()
            except Exception:
                data = response.text
            if 200 <= status < 300:
                return True, data, status
            logger.warning(f"API {method} {url} -> {status}: {data}")
            return False, data, status
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {method} {url} -> {e}")
            return False, str(e), 0


def check_api_health() -> Dict[str, Any]:
    """Prueba de salud de Belgrano Ahorro y DevOps; no bloquea."""
    belgrano_url = os.getenv("BELGRANO_AHORRO_URL", "https://belgranoahorro-hp30.onrender.com")
    belgrano_key = os.getenv("BELGRANO_AHORRO_API_KEY")
    devops_url = os.getenv("DEVOPS_API_URL", os.getenv("TICKETERA_URL", "http://localhost:5002"))
    devops_key = os.getenv("DEVOPS_API_KEY")

    belgrano = ApiClient(belgrano_url, belgrano_key)
    devops = ApiClient(devops_url, devops_key)

    ok_belgrano, data_belgrano, status_belgrano = belgrano.request("GET", "/api/health")
    ok_devops, data_devops, status_devops = devops.request("GET", "/api/health")

    return {
        "belgrano": {"ok": ok_belgrano, "status": status_belgrano, "data": data_belgrano},
        "devops": {"ok": ok_devops, "status": status_devops, "data": data_devops},
    }



