#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente robusto para invocar la Ticketera desde Belgrano Ahorro.
Limita el impacto de timeouts y entrega siempre un fallback seguro.
"""

import json
import logging
import os
import time
from typing import Dict, Tuple, Union

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = min(float(os.getenv("TICKETERA_TIMEOUT_SECS", "2.5")), 3.0)
MAX_RETRIES = max(0, min(int(os.getenv("TICKETERA_RETRY_TOTAL", "1")), 3))
BACKOFF_FACTOR = float(os.getenv("TICKETERA_RETRY_BACKOFF", "0.4"))

_SESSION = requests.Session()


def _build_headers() -> Dict[str, str]:
    api_key = os.getenv("TICKETERA_API_KEY", os.getenv("BELGRANO_AHORRO_API_KEY", ""))
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        headers["X-API-Key"] = api_key
    return headers


def _normalize_ofertas(payload: Union[Dict, list]) -> Dict[str, list]:
    """
    Normaliza la respuesta de Ticketera para devolver siempre {"ofertas": [...]}
    """
    ofertas: list = []

    if isinstance(payload, dict):
        if "data" in payload:
            payload = payload["data"]
        elif "ofertas" in payload:
            payload = payload["ofertas"]
        else:
            # Posible formato {negocio: [ofertas]}
            flattened = []
            for value in payload.values():
                if isinstance(value, list):
                    flattened.extend(value)
                elif isinstance(value, dict):
                    flattened.append(value)
            payload = flattened or []

    if isinstance(payload, list):
        ofertas = [item for item in payload if isinstance(item, dict)]
    elif isinstance(payload, dict):
        ofertas = [payload]

    return {"ofertas": ofertas}


def _safe_json(response: requests.Response) -> Union[Dict, list]:
    try:
        return response.json()
    except ValueError:
        logger.warning("[Ticketera] Respuesta sin JSON válido; usando contenido plano.")
        return json.loads(response.text or "{}") if response.text else {}


def _call_ticketera_endpoint(
    url: str,
    timeout: float,
    retries: int,
) -> Tuple[bool, Dict[str, list]]:
    headers = _build_headers()
    attempts = max(1, retries + 1)
    timeout = max(0.5, min(timeout, 3.0))

    for attempt in range(attempts):
        try:
            response = _SESSION.get(url, headers=headers, timeout=timeout)

            if 200 <= response.status_code < 300:
                payload = _safe_json(response) if response.content else {}
                return True, _normalize_ofertas(payload)

            if response.status_code in (404, 405):
                logger.info(f"[Ticketera] Endpoint {url} no disponible ({response.status_code}).")
                return False, {"ofertas": []}

            logger.warning(
                "[Ticketera] Código inesperado %s en %s",
                response.status_code,
                url,
            )
        except requests.exceptions.Timeout:
            logger.warning("[Ticketera] Timeout (%ss) consultando %s", timeout, url)
        except requests.exceptions.RequestException as exc:
            logger.error("[Ticketera] Error de conexión (%s): %s", url, exc)
            break  # Errores graves no tienen sentido reintentar

        if attempt < attempts - 1:
            sleep_time = BACKOFF_FACTOR * (2 ** attempt)
            time.sleep(min(sleep_time, 1.5))

    return False, {"ofertas": []}


def fetch_ticketera_ofertas(
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = MAX_RETRIES,
) -> Tuple[bool, Dict[str, list]]:
    """
    Intenta obtener ofertas desde Ticketera respetando timeouts cortos.
    Nunca levanta excepción: siempre retorna (exito, {"ofertas": [...]})
    """
    base_url = os.getenv("TICKETERA_URL", "https://ticketerabelgrano.onrender.com").rstrip("/")
    if not base_url:
        logger.info("[Ticketera] URL no configurada; usando fallback.")
        return False, {"ofertas": []}

    paths = ("/api/ofertas", "/ofertas")
    for path in paths:
        success, data = _call_ticketera_endpoint(f"{base_url}{path}", timeout, retries)
        if success:
            logger.info("[Ticketera] Ofertas obtenidas exitosamente desde %s", path)
            return True, data

    logger.info("[Ticketera] No se pudieron obtener ofertas, usando fallback vacío.")
    return False, {"ofertas": []}


