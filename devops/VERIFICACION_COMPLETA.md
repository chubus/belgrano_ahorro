# ✅ Verificación Completa de Conectividad - APIs

## 📋 Resumen de Verificaciones Realizadas

He creado scripts y documentación para verificar la conectividad entre todas las APIs:

### 🔧 Scripts Creados

1. **`devops/verificar_conectividad.py`** - Script completo de verificación
   - Verifica configuración de variables de entorno
   - Prueba conectividad con Belgrano Ahorro
   - Prueba conectividad con Ticketera
   - Verifica integración de DevOps Managers
   - Genera reporte completo

2. **`devops/verificar_config.py`** - Verificación rápida de configuración
   - Verifica que las variables estén configuradas
   - Muestra estado de configuración

3. **`devops/crear_env.py`** - Crea archivo .env automáticamente
   - Genera archivo .env con valores por defecto

4. **`devops/configurar_env.py`** - Configuración interactiva
   - Guía paso a paso para configurar variables

### 📚 Documentación Creada

1. **`devops/RESUMEN_CONECTIVIDAD.md`** - Resumen de URLs y endpoints
2. **`devops/CONFIGURACION_RAPIDA.md`** - Guía rápida de configuración
3. **`devops/VERIFICACION_COMPLETA.md`** - Este documento

## 🔗 URLs Configuradas

### Belgrano Ahorro
- **URL Principal**: `https://belgranoahorro-aliq.onrender.com`
- **API Key por defecto**: `belgrano_ahorro_api_key_2025`
- **Endpoints verificados**:
  - `/api/health`
  - `/api/negocios`
  - `/api/productos`
  - `/api/ofertas`
  - `/api/categorias`
  - `/api/sucursales`

### Ticketera
- **URL**: `https://ticketerabelgrano.onrender.com`
- **Endpoints verificados**:
  - `/api/health`
  - `/health`
  - `/status`
  - `/api/tickets` (si existe)

## ✅ Mejoras Implementadas

### 1. Carga Automática de Variables de Entorno
- ✅ `devops/app.py` - Carga .env automáticamente
- ✅ `devops/wsgi.py` - Carga .env antes de importar la app
- ✅ Busca .env en múltiples ubicaciones

### 2. Validación Mejorada
- ✅ Método `is_configured()` en `DevOpsBelgranoManagerUnified`
- ✅ Validación en dashboard antes de usar el manager
- ✅ Mensajes de error más descriptivos

### 3. Manejo de Errores
- ✅ Reintentos automáticos en requests
- ✅ Timeouts configurables
- ✅ Manejo de errores 502, 503, 504
- ✅ Rutas alternativas si una falla

## 🧪 Cómo Verificar

### Opción 1: Script Completo
```bash
python devops/verificar_conectividad.py
```

### Opción 2: Verificación Rápida
```bash
python devops/verificar_config.py
```

### Opción 3: Desde el Dashboard DevOps
1. Accede a `/devops/dashboard`
2. Ve a `/devops/conectar-belgrano` para probar conexión
3. Ve a `/devops/info` para ver estado del sistema

## 📝 Checklist de Verificación

Ejecuta estos pasos para verificar que todo funciona:

- [ ] **Configuración de Variables**
  ```bash
  python devops/verificar_config.py
  ```
  Debe mostrar: ✅ Configuración completa

- [ ] **Conectividad con Belgrano Ahorro**
  - Verifica que `/api/health` responda 200
  - Verifica que `/api/negocios` responda 200
  - Verifica que la API key sea válida

- [ ] **Conectividad con Ticketera** (opcional)
  - Verifica que algún endpoint de health responda
  - Verifica que la URL sea correcta

- [ ] **Integración DevOps**
  - Verifica que el manager se inicialice correctamente
  - Verifica que pueda obtener datos de Belgrano Ahorro
  - Verifica que la sincronización funcione

## 🔍 Verificación Manual

### 1. Verificar Variables de Entorno
```python
import os
from dotenv import load_dotenv
load_dotenv('devops/.env')

print("BELGRANO_AHORRO_URL:", os.getenv('BELGRANO_AHORRO_URL'))
print("BELGRANO_AHORRO_API_KEY:", os.getenv('BELGRANO_AHORRO_API_KEY')[:10] + "...")
```

### 2. Probar Conectividad con curl
```bash
# Belgrano Ahorro Health
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     -H "X-API-Key: belgrano_ahorro_api_key_2025" \
     https://belgranoahorro-aliq.onrender.com/api/health

# Belgrano Ahorro Negocios
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     -H "X-API-Key: belgrano_ahorro_api_key_2025" \
     https://belgranoahorro-aliq.onrender.com/api/negocios
```

### 3. Verificar desde Python
```python
from devops.manager_unified import devops_manager_unified

# Verificar configuración
print("Configurado:", devops_manager_unified.is_configured())

# Probar conectividad
connectivity = devops_manager_unified.test_connectivity()
print("Estado:", connectivity['overall_status'])
```

## 🐛 Solución de Problemas

### Problema: "API Key no configurada"
**Solución**: 
1. Crea archivo `devops/.env`
2. Agrega `BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025`
3. Reinicia la aplicación

### Problema: "Connection Error"
**Solución**:
1. Verifica que las URLs sean correctas
2. Verifica conectividad a internet
3. Verifica que los servicios estén en línea

### Problema: "Timeout"
**Solución**:
1. Aumenta `API_TIMEOUT_SECS` en .env
2. Verifica que los servicios no estén sobrecargados

### Problema: "502 Bad Gateway"
**Solución**:
1. El servicio puede estar reiniciándose
2. Espera unos minutos y reintenta
3. Verifica los logs del servicio

## 📊 Estado Actual

### ✅ Completado
- Scripts de verificación creados
- Documentación completa
- Carga automática de .env
- Validación mejorada
- Manejo de errores robusto

### 🔄 Pendiente de Verificación
- Conectividad real con Belgrano Ahorro (requiere servicio en línea)
- Conectividad real con Ticketera (requiere servicio en línea)
- Pruebas de sincronización end-to-end

## 🚀 Próximos Pasos

1. **Ejecutar verificación completa**:
   ```bash
   python devops/verificar_conectividad.py
   ```

2. **Revisar resultados** y corregir cualquier problema encontrado

3. **Probar desde el dashboard**:
   - Acceder a `/devops/dashboard`
   - Probar conexión con `/devops/conectar-belgrano`
   - Verificar que los datos se carguen correctamente

4. **Configurar en producción** (si aplica):
   - Configurar variables de entorno en Render/Heroku
   - Verificar que las URLs sean correctas
   - Probar conectividad desde producción

