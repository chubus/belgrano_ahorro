# 🔧 Solución para Timeouts en DevOps -> Belgrano Ahorro

## 📋 Problema Identificado

Los logs muestran timeouts al conectar DevOps con Belgrano Ahorro:
- `ReadTimeoutError` con timeout de 15 segundos
- Servicio en Render puede estar "dormido" (sleep mode)
- Múltiples reintentos que fallan

## ✅ Soluciones Implementadas

### 1. **Timeout Aumentado**
- **Antes**: 15 segundos
- **Ahora**: 30 segundos (configurable via `API_TIMEOUT_SECS`)
- Permite que servicios en Render "despierten" antes de fallar

### 2. **Sistema de Cache Local**
- Cache automático para requests GET
- TTL de 60 segundos (configurable via `API_CACHE_TTL_SECS`)
- Reduce llamadas innecesarias a la API
- **Fallback automático**: Si hay timeout, devuelve datos del cache

### 3. **Wake-up Request**
- Para servicios en Render, hace un HEAD request rápido primero
- Ayuda a "despertar" el servicio antes de la petición real
- No bloquea si falla

### 4. **Reintentos Optimizados**
- Reducidos de 3 a 2 reintentos
- Backoff aumentado a 2.0 segundos (más tiempo entre reintentos)
- Evita saturar el servicio con requests

### 5. **Manejo de Errores Mejorado**
- Timeouts se loguean como `WARNING` (no `ERROR`)
- Mensajes más claros para el usuario
- Cache se usa automáticamente cuando hay timeout

### 6. **Invalidación de Cache Inteligente**
- Cache se limpia automáticamente después de CREATE/UPDATE/DELETE
- Asegura que los datos mostrados estén actualizados

## 🎯 Variables de Entorno Configurables

Puedes ajustar el comportamiento con estas variables:

```bash
# Timeout para requests (segundos)
API_TIMEOUT_SECS=30

# Tiempo de vida del cache (segundos)
API_CACHE_TTL_SECS=60

# Número de reintentos
API_RETRY_TOTAL=2

# Tiempo de espera entre reintentos (segundos)
API_RETRY_BACKOFF=2.0
```

## 📊 Comportamiento Actual

### Escenario 1: Servicio Activo
1. Request GET → Cache miss → Llamada a API → Respuesta exitosa → Guarda en cache
2. Request GET (dentro de 60s) → Cache hit → Devuelve datos del cache (sin llamada a API)

### Escenario 2: Servicio Dormido (Render)
1. Request GET → Cache miss → Wake-up request → Timeout
2. Si hay cache válido → Devuelve datos del cache
3. Si no hay cache → Devuelve error con mensaje claro

### Escenario 3: Crear/Actualizar/Eliminar
1. Request POST/PUT/DELETE → Llamada a API → Limpia cache del tipo de item
2. Próximo GET → Cache miss → Llamada a API → Obtiene datos actualizados

## 🔍 Logs Mejorados

Los logs ahora son más informativos:

**Antes:**
```
ERROR:manager_unified:HTTP error GET ...: Read timed out
```

**Ahora:**
```
WARNING:manager_unified:Timeout en GET ... (servicio puede estar dormido en Render)
INFO:manager_unified:Usando datos en cache debido a timeout
```

## 🚀 Próximos Pasos Recomendados

1. **Monitorear logs**: Verificar que los timeouts se manejen correctamente
2. **Ajustar TTL**: Si los datos cambian frecuentemente, reducir `API_CACHE_TTL_SECS`
3. **Considerar Keep-Alive**: Para servicios críticos, considerar un servicio de keep-alive que haga requests periódicos

## ⚠️ Notas Importantes

- El cache solo funciona para requests GET
- POST/PUT/DELETE siempre invalidan el cache
- El wake-up request solo se hace para servicios en Render
- Los timeouts son esperados en servicios gratuitos de Render

## 🐛 Troubleshooting

### Si sigues viendo timeouts frecuentes:
1. Verificar que `API_TIMEOUT_SECS` esté configurado a 30 o más
2. Verificar que el servicio Belgrano Ahorro esté activo
3. Considerar aumentar `API_CACHE_TTL_SECS` para reducir llamadas

### Si los datos no se actualizan:
1. Verificar que el cache se esté limpiando después de CREATE/UPDATE/DELETE
2. Reducir `API_CACHE_TTL_SECS` si necesitas datos más frescos
3. Forzar refresh haciendo un request sin cache (modificar código temporalmente)



