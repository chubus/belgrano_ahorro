# 🔧 CONFIGURACIÓN APIS REALES - DevOps con Belgrano Ahorro

## Variables de Entorno para Producción (Render)

### Variables Obligatorias
```bash
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

### Variables Opcionales
```bash
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3
API_RETRY_DELAY=1
CACHE_TTL=300
FLASK_ENV=production
```

### Gateway (si usas API Gateway)
```bash
GATEWAY_URL=https://tu-gateway.onrender.com/gateway
GATEWAY_API_KEY=devops_gateway_key_2025
```

## Endpoints Reales de Belgrano Ahorro

### Base URL: `https://belgranoahorro-aliq.onrender.com`

#### APIs Disponibles:
- `GET /api/health` - Health check
- `GET /api/v1/negocios` - Listar negocios
- `POST /api/v1/negocios` - Crear negocio
- `PUT /api/v1/negocios/{id}` - Actualizar negocio
- `DELETE /api/v1/negocios/{id}` - Eliminar negocio

- `GET /api/v1/productos` - Listar productos
- `POST /api/v1/productos` - Crear producto
- `PUT /api/v1/productos/{id}` - Actualizar producto
- `DELETE /api/v1/productos/{id}` - Eliminar producto

- `GET /api/v1/ofertas` - Listar ofertas
- `POST /api/v1/ofertas` - Crear oferta
- `PUT /api/v1/ofertas/{id}` - Actualizar oferta
- `DELETE /api/v1/ofertas/{id}` - Eliminar oferta

- `GET /api/v1/sucursales` - Listar sucursales
- `POST /api/v1/sucursales` - Crear sucursal
- `PUT /api/v1/sucursales/{id}` - Actualizar sucursal
- `DELETE /api/v1/sucursales/{id}` - Eliminar sucursal

- `GET /api/v1/precios` - Listar precios
- `PUT /api/v1/precios/{producto_id}` - Actualizar precio

## Configuración en Render

1. **Ve a tu servicio en Render Dashboard**
2. **Settings → Environment**
3. **Agrega estas variables:**

```
BELGRANO_AHORRO_URL = https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY = belgrano_ahorro_api_key_2025
API_TIMEOUT = 30
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 1
CACHE_TTL = 300
FLASK_ENV = production
```

4. **Guarda y redeploy**

## Verificación Post-Deploy

### 1. Health Check
```bash
curl https://tu-servicio.onrender.com/api/devops/health
```

### 2. Conectividad DevOps
```bash
curl https://tu-servicio.onrender.com/devops/conectar-belgrano
```

### 3. Dashboard DevOps
- Ve a `/devops/login`
- Usuario: `devops`
- Password: `devops_password`
- Navega a `/devops/dashboard`

## Flujo de Datos Real

```
DevOps Interface → API Manager → Belgrano Ahorro API → Base de Datos Real
```

### Operaciones que se sincronizan:
- ✅ Crear negocio → Se crea en Belgrano Ahorro
- ✅ Crear producto → Se crea en Belgrano Ahorro  
- ✅ Crear oferta → Se crea en Belgrano Ahorro
- ✅ Actualizar precio → Se actualiza en Belgrano Ahorro
- ✅ Listar datos → Se obtienen desde Belgrano Ahorro

## Troubleshooting

### Si ves "Negocios cargados desde base local":
- Verifica que `BELGRANO_AHORRO_URL` esté configurada
- Verifica que `BELGRANO_AHORRO_API_KEY` esté configurada
- Revisa los logs en Render

### Si ves errores 401/403:
- Verifica que la API key sea correcta
- Verifica que Belgrano Ahorro esté funcionando

### Si ves errores 404:
- Verifica que la URL base sea correcta
- Verifica que los endpoints estén disponibles

## Logs Importantes

```
✅ Cliente API configurado correctamente
✅ Token de autenticación generado exitosamente
✅ negocios obtenidos desde API: X items
✅ negocio creado en API: Nombre del negocio
```

## Notas de Seguridad

- Las API keys son sensibles, no las compartas
- Usa HTTPS en producción
- Los requests tienen timeout de 30 segundos
- Hay retry automático en caso de fallos temporales
