# 🚀 GUÍA DE SINCRONIZACIÓN DEVOPS - BELGRANO AHORRO

## 📋 Descripción General

El sistema de sincronización DevOps permite gestionar **sucursales**, **negocios** y **ofertas** desde el panel de DevOps con **sincronización en tiempo real** hacia la plataforma de Belgrano Ahorro. Todos los cambios se reflejan inmediatamente sin necesidad de reiniciar servicios.

## 🔄 Características Principales

- ✅ **Sincronización en tiempo real** - Cambios inmediatos
- ✅ **Gestión centralizada** desde DevOps
- ✅ **API REST completa** para todas las operaciones
- ✅ **Validación automática** de datos
- ✅ **Logging detallado** de todas las operaciones
- ✅ **Manejo de errores** robusto
- ✅ **Metadatos de sincronización** para auditoría

## 🛠️ Endpoints Disponibles

### 📍 Gestión de Sucursales

#### Obtener Todas las Sucursales
```http
GET /devops/sucursales
```

#### Agregar Nueva Sucursal
```http
POST /devops/agregar_sucursal
Content-Type: application/json

{
    "nombre": "Sucursal Centro",
    "negocio_id": "neg_001",
    "direccion": "Av. Belgrano 1234",
    "telefono": "011-1234-5678",
    "horarios": "Lun-Vie 9:00-18:00",
    "coordenadas": {
        "lat": -34.6037,
        "lng": -58.3816
    }
}
```

#### Editar Sucursal Existente
```http
PUT /devops/editar_sucursal/{sucursal_id}
Content-Type: application/json

{
    "nombre": "Sucursal Centro Actualizada",
    "telefono": "011-1234-9999"
}
```

#### Eliminar Sucursal
```http
DELETE /devops/eliminar_sucursal/{sucursal_id}
```

### 🏢 Gestión de Negocios

#### Obtener Todos los Negocios
```http
GET /devops/negocios
```

#### Agregar Nuevo Negocio
```http
POST /devops/agregar_negocio
Content-Type: application/json

{
    "nombre": "Supermercado Belgrano",
    "descripcion": "Cadena de supermercados con las mejores ofertas",
    "categoria": "supermercado",
    "logo_url": "https://ejemplo.com/logo.png",
    "sitio_web": "https://supermercadobelgrano.com"
}
```

#### Editar Negocio Existente
```http
PUT /devops/editar_negocio/{negocio_id}
Content-Type: application/json

{
    "descripcion": "Descripción actualizada del negocio"
}
```

#### Eliminar Negocio
```http
DELETE /devops/eliminar_negocio/{negocio_id}
```

### 🎯 Gestión de Ofertas

#### Obtener Todas las Ofertas
```http
GET /devops/ofertas
```

#### Agregar Nueva Oferta
```http
POST /devops/agregar_oferta
Content-Type: application/json

{
    "titulo": "Descuento 20% en Lácteos",
    "descripcion": "Oferta especial en todos los productos lácteos",
    "descuento": 20,
    "fecha_inicio": "2025-01-01T00:00:00",
    "fecha_fin": "2025-01-31T23:59:59",
    "productos_aplicables": ["leche", "queso", "yogur"],
    "condiciones": "Válido solo en sucursales seleccionadas"
}
```

#### Editar Oferta Existente
```http
PUT /devops/editar_oferta/{oferta_id}
Content-Type: application/json

{
    "descuento": 25,
    "fecha_fin": "2025-02-15T23:59:59"
}
```

#### Eliminar Oferta
```http
DELETE /devops/eliminar_oferta/{oferta_id}
```

## 🔧 Endpoints de Sistema

### Estado de Sincronización
```http
GET /devops/sync/status
```

### Forzar Sincronización
```http
POST /devops/sync/force
```

### Health Check
```http
GET /devops/health
```

### Información del Sistema
```http
GET /devops/info
```

## 📊 Respuestas de la API

### Respuesta Exitosa
```json
{
    "status": "success",
    "message": "Operación completada exitosamente",
    "data": {
        // Datos de la operación
    }
}
```

### Respuesta de Error
```json
{
    "status": "error",
    "message": "Descripción del error",
    "error_code": "ERROR_CODE"
}
```

## 🔐 Autenticación

El sistema utiliza API keys para autenticación. Todas las requests deben incluir:

```http
X-API-Key: belgrano_ahorro_api_key_2025
X-Origin: devops
```

## 📝 Ejemplos de Uso

