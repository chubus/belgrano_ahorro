# 🚀 Deploy de Belgrano Tickets en Render

## 📋 Configuración para Render

### **Archivos Necesarios**

1. **`render_ticketera.yaml`** - Configuración principal de Render
2. **`requirements_ticketera.txt`** - Dependencias específicas
3. **`start_ticketera.sh`** - Script de inicio (opcional)
4. **`Dockerfile.render`** - Dockerfile alternativo para Render

## 🔧 Configuración de Render

### **Variables de Entorno Configuradas**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `PYTHON_VERSION` | `3.12.0` | Versión de Python |
| `FLASK_ENV` | `production` | Entorno de producción |
| `FLASK_APP` | `belgrano_tickets/app.py` | Archivo principal |
| `PORT` | `5001` | Puerto del servicio |
| `SECRET_KEY` | `belgrano_tickets_secret_2025` | Clave secreta |
| `BELGRANO_AHORRO_URL` | `https://belgrano-ahorro.onrender.com` | URL de Belgrano Ahorro |

## 🚀 Pasos para Deploy

### **Opción 1: Deploy Automático (Recomendado)**

1. **Conectar repositorio a Render**
   - Ir a [Render Dashboard](https://dashboard.render.com)
   - Crear nuevo "Web Service"
   - Conectar con tu repositorio de GitHub

2. **Configuración del servicio**
   - **Name**: `belgrano-ticketera`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r belgrano_tickets/requirements_ticketera.txt`
   - **Start Command**: `cd belgrano_tickets && python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Base de datos inicializada')" && python app.py`

3. **Variables de entorno**
   - Agregar todas las variables listadas arriba
   - Asegurar que `BELGRANO_AHORRO_URL` apunte a tu servicio principal

### **Opción 2: Usar render.yaml**

1. **Subir el archivo `render_ticketera.yaml`** al repositorio
2. **Render detectará automáticamente** la configuración
3. **El deploy se iniciará automáticamente**

## 🔍 Verificación del Deploy

### **Logs de Render**
```bash
# Ver logs en tiempo real
# Ir a Render Dashboard > Tu Servicio > Logs
```

### **Verificar que funciona**
```bash
# Probar el endpoint
curl https://tu-app.onrender.com

# Verificar health check
curl https://tu-app.onrender.com/health
```

## 🛠️ Solución de Problemas

### **Error: "start_ticketera.sh not found"**
- **Causa**: El archivo no existe en el contexto de build
- **Solución**: Usar comando directo en startCommand (ya corregido)

### **Error: "Module not found"**
- **Causa**: Dependencias no instaladas
- **Solución**: Verificar `requirements_ticketera.txt`

### **Error: "Database locked"**
- **Causa**: Múltiples instancias accediendo a la BD
- **Solución**: Render maneja esto automáticamente

### **Error: "Port already in use"**
- **Causa**: Puerto configurado incorrectamente
- **Solución**: Usar variable `$PORT` de Render

## 📊 Monitoreo

### **Métricas de Render**
- **Uptime**: Disponibilidad del servicio
- **Response Time**: Tiempo de respuesta
- **Error Rate**: Tasa de errores
- **Logs**: Logs en tiempo real

### **Health Checks**
- Render verifica automáticamente `/` endpoint
- Configurado en `render_ticketera.yaml`

## 🔄 Actualizaciones

### **Deploy Automático**
- Cada push a `main` activa un nuevo deploy
- Rollback automático si hay errores

### **Deploy Manual**
- Ir a Render Dashboard
- Seleccionar tu servicio
- Hacer click en "Manual Deploy"

## ✅ Configuración Final

### **Archivos Verificados**
- ✅ `render_ticketera.yaml` - Configuración completa
- ✅ `requirements_ticketera.txt` - Dependencias
- ✅ `start_ticketera.sh` - Script de inicio
- ✅ Variables de entorno configuradas

### **URLs de Acceso**
- **Ticketera**: `https://tu-app.onrender.com`
- **Belgrano Ahorro**: `https://belgrano-ahorro.onrender.com`

## 🎯 Próximos Pasos

1. **Hacer commit** de todos los archivos
2. **Push a GitHub**
3. **Conectar repositorio a Render**
4. **Verificar deploy automático**
5. **Probar funcionalidad**

**La ticketera está lista para deploy en Render con configuración completa.**
