# 📋 Variables de Entorno Completas - DevOps

## 🔑 Variables OBLIGATORIAS (Sin estas, el dashboard NO funcionará)

### Belgrano Ahorro API

| KEY | VALUE | Descripción |
|-----|-------|-------------|
| `BELGRANO_AHORRO_URL` | `https://belgranoahorro-aliq.onrender.com` | URL base de la API de Belgrano Ahorro |
| `BELGRANO_AHORRO_API_KEY` | `belgrano_ahorro_api_key_2025` | API Key para autenticación (DEBE ser la misma que en Belgrano Ahorro) |

## ⚙️ Variables OPCIONALES (Tienen valores por defecto)

### Configuración de API

| KEY | VALUE por Defecto | Descripción |
|-----|-------------------|-------------|
| `API_TIMEOUT_SECS` | `20` | Timeout en segundos para requests HTTP (recomendado: 20s para Render) |
| `API_RETRY_TOTAL` | `3` | Número total de reintentos en caso de fallo |
| `API_RETRY_BACKOFF` | `1.0` | Factor de espera entre reintentos en segundos |
| `API_CACHE_TTL_SECS` | `120` | Tiempo de vida del cache en segundos (solo para manager_unified) |

### Ticketera / Sistema de Tickets (OPCIONAL)

| KEY | VALUE por Defecto | Descripción |
|-----|-------------------|-------------|
| `TICKETERA_URL` | `https://ticketerabelgrano.onrender.com` | URL de la API de Ticketera (alias) |
| `TICKETS_API_URL` | `https://ticketerabelgrano.onrender.com` | URL de la API de Ticketera (prioridad 1) |
| `DEVOPS_API_URL` | `https://ticketerabelgrano.onrender.com` | URL de la API de Ticketera (prioridad 3) |
| `TICKETS_API_KEY` | (vacío) | API Key para Ticketera (prioridad 1) |
| `TICKETERA_API_KEY` | (vacío) | API Key para Ticketera (prioridad 2) |
| `DEVOPS_API_KEY` | (vacío) | API Key para Ticketera (prioridad 3) |
| `TICKETS_API_USERNAME` | (vacío) | Username para autenticación con Ticketera |
| `TICKETS_API_PASSWORD` | (vacío) | Password para autenticación con Ticketera |

### Seguridad DevOps (Login del Dashboard)

| KEY | VALUE por Defecto | Descripción |
|-----|-------------------|-------------|
| `DEVOPS_USERNAME` | `devops` | Usuario para login en panel DevOps |
| `DEVOPS_PASSWORD` | `devops_password` | Contraseña para login en panel DevOps |

### Flask / Aplicación

| KEY | VALUE por Defecto | Descripción |
|-----|-------------------|-------------|
| `SECRET_KEY` | `devops_secret_key_2025_prod_segura` | Secret key de Flask (cambiar en producción) |
| `FLASK_ENV` | `production` | Entorno de Flask (development/production) |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Configuración de cookies SameSite |
| `SESSION_COOKIE_SECURE` | `false` | Cookies seguras (true para HTTPS) |
| `REMEMBER_COOKIE_SECURE` | `false` | Cookies de recordar seguras (true para HTTPS) |
| `PORT` | `5000` | Puerto donde corre la aplicación (Render lo asigna automáticamente) |
| `HOST` | `0.0.0.0` | Host donde escucha la aplicación |

### Base de Datos (Solo si usas manager.py con SQLite)

| KEY | VALUE por Defecto | Descripción |
|-----|-------------------|-------------|
| `BELGRANO_AHORRO_DB_PATH` | `belgrano_ahorro.db` | Ruta a la base de datos SQLite |

## 📝 Configuración Completa para Render Dashboard

Copia y pega estas variables en Render Dashboard → Environment:

```bash
# ============================================================
# OBLIGATORIAS - Sin estas el dashboard NO funcionará
# ============================================================
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# ============================================================
# RECOMENDADAS - Para mejor funcionamiento
# ============================================================
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0

# ============================================================
# OPCIONALES - Para integración con Ticketera
# ============================================================
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_USERNAME=admin@belgranoahorro.com
TICKETS_API_PASSWORD=admin123

# ============================================================
# SEGURIDAD - Cambiar en producción
# ============================================================
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion
FLASK_ENV=production
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=false
REMEMBER_COOKIE_SECURE=false
```

## 📄 Archivo .env Completo

Copia este contenido a `devops/.env`:

```env
# ============================================================
# Variables de Entorno para DevOps - PRODUCCIÓN
# ============================================================

# ============================================================
# OBLIGATORIAS
# ============================================================
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# ============================================================
# CONFIGURACIÓN DE API
# ============================================================
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0
API_CACHE_TTL_SECS=120

# ============================================================
# TICKETERA (OPCIONAL)
# ============================================================
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_URL=https://ticketerabelgrano.onrender.com
DEVOPS_API_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_KEY=
TICKETERA_API_KEY=
DEVOPS_API_KEY=
TICKETS_API_USERNAME=admin@belgranoahorro.com
TICKETS_API_PASSWORD=admin123

# ============================================================
# SEGURIDAD DEVOPS
# ============================================================
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password

# ============================================================
# FLASK
# ============================================================
FLASK_ENV=production
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=false
REMEMBER_COOKIE_SECURE=false
```

## ✅ Checklist de Configuración

### Mínimo Requerido (Dashboard funcionará)
- [ ] `BELGRANO_AHORRO_URL`
- [ ] `BELGRANO_AHORRO_API_KEY`

### Recomendado (Mejor rendimiento)
- [ ] `API_TIMEOUT_SECS=20`
- [ ] `API_RETRY_TOTAL=3`
- [ ] `API_RETRY_BACKOFF=1.0`

### Opcional (Integración completa)
- [ ] `TICKETERA_URL`
- [ ] `TICKETS_API_USERNAME` y `TICKETS_API_PASSWORD` (o API Key)
- [ ] `DEVOPS_USERNAME` y `DEVOPS_PASSWORD` (para login)

### Seguridad (Producción)
- [ ] `SECRET_KEY` (cambiar por una clave segura)
- [ ] `DEVOPS_PASSWORD` (cambiar por una contraseña segura)
- [ ] `SESSION_COOKIE_SECURE=true` (si usas HTTPS)

## 🔍 Verificar Configuración

Ejecuta:
```bash
python devops/verificar_config.py
```

O verifica manualmente:
```bash
python devops/verificar_api_key.py
```

## 🐛 Solución de Errores

### Error: "API de Belgrano Ahorro no configurada"

**Causa**: Faltan las variables obligatorias

**Solución**: Configura estas dos variables:
```
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

### Error: "API Key inválida"

**Causa**: La API key no coincide con la de Belgrano Ahorro

**Solución**: Verifica que `BELGRANO_AHORRO_API_KEY` sea exactamente `belgrano_ahorro_api_key_2025`

### Error: "Timeout"

**Causa**: Timeout muy corto para servicios en Render

**Solución**: Aumenta `API_TIMEOUT_SECS=20`

## 📊 Prioridad de Variables (Ticketera)

Para Ticketera, el código busca en este orden:

1. **URL**: `TICKETS_API_URL` → `TICKETERA_URL` → `DEVOPS_API_URL`
2. **API Key**: `TICKETS_API_KEY` → `TICKETERA_API_KEY` → `DEVOPS_API_KEY`
3. **Auth**: Si no hay API Key, usa `TICKETS_API_USERNAME` + `TICKETS_API_PASSWORD`

## 🚀 Configuración Rápida

Para empezar rápido, solo necesitas estas 2 variables:

```env
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

El resto tiene valores por defecto que funcionan bien.

