# 🔄 Flujo de Comunicación API - Belgrano Ahorro ↔ Belgrano Tickets

## 📋 Resumen del Flujo

Este documento describe el flujo completo de comunicación entre **Belgrano Ahorro** y **Belgrano Tickets** cuando un usuario realiza una compra.

## 🚀 Flujo Completo

### 1. **Usuario inicia compra en Belgrano Ahorro**
- El usuario navega por productos en la plataforma de Ahorro
- Agrega productos al carrito
- Completa el formulario de compra con datos personales
- Selecciona método de pago y dirección de entrega

### 2. **Backend de Ahorro valida y prepara la petición**
```python
# En app.py - función enviar_pedido_a_ticketera()
def enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas):
    # Validar datos del usuario
    # Preparar lista de productos
    # Crear payload para la API de Tickets
    ticket_data = {
        "numero": numero_pedido,
        "cliente_nombre": nombre_completo,
        "cliente_direccion": direccion,
        "cliente_telefono": usuario.get('telefono', ''),
        "cliente_email": usuario['email'],
        "productos": productos,
        "total": total,
        "metodo_pago": metodo_pago,
        "indicaciones": notas,
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente"
    }
```

### 3. **HTTP POST a Ticketera con autenticación**
```python
# Enviar request con API Key y reintentos
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': BELGRANO_AHORRO_API_KEY
}

response = requests.post(
    f"{TICKETERA_URL}/api/tickets",
    json=ticket_data,
    headers=headers,
    timeout=10
)
```

### 4. **Ticketera recibe y procesa la petición**
```python
# En belgrano_tickets/app.py - endpoint /api/tickets
@app.route('/api/tickets', methods=['POST'])
def recibir_ticket_externo():
    # 1. Autenticación por API Key
    api_key_header = request.headers.get('X-API-Key')
    if not api_key_header or api_key_header != BELGRANO_AHORRO_API_KEY:
        return jsonify({'error': 'API key inválida'}), 401
    
    # 2. Idempotencia - verificar si ya existe
    numero_ticket = data.get('numero')
    if numero_ticket:
        existente = Ticket.query.filter_by(numero=numero_ticket).first()
        if existente:
            return jsonify({'exito': True, 'ticket_id': existente.id, 'idempotent': True}), 200
    
    # 3. Crear nuevo ticket
    ticket = Ticket(
        numero=numero_ticket,
        cliente_nombre=data.get('cliente_nombre'),
        cliente_direccion=data.get('cliente_direccion'),
        # ... más campos
    )
    
    # 4. Asignar repartidor automáticamente
    repartidor_asignado = asignar_repartidor_automatico(ticket)
    if repartidor_asignado:
        ticket.repartidor_nombre = repartidor_asignado
    
    # 5. Guardar en base de datos
    db.session.add(ticket)
    db.session.commit()
    
    # 6. Emitir evento WebSocket para actualización en tiempo real
    socketio.emit('nuevo_ticket', {
        'ticket_id': ticket.id,
        'numero': ticket.numero,
        'cliente_nombre': ticket.cliente_nombre,
        'estado': ticket.estado,
        'repartidor': ticket.repartidor_nombre
    })
```

### 5. **Ticketera devuelve respuesta con datos del ticket**
```json
{
    "exito": true,
    "ticket_id": 123,
    "numero": "PED-20241201123456",
    "estado": "pendiente",
    "repartidor_asignado": "Repartidor1",
    "fecha_creacion": "2024-12-01T12:34:56",
    "cliente_nombre": "Juan Pérez",
    "total": 130.0
}
```

### 6. **Ahorro recibe respuesta y actualiza su base de datos**
```python
# En app.py - función actualizar_pedido_con_ticket()
def actualizar_pedido_con_ticket(numero_pedido, ticket_response):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE pedidos 
        SET ticket_id = ?, 
            ticket_estado = ?, 
            ticket_fecha_creacion = ?,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE numero = ?
    """, (
        ticket_response.get('ticket_id'),
        ticket_response.get('estado', 'pendiente'),
        ticket_response.get('fecha_creacion'),
        numero_pedido
    ))
    
    conn.commit()
    conn.close()
```