### Ejemplo 1: Agregar Sucursal y Verificar Sincronización

```bash
# 1. Agregar nueva sucursal
curl -X POST http://localhost:5000/devops/agregar_sucursal \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "nombre": "Sucursal Norte",
    "negocio_id": "neg_001",
    "direccion": "Av. del Norte 567",
    "telefono": "011-9876-5432"
  }'

# 2. Verificar estado de sincronización
curl -X GET http://localhost:5000/devops/sync/status \
  -H "X-API-Key: belgrano_ahorro_api_key_2025"

# 3. Obtener sucursales para confirmar
curl -X GET http://localhost:5000/devops/sucursales \
  -H "X-API-Key: belgrano_ahorro_api_key_2025"
```

### Ejemplo 2: Gestión Completa de Negocio

```bash
# 1. Crear negocio
curl -X POST http://localhost:5000/devops/agregar_negocio \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "nombre": "Farmacia Belgrano",
    "descripcion": "Farmacia de turno 24/7",
    "categoria": "farmacia"
  }'

# 2. Agregar sucursal al negocio
curl -X POST http://localhost:5000/devops/agregar_sucursal \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "nombre": "Farmacia Centro",
    "negocio_id": "ID_DEL_NEGOCIO_CREADO",
    "direccion": "Av. Belgrano 1000",
    "telefono": "011-1111-2222"
  }'

# 3. Crear oferta para el negocio
curl -X POST http://localhost:5000/devops/agregar_oferta \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "titulo": "Descuento en Medicamentos",
    "descripcion": "15% de descuento en medicamentos genéricos",
    "descuento": 15,
    "fecha_inicio": "2025-01-01T00:00:00",
    "fecha_fin": "2025-12-31T23:59:59"
  }'
```

## 🚨 Manejo de Errores

### Errores Comunes

1. **Campos Requeridos Faltantes**
   ```json
   {
     "status": "error",
     "message": "Campo requerido faltante: nombre"
   }
   ```

2. **Error de Conexión**
   ```json
   {
     "status": "error",
     "message": "Error de conexión con Belgrano Ahorro"
   }
   ```

3. **Error de Autenticación**
   ```json
   {
     "status": "error",
     "message": "API Key inválida"
   }
   ```

### Códigos de Estado HTTP

- `200` - Operación exitosa
- `201` - Recurso creado exitosamente
- `400` - Error en los datos enviados
- `401` - Error de autenticación
- `500` - Error interno del servidor

## 📈 Monitoreo y Logs

### Logs de Sincronización

El sistema genera logs detallados para todas las operaciones:

```
2025-01-27 10:30:15 - INFO - ✅ Sucursal 'Sucursal Centro' agregada y sincronizada exitosamente
2025-01-27 10:30:16 - INFO - ✅ Sincronización exitosa a Belgrano Ahorro: /api/v1/sucursales
```

### Métricas de Sincronización

- Tiempo de respuesta de sincronización
- Tasa de éxito/fallo
- Número de operaciones por minuto
- Estado de conectividad con Belgrano Ahorro

## 🔧 Configuración

### Variables de Entorno

```bash
# URL de Belgrano Ahorro
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com

# API Key para autenticación
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Configuración de sincronización
DEVOPS_SYNC_TIMEOUT=10
DEVOPS_SYNC_RETRY_ATTEMPTS=3
DEVOPS_SYNC_RETRY_DELAY=2
DEVOPS_RATE_LIMIT=100
DEVOPS_LOG_LEVEL=INFO
```

## 🚀 Despliegue

### Requisitos

- Python 3.8+
- Flask
- Requests
- SQLite3

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp config.env.example .env
# Editar .env con las configuraciones correctas

# Ejecutar aplicación
python app.py
```

## 📞 Soporte

Para soporte técnico o reportar problemas:

1. Revisar logs del sistema
2. Verificar estado de sincronización (`/devops/sync/status`)
3. Comprobar conectividad con Belgrano Ahorro
4. Verificar configuración de variables de entorno

## 🔄 Flujo de Sincronización

```
DevOps Panel → API Request → Validación → Sincronización → Belgrano Ahorro
     ↓              ↓           ↓           ↓              ↓
  Interfaz    Endpoint    Datos OK    HTTP Request    Base de Datos
  Usuario     DevOps      Campos      Headers        Actualizada
              Routes      Validados   API Key        Inmediatamente
```

---

**Versión**: 1.0.0  
**Última Actualización**: Enero 2025  
**Mantenido por**: Equipo DevOps Belgrano
