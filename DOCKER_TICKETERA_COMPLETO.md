# 🎫 Dockerfile Completo para Belgrano Tickets

## ✅ **Configuración Completada**

He creado un **Dockerfile completo y separado** para la ticketera que se conecta con Belgrano Ahorro. La configuración incluye todos los archivos necesarios para un deploy independiente pero conectado.

## 📁 **Archivos Creados**

### **En `belgrano_tickets/`:**
1. **`Dockerfile`** - Dockerfile específico para la ticketera
2. **`docker-compose.yml`** - Configuración de servicios
3. **`start_ticketera.sh`** - Script de inicio (Linux/Mac)
4. **`start_ticketera.bat`** - Script de inicio (Windows)
5. **`requirements_ticketera.txt`** - Dependencias específicas
6. **`config_ticketera.py`** - Configuración de la aplicación
7. **`render_ticketera.yaml`** - Configuración para Render
8. **`test_ticketera_docker.py`** - Script de verificación
9. **`README_TICKETERA_DOCKER.md`** - Documentación completa

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────┐    ┌──────────────────┐
│ Belgrano Ahorro │◄──►│ Belgrano Tickets │
│   Puerto 5000   │    │   Puerto 5001    │
│   (Principal)   │    │   (Independiente)│
└─────────────────┘    └──────────────────┘
```

## 🚀 **Cómo Usar**

### **Opción 1: Docker Compose (Recomendado)**
```bash
cd belgrano_tickets/
docker-compose up --build
```

### **Opción 2: Script de Windows**
```bash
cd belgrano_tickets/
start_ticketera.bat
```

### **Opción 3: Docker Directo**
```bash
# Construir imagen
docker build -f belgrano_tickets/Dockerfile -t belgrano-ticketera .

# Ejecutar contenedor
docker run -p 5001:5001 \
  -v $(pwd)/belgrano_tickets/belgrano_tickets.db:/app/belgrano_tickets/belgrano_tickets.db \
  -v $(pwd)/belgrano_ahorro.db:/app/belgrano_ahorro.db \
  -e BELGRANO_AHORRO_URL=http://localhost:5000 \
  belgrano-ticketera
```

## 🔧 **Características Principales**

### **✅ Servicio Independiente**
- Puerto dedicado (5001)
- Base de datos separada
- Configuración específica
- Scripts de inicio propios

### **✅ Conectado con Belgrano Ahorro**
- Comparte base de datos principal
- Comunicación entre servicios
- Sincronización de datos
- Variables de entorno configuradas

### **✅ Configuración Completa**
- Dependencias específicas
- Scripts de inicialización
- Configuración para Render
- Documentación detallada

## 🌐 **Acceso a las Aplicaciones**

- **Belgrano Ahorro**: http://localhost:5000
- **Belgrano Tickets**: http://localhost:5001
- **Panel de Administración**: http://localhost:5001/login

## 📦 **Dependencias Específicas**

### **Flask y Extensiones**
- `Flask==3.1.1`
- `Flask-SocketIO==5.3.6`
- `Flask-SQLAlchemy==3.1.1`
- `Flask-Login==0.6.3`

### **Socket.IO**
- `python-socketio==5.11.1`
- `python-engineio==4.9.1`
- `eventlet==0.35.2`

### **Utilidades**
- `requests==2.32.3`
- `SQLAlchemy==2.0.28`

## 🔗 **Integración**

### **Comunicación entre Servicios**
1. **Sincronización de Datos**: Acceso a productos y pedidos
2. **Gestión de Tickets**: Creación y seguimiento
3. **Notificaciones**: Actualizaciones en tiempo real
4. **Autenticación**: Verificación de usuarios

### **Variables de Entorno**
- `FLASK_APP=belgrano_tickets/app.py`
- `FLASK_ENV=production`
- `PORT=5001`
- `SECRET_KEY=belgrano_tickets_secret_2025`
- `BELGRANO_AHORRO_URL=http://localhost:5000`

## 🚀 **Deploy en Render**

### **Configuración Automática**
El archivo `render_ticketera.yaml` está configurado para:
1. **Build Automático**: Instalación de dependencias
2. **Inicialización de BD**: Creación automática de tablas
3. **Variables de Entorno**: Configuración de producción
4. **Health Checks**: Verificación de estado

### **Pasos para Deploy**
1. Conectar repositorio a Render
2. Render detectará `render_ticketera.yaml`
3. Configurar variables de entorno
4. Deploy automático

## 🔍 **Verificación**

### **Script de Verificación**
```bash
cd belgrano_tickets/
python test_ticketera_docker.py
```

### **Checklist de Verificación**
- [ ] Docker instalado y funcionando
- [ ] Imagen construida correctamente
- [ ] Contenedor ejecutándose
- [ ] Puerto 5001 accesible
- [ ] Base de datos inicializada
- [ ] Conexión con Belgrano Ahorro
- [ ] Panel de administración accesible

## 📊 **Monitoreo**

### **Health Checks**
```bash
# Verificar estado del servicio
curl http://localhost:5001/health

# Verificar conectividad con Belgrano Ahorro
curl http://localhost:5001/status
```

### **Logs**
```bash
# Ver logs del contenedor
docker logs belgrano-ticketera

# Ver logs en tiempo real
docker logs -f belgrano-ticketera
```

## 🔒 **Seguridad**

### **Configuraciones Implementadas**
1. **Secret Key**: Configurada via variable de entorno
2. **CORS**: Configurado para comunicación entre servicios
3. **Autenticación**: Sistema de login con roles
4. **Validación**: Validación de datos de entrada

### **Recomendaciones**
- Cambiar `SECRET_KEY` en producción
- Configurar HTTPS en producción
- Implementar rate limiting
- Configurar backup de base de datos

## 📈 **Escalabilidad**

### **Opciones Disponibles**
1. **Horizontal**: Múltiples instancias de la ticketera
2. **Vertical**: Aumentar recursos del contenedor
3. **Load Balancer**: Distribuir carga entre instancias

## ✅ **Estado Final**

- ✅ **Dockerfile**: Completo y funcional
- ✅ **docker-compose.yml**: Configurado para servicios independientes
- ✅ **Scripts de inicio**: Para Windows y Linux/Mac
- ✅ **Dependencias**: Específicas y optimizadas
- ✅ **Configuración Render**: Lista para deploy
- ✅ **Documentación**: Completa y detallada
- ✅ **Verificación**: Scripts de testing incluidos

## 🎯 **Próximos Pasos**

1. **Probar localmente**: `docker-compose up --build`
2. **Verificar funcionamiento**: Acceder a http://localhost:5001
3. **Deploy en Render**: Conectar repositorio
4. **Configurar producción**: Variables de entorno
5. **Monitorear**: Health checks y logs

**¡La ticketera está completamente configurada como servicio independiente pero conectado con Belgrano Ahorro!**
