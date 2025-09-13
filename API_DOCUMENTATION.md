# 📋 Documentación de APIs - Sistema Belgrano Ahorro + Ticketera

## 🎯 Variables de Entorno Requeridas

Para que el sistema funcione correctamente, debes configurar estas variables de entorno:

```bash
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=tu_api_key_aqui
```

## 🏪 APIs de Belgrano Ahorro (Sistema Principal)

### Endpoints disponibles en la API de Belgrano Ahorro:

#### Productos
- `GET /api/productos` - Obtener lista de productos
- `GET /api/productos/{id}` - Obtener producto específico

#### Tickets
- `GET /api/tickets` - Obtener lista de tickets
- `GET /api/tickets/{id}` - Obtener ticket específico
- `POST /api/tickets` - Crear nuevo ticket
- `PUT /api/tickets/{id}` - Actualizar ticket existente

#### Sincronización
- `POST /api/sync/{tipo}` - Sincronizar datos con el sistema

#### Salud del Sistema
- `GET /api/health` - Verificar estado de la API

## 🎫 APIs de la Ticketera (Sistema de Tickets)

### Rutas Principales de la Aplicación:

#### Autenticación y Panel
- `GET /` - Página principal
- `GET /login` - Página de login
- `POST /login` - Procesar login
- `GET /logout` - Cerrar sesión
- `GET /panel` - Panel principal

#### APIs de Tickets
- `POST /api/tickets/recibir` - Recibir tickets desde Belgrano Ahorro
- `POST /api/tickets` - Crear nuevo ticket
- `POST /ticket/{id}/estado` - Cambiar estado de ticket
- `GET /ticket/{id}/editar` - Editar ticket
- `POST /ticket/{id}/editar` - Procesar edición de ticket
- `POST /ticket/{id}/asignar_repartidor` - Asignar repartidor
- `GET /ticket/{id}/detalle` - Ver detalle de ticket
- `POST /ticket/{id}/eliminar` - Eliminar ticket

#### Gestión
- `GET /gestion_flota` - Gestión de flota
- `GET /reportes` - Reportes del sistema
- `GET /gestion_usuarios` - Gestión de usuarios
- `GET /crear_usuario` - Formulario crear usuario
- `POST /crear_usuario` - Procesar creación de usuario

#### Salud del Sistema
- `GET /health` - Estado básico de salud
- `GET /healthz` - Estado detallado de salud

#### Debug y Mantenimiento
- `GET /debug/credenciales` - Ver credenciales (debug)
- `POST /debug/reparar_credenciales` - Reparar credenciales

## ⚙️ APIs de DevOps (Administración y Monitoreo)

### Rutas DevOps (prefijo: `/devops`):

#### Información del Sistema
- `GET /devops` - Panel principal de DevOps
- `GET /devops/health` - Estado de salud del sistema
- `GET /devops/status` - Estado detallado de servicios
- `GET /devops/info` - Información del sistema
- `GET /devops/logs` - Logs del sistema
- `GET /devops/config` - Configuración actual

#### Datos de Negocio
- `GET /devops/ofertas` - Lista de ofertas disponibles
- `GET /devops/negocios` - Lista de negocios

#### Sincronización
- `POST /devops/sync` - Sincronizar datos con Belgrano Ahorro

## 🔧 Cliente API (api_client.py)

### Clase BelgranoAhorroAPIClient

```python
from belgrano_tickets.api_client import create_api_client

# Crear cliente
client = create_api_client(base_url, api_key)

# Métodos disponibles:
client.get_productos()           # Obtener productos
client.get_producto(id)          # Obtener producto específico
client.create_ticket(data)       # Crear ticket
client.update_ticket(id, data)   # Actualizar ticket
client.get_tickets()            # Obtener tickets
client.get_ticket(id)           # Obtener ticket específico
client.sync_data(tipo, data)    # Sincronizar datos
client.test_connection()        # Probar conexión
```

## 🔄 Flujo de Integración

### Ticketera → Belgrano Ahorro
1. La ticketera recibe tickets en `/api/tickets/recibir`
2. Los procesa internamente
3. Sincroniza cambios usando el cliente API

### DevOps → Belgrano Ahorro
1. DevOps usa el cliente API para sincronizar datos
2. Monitorea el estado de la conexión
3. Proporciona endpoints para administración

### Belgrano Ahorro → Ticketera
1. Belgrano Ahorro envía tickets a `/api/tickets/recibir`
2. Incluye la API key en el header `X-API-Key`
3. La ticketera valida y procesa los tickets

## 🛡️ Autenticación

### Para APIs de la Ticketera:
- Header: `X-API-Key: {BELGRANO_AHORRO_API_KEY}`

### Para APIs de Belgrano Ahorro:
- Header: `Authorization: Bearer {api_key}`
- Header: `X-API-Key: {api_key}`

## 📝 Formato de Datos

### Ticket (ejemplo):
```json
{
  "id": 123,
  "cliente_nombre": "Juan Pérez",
  "productos": [
    {
      "id": 1,
      "nombre": "Producto A",
      "cantidad": 2,
      "precio": 100.00
    }
  ],
  "estado": "pendiente",
  "fecha_creacion": "2025-01-01T10:00:00Z"
}
```

## 🚀 Configuración para Render

### Variables de entorno en Render:
```
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=tu_api_key_de_produccion
```

### Healthcheck URLs:
- Ticketera: `https://tu-ticketera.onrender.com/health`
- DevOps: `https://tu-ticketera.onrender.com/devops/health`

## ⚠️ Validaciones Implementadas

El sistema ahora valida correctamente las variables de entorno y muestra advertencias claras:

```
⚠️ Variable de entorno BELGRANO_AHORRO_URL no está definida
BELGRANO_AHORRO_URL: None
WARNING:api_client:Variables de entorno no configuradas para cliente API global
```

Estas validaciones están implementadas en:
- `api_client.py` - Cliente API global
- `app.py` - Aplicación principal
- `devops_routes.py` - Rutas de DevOps

## 🔍 Troubleshooting

### Error común: "Variable de entorno no está definida"
**Solución:** Configurar las variables en Render o en tu archivo `.env`

### Error: "Cliente API no disponible"
**Solución:** Verificar que ambas variables estén configuradas correctamente

### Error: "No se pudo inicializar el cliente API"
**Solución:** Verificar que el módulo `api_client.py` esté accesible
