# 📡 API DevOps - Documentación Completa

## 🎯 Visión General

El servicio DevOps proporciona una API RESTful completa para conectar y sincronizar datos entre:
- **Belgrano Ahorro** (API principal)
- **Ticketera** (Sistema de tickets)

## 🔐 Autenticación

Todos los endpoints requieren autenticación mediante sesión de DevOps (login en `/devops/login`).

Para uso de API programática, puedes usar la sesión Flask o implementar autenticación por token.

## 📋 Endpoints de Belgrano Ahorro

### Negocios

- **GET** `/devops/api/negocios` - Obtener todos los negocios
- **POST** `/devops/api/negocios` - Crear un negocio
  ```json
  {
    "nombre": "Mi Negocio",
    "descripcion": "Descripción",
    "direccion": "Dirección",
    "telefono": "123456789",
    "email": "email@ejemplo.com",
    "activo": true
  }
  ```
- **GET** `/devops/api/ahorro/negocios/<id>` - Obtener detalle de un negocio
- **PUT** `/devops/api/negocios/<id>` - Actualizar un negocio
- **DELETE** `/devops/api/negocios/<id>` - Eliminar un negocio

### Productos

- **GET** `/devops/api/productos` - Obtener todos los productos
- **POST** `/devops/api/productos` - Crear un producto
  ```json
  {
    "nombre": "Producto",
    "descripcion": "Descripción",
    "precio": 100.50,
    "negocio_id": 1,
    "categoria_id": 1,
    "activo": true
  }
  ```
- **GET** `/devops/api/ahorro/productos/<id>` - Obtener detalle de un producto
- **PUT** `/devops/api/productos/<id>` - Actualizar un producto
- **DELETE** `/devops/api/productos/<id>` - Eliminar un producto

### Ofertas

- **GET** `/devops/api/ofertas` - Obtener todas las ofertas
- **POST** `/devops/api/ofertas` - Crear una oferta
- **GET** `/devops/api/ahorro/ofertas/<id>` - Obtener detalle de una oferta
- **PUT** `/devops/api/ofertas/<id>` - Actualizar una oferta
- **DELETE** `/devops/api/ofertas/<id>` - Eliminar una oferta

### Sucursales

- **GET** `/devops/api/sucursales` - Obtener todas las sucursales
- **POST** `/devops/api/sucursales` - Crear una sucursal
- **GET** `/devops/api/ahorro/sucursales/<id>` - Obtener detalle de una sucursal
- **PUT** `/devops/api/sucursales/<id>` - Actualizar una sucursal
- **DELETE** `/devops/api/sucursales/<id>` - Eliminar una sucursal

### Categorías

- **GET** `/devops/api/categorias` - Obtener todas las categorías
- **GET** `/devops/api/categorias/<id>` - Obtener detalle de una categoría

### Precios

- **GET** `/devops/api/precios` - Obtener todos los precios
- **GET** `/devops/api/precios?producto_id=<id>` - Obtener precios de un producto específico
- **PUT** `/devops/api/precios` - Actualizar precio de un producto
  ```json
  {
    "producto_id": 1,
    "precio": 150.00,
    "descuento": 10
  }
  ```

## 🎫 Endpoints de Ticketera

### Tickets

- **GET** `/devops/api/ticketera/tickets` - Obtener todos los tickets
- **POST** `/devops/api/ticketera/tickets` - Crear un ticket
  ```json
  {
    "titulo": "Título del ticket",
    "descripcion": "Descripción",
    "estado": "activo",
    "negocio_id": 1,
    "producto_id": 1
  }
  ```
- **GET** `/devops/api/ticketera/tickets/<id>` - Obtener detalle de un ticket
- **PUT** `/devops/api/ticketera/tickets/<id>` - Actualizar un ticket
- **DELETE** `/devops/api/ticketera/tickets/<id>` - Eliminar un ticket

## 🔄 Endpoints de Sincronización

### Estado de Sincronización

- **GET** `/devops/api/sync/status` - Obtener estado de conexión con ambas APIs
  ```json
  {
    "status": "success",
    "data": {
      "timestamp": "2025-01-XX...",
      "belgrano_ahorro": {
        "connected": true,
        "url": "https://...",
        "details": {...}
      },
      "ticketera": {
        "connected": true,
        "url": "https://...",
        "details": {...}
      },
      "sync_ready": true
    }
  }
  ```

### Sincronización de Datos

