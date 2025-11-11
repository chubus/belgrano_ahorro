#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper robusto para requests a APIs externas
Evita bloqueos por APIs lentas y previene errores de timeout
"""
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Cache local simple en memoria
CACHE: Dict[str, Dict[str, Any]] = {}


def cached_request(
    url: str,
    method: str = "GET",
    timeout: int = 20,  # 20s por defecto para producción
    retries: int = 2,
    cache_ttl: int = 60,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Helper robusto para hacer requests a APIs externas con cache y manejo de errores
    
    Args:
        url: URL a la que hacer el request
        method: Método HTTP (GET, POST, PUT, DELETE)
        timeout: Timeout en segundos (default: 10)
        retries: Número de reintentos (default: 2)
        cache_ttl: Tiempo de vida del cache en segundos (default: 60)
        headers: Headers HTTP opcionales
        json_data: Datos JSON para POST/PUT
        **kwargs: Argumentos adicionales para requests
    
    Returns:
        Dict con los datos de la respuesta o error
    """
    # Solo cachear GET requests
    use_cache = method.upper() == "GET"
    cache_key = f"{method}:{url}"
    
    # Devuelve desde caché si no ha expirado (solo para GET)
    if use_cache and cache_key in CACHE:
        elapsed = time.time() - CACHE[cache_key]["time"]
        if elapsed < cache_ttl:
            logger.debug(f"✅ Cache hit para {url} ({elapsed:.1f}s)")
            return CACHE[cache_key]["data"]
        else:
            # Cache expirado, limpiar
            del CACHE[cache_key]
    
    # Configurar sesión con retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # Headers por defecto
    request_headers = headers or {}
    if json_data and "Content-Type" not in request_headers:
        request_headers["Content-Type"] = "application/json"
    
    try:
        # Para servicios en Render, hacer un "wake-up" request rápido primero si es GET
        if method.upper() == "GET" and "render.com" in url:
            try:
                session.head(url, headers=request_headers, timeout=5)
            except:
                pass  # Ignorar errores del wake-up
        
        # Realizar request
        if method.upper() == "GET":
            response = session.get(url, headers=request_headers, timeout=timeout, **kwargs)
        elif method.upper() == "POST":
            response = session.post(url, headers=request_headers, json=json_data, timeout=timeout, **kwargs)
        elif method.upper() == "PUT":
            response = session.put(url, headers=request_headers, json=json_data, timeout=timeout, **kwargs)
        elif method.upper() == "DELETE":
            response = session.delete(url, headers=request_headers, timeout=timeout, **kwargs)
        else:
            return {"error": f"Método {method} no soportado"}
        
        response.raise_for_status()
        
        # Intentar parsear JSON
        try:
            data = response.json()
        except:
            data = {"text": response.text, "status_code": response.status_code}
        
        # Guardar en cache solo para GET requests exitosos
        if use_cache and 200 <= response.status_code < 300:
            CACHE[cache_key] = {"data": data, "time": time.time()}
            logger.debug(f"✅ Request exitoso y cacheado: {url}")
        
        return data
        
    except requests.Timeout:
        logger.warning(f"⏳ Timeout alcanzado en {url}, usando datos cacheados si existen.")
        # Intentar devolver cache si existe
        if use_cache and cache_key in CACHE:
            logger.info(f"📦 Usando datos en cache debido a timeout")
            return CACHE[cache_key]["data"]
        return {"error": "timeout", "message": "El servicio puede estar iniciando. Intenta nuevamente en unos segundos."}
    
    except requests.HTTPError as e:
        logger.warning(f"⚠️ HTTP error en {url}: {e.response.status_code}")
        # Intentar devolver cache si existe
        if use_cache and cache_key in CACHE:
            logger.info(f"📦 Usando datos en cache debido a error HTTP")
            return CACHE[cache_key]["data"]
        return {"error": f"http_error_{e.response.status_code}", "message": str(e)}
    
    except Exception as e:
        logger.error(f"⚠️ Error accediendo a {url}: {e}")
        # Intentar devolver cache si existe
        if use_cache and cache_key in CACHE:
            logger.info(f"📦 Usando datos en cache debido a error")
            return CACHE[cache_key]["data"]
        return {"error": str(e), "message": "Error de conexión"}


def clear_cache(pattern: Optional[str] = None):
    """
    Limpiar cache (opcionalmente por patrón)
    
    Args:
        pattern: Patrón para filtrar keys a eliminar (ej: "GET:/api/negocios")
    """
    global CACHE
    if pattern:
        keys_to_delete = [k for k in CACHE.keys() if pattern in k]
        for key in keys_to_delete:
            del CACHE[key]
        logger.info(f"🗑️ Cache limpiado: {len(keys_to_delete)} entradas eliminadas")
    else:
        CACHE.clear()
        logger.info("🗑️ Cache completamente limpiado")


