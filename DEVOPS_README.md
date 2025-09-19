# 🔧 Sistema DevOps - Belgrano Tickets

## 📋 Descripción General

El sistema DevOps proporciona una interfaz completa de administración para gestionar ofertas, productos, negocios y precios de Belgrano Ahorro desde la aplicación de tickets.

## 🏗️ Arquitectura

### Componentes Principales

1. **`devops_routes.py`** - Blueprint principal con todos los endpoints
2. **`devops_belgrano_manager.py`** - Gestor de base de datos para operaciones CRUD
3. **`config_devops.py`** - Configuración específica de DevOps
4. **Fallbacks en aplicaciones** - Sistema de respaldo en `app_tickets.py` y `belgrano_tickets/app.py`

### Integración

- **Aplicación Principal**: `belgrano_tickets/app.py`
- **Aplicación de Tickets**: `app_tickets.py`
- **Base de Datos**: `belgrano_ahorro.db` y `belgrano_tickets.db`

## 🔐 Autenticación

### Credenciales por Defecto
- **Usuario**: `devops`
- **Contraseña**: `DevOps2025!Secure`

### Variables de Entorno
```bash
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=DevOps2025!Secure
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
BELGRANO_AHORRO_DB_PATH=belgrano_ahorro.db
TICKETS_DB_PATH=belgrano_tickets.db
SECRET_KEY=devops_secret_key_2025
```

## 🌐 Endpoints Disponibles

### Autenticación
- `GET /devops/login` - Formulario de login
- `POST /devops/login` - Autenticación
- `GET /devops/logout` - Cerrar sesión

### Panel Principal
- `GET /devops/` - Panel principal con información del sistema
- `GET /devops/health` - Health check del sistema
- `GET /devops/status` - Estado detallado del sistema
- `GET /devops/info` - Información completa del servicio

### Gestión de Contenido
- `GET /devops/ofertas` - Gestión de ofertas (HTML + JSON)
- `GET /devops/negocios` - Gestión de negocios (HTML + JSON)
- `GET /devops/productos` - Gestión de productos (HTML + JSON)
- `GET /devops/precios` - Gestión de precios (HTML + JSON)

### Utilidades
- `GET /devops/sync` - Sincronización manual
- `GET /devops/logs` - Ver logs del sistema
- `GET /devops/config` - Configuración actual

## 🎨 Frontend

### Características del Frontend

#### Gestión de Ofertas (`/devops/ofertas`)
- **Interfaz HTML completa** con tabla de ofertas
- **Crear ofertas** con formularios interactivos
- **Editar ofertas** con confirmaciones
- **Eliminar ofertas** con confirmación de seguridad
- **Estados visuales** (Activa/Inactiva)
- **Carga dinámica** con AJAX

#### Gestión de Negocios (`/devops/negocios`)
- **Lista completa** de comerciantes
- **Crear negocios** con todos los campos
- **Editar negocios** con información detallada
- **Eliminar negocios** con confirmación
- **Ver productos** por negocio
- **Información completa** (dirección, teléfono, email)

#### Gestión de Productos (`/devops/productos`)
- **Catálogo completo** de productos
- **Búsqueda en tiempo real** por nombre/descripción
- **Crear productos** con categorías y precios
- **Editar productos** con validaciones
- **Eliminar productos** con confirmación
- **Ver precios** por producto
- **Estados visuales** (Activo/Inactivo)

#### Gestión de Precios (`/devops/precios`)
- **Panel de precios** completo
- **Filtros avanzados** por negocio
- **Búsqueda de productos** en tiempo real
- **Editar precios** individuales
- **Ver historial** de cambios
- **Exportar datos** a Excel
- **Actualización masiva** de precios

### Características Técnicas

- **Diseño Responsivo** - Optimizado para móviles y desktop
- **AJAX Support** - Carga dinámica sin recargas
- **CSS Moderno** - Gradientes y animaciones
- **JavaScript Interactivo** - Funciones dinámicas
- **Estados Visuales** - Indicadores claros de estado
- **Confirmaciones** - Seguridad en operaciones críticas

## 🗄️ Base de Datos

### Tablas Principales

