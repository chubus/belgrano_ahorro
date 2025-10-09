# 🔧 DevOps Integration - Belgrano Tickets

## 📋 Descripción General

Sistema DevOps completo para el control total del contenido de Belgrano Ahorro. Permite gestionar negocios, sucursales, productos, ofertas y precios desde una interfaz centralizada con sincronización automática.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **DevOps Panel** (`devops_routes.py`) - Interfaz de gestión
2. **API REST** (`api_belgrano_ahorro.py`) - Endpoints para comunicación
3. **Cliente API** (`belgrano_client.py`) - Métodos CRUD completos
4. **Templates HTML** - Interfaz de usuario moderna
5. **Base de Datos** - SQLite con tablas optimizadas

### Flujo de Datos

```
DevOps Panel → API REST → Base de Datos → Belgrano Ahorro App
     ↓              ↓           ↓              ↓
  Templates    Endpoints    SQLite DB    Página Pública
```

## 🚀 Instalación y Configuración

### Variables de Entorno

```bash
# Configuración DevOps
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=DevOps2025!Secure

# API Belgrano Ahorro
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Base de Datos
BELGRANO_AHORRO_DB_PATH=belgrano_ahorro.db
TICKETS_DB_PATH=belgrano_tickets.db

# Seguridad
SECRET_KEY=devops_secret_key_2025
```

### Dependencias

```bash
pip install flask requests sqlite3 werkzeug
```

## 📡 Endpoints API Disponibles

### 🔐 Autenticación
- **Método**: `Bearer Token`
- **Header**: `Authorization: Bearer {API_KEY}`

### 🏪 Negocios

#### Listar Negocios
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/negocios" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025"
```

#### Crear Negocio
```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/negocios" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Supermercado Belgrano",
    "descripcion": "Supermercado de barrio",
    "direccion": "Av. Belgrano 1234",
    "telefono": "011-1234-5678",
    "email": "contacto@belgrano.com",
    "activo": true
  }'
```

#### Actualizar Negocio
```bash
curl -X PUT "https://belgranoahorro-aliq.onrender.com/api/negocios/1" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Supermercado Belgrano Actualizado",
    "activo": false
  }'
```

#### Eliminar Negocio
```bash
curl -X DELETE "https://belgranoahorro-aliq.onrender.com/api/negocios/1" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025"
```

### 🏢 Sucursales

#### Listar Sucursales
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/sucursales" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025"
```

#### Crear Sucursal
```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/sucursales" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sucursal Centro",
    "direccion": "Av. Corrientes 1234",
    "telefono": "011-9876-5432",
    "email": "centro@belgrano.com",
    "negocio_id": 1,
    "activo": true
  }'
```

### 📦 Productos

#### Listar Productos
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/productos" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025"
```

#### Crear Producto
```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/productos" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Arroz Integral",
    "descripcion": "Arroz integral de primera calidad",
    "precio": 450.50,
    "categoria": "Granos",
    "stock": 100,
    "negocio_id": 1,
    "activo": true
  }'
```

### 🏷️ Ofertas

#### Listar Ofertas
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/ofertas" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025"
```

#### Crear Oferta
```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/ofertas" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Oferta Especial Granos",
    "descripcion": "20% de descuento en todos los granos",
    "descuento_porcentaje": 20.0,
    "descuento_fijo": 0.0,
    "activa": true
  }'
```

### 💰 Precios

#### Listar Precios
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/precios" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025"
```

#### Actualizar Precio
```bash
curl -X PUT "https://belgranoahorro-aliq.onrender.com/api/precios/1" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 500.00,
    "motivo": "Ajuste por inflación"
  }'
```

## 🖥️ Uso desde DevOps

### Acceso al Panel

1. **URL**: `http://localhost:5000/devops/`
2. **Credenciales**:
   - Usuario: `devops`
   - Contraseña: `DevOps2025!Secure`

### Funcionalidades Disponibles

#### 🏪 Gestión de Negocios
- ✅ Crear nuevos negocios
- ✅ Editar información existente
- ✅ Activar/desactivar negocios
- ✅ Eliminar negocios
- ✅ Vista de lista con filtros

#### 🏢 Gestión de Sucursales
- ✅ Crear sucursales por negocio
- ✅ Editar información de sucursales
- ✅ Asignar sucursales a negocios
- ✅ Gestión de estado (activa/inactiva)

#### 📦 Gestión de Productos
- ✅ Crear productos con categorías
- ✅ Gestionar stock y precios
- ✅ Asignar productos a negocios
- ✅ Control de estado (activo/inactivo)

#### 🏷️ Gestión de Ofertas
- ✅ Crear ofertas con descuentos
- ✅ Descuentos porcentuales y fijos
- ✅ Activar/desactivar ofertas
- ✅ Gestión de fechas y condiciones

#### 💰 Gestión de Precios
- ✅ Actualizar precios de productos
- ✅ Historial de cambios de precios
- ✅ Motivos de actualización
- ✅ Comparación de precios

### Características de la Interfaz

