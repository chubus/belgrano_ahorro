# 🎫 Belgrano Tickets - Deploy Independiente con Docker

## 📋 Descripción

Este directorio contiene la configuración completa para desplegar **Belgrano Tickets** como un servicio web independiente, conectado con **Belgrano Ahorro**.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐
│ Belgrano Ahorro │◄──►│ Belgrano Tickets │
│   (Puerto 5000) │    │   (Puerto 5001)  │
└─────────────────┘    └──────────────────┘
```

## 📁 Archivos de Configuración

### **Docker**
- `Dockerfile` - Configuración del contenedor de la ticketera
- `docker-compose.yml` - Orquestación de servicios
- `requirements_ticketera.txt` - Dependencias específicas

### **Scripts de Inicio**
- `start_ticketera.bat` - Script para Windows
- `start_ticketera.sh` - Script para Linux/Mac

### **Configuración**
- `config_ticketera.py` - Configuración específica
- `render_ticketera.yaml` - Deploy en Render

## 🚀 Opciones de Deploy

### **Opción 1: Docker Local**

#### **Con Docker Compose (Recomendado)**
```bash
# Desde el directorio belgrano_tickets/
cd belgrano_tickets/

# Construir y ejecutar
docker-compose up --build

# En segundo plano
docker-compose up -d --build
```

#### **Con Script de Windows**
```cmd
# Ejecutar el script
start_ticketera.bat
```

#### **Con Docker Directo**
```bash
# Construir imagen
docker build -f belgrano_tickets/Dockerfile -t belgrano-ticketera .

# Ejecutar contenedor
docker run -p 5001:5001 \
  -e BELGRANO_AHORRO_URL=http://localhost:5000 \
  -e SECRET_KEY=belgrano_tickets_secret_2025 \
  belgrano-ticketera
```

### **Opción 2: Render (Producción)**

1. **Conectar repositorio a Render**
2. **Usar configuración específica:**
   - Archivo: `belgrano_tickets/render_ticketera.yaml`
   - Build Command: `pip install -r belgrano_tickets/requirements_ticketera.txt`
   - Start Command: `cd belgrano_tickets && python app.py`

## 🔧 Configuración

### **Variables de Entorno**

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `PORT` | Puerto de la ticketera | `5001` |
| `FLASK_ENV` | Entorno Flask | `production` |
| `SECRET_KEY` | Clave secreta | `belgrano_tickets_secret_2025` |
| `BELGRANO_AHORRO_URL` | URL de Belgrano Ahorro | `http://localhost:5000` |

### **Conexión con Belgrano Ahorro**

La ticketera se conecta automáticamente con Belgrano Ahorro para:
- Obtener datos de productos
- Sincronizar información de usuarios
- Compartir bases de datos

## 📊 Bases de Datos

### **Archivos de BD**
- `belgrano_tickets.db` - Base de datos de tickets
- `../belgrano_ahorro.db` - Base de datos principal (compartida)

### **Inicialización Automática**
La base de datos se inicializa automáticamente al iniciar el contenedor:
```python
from app import app, db
with app.app_context():
    db.create_all()
```

## 🔍 Verificación

### **Verificar que funciona**
```bash
# Verificar contenedor
docker ps

# Ver logs
docker logs belgrano-ticketera

# Probar conexión
curl http://localhost:5001
```

### **URLs de Acceso**
- **Ticketera**: http://localhost:5001
- **Belgrano Ahorro**: http://localhost:5000

## 🛠️ Solución de Problemas

### **Error: "start_ticketera.sh not found"**
- **Causa**: El archivo no existe en el contexto de build
- **Solución**: Usar comando directo en Dockerfile (ya corregido)

### **Error: "Module not found"**
- **Causa**: Dependencias no instaladas
- **Solución**: Verificar `requirements_ticketera.txt`

### **Error: "Database locked"**
- **Causa**: Múltiples instancias accediendo a la BD
- **Solución**: Usar volúmenes Docker para persistencia

## 📈 Monitoreo

### **Logs del Contenedor**
```bash
# Ver logs en tiempo real
docker logs -f belgrano-ticketera

# Ver logs de los últimos 100 líneas
docker logs --tail 100 belgrano-ticketera
```

### **Estado del Servicio**
```bash
# Verificar estado
docker ps | grep belgrano-ticketera

# Ver uso de recursos
docker stats belgrano-ticketera
```

## 🔄 Actualizaciones

### **Reconstruir después de cambios**
```bash
# Detener servicios
docker-compose down

# Reconstruir
docker-compose up --build

# O solo la ticketera
docker-compose up --build belgrano-ticketera
```

## ✅ Estado Final

- ✅ **Dockerfile**: Configurado y funcional
- ✅ **docker-compose.yml**: Orquestación completa
- ✅ **Scripts de inicio**: Para Windows y Linux
- ✅ **Configuración Render**: Lista para producción
- ✅ **Conexión con Belgrano Ahorro**: Configurada
- ✅ **Bases de datos**: Inicialización automática

**La ticketera está lista para deploy independiente y conectada con Belgrano Ahorro.**