### 7. **Ahorro devuelve respuesta al frontend**
```json
{
    "success": true,
    "message": "Compra realizada exitosamente",
    "pedido": {
        "numero": "PED-20241201123456",
        "cliente": "Juan Pérez",
        "total": 130.0,
        "fecha": "2024-12-01T12:34:56"
    },
    "ticket": {
        "id": 123,
        "numero": "PED-20241201123456",
        "estado": "pendiente",
        "repartidor": "Repartidor1",
        "fecha_creacion": "2024-12-01T12:34:56"
    }
}
```

## 🔧 Configuración de Variables de Entorno

### Belgrano Ahorro
```bash
TICKETERA_URL=http://localhost:5001  # Local
TICKETERA_URL=https://belgrano-tickets.onrender.com  # Producción
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
RENDER_ENVIRONMENT=production  # Para detectar entorno
```

### Belgrano Tickets
```bash
BELGRANO_AHORRO_URL=http://localhost:5000  # Local
BELGRANO_AHORRO_URL=https://belgrano-ahorro.onrender.com  # Producción
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
RENDER_ENVIRONMENT=production  # Para detectar entorno
```

## 🛡️ Características de Seguridad

### Autenticación
- **API Key**: Todas las peticiones requieren `X-API-Key` header
- **Valor por defecto**: `belgrano_ahorro_api_key_2025`
- **Configurable**: Via variable de entorno `BELGRANO_AHORRO_API_KEY`

### Idempotencia
- **Verificación**: Antes de crear ticket, verifica si ya existe por número
- **Respuesta**: Si existe, devuelve el ticket existente con flag `idempotent: true`
- **Prevención**: Evita duplicados en caso de reintentos

### Reintentos
- **Estrategia**: Backoff exponencial (1s, 2s, 4s)
- **Máximo**: 3 intentos
- **Timeout**: 10 segundos por petición

## 📊 Monitoreo y Logs

### Logs de Ahorro
```
📤 Enviando datos a Ticketera:
   URL: http://localhost:5001/api/tickets
   Datos: {"numero": "PED-123", ...}
✅ Pedido enviado exitosamente a Ticketera: PED-123
   Cliente: Juan Pérez
   Total: $130.0
   Productos: 2 items
   Ticket ID: 123
✅ Pedido PED-123 actualizado con información del ticket
```

### Logs de Tickets
```
Datos recibidos en Ticketera:
   Datos: {"numero": "PED-123", ...}
Ticket recibido exitosamente: PED-123 - Juan Pérez (CLIENTE) - Prioridad: normal
```

## 🧪 Testing

### Script de Prueba Completa
```bash
python scripts/test_flujo_completo.py
```

Este script simula todo el flujo:
1. ✅ Verifica estado de servicios
2. 🛒 Simula datos de compra
3. 📤 Envía pedido a Ticketera
4. 🔍 Verifica ticket creado
5. 💾 Simula actualización en Ahorro
6. 🎯 Simula respuesta al frontend

### Prueba Individual
```bash
python scripts/post_ticket_test.py
```

## 🚀 Deployment

### Render.com Configuration
- **render_ahorro.yaml**: Configuración para Belgrano Ahorro
- **render_tickets.yaml**: Configuración para Belgrano Tickets
- **Variables automáticas**: Se configuran según entorno

### Health Checks
- **Ahorro**: `/test` endpoint
- **Tickets**: `/health` endpoint
- **Cross-service**: Verificación de conectividad entre servicios

## 📈 Beneficios del Flujo

1. **Separación de responsabilidades**: Cada servicio maneja su dominio
2. **Escalabilidad**: Servicios independientes pueden escalar por separado
3. **Resiliencia**: Reintentos y manejo de errores robusto
4. **Trazabilidad**: Logs detallados en cada paso
5. **Idempotencia**: Operaciones seguras para reintentos
6. **Tiempo real**: WebSocket para actualizaciones inmediatas

## 🔄 Flujo Alternativo (Legacy)

Para compatibilidad, se mantiene el endpoint legacy:
- **Ahorro**: `/api/tickets` (POST) - Recibe tickets desde Tickets
- **Tickets**: `/api/tickets/recibir` (POST) - Endpoint alternativo

---

**Estado**: ✅ **LISTO PARA PRODUCCIÓN**

El flujo está completamente implementado y probado. Ambos servicios pueden comunicarse de forma bidireccional y robusta.
