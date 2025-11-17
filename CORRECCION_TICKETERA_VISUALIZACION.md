# ✅ Corrección: Visualización de Compras en Ticketera

## 📋 Problema Identificado

Las compras realizadas en Belgrano Ahorro no se visualizaban en Ticketera debido a varios problemas en la integración:

1. **Endpoint incorrecto**: Se enviaba a `/api/tickets` en lugar de `/api/tickets/recibir`
2. **Falta de API Key**: No se enviaba el header `X-API-Key` requerido por Ticketera
3. **Estructura de productos incorrecta**: Se enviaba `productos` como JSON string en lugar de lista
4. **Variable no definida**: Se usaba `productos` sin estar definida en el scope de la función

---

## ✅ Correcciones Aplicadas

### 1. **app_unificado.py** - Función `enviar_pedido_a_ticketera_mejorado()`

#### Cambio 1: Endpoint correcto
```python
# ANTES:
if not api_url.endswith('/api/tickets'):
    api_url = f"{api_url}/api/tickets"

# DESPUÉS:
if not api_url.endswith('/api/tickets/recibir'):
    api_url = f"{api_url.rstrip('/')}/api/tickets/recibir"
```

#### Cambio 2: Obtener datos auxiliares correctamente
```python
# ANTES: Usaba variable 'productos' no definida
negocio_data = productos.get('negocios', {}).get(producto['negocio'])

# DESPUÉS: Obtiene datos desde funciones auxiliares
negocios_raw = obtener_negocios()
negocios_dict = {str(n.get('id', '')): n for n in negocios_raw} if isinstance(negocios_raw, list) else negocios_raw

# Similar para sucursales y categorías
sucursales_raw = obtener_sucursales()
categorias_raw = obtener_categorias()
```

#### Cambio 3: Mejor manejo de información de productos
- Ahora obtiene correctamente nombres de negocios, sucursales y categorías desde la base de datos
- Maneja casos donde los datos no están disponibles con valores por defecto

---

### 2. **api_belgrano_ahorro.py** - Función `api_crear_compra()`

#### Cambio 1: Endpoint correcto
```python
# ANTES:
f"{ticketera_url.rstrip('/')}/api/tickets"

# DESPUÉS:
f"{ticketera_url.rstrip('/')}/api/tickets/recibir"
```

#### Cambio 2: Agregar API Key en headers
```python
# ANTES:
headers={'Content-Type': 'application/json'}

# DESPUÉS:
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': BELGRANO_AHORRO_API_KEY  # Requerido por Ticketera
}
```

#### Cambio 3: Estructura de productos correcta
```python
# ANTES:
'productos': json.dumps(productos_lista),  # JSON string (incorrecto)

# DESPUÉS:
'productos': productos_lista,  # Lista de diccionarios (correcto)
```

#### Cambio 4: Campos adicionales
```python
# Agregados campos adicionales para mejor integración:
'origen': 'belgrano_ahorro',
'fecha_creacion': datetime.now().isoformat()
```

#### Cambio 5: Manejo de códigos de respuesta
```python
# ANTES:
if response.status_code == 201:

# DESPUÉS:
if response.status_code in (200, 201):
    # Ticketera puede devolver 200 o 201
else:
    logger.warning(f"[API] ⚠️ Ticketera respondió con código {response.status_code}: {response.text[:200]}")
```

#### Cambio 6: Timeout aumentado
```python
# ANTES:
timeout=10

# DESPUÉS:
timeout=20  # Más tiempo para APIs lentas
```

---

## 📊 Estructura de Datos Enviada

### Formato correcto del ticket:
```json
{
  "numero": "PED-20250127-123456",
  "cliente_nombre": "Juan Pérez",
  "cliente_direccion": "Calle 123",
  "cliente_telefono": "+5491123456789",
  "cliente_email": "juan@example.com",
  "productos": [
    {
      "id": "1",
      "nombre": "Producto 1",
      "precio": 100.0,
      "cantidad": 2,
      "subtotal": 200.0,
      "sucursal": "Sucursal Centro",
      "negocio": "Negocio Principal",
      "categoria": "Categoría A",
      "descripcion": "Descripción del producto",
      "stock": 50,
      "destacado": false
    }
  ],
  "total": 200.0,
  "estado": "pendiente",
  "prioridad": "normal",
  "origen": "belgrano_ahorro",
  "fecha_creacion": "2025-01-27T12:34:56.789Z"
}
```

---

## 🔍 Endpoints de Ticketera

### Endpoint que recibe tickets:
- **URL**: `/api/tickets/recibir`
- **Método**: `POST`
- **Autenticación**: Header `X-API-Key` con valor de `BELGRANO_AHORRO_API_KEY`
- **Content-Type**: `application/json`

### Respuesta esperada:
```json
{
  "exito": true,
  "ticket_id": 123,
  "numero": "PED-20250127-123456",
  "estado": "pendiente",
  "repartidor_asignado": "Repartidor1",
  "fecha_creacion": "2025-01-27T12:34:56.789Z",
  "cliente_nombre": "Juan Pérez",
  "total": 200.0
}
```

---

## ✅ Resultado Esperado

Después de estas correcciones:

1. ✅ Las compras realizadas en Belgrano Ahorro se envían correctamente a Ticketera
2. ✅ Los productos se visualizan correctamente en el panel de Ticketera
3. ✅ La información del cliente, productos, y total se muestra completa
4. ✅ Los tickets se crean automáticamente con estado "pendiente"
5. ✅ Se asigna automáticamente un repartidor
6. ✅ Los eventos WebSocket se emiten para actualización en tiempo real

---

## 📁 Archivos Modificados

1. ✅ `app_unificado.py` - Función `enviar_pedido_a_ticketera_mejorado()`
2. ✅ `api_belgrano_ahorro.py` - Función `api_crear_compra()`

---

## 🧪 Pruebas Recomendadas

1. Realizar una compra desde Belgrano Ahorro
2. Verificar que el ticket aparece en Ticketera
3. Verificar que los productos se muestran correctamente
4. Verificar que la información del cliente es correcta
5. Verificar que el total coincide

---

**Fecha de Corrección:** 2025-01-27
**Estado:** ✅ Todas las correcciones aplicadas