#### Ofertas
```sql
CREATE TABLE ofertas (
    id INTEGER PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    descuento DECIMAL(5,2),
    fecha_inicio DATE,
    fecha_fin DATE,
    activa BOOLEAN DEFAULT 1,
    negocio_id INTEGER
);
```

#### Negocios
```sql
CREATE TABLE negocios (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(300),
    telefono VARCHAR(50),
    email VARCHAR(100),
    activo BOOLEAN DEFAULT 1
);
```

#### Productos
```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2),
    categoria_id INTEGER,
    negocio_id INTEGER,
    activo BOOLEAN DEFAULT 1
);
```

## 🚀 Despliegue

### Configuración de Producción

1. **Variables de Entorno**:
   ```bash
   export DEVOPS_USERNAME=devops
   export DEVOPS_PASSWORD=DevOps2025!Secure
   export BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
   export BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
   ```

2. **Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Base de Datos**:
   - Asegurar que `belgrano_ahorro.db` existe
   - Verificar permisos de escritura
   - Configurar rutas absolutas si es necesario

### Verificación Post-Deploy

1. **Probar Login**:
   ```bash
   curl -X POST http://tu-dominio.com/devops/login \
        -d "username=devops&password=DevOps2025!Secure"
   ```

2. **Verificar Endpoints**:
   ```bash
   curl http://tu-dominio.com/devops/health
   curl http://tu-dominio.com/devops/status
   ```

3. **Probar Frontend**:
   - Acceder a `/devops/login`
   - Autenticarse con credenciales
   - Navegar por todos los paneles

## 🔧 Mantenimiento

### Logs del Sistema
- **Endpoint**: `/devops/logs`
- **Ubicación**: Logs de la aplicación Flask
- **Nivel**: INFO, WARNING, ERROR

### Monitoreo
- **Health Check**: `/devops/health`
- **Estado del Sistema**: `/devops/status`
- **Configuración**: `/devops/config`

### Resolución de Problemas

#### Error 404 en DevOps
1. Verificar que el blueprint está registrado
2. Comprobar rutas en `devops_routes.py`
3. Verificar fallbacks en aplicaciones principales

#### Error de Autenticación
1. Verificar credenciales en variables de entorno
2. Comprobar hash de contraseña
3. Verificar configuración de sesión

#### Error de Base de Datos
1. Verificar que las bases de datos existen
2. Comprobar permisos de acceso
3. Verificar rutas en `devops_belgrano_manager.py`

## 📊 Scripts de Diagnóstico

### Diagnóstico Completo
```bash
python diagnostico_devops_completo.py
```

### Verificación de Endpoints
```bash
python verificar_endpoints_devops.py
```

### Configuración
```bash
python config_devops.py
```

## 🔒 Seguridad

### Medidas Implementadas
- **Autenticación independiente** para DevOps
- **Hash seguro** de contraseñas con Werkzeug
- **Sesiones seguras** con timeout configurable
- **Validación de entrada** en todos los endpoints
- **Logs de seguridad** para auditoría

### Recomendaciones
1. **Cambiar credenciales** en producción
2. **Configurar HTTPS** para comunicación segura
3. **Monitorear logs** de acceso
4. **Actualizar contraseñas** regularmente

## 📈 Monitoreo y Métricas

### Métricas Disponibles
- **Uptime del sistema**
- **Tiempo de respuesta** de endpoints
- **Errores por endpoint**
- **Uso de base de datos**
- **Sesiones activas**

### Alertas Recomendadas
- **Error rate > 5%**
- **Tiempo de respuesta > 5s**
- **Fallos de autenticación > 10/min**
- **Errores de base de datos**

## 🆘 Soporte

### Contacto
- **Sistema**: DevOps Belgrano Tickets v2.0
- **Versión**: 2.0.0
- **Última actualización**: 2025-01-19

### Documentación Adicional
- **API Docs**: `/devops/docs`
- **Health Endpoint**: `/devops/health`
- **Status Endpoint**: `/devops/status`

---

**🔧 Sistema DevOps - Belgrano Tickets v2.0**  
*Administración completa de ofertas, productos, negocios y precios*
