# 🚀 Configuración Rápida - DevOps Dashboard

## ⚠️ Error: "API de Belgrano Ahorro no configurada"

Si ves este error en el dashboard de DevOps, necesitas configurar las variables de entorno.

## 📋 Solución Rápida

### Opción 1: Usar el script de configuración (Recomendado)

```bash
python devops/configurar_env.py
```

Este script te guiará paso a paso para crear el archivo `.env` con todas las variables necesarias.

### Opción 2: Configuración Manual

1. **Crear archivo `.env`** en el directorio `devops/`:

```bash
# Windows
copy devops\env\env.example devops\.env

# Linux/Mac
cp devops/env/env.example devops/.env
```

2. **Editar el archivo `devops/.env`** y configurar:

```env
# OBLIGATORIO - URL de la API de Belgrano Ahorro
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com

# OBLIGATORIO - API Key de Belgrano Ahorro
# Obtener desde el panel de administración de Belgrano Ahorro
BELGRANO_AHORRO_API_KEY=tu_api_key_aqui

# OPCIONAL - Configuración de DevOps
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=tu_contraseña_segura
```

### Opción 3: Variables de Entorno del Sistema

Si estás ejecutando en producción (Render, Heroku, etc.), configura las variables en el panel de administración:

**Variables obligatorias:**
- `BELGRANO_AHORRO_URL` - URL de la API
- `BELGRANO_AHORRO_API_KEY` - API Key para autenticación

**Variables opcionales:**
- `DEVOPS_USERNAME` - Usuario para login (default: devops)
- `DEVOPS_PASSWORD` - Contraseña para login
- `API_TIMEOUT_SECS` - Timeout en segundos (default: 15)

## 🔑 Obtener la API Key

La API Key debe ser la misma que está configurada en tu aplicación de Belgrano Ahorro. 

1. Revisa el archivo de configuración de Belgrano Ahorro
2. Busca la variable `API_KEY` o `SECRET_KEY`
3. Úsala como valor de `BELGRANO_AHORRO_API_KEY`

## ✅ Verificar Configuración

Después de configurar, reinicia la aplicación y verifica:

1. Los logs deberían mostrar:
   ```
   ✅ Variables de entorno cargadas desde: [ruta]
   ✅ Cliente API Belgrano Ahorro configurado
      API Key: ********
   ```

2. Si ves `API Key: no-set`, la API Key no está configurada correctamente.

3. Accede al dashboard: `/devops/dashboard`

## 🐛 Solución de Problemas

### Error: "API Key no configurada"

- Verifica que el archivo `.env` existe en `devops/.env`
- Verifica que `BELGRANO_AHORRO_API_KEY` tiene un valor (no está vacío)
- Reinicia la aplicación después de cambiar el archivo `.env`

### Error: "No se encontró archivo .env"

- El archivo `.env` debe estar en `devops/.env` o en la raíz del proyecto
- Verifica que el archivo no esté en `.gitignore` (no debe subirse a git)
- Usa el script `configurar_env.py` para crearlo automáticamente

### En Render.com

1. Ve a tu servicio en Render Dashboard
2. Ve a "Environment"
3. Agrega las variables:
   - `BELGRANO_AHORRO_URL`
   - `BELGRANO_AHORRO_API_KEY`
4. Reinicia el servicio

## 📚 Más Información

- Ver `devops/env/env.example` para todas las opciones disponibles
- Ver `devops/API_DOCUMENTATION.md` para documentación de la API

