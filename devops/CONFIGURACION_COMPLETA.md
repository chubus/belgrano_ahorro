# ✅ Configuración Completa - API Key Configurada

## 🔑 API Key Configurada

**API Key**: `belgrano_ahorro_api_key_2025`

Esta API key está configurada en todos los lugares necesarios:

### ✅ Archivos Configurados

1. **`devops/.env`** - Variables de entorno
   ```env
   BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
   BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
   ```

2. **`app_unificado.py`** - Aplicación principal Belgrano Ahorro
   - Usa `belgrano_ahorro_api_key_2025` como valor por defecto
   - Configurado en línea 172 y 192

3. **`api_belgrano_ahorro.py`** - API REST de Belgrano Ahorro
   - Usa `belgrano_ahorro_api_key_2025` como valor por defecto
   - Configurado en línea 36

4. **`devops/manager_unified.py`** - Manager de DevOps
   - Lee la API key desde variables de entorno
   - Se carga desde `devops/.env`

5. **`devops/app.py`** - Aplicación DevOps
   - Crea automáticamente `.env` con la API key si no existe
   - Verifica que las variables estén configuradas

## 🚀 Estado Actual

### ✅ Configuración Completa

- ✅ API Key configurada: `belgrano_ahorro_api_key_2025`
- ✅ URL de Belgrano Ahorro: `https://belgranoahorro-aliq.onrender.com`
- ✅ Archivo `.env` creado en `devops/.env`
- ✅ Código configurado para usar esta API key
- ✅ Timeouts optimizados para producción (20s)
- ✅ Reintentos configurados (3 intentos)

## 🔍 Verificación

### Verificar que todo esté configurado:

```bash
python devops/verificar_api_key.py
```

Este script verifica:
- ✅ Variables de entorno cargadas
- ✅ API key correcta en `.env`
- ✅ API key correcta en el código
- ✅ Manager configurado correctamente

## 📋 Flujo de Trabajo

### 1. Crear Negocio desde DevOps

1. Accede a: `https://[tu-url-devops].onrender.com/devops/dashboard`
2. Login: `devops` / `devops_password`
3. Ve a "Negocios" → "Crear Negocio"
4. Completa el formulario y guarda

### 2. Ver Negocio en Belgrano Ahorro

El negocio creado desde DevOps debería aparecer automáticamente en Belgrano Ahorro porque:
- DevOps usa la misma API key que Belgrano Ahorro
- DevOps hace POST a `/api/negocios` de Belgrano Ahorro
- Belgrano Ahorro valida la API key y crea el negocio

## 🔧 Configuración en Render

### Variables de Entorno en Render Dashboard

**Servicio DevOps:**
```
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
TICKETERA_URL=https://ticketerabelgrano.onrender.com
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=[tu_contraseña_segura]
SECRET_KEY=[tu_secret_key_segura]
```

**Servicio Belgrano Ahorro:**
```
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

## ✅ Todo Listo

Con esta configuración:
- ✅ DevOps puede crear negocios en Belgrano Ahorro
- ✅ DevOps puede leer datos de Belgrano Ahorro
- ✅ La API key es consistente en todos los servicios
- ✅ Todo está optimizado para producción

## 🐛 Si Aún Ves el Error

1. **Reinicia el servicio DevOps** en Render
2. **Verifica los logs** para ver si las variables se cargaron
3. **Ejecuta el script de verificación**:
   ```bash
   python devops/verificar_api_key.py
   ```
4. **Verifica que el archivo `.env` exista** en `devops/.env`

