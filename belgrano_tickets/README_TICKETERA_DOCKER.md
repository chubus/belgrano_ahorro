# 🎫 Belgrano Tickets - Docker Independiente

## 📋 Descripción

Este Dockerfile y configuración permiten ejecutar **Belgrano Tickets** como un servicio web independiente pero conectado con **Belgrano Ahorro**. La ticketera funciona en el puerto 5001 y se comunica con el servicio principal.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐
│ Belgrano Ahorro │◄──►│ Belgrano Tickets │
│   Puerto 5000   │    │   Puerto 5001    │
└─────────────────┘    └──────────────────┘
```

## 📁 Estructura de Archivos

```
belgrano_tickets/
├── Dockerfile                    # Dockerfile específico para la ticketera
├── docker-compose.yml           # Configuración de servicios
├── start_ticketera.sh           # Script de inicio (Linux/Mac)
├── start_ticketera.bat          # Script de inicio (Windows)
├── requirements_ticketera.txt   # Dependencias específicas
├── config_ticketera.py          # Configuración de la aplicación
├── render_ticketera.yaml        # Configuración para Render
└── README_TICKETERA_DOCKER.md   # Esta documentación
```

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
# Desde el directorio belgrano_tickets/
docker-compose up --build
```

### Opción 2: Script de Windows

```bash
# Ejecutar el script de Windows
start_ticketera.bat
```

### Opción 3: Docker Directo

```bash
# Construir la imagen
docker build -f belgrano_tickets/Dockerfile -t belgrano-ticketera .

# Ejecutar el contenedor
docker run -p 5001:5001 \
  -v $(pwd)/belgrano_tickets/belgrano_tickets.db:/app/belgrano_tickets/belgrano_tickets.db \
  -v $(pwd)/belgrano_ahorro.db:/app/belgrano_ahorro.db \
  -e BELGRANO_AHORRO_URL=http://localhost:5000 \
  belgrano-ticketera
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `FLASK_APP` | Archivo principal de Flask | `belgrano_tickets/app.py` |
| `FLASK_ENV` | Entorno de Flask | `production` |
| `PORT` | Puerto de la aplicación | `5001` |
| `SECRET_KEY` | Clave secreta de Flask | `belgrano_tickets_secret_2025` |
| `BELGRANO_AHORRO_URL` | URL del servicio principal | `http://localhost:5000` |

### Volúmenes

- `./instance` → `/app/belgrano_tickets/instance`
- `./static` → `/app/belgrano_tickets/static`
- `./belgrano_tickets.db` → `/app/belgrano_tickets/belgrano_tickets.db`
- `../belgrano_ahorro.db` → `/app/belgrano_ahorro.db`

## 🌐 Acceso a la Aplicación

- **URL Local**: http://localhost:5001
- **URL Belgrano Ahorro**: http://localhost:5000
- **Panel de Administración**: http://localhost:5001/login

## 🔗 Integración con Belgrano Ahorro

### Comunicación entre Servicios

La ticketera se conecta con Belgrano Ahorro para:

1. **Sincronización de Datos**: Acceso a productos y pedidos
2. **Gestión de Tickets**: Creación y seguimiento de tickets
3. **Notificaciones**: Actualizaciones en tiempo real
4. **Autenticación**: Verificación de usuarios

### Configuración de Red

```yaml
networks:
  belgrano-network:
    driver: bridge
    name: belgrano-network
```

## 📦 Dependencias Específicas

### Flask y Extensiones
- `Flask==3.1.1`
- `Flask-SocketIO==5.3.6`
- `Flask-SQLAlchemy==3.1.1`
- `Flask-Login==0.6.3`

### Socket.IO
- `python-socketio==5.11.1`
- `python-engineio==4.9.1`
- `eventlet==0.35.2`

### Utilidades
- `requests==2.32.3`
- `SQLAlchemy==2.0.28`

## 🚀 Deploy en Render

### Configuración Automática

El archivo `render_ticketera.yaml` está configurado para:

1. **Build Automático**: Instalación de dependencias
2. **Inicialización de BD**: Creación automática de tablas
3. **Variables de Entorno**: Configuración de producción
4. **Health Checks**: Verificación de estado

### Pasos para Deploy

1. Conectar repositorio a Render
2. Render detectará `render_ticketera.yaml`
3. Configurar variables de entorno
4. Deploy automático

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión con Belgrano Ahorro
```bash
# Verificar que Belgrano Ahorro esté corriendo
curl http://localhost:5000

# Verificar variables de entorno
echo $BELGRANO_AHORRO_URL
```

#### 2. Error de Base de Datos
```bash
# Verificar permisos de archivos
ls -la belgrano_tickets.db

# Recrear base de datos
rm belgrano_tickets.db
docker-compose up --build
```

#### 3. Error de Puerto
```bash
# Verificar puertos en uso
netstat -tulpn | grep :5001

# Cambiar puerto en docker-compose.yml
ports:
  - "5002:5001"
```

### Logs de Debug

```bash
# Ver logs del contenedor
docker logs belgrano-ticketera

# Ver logs en tiempo real
docker logs -f belgrano-ticketera
```

## 📊 Monitoreo

### Health Check

```bash
# Verificar estado del servicio
curl http://localhost:5001/health

# Verificar conectividad con Belgrano Ahorro
curl http://localhost:5001/status
```

### Métricas

- **Uptime**: Tiempo de funcionamiento
- **Tickets Activos**: Número de tickets pendientes
- **Usuarios Conectados**: Usuarios activos en el sistema
- **Rendimiento**: Tiempo de respuesta de la API

## 🔒 Seguridad

### Configuraciones de Seguridad

1. **Secret Key**: Configurada via variable de entorno
2. **CORS**: Configurado para comunicación entre servicios
3. **Autenticación**: Sistema de login con roles
4. **Validación**: Validación de datos de entrada

### Recomendaciones

- Cambiar `SECRET_KEY` en producción
- Configurar HTTPS en producción
- Implementar rate limiting
- Configurar backup de base de datos

## 📈 Escalabilidad

### Opciones de Escalado

1. **Horizontal**: Múltiples instancias de la ticketera
2. **Vertical**: Aumentar recursos del contenedor
3. **Load Balancer**: Distribuir carga entre instancias

### Configuración para Producción

```yaml
# docker-compose.prod.yml
services:
  belgrano-ticketera:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## ✅ Verificación de Instalación

### Script de Verificación

```bash
# Ejecutar script de verificación
python test_ticketera_docker.py
```

### Checklist

- [ ] Docker instalado y funcionando
- [ ] Imagen construida correctamente
- [ ] Contenedor ejecutándose
- [ ] Puerto 5001 accesible
- [ ] Base de datos inicializada
- [ ] Conexión con Belgrano Ahorro
- [ ] Panel de administración accesible

## 📞 Soporte

### Comandos Útiles

```bash
# Reiniciar servicios
docker-compose restart

# Ver estado de servicios
docker-compose ps

# Limpiar recursos
docker-compose down --volumes

# Actualizar imagen
docker-compose pull
```

### Documentación Adicional

- [Guía de Usuario de Belgrano Tickets](../GUIA_INICIALIZACION.md)
- [Documentación de API](../DOCUMENTACION.md)
- [Troubleshooting](../GUIA_MANTENIMIENTO.md)
