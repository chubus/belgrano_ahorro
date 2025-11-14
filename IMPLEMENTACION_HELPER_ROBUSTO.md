# ✅ Implementación del Helper Robusto para APIs

## 📋 Cambios Realizados

### 1. **Nuevo Módulo `devops/api_helpers.py`**
- Helper `cached_request()` implementado según especificaciones
- Cache en memoria con TTL configurable
- Manejo robusto de timeouts y errores
- Wake-up request para servicios en Render
- Fallback automático a cache cuando hay timeout

### 2. **Actualización de `devops/manager_unified.py`**
- Reemplazado sistema de requests directos por `cached_request()`
- Simplificado código eliminando lógica duplicada
- Timeout por defecto: 8 segundos (configurable)
- Cache TTL: 120 segundos (configurable)
- Reintentos: 2 (configurable)

### 3. **Actualización de `devops/routes.py`**
- Reemplazados `requests.get()` directos por `cached_request()`
- Health checks ahora usan el helper robusto
- MockResponse para compatibilidad con código existente

### 4. **Configuración de Gunicorn Actualizada**
- **Procfile**: Agregado `--threads 2`
- **render.yaml**: Agregado `--threads 2`
- **render_devops.yaml**: Agregado `--threads 2`
- Timeout: 120 segundos (ya estaba configurado)

## 🎯 Características del Helper

### `cached_request()` - Funcionalidades

1. **Cache Automático**
   - Solo cachea GET requests
   - TTL configurable (default: 120s)
   - Devuelve datos del cache si están válidos

2. **Manejo de Timeouts**
   - Timeout configurable (default: 8s)
   - Si hay timeout, devuelve datos del cache si existen
   - Logs informativos (no errores críticos)

3. **Reintentos Inteligentes**
   - 2 reintentos por defecto
   - Backoff de 2 segundos entre reintentos
   - Solo reintenta en errores 429, 500, 502, 503, 504

4. **Wake-up Request**
   - Para servicios en Render, hace HEAD request rápido primero
   - Ayuda a "despertar" servicios dormidos
   - No bloquea si falla

5. **Soporte para Todos los Métodos HTTP**
   - GET: Con cache
   - POST/PUT/DELETE: Sin cache (siempre fresh)

## 📊 Variables de Entorno

Puedes configurar el comportamiento con estas variables:

```bash
# Timeout para requests (segundos)
API_TIMEOUT_SECS=8

# Tiempo de vida del cache (segundos)
API_CACHE_TTL_SECS=120

# Número de reintentos
API_RETRY_TOTAL=2
```

## 🔍 Uso del Helper

### Ejemplo Básico
```python
from devops.api_helpers import cached_request

# GET request con cache
data = cached_request(
    "https://belgranoahorro-aliq.onrender.com/api/negocios",
    timeout=8,
    cache_ttl=120,
    headers={"Authorization": "Bearer token"}
)
```

### Ejemplo con POST
```python
# POST request (sin cache)
data = cached_request(
    "https://belgranoahorro-aliq.onrender.com/api/negocios",
    method="POST",
    timeout=8,
    json_data={"nombre": "Nuevo Negocio"},
    headers={"Authorization": "Bearer token"}
)
```

## ✅ Resultados Esperados

### Antes
- ❌ ReadTimeoutError frecuentes
- ❌ Worker Timeout en Gunicorn
- ❌ Max retries exceeded
- ❌ Dashboard lento cuando APIs están lentas

### Después
- ✅ No más ReadTimeoutError (usa cache si hay timeout)
- ✅ No más Worker Timeout (timeout de 120s en Gunicorn)
- ✅ No más Max retries exceeded (solo 2 reintentos)
- ✅ Dashboard carga rápido (usa cache cuando APIs están lentas)

## 🚀 Configuración de Gunicorn

Todos los archivos de configuración ahora incluyen:

```bash
gunicorn app:app \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --keep-alive 5
```

### Parámetros Explicados

- `--workers 2`: 2 procesos worker
- `--threads 2`: 2 threads por worker (4 requests concurrentes total)
- `--timeout 120`: 120 segundos de timeout antes de matar worker
- `--keep-alive 5`: Mantener conexiones vivas 5 segundos

## 🔧 Limpieza de Cache

Si necesitas limpiar el cache manualmente:

```python
from devops.api_helpers import clear_cache

# Limpiar todo el cache
clear_cache()

# Limpiar cache de un patrón específico
clear_cache("GET:/api/negocios")
```

## 📝 Notas Importantes

1. **Cache es en memoria**: Se pierde al reiniciar el servicio
2. **Solo GET requests se cachean**: POST/PUT/DELETE siempre van directo
3. **Cache se invalida automáticamente**: Después de CREATE/UPDATE/DELETE
4. **Timeouts son esperados**: En servicios gratuitos de Render
5. **Logs informativos**: Timeouts se loguean como WARNING, no ERROR

## 🐛 Troubleshooting

### Si sigues viendo timeouts:
1. Verificar que `API_TIMEOUT_SECS` esté configurado
2. Verificar que el servicio destino esté activo
3. Aumentar `API_CACHE_TTL_SECS` para reducir llamadas

### Si los datos no se actualizan:
1. El cache se limpia automáticamente después de POST/PUT/DELETE
2. Reducir `API_CACHE_TTL_SECS` si necesitas datos más frescos
3. Verificar logs para ver si está usando cache





