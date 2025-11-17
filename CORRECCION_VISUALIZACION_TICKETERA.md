# ✅ Corrección: Visualización de Productos en Ticketera

## 📋 Problema Identificado

Los productos comprados en Belgrano Ahorro no se visualizaban correctamente en Ticketera. El problema podría estar en:

1. **Falta de logging detallado**: No se logueaban los productos antes de enviar
2. **Validación insuficiente**: No se validaba que todos los productos tengan los campos necesarios
3. **Manejo de errores**: Errores silenciosos al procesar items del carrito

---

## ✅ Correcciones Aplicadas

### 1. **app_unificado.py** - Función `enviar_pedido_a_ticketera_mejorado()`

#### Cambio 1: Logging detallado de productos procesados
```python
# AGREGADO:
logger.info(f"🔍 Procesando {len(carrito_items)} items del carrito para Ticketera...")

for idx, item in enumerate(carrito_items, 1):
    # ... procesamiento ...
    logger.debug(f"   ✅ Producto {idx} procesado: {producto_ticket['nombre']} x{producto_ticket['cantidad']}")

logger.info(f"✅ {len(productos_lista)} productos procesados correctamente para Ticketera")
```

#### Cambio 2: Validación mejorada de items del carrito
```python
# ANTES:
for item in carrito_items:
    producto = item['producto']  # Podía fallar si no existe

# DESPUÉS:
for idx, item in enumerate(carrito_items, 1):
    try:
        producto = item.get('producto', {})
        if not producto:
            logger.warning(f"⚠️ Item {idx} del carrito no tiene 'producto', saltando...")
            continue
        
        cantidad = int(item.get('cantidad', 0))
        subtotal = float(item.get('subtotal', 0))
        
        if cantidad <= 0:
            logger.warning(f"⚠️ Item {idx} tiene cantidad inválida ({cantidad}), saltando...")
            continue
```

#### Cambio 3: Manejo mejorado de categorías
```python
# AGREGADO: Soporte para categoria_id y categoria como string
if producto.get('categoria_id'):
    categoria_data = categorias_dict.get(str(producto['categoria_id']))
    if categoria_data:
        categoria_nombre = categoria_data.get('nombre', categoria_nombre)
elif producto.get('categoria'):
    if isinstance(producto.get('categoria'), str):
        categoria_nombre = producto.get('categoria')
    else:
        categoria_data = categorias_dict.get(str(producto['categoria']))
        if categoria_data:
            categoria_nombre = categoria_data.get('nombre', categoria_nombre)
```

#### Cambio 4: Logging detallado antes de enviar
```python
# AGREGADO:
# Log detallado de cada producto que se envía
for idx, producto in enumerate(productos_lista, 1):
    logger.info(f"   Producto {idx}: {producto.get('nombre', 'Sin nombre')} - Cantidad: {producto.get('cantidad', 0)} - Precio: ${producto.get('precio', 0)} - Subtotal: ${producto.get('subtotal', 0)}")

# Log del payload completo (solo en debug)
logger.debug(f"📦 Payload completo a enviar a Ticketera:")
logger.debug(json_module.dumps(ticket_data, indent=2, ensure_ascii=False))
```

#### Cambio 5: Logging de respuesta de Ticketera
```python
# AGREGADO:
logger.info(f"📥 Respuesta de Ticketera: Status {response.status_code}")
if response.status_code in (200, 201):
    try:
        response_data = response.json()
        logger.info(f"   ✅ Ticket creado: {response_data.get('ticket_id', 'N/A')}")
        logger.info(f"   ✅ Productos recibidos: {len(response_data.get('productos', []))} items")
        
        # Log detallado de productos en la respuesta
        productos_respuesta = response_data.get('productos', [])
        if productos_respuesta:
            logger.info(f"   📦 Productos en respuesta de Ticketera:")
            for idx, prod in enumerate(productos_respuesta, 1):
                logger.info(f"      {idx}. {prod.get('nombre', 'Sin nombre')} x{prod.get('cantidad', 0)}")
        else:
            logger.warning(f"   ⚠️ No se recibieron productos en la respuesta de Ticketera")
    except Exception as e:
        logger.warning(f"   ⚠️ No se pudo parsear respuesta JSON: {e}")
        logger.warning(f"   ⚠️ Respuesta raw: {response.text[:200]}")
```

