# 🚀 Configuración para Render - Sistema Belgrano Ahorro + Ticketera

## ⚙️ Variables de Entorno Requeridas

### En el panel de Render, configura estas variables de entorno:

```bash
# URL del sistema Belgrano Ahorro (OBLIGATORIA)
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com

# API Key para comunicación entre servicios (OBLIGATORIA)  
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Puerto (ya configurado automáticamente por Render)
PORT=10000

# Variables adicionales opcionales
BELGRANO_AHORRO_TIMEOUT=30
FLASK_ENV=production
```

## 🛠️ Pasos para Configurar en Render

### 1. Ir al Dashboard de Render
- Accede a tu servicio en render.com
- Ve a la sección "Environment"

### 2. Agregar Variables de Entorno
Agrega cada variable con estos valores:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `BELGRANO_AHORRO_URL` | `https://belgranoahorro-hp30.onrender.com` | URL del sistema principal |
| `BELGRANO_AHORRO_API_KEY` | `belgrano_ahorro_api_key_2025` | Clave de API |

### 3. Guardar y Redesplegar
- Haz clic en "Save Changes"
- Render automáticamente redespliegará el servicio

## ✅ Verificación

Después del deploy, deberías ver en los logs:

```
🔗 Configuración API:
   BELGRANO_AHORRO_URL: https://belgranoahorro-hp30.onrender.com
   API_KEY: belgrano_a...
✅ Cliente API de Belgrano Ahorro inicializado
✅ Cliente API de Belgrano Ahorro inicializado para DevOps
```

**En lugar de:**
```
⚠️ Variable de entorno BELGRANO_AHORRO_URL no está definida
BELGRANO_AHORRO_URL: None
```

## 🔧 Solución de Problemas

### Problema: IndentationError en init_users_flota.py
**✅ SOLUCIONADO** - Se corrigió la indentación y se agregó encoding UTF-8

### Problema: Variables de entorno no configuradas
**🔧 SOLUCIÓN** - Configurar `BELGRANO_AHORRO_URL` en Render como se indica arriba

### Problema: Cliente API no disponible
**✅ SOLUCIONADO** - Se implementó manejo robusto de errores

## 📋 Checklist de Deploy

- [ ] ✅ Corregir IndentationError en `scripts/init_users_flota.py`
- [ ] ⚙️ Configurar `BELGRANO_AHORRO_URL` en Render
- [ ] ⚙️ Verificar `BELGRANO_AHORRO_API_KEY` en Render  
- [ ] 🚀 Redesplegar servicio
- [ ] 📊 Verificar logs para confirmar configuración correcta

## 🎯 Resultado Esperado

Después de aplicar estas configuraciones, el deploy debería ser exitoso y mostrar:

```
🚀 Iniciando Ticketera...
================================
🎯 Ticketera - Script de Inicio
================================
🔍 Verificando dependencias...
✅ Dependencias verificadas
🔧 Verificando variables de entorno...
✅ BELGRANO_AHORRO_URL está configurada
✅ BELGRANO_AHORRO_API_KEY está configurada
✅ Puerto configurado: 10000
🗄️ Inicializando base de datos...
✅ Script ejecutado exitosamente
🔧 Actualizando esquema de base de datos...
✅ Base de datos actualizada exitosamente
✅ Inicialización completada exitosamente
🎉 Ticketera iniciada correctamente
```