#### 🎨 Diseño Moderno
- **Bootstrap 5** para componentes
- **Font Awesome** para iconos
- **Gradientes** y animaciones
- **Responsive design**

#### ⚡ Funcionalidades Avanzadas
- **Modales** para formularios
- **Confirmaciones** para eliminaciones
- **Validación** en tiempo real
- **Mensajes** de éxito/error
- **Auto-hide** de notificaciones

## 🔧 Configuración Técnica

### Base de Datos

#### Tabla: `negocios`
```sql
CREATE TABLE negocios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: `sucursales`
```sql
CREATE TABLE sucursales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    negocio_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
);
```

#### Tabla: `productos`
```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    categoria TEXT,
    stock INTEGER DEFAULT 0,
    negocio_id INTEGER,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
);
```

#### Tabla: `ofertas`
```sql
CREATE TABLE ofertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    descuento_porcentaje REAL DEFAULT 0.0,
    descuento_fijo REAL DEFAULT 0.0,
    activa BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: `precios_historial`
```sql
CREATE TABLE precios_historial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    precio_anterior REAL NOT NULL,
    precio_nuevo REAL NOT NULL,
    motivo TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
```

### Cliente API

#### Métodos Disponibles

```python
from belgrano_client import BelgranoAhorroClient

client = BelgranoAhorroClient()

# Negocios
negocios = client.get_negocios()
negocio = client.get_negocio(1)
client.create_negocio(data)
client.update_negocio(1, data)
client.delete_negocio(1)

# Sucursales
sucursales = client.get_sucursales()
sucursal = client.get_sucursal(1)
client.create_sucursal(data)
client.update_sucursal(1, data)
client.delete_sucursal(1)

# Productos
productos = client.get_productos()
producto = client.get_producto(1)
client.create_producto(data)
client.update_producto(1, data)
client.delete_producto(1)

# Ofertas
ofertas = client.get_ofertas()
oferta = client.get_oferta(1)
client.create_oferta(data)
client.update_oferta(1, data)
client.delete_oferta(1)

# Precios
precios = client.get_precios()
client.update_precio(1, data)

# Utilidades
health = client.health_check()
status = client.get_status()
```

## 🔒 Seguridad

### Autenticación
- **API Key** requerida para todos los endpoints
- **Sesiones** seguras para DevOps
- **Hash** de contraseñas con Werkzeug
- **Timeouts** configurados para requests

### Validación
- **Campos requeridos** validados
- **Tipos de datos** verificados
- **Rangos** de valores controlados
- **Sanitización** de inputs

## 📊 Monitoreo y Logs

### Health Check
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/health"
```

### Status Detallado
```bash
curl -X GET "https://belgranoahorro-aliq.onrender.com/api/status"
```

### Logs del Sistema
- **INFO**: Operaciones exitosas
- **WARNING**: Configuraciones faltantes
- **ERROR**: Errores de conexión/API

## 🚀 Despliegue

### Desarrollo Local
```bash
# Iniciar DevOps
python devops_routes.py

# Iniciar API
python api_belgrano_ahorro.py

# Verificar conexión
python belgrano_client.py
```

### Producción
```bash
# Variables de entorno
export BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
export BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Iniciar servicios
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 Solución de Problemas

### Errores Comunes

#### 1. API Key Inválida
```
Error: Invalid API key
Solución: Verificar BELGRANO_AHORRO_API_KEY
```

#### 2. Conexión Fallida
```
Error: Connection error
Solución: Verificar BELGRANO_AHORRO_URL
```

#### 3. Base de Datos Bloqueada
```
Error: Database is locked
Solución: Verificar permisos de archivo .db
```

### Debugging

#### Logs Detallados
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Test de Conexión
```python
from belgrano_client import test_connection
test_connection()
```

## 📈 Mejoras Futuras

### Funcionalidades Planificadas
- [ ] **Backup automático** de base de datos
- [ ] **Sincronización** en tiempo real
- [ ] **Notificaciones** push
- [ ] **Métricas** de rendimiento
- [ ] **API rate limiting**
- [ ] **Auditoría** de cambios

### Optimizaciones
- [ ] **Caché** de consultas frecuentes
- [ ] **Índices** de base de datos
- [ ] **Compresión** de respuestas
- [ ] **CDN** para assets estáticos

## 📞 Soporte

### Contacto
- **Email**: devops@belgrano.com
- **Documentación**: Este archivo
- **Issues**: GitHub Issues

### Recursos
- **API Docs**: `/api/status`
- **Health Check**: `/api/health`
- **Logs**: Sistema de logging integrado

---

## ✅ Checklist de Implementación

- [x] **DevOps Routes** - Rutas CRUD completas
- [x] **API REST** - Endpoints bilingües
- [x] **Cliente API** - Métodos CRUD
- [x] **Templates HTML** - Interfaz moderna
- [x] **Base de Datos** - Tablas optimizadas
- [x] **Autenticación** - Seguridad implementada
- [x] **Documentación** - Guía completa
- [x] **Testing** - Verificación de funcionalidad

**🎉 Sistema DevOps completamente operativo y listo para producción!**