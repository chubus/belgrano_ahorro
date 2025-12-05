# Implementación de Tickets por Negocio - Compras Múltiples

## Fecha: 2025-12-04

## Resumen

Se implementó la lógica para generar **tickets separados por cada negocio** cuando un cliente realiza una compra con productos de diferentes negocios. Esto permite que cada ticket pueda ser asignado a un repartidor diferente.

## Cambios Realizados

### 1. Modelo de Datos (`belgrano_tickets/models.py`)

Se agregaron 3 nuevos campos al modelo `Ticket`:

```python
# Campos para agrupar tickets de compra múltiple (diferentes negocios)
grupo_compra = db.Column(db.String(50), nullable=True)      # ID del grupo de compra (pedido original)
negocio_nombre = db.Column(db.String(100), nullable=True)   # Nombre del negocio para este ticket
tickets_grupo_total = db.Column(db.Integer, default=1)      # Total de tickets en el grupo de compra
```

### 2. API de Belgrano Ahorro (`api_belgrano_ahorro.py`)

La función `api_crear_compra()` ahora:

1. **Agrupa productos por negocio**: Los items del carrito se agrupan según su `negocio_id`
2. **Genera un ticket por cada negocio**: Si hay productos de 3 negocios diferentes, se crean 3 tickets
3. **Números de ticket únicos**: Los tickets se numeran como `{PEDIDO}-N1`, `{PEDIDO}-N2`, etc.
4. **Información del grupo**: Cada ticket contiene:
   - `grupo_compra`: ID del pedido original
   - `negocio_nombre`: Nombre del negocio
   - `tickets_grupo_total`: Total de tickets en el grupo

### 3. Endpoint de Ticketera (`belgrano_tickets/app.py`)

El endpoint `recibir_ticket_externo()` ahora:

1. Acepta los nuevos campos `grupo_compra`, `negocio_nombre` y `tickets_grupo_total`
2. Guarda esta información en la base de datos

La función `_serialize_ticket()` incluye los nuevos campos en las respuestas de la API.

### 4. Interfaz de Usuario

#### Panel de Administración (`templates/admin_panel.html`)
- Muestra un badge púrpura cuando el ticket es parte de un grupo de compra múltiple
- Muestra el nombre del negocio debajo del número de ticket
- Indica cuántos negocios tiene el grupo

#### Panel de Flota (`templates/flota_panel.html`)
- Los repartidores pueden ver la misma información de grupo
- Pueden identificar fácilmente qué tickets pertenecen a la misma compra

#### Estilos (`templates/base.html`)
- Se agregó el estilo `.bg-purple` para el badge de grupo múltiple

## Flujo de Ejemplo

### Compra del Cliente
El cliente compra:
- 2 productos del "Supermercado Belgrano"
- 1 producto del "Almacén Don José"
- 3 productos de "Carnicería Los Andes"

### Tickets Generados
Se generan 3 tickets:

| Ticket | Negocio | Productos | Grupo Compra |
|--------|---------|-----------|--------------|
| PED-xxx-N1 | Supermercado Belgrano | 2 | PED-xxx |
| PED-xxx-N2 | Almacén Don José | 1 | PED-xxx |
| PED-xxx-N3 | Carnicería Los Andes | 3 | PED-xxx |

### En la Ticketera
El administrador ve los 3 tickets con:
- Badge púrpura "Grupo: 3 negocios"
- Nombre del negocio visible
- Puede asignar cada ticket a un repartidor diferente

## Respuesta de API

La respuesta de `POST /api/compras` ahora incluye:

```json
{
  "status": "success",
  "message": "Compra realizada exitosamente",
  "data": {
    "pedido_id": 123,
    "numero_pedido": "PED-20251204113340-5",
    "total": 15000.00,
    "items": [...],
    "stock_actualizado": true,
    "ticket_creado": true,
    "tickets_por_negocio": [
      {
        "ticket_id": 45,
        "numero": "PED-20251204113340-5-N1",
        "negocio": "Supermercado Belgrano",
        "productos_count": 2,
        "total": 5000.00
      },
      {
        "ticket_id": 46,
        "numero": "PED-20251204113340-5-N2",
        "negocio": "Almacén Don José",
        "productos_count": 1,
        "total": 3000.00
      },
      {
        "ticket_id": 47,
        "numero": "PED-20251204113340-5-N3",
        "negocio": "Carnicería Los Andes",
        "productos_count": 3,
        "total": 7000.00
      }
    ],
    "negocios_count": 3
  }
}
```

## Notas Importantes

1. **Compatibilidad**: Si la compra tiene productos de un solo negocio, se genera un solo ticket como antes
2. **Migración de Base de Datos**: Los nuevos campos son opcionales (`nullable=True`), por lo que no afectan a los tickets existentes
3. **Asignación Automática**: Cada ticket sigue teniendo asignación automática a repartidores
4. **Los tickets existentes** no se verán afectados y seguirán funcionando normalmente
