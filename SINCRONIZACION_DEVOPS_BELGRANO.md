# Sincronización DevOps - Belgrano Ahorro

## Resumen de Mejoras Implementadas

### 1. Corrección de URLs de API
- **Problema**: Las URLs de la API no estaban usando la versión correcta (`v1/`)
- **Solución**: Actualizadas todas las rutas para usar `v1/productos`, `v1/negocios`, `v1/sucursales`, `v1/ofertas`, `v1/precios`

### 2. Función de Sincronización Automática
- **Nueva función**: `sincronizar_con_belgrano_ahorro()`
- **Propósito**: Sincroniza todos los datos (productos, negocios, sucursales, ofertas, precios) con Belgrano Ahorro
- **Uso**: Se ejecuta automáticamente en el dashboard y manualmente con el botón de sincronización

### 3. Sistema de Notificaciones
- **Nueva función**: `notificar_cambio_a_belgrano(tipo_cambio, datos)`
- **Propósito**: Notifica a Belgrano Ahorro sobre cambios realizados desde DevOps
- **Tipos de notificación**:
  - `negocio_agregado`: Cuando se agrega un nuevo negocio
  - `negocio_actualizado`: Cuando se edita un negocio existente
  - `negocio_eliminado`: Cuando se elimina un negocio
  - `negocio_agregado_local`: Cuando se agrega localmente (fallback)
  - `negocio_actualizado_local`: Cuando se actualiza localmente (fallback)
  - `negocio_eliminado_local`: Cuando se elimina localmente (fallback)

### 4. Dashboard Mejorado
- **Sincronización automática**: Se ejecuta al cargar el dashboard
- **Estado de sincronización**: Muestra si la sincronización fue exitosa o falló
- **Botón de sincronización manual**: Permite forzar la sincronización

### 5. Funciones de Gestión de Negocios Operativas
- **Agregar negocio**: Funciona con API y fallback local
- **Editar negocio**: Funciona con API y fallback local
- **Eliminar negocio**: Funciona con API y fallback local
- **Notificaciones**: Todas las operaciones notifican los cambios a Belgrano Ahorro

## Cómo Funciona la Sincronización

### Flujo de Datos
1. **Operación en DevOps** → **API de Belgrano Ahorro** → **Notificación** → **Actualización en Belgrano Ahorro**
2. **Si falla la API** → **Fallback local** → **Notificación local** → **Sincronización posterior**

### Endpoints de API Utilizados
- `GET /api/v1/productos` - Obtener productos
- `POST /api/v1/productos` - Crear producto
- `PUT /api/v1/productos/{id}` - Actualizar producto
- `DELETE /api/v1/productos/{id}` - Eliminar producto
- `GET /api/v1/negocios` - Obtener negocios
- `POST /api/v1/negocios` - Crear negocio
- `PUT /api/v1/negocios/{id}` - Actualizar negocio
- `DELETE /api/v1/negocios/{id}` - Eliminar negocio
- `GET /api/v1/sucursales` - Obtener sucursales
- `POST /api/v1/sucursales` - Crear sucursal
- `GET /api/v1/ofertas` - Obtener ofertas
- `POST /api/v1/ofertas` - Crear oferta
- `PUT /api/v1/ofertas/{id}` - Actualizar oferta
- `DELETE /api/v1/ofertas/{id}` - Eliminar oferta
- `GET /api/v1/precios` - Obtener precios
- `POST /api/v1/notificaciones/cambios` - Notificar cambios

### Configuración
- **URL Base**: `https://belgranoahorro-hp30.onrender.com/api/`
- **API Key**: `belgrano_ahorro_api_key_2025`
- **Timeout**: 8 segundos
- **Fallback**: Archivo local `productos.json`

## Características de Seguridad
- **Autenticación**: Requiere sesión DevOps activa
- **API Key**: Autenticación con token Bearer
- **Logging**: Registro detallado de todas las operaciones
- **Manejo de errores**: Fallback local en caso de fallo de API

## Uso
1. **Acceder al dashboard DevOps**: `/devops/dashboard`
2. **Gestionar negocios**: `/devops/negocios`
3. **Sincronización manual**: Botón "Sincronizar" en el dashboard
4. **Ver estado**: El dashboard muestra el estado de la sincronización

## Logs
- **Éxito**: "Sincronización completada exitosamente"
- **Error**: "Error en sincronización, usando datos locales"
- **Operaciones**: Todas las operaciones se registran en los logs

## Notas Importantes
- Los cambios se reflejan inmediatamente en Belgrano Ahorro
- Si falla la API, se guarda localmente y se notifica para sincronización posterior
- Todas las operaciones incluyen metadatos de origen (`origen: 'devops'`)
- Los negocios creados desde DevOps tienen prioridad alta para aparecer primero
