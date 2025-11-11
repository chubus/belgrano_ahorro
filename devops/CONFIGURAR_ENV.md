# 🔧 Configuración de Variables de Entorno - DevOps

## ⚠️ Error: "API de Belgrano Ahorro no configurada"

Si ves este error, necesitas configurar las variables de entorno.

## 🚀 Solución Rápida

### Opción 1: El código crea el archivo automáticamente

Al iniciar DevOps, si no existe `devops/.env`, se creará automáticamente con valores por defecto.

**Luego edita el archivo** `devops/.env` y configura tu API key real:

```env
BELGRANO_AHORRO_API_KEY=tu_api_key_real_aqui
```

### Opción 2: Crear manualmente

Ejecuta:
```bash
python devops/crear_env.py
```

Esto creará el archivo `devops/.env` con la configuración base.

### Opción 3: Configurar en Render Dashboard (Producción)

1. Ve a tu servicio DevOps en Render Dashboard
2. Ve a "Environment"
3. Agrega estas variables:

**Obligatorias:**
- `BELGRANO_AHORRO_URL` = `https://belgranoahorro-aliq.onrender.com`
- `BELGRANO_AHORRO_API_KEY` = `tu_api_key_real`

**Opcionales (recomendadas):**
- `API_TIMEOUT_SECS` = `20`
- `API_RETRY_TOTAL` = `3`
- `TICKETERA_URL` = `https://ticketerabelgrano.onrender.com`
- `DEVOPS_USERNAME` = `devops`
- `DEVOPS_PASSWORD` = `tu_contraseña_segura`
- `SECRET_KEY` = `tu_secret_key_segura`

## 📋 Variables Requeridas

### Obligatorias

```env
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

### Opcionales (con valores por defecto)

```env
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0
TICKETERA_URL=https://ticketerabelgrano.onrender.com
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password
```

## 🔑 Obtener la API Key

La API Key debe ser la misma que está configurada en tu aplicación de Belgrano Ahorro.

1. Revisa el archivo de configuración de Belgrano Ahorro
2. Busca la variable `API_KEY` o `BELGRANO_AHORRO_API_KEY`
3. Úsala como valor de `BELGRANO_AHORRO_API_KEY` en DevOps

## ✅ Verificar Configuración

Después de configurar, reinicia la aplicación y verifica los logs:

```
✅ Variables de entorno cargadas desde: devops/.env
✅ Cliente API Belgrano Ahorro configurado
   API Key: ********
```

Si ves `API Key: no-set`, la API key no está configurada correctamente.

## 🐛 Solución de Problemas

### El archivo .env no se crea automáticamente

**Solución**: Ejecuta manualmente:
```bash
python devops/crear_env.py
```

### La API key no se carga

**Solución**: 
1. Verifica que el archivo `.env` esté en `devops/.env`
2. Verifica que no tenga espacios extra: `BELGRANO_AHORRO_API_KEY=tu_key` (sin espacios)
3. Reinicia la aplicación después de cambiar el archivo

### En Render, las variables no se cargan

**Solución**:
1. Verifica que las variables estén configuradas en Render Dashboard
2. Verifica que los nombres sean exactos (case-sensitive)
3. Reinicia el servicio en Render

## 📝 Archivo .env de Ejemplo

```env
# Variables de Entorno para DevOps - PRODUCCIÓN
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_URL=https://ticketerabelgrano.onrender.com
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password
FLASK_ENV=production
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion
```

