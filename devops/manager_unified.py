#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor DevOps Unificado (migrado a paquete devops)
"""
import os
import logging
from datetime import datetime
from typing import Any, Dict, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsBelgranoManagerUnified:
    def __init__(self) -> None:
        self.belgrano_url = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com').rstrip('/')
        self.api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '')
        self.timeout = int(os.getenv('API_TIMEOUT_SECS', '15'))
        retry_strategy = Retry(
            total=int(os.getenv('API_RETRY_TOTAL', '3')),
            backoff_factor=float(os.getenv('API_RETRY_BACKOFF', '0.5')),
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT", "DELETE", "PATCH")
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        logger.info("✅ Cliente API configurado para SOLO datos reales")
        logger.info(f"   URL: {self.belgrano_url}")
        logger.info(f"   API Key: {'*' * len(self.api_key) if self.api_key else 'no-set'}")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    def _req(self, method: str, path: str, **kwargs) -> Tuple[bool, Any]:
        url = f"{self.belgrano_url}/{path.lstrip('/')}"
        try:
            resp = self.session.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
            try:
                data = resp.json()
            except Exception:
                data = resp.text
            return (200 <= resp.status_code < 300), data
        except requests.RequestException as e:
            logger.error(f"HTTP error {method} {url}: {e}")
            return False, str(e)

    def get_items(self, kind: str):
        ok, data = self._req('GET', f"/api/{kind}")
        if ok and isinstance(data, dict) and 'data' in data:
            return data['data']
        return data if ok else []

    def create_item(self, kind: str, payload: Dict[str, Any]):
        ok, data = self._req('POST', f"/api/{kind}", json=payload)
        return (True, 'ok') if ok else (False, str(data))

    def update_item(self, kind: str, item_id: Any, payload: Dict[str, Any]):
        ok, data = self._req('PUT', f"/api/{kind}/{item_id}", json=payload)
        return (True, 'ok') if ok else (False, str(data))

    def delete_item(self, kind: str, item_id: Any):
        ok, data = self._req('DELETE', f"/api/{kind}/{item_id}")
        return (True, 'ok') if ok else (False, str(data))

    def get_productos(self):
        return self.get_items('productos')

    def get_negocios(self):
        return self.get_items('negocios')

    def get_ofertas(self):
        return self.get_items('ofertas')

    def get_sucursales(self):
        return self.get_items('sucursales')

    def create_sucursal(self, payload: Dict[str, Any]):
        return self.create_item('sucursales', payload)

    def test_connectivity(self) -> Dict[str, Any]:
        ok, data = self._req('GET', '/api/health')
        return {"overall_status": "success" if ok else "error", "details": data}

    def get_system_status(self) -> Dict[str, Any]:
        return {
            'timestamp': datetime.now().isoformat(),
            'fallback_mode': False,
            'api_url': self.belgrano_url,
            'api_configured': bool(self.api_key),
        }

# Instancia global exportada
devops_manager_unified = DevOpsBelgranoManagerUnified()
