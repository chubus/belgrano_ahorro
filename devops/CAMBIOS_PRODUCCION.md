# ✅ Cambios Aplicados para Producción

## 📋 Resumen

Se han realizado modificaciones en el código para optimizar el funcionamiento post-deploy en producción con las APIs en Render.

## 🔧 Cambios Realizados

### 1. Timeouts Aumentados para Producción

**Antes**: 8-15 segundos  
**Ahora**: 20 segundos

Los servicios en Render pueden tener cold starts y latencia, por lo que se aumentaron los timeouts:

- ✅ `devops/manager_unified.py` - Timeout: 8s → 20s
- ✅ `devops/api_helpers.py` - Timeout: 10s → 20s
- ✅ `devops/routes.py` - Timeout: 8s → 20s
- ✅ `app_unificado.py` - Timeout: 15s → 20s

### 2. Reintentos Mejorados

- ✅ Reintentos: 2 → 3
- ✅ Backoff factor: 0.5s → 1.0s (más tiempo entre reintentos)

### 3. URLs de Producción Configuradas

Todas las URLs por defecto apuntan a producción:

- ✅ Belgrano Ahorro: `https://belgranoahorro-aliq.onrender.com`
- ✅ Ticketera: `https://ticketerabelgrano.onrender.com`

### 4. Configuración de Variables de Entorno

El archivo `devops/crear_env.py` ahora genera configuración para producción:

```env
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0
TICKETERA_URL=https://ticketerabelgrano.onrender.com
```

## 🚀 Configuración en Render

### Variables de Entorno Requeridas

Configurar en Render Dashboard:

**Obligatorias:**
- `BELGRANO_AHORRO_URL` = `https://belgranoahorro-aliq.onrender.com`
- `BELGRANO_AHORRO_API_KEY` = `belgrano_ahorro_api_key_2025`

**Opcionales (recomendadas):**
- `API_TIMEOUT_SECS` = `20`
- `API_RETRY_TOTAL` = `3`
- `API_RETRY_BACKOFF` = `1.0`
- `TICKETERA_URL` = `https://ticketerabelgrano.onrender.com`
- `DEVOPS_USERNAME` = `devops`
- `DEVOPS_PASSWORD` = `[tu_contraseña_segura]`
- `SECRET_KEY` = `[tu_secret_key_segura]`

## ✅ Verificación Post-Deploy

### 1. Verificar Health Checks

```bash
# Belgrano Ahorro
curl https://belgranoahorro-aliq.onrender.com/api/health

# DevOps
curl https://[tu-url-devops].onrender.com/health
```

### 2. Verificar Dashboard DevOps

1. Accede a: `https://[tu-url-devops].onrender.com/devops/dashboard`
2. Login: `devops` / `[tu_contraseña]`
3. Verifica que se carguen datos de Belgrano Ahorro

### 3. Verificar Conectividad

Ejecuta el script de verificación:
```bash
python devops/verificar_conectividad.py
```

## 📊 Mejoras de Rendimiento

### Antes
- Timeouts cortos (8-15s) → Errores frecuentes en producción
- Reintentos insuficientes (2) → Fallos en cold starts
- Backoff corto (0.5s) → Sobrecarga en reintentos

### Ahora
- Timeouts adecuados (20s) → Manejo de cold starts
- Reintentos suficientes (3) → Mayor resiliencia
- Backoff adecuado (1.0s) → Mejor distribución de carga

## 🔍 Archivos Modificados

1. `devops/manager_unified.py` - Timeouts y reintentos
2. `devops/api_helpers.py` - Timeout por defecto
3. `devops/routes.py` - Timeouts en health checks
4. `app_unificado.py` - Timeout en obtención de ofertas
5. `devops/crear_env.py` - Configuración de producción

## ⚠️ Notas Importantes

1. **Cold Starts**: Los servicios en Render pueden tardar 10-30 segundos en iniciar. Los timeouts de 20s son adecuados.

2. **API Keys**: Asegúrate de que la API key sea la misma en todos los servicios.

3. **Variables de Entorno**: Configura todas las variables en Render Dashboard, no solo en .env local.

4. **Monitoreo**: Revisa los logs en Render para detectar problemas de conectividad.

## 🐛 Solución de Problemas

### Error: Timeout
- Verifica que `API_TIMEOUT_SECS=20` esté configurado
- Revisa los logs para ver si el servicio está respondiendo

### Error: 502 Bad Gateway
- El servicio puede estar en cold start
- Espera 30 segundos y reintenta
- Verifica que el servicio esté en línea

### Error: API Key inválida
- Verifica que `BELGRANO_AHORRO_API_KEY` sea correcta
- Debe ser la misma en Belgrano Ahorro y DevOps

