# 📡 Resumen de Conectividad - APIs Belgrano Ahorro

## 🔗 URLs de los Servicios

### Belgrano Ahorro
- **URL Principal**: `https://belgranoahorro-aliq.onrender.com`
- **URL Alternativa**: `https://belgranoahorro-hp30.onrender.com` (usada en algunos archivos)
- **API Key por defecto**: `belgrano_ahorro_api_key_2025`

### Ticketera
- **URL**: `https://ticketerabelgrano.onrender.com`

## 🔑 Variables de Entorno Requeridas

### Obligatorias para DevOps
```env
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

### Opcionales
```env
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_KEY=tu_api_key_ticketera
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password
```

## 🔍 Endpoints a Verificar

### Belgrano Ahorro
- `GET /api/health` - Health check
- `GET /api/negocios` - Lista de negocios
- `GET /api/productos` - Lista de productos
- `GET /api/ofertas` - Lista de ofertas
- `GET /api/categorias` - Lista de categorías
- `GET /api/sucursales` - Lista de sucursales

### Ticketera
- `GET /api/health` o `/health` o `/status` - Health check
- `GET /api/tickets` - Lista de tickets (si existe)

## 🧪 Scripts de Verificación

### 1. Verificar Configuración
```bash
python devops/verificar_config.py
```

### 2. Verificar Conectividad Completa
```bash
python devops/verificar_conectividad.py
```

### 3. Crear Archivo .env
```bash
python devops/crear_env.py
```

## ✅ Checklist de Verificación

- [ ] Variables de entorno configuradas
- [ ] Belgrano Ahorro responde en `/api/health`
- [ ] API Key válida para Belgrano Ahorro
- [ ] Endpoints de Belgrano Ahorro funcionando
- [ ] Ticketera responde (si está configurada)
- [ ] DevOps Manager puede conectarse a Belgrano Ahorro
- [ ] DevOps Manager puede conectarse a Ticketera (si está configurada)
- [ ] Sincronización entre servicios funciona

## 🐛 Problemas Comunes

### Error: "API Key inválida"
- Verificar que `BELGRANO_AHORRO_API_KEY` sea la misma que en Belgrano Ahorro
- Verificar que la API key no tenga espacios extra

### Error: "Connection Error"
- Verificar que las URLs sean correctas
- Verificar conectividad a internet
- Verificar que los servicios estén en línea

### Error: "Timeout"
- Aumentar `API_TIMEOUT_SECS` en el archivo .env
- Verificar que los servicios no estén sobrecargados

### Error: "502 Bad Gateway"
- El servicio puede estar caído o reiniciándose
- Esperar unos minutos y reintentar

## 📝 Notas

- Las URLs pueden variar según el entorno (desarrollo/producción)
- La API key debe ser la misma en todos los servicios que se comunican
- Los timeouts deben ser suficientes para servicios en Render (mínimo 15s)