- **POST** `/devops/api/sync/negocios` - Sincronizar todos los negocios a Ticketera
  ```json
  {
    "status": "success",
    "data": {
      "success": 5,
      "failed": 0,
      "errors": []
    }
  }
  ```

- **POST** `/devops/api/sync/productos` - Sincronizar todos los productos a Ticketera
- **POST** `/devops/api/sync/all` - Sincronización completa (negocios + productos)

## 🔌 Proxy a APIs Externas

### Belgrano Ahorro Proxy

- **GET/POST/PUT/PATCH/DELETE** `/devops/api/ahorro/<path:subpath>` - Proxy directo a API de Belgrano Ahorro

Ejemplo: `/devops/api/ahorro/api/negocios` → `https://belgranoahorro-hp30.onrender.com/api/negocios`

### Ticketera Proxy

- **GET/POST/PUT/PATCH/DELETE** `/devops/api/ticketera/<path:subpath>` - Proxy directo a API de Ticketera

Ejemplo: `/devops/api/ticketera/api/tickets` → `{TICKETERA_URL}/api/tickets`

## 🔍 Health Check

- **GET** `/devops/api/integrations/health` - Verificar salud de ambas APIs
  ```json
  {
    "status": "success",
    "results": {
      "ahorro": {
        "ok": true,
        "status": {...}
      },
      "ticketera": {
        "ok": true,
        "status": {...}
      }
    }
  }
  ```

## 📝 Formato de Respuesta

Todas las respuestas siguen este formato:

```json
{
  "status": "success" | "error",
  "message": "Mensaje descriptivo",
  "data": {...} // Datos de respuesta (si aplica)
}
```

### Códigos de Estado HTTP

- `200` - OK (operación exitosa)
- `201` - Created (recurso creado)
- `207` - Multi-Status (sincronización parcial)
- `400` - Bad Request (error en la petición)
- `401` - Unauthorized (no autenticado)
- `404` - Not Found (recurso no encontrado)
- `500` - Internal Server Error
- `503` - Service Unavailable (servicio no disponible)

## ⚙️ Configuración Requerida

### Variables de Entorno para Belgrano Ahorro

```bash
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=tu_api_key_aqui
```

### Variables de Entorno para Ticketera

```bash
# Opción 1: URL y API Key
TICKETS_API_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_KEY=tu_api_key_aqui

# Opción 2: Username/Password (se autentica automáticamente)
# Credenciales de prueba: admin@belgranoahorro.com / admin123
TICKETS_API_USERNAME=admin@belgranoahorro.com
TICKETS_API_PASSWORD=admin123

# Aliases alternativos (todos funcionan)
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETERA_API_KEY=tu_api_key_aqui
DEVOPS_API_URL=https://ticketerabelgrano.onrender.com
DEVOPS_API_KEY=tu_api_key_aqui
```

### Configuración de Timeouts y Reintentos

```bash
API_TIMEOUT_SECS=15
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=0.5
```

## 🚀 Ejemplos de Uso

### Obtener todos los negocios

```bash
curl -X GET http://localhost:5000/devops/api/negocios \
  -H "Cookie: session=tu_session_cookie"
```

### Crear un producto y sincronizar a Ticketera

```bash
# 1. Crear producto
curl -X POST http://localhost:5000/devops/api/productos \
  -H "Content-Type: application/json" \
  -H "Cookie: session=tu_session_cookie" \
  -d '{
    "nombre": "Nuevo Producto",
    "descripcion": "Descripción",
    "precio": 99.99,
    "negocio_id": 1,
    "activo": true
  }'

# 2. Sincronizar productos a Ticketera
curl -X POST http://localhost:5000/devops/api/sync/productos \
  -H "Cookie: session=tu_session_cookie"
```

### Verificar estado de sincronización

```bash
curl -X GET http://localhost:5000/devops/api/sync/status \
  -H "Cookie: session=tu_session_cookie"
```

## 📌 Notas Importantes

1. **Autenticación**: Todos los endpoints requieren estar autenticado mediante login en `/devops/login`
2. **Sincronización**: La sincronización crea tickets en Ticketera basados en los datos de Belgrano Ahorro
3. **Proxies**: Los endpoints proxy permiten acceso directo a las APIs externas sin procesamiento adicional
4. **Manejo de Errores**: Todos los errores devuelven un formato JSON consistente con `status: "error"`
5. **Reintentos**: El sistema automáticamente reintenta peticiones fallidas según la configuración