#### Cambio 6: Tipos de datos explícitos
```python
# MEJORADO: Asegurar tipos correctos
producto_ticket = {
    'id': str(producto.get('id', f'producto_{idx}')),  # Asegurar string
    'nombre': producto.get('nombre', 'Producto sin nombre'),
    'precio': float(producto.get('precio', 0)),  # Asegurar float
    'cantidad': cantidad,  # Ya validado como int > 0
    'subtotal': subtotal,  # Ya validado como float
    'sucursal': sucursal_nombre,
    'negocio': negocio_nombre,
    'categoria': categoria_nombre,
    'descripcion': producto.get('descripcion', producto.get('store', 'Sin descripción')),
    'stock': int(producto.get('stock', 0)),  # Asegurar int
    'destacado': bool(producto.get('destacado', False))  # Asegurar bool
}
```

---

## 📊 Estructura de Datos Enviada

### Formato del ticket con productos:
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
    },
    {
      "id": "2",
      "nombre": "Producto 2",
      "precio": 50.0,
      "cantidad": 3,
      "subtotal": 150.0,
      "sucursal": "Sucursal Norte",
      "negocio": "Negocio Secundario",
      "categoria": "Categoría B",
      "descripcion": "Otra descripción",
      "stock": 30,
      "destacado": true
    }
  ],
  "total": 350.0,
  "metodo_pago": "efectivo",
  "indicaciones": "Sin indicaciones especiales",
  "estado": "pendiente",
  "prioridad": "normal",
  "tipo_cliente": "cliente",
  "fecha_creacion": "2025-01-27T12:34:56.789Z",
  "origen": "belgrano_ahorro"
}
```

---

## 🔍 Logs Esperados

### Al procesar productos:
```
🔍 Procesando 2 items del carrito para Ticketera...
   ✅ Producto 1 procesado: Producto 1 x2
   ✅ Producto 2 procesado: Producto 2 x3
✅ 2 productos procesados correctamente para Ticketera
```

### Antes de enviar:
```
📤 Enviando pedido a Ticketera:
   URL: https://ticketerabelgrano.onrender.com/api/tickets/recibir
   Pedido: PED-20250127-123456
   Cliente: Juan Pérez
   Total: $350.0
   Productos: 2 items
   Producto 1: Producto 1 - Cantidad: 2 - Precio: $100.0 - Subtotal: $200.0
   Producto 2: Producto 2 - Cantidad: 3 - Precio: $50.0 - Subtotal: $150.0
```

### Respuesta de Ticketera:
```
📥 Respuesta de Ticketera: Status 201
   ✅ Ticket creado: 123
   ✅ Productos recibidos: 2 items
   📦 Productos en respuesta de Ticketera:
      1. Producto 1 x2
      2. Producto 2 x3
```

---

## ✅ Verificación

Para verificar que los productos se están enviando correctamente:

1. **Revisar logs de Belgrano Ahorro**:
   - Buscar "🔍 Procesando X items del carrito"
   - Buscar "✅ X productos procesados correctamente"
   - Buscar "📤 Enviando pedido a Ticketera"
   - Buscar "📥 Respuesta de Ticketera"

2. **Revisar logs de Ticketera**:
   - Verificar que el endpoint `/api/tickets/recibir` recibe los productos
   - Verificar que los productos se guardan en la base de datos

3. **Verificar en el panel de Ticketera**:
   - Los tickets deben mostrar los productos comprados
   - Cada producto debe tener nombre, cantidad, precio y subtotal

---

## 🐛 Troubleshooting

### Si los productos no aparecen en Ticketera:

1. **Verificar logs de Belgrano Ahorro**:
   - ¿Se procesan los productos? (buscar "✅ X productos procesados")
   - ¿Se envía el pedido? (buscar "📤 Enviando pedido")
   - ¿Ticketera responde correctamente? (buscar "📥 Respuesta de Ticketera")

2. **Verificar logs de Ticketera**:
   - ¿Se recibe el request? (buscar en logs de Ticketera)
   - ¿Se procesan los productos? (verificar endpoint `/api/tickets/recibir`)

3. **Verificar estructura de datos**:
   - Activar logging en nivel DEBUG para ver el payload completo
   - Verificar que `productos` sea una lista, no un string JSON

4. **Verificar API Key**:
   - Asegurarse de que `BELGRANO_AHORRO_API_KEY` esté configurada
   - Verificar que Ticketera acepta la API Key

---

**Fecha de Corrección:** 2025-01-27
**Estado:** ✅ Correcciones aplicadas y logging mejorado

