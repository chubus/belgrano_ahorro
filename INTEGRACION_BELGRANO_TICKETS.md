# 🔗 INTEGRACIÓN BELGRANO AHORRO + BELGRANO TICKETS

## 📋 Descripción

Este documento explica cómo conectar la aplicación principal de **Belgrano Ahorro** con **Belgrano Tickets** para la gestión automática de pedidos.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────┐    HTTP POST    ┌─────────────────────┐
│   Belgrano Ahorro   │ ──────────────► │  Belgrano Tickets   │
│   (Puerto 5000)     │                 │   (Puerto 5001)     │
│                     │                 │                     │
│ • Catálogo          │                 │ • Gestión de        │
│ • Carrito           │                 │   tickets           │
│ • Pedidos           │                 │ • Panel admin       │
│ • Usuarios          │                 │ • Panel flota       │
└─────────────────────┘                 └─────────────────────┘
```

## 🚀 Cómo Iniciar el Sistema Completo

### Opción 1: Iniciar Manualmente

1. **Terminal 1 - Belgrano Ahorro:**
   ```bash
   cd Belgrano_ahorro-back
   python app.py
   ```

2. **Terminal 2 - Belgrano Tickets:**
   ```bash
   cd Belgrano_ahorro-back/belgrano_tickets
   python app.py
   ```

### Opción 2: Script Automático

```bash
python iniciar_sistema_completo.py
```

## 🔧 Configuración de Puertos

- **Belgrano Ahorro**: `http://localhost:5000`
- **Belgrano Tickets**: `http://localhost:5001`

## 📡 API de Integración

### Endpoint de Recepción de Tickets

**URL**: `POST http://localhost:5001/api/tickets`

**Datos enviados**:
```json
{
  "numero": "PED-001",
  "cliente_nombre": "Juan Pérez",
  "cliente_direccion": "Av. Belgrano 123",
  "cliente_telefono": "11-1234-5678",
  "cliente_email": "juan@ejemplo.com",
  "productos": [
    {
      "nombre": "Arroz",
      "cantidad": 2,
      "precio": 500,
      "subtotal": 1000
    }
  ],
  "total": 1000,
  "metodo_pago": "Efectivo",
  "fecha_pedido": "2025-01-19T16:30:00",
  "indicaciones": "Entregar antes de las 18:00"
}
```

## 🔄 Flujo de Integración

1. **Usuario completa pedido** en Belgrano Ahorro
2. **Sistema procesa pago** y crea pedido en BD
3. **Se envía ticket automáticamente** a Belgrano Tickets
4. **Belgrano Tickets recibe** y crea ticket de gestión
5. **Admin/Flota gestiona** el ticket en su panel

## 👥 Roles en Belgrano Tickets

### Admin
- ✅ Ver todos los tickets
- ✅ Asignar tickets a flota
- ✅ Gestionar usuarios
- ✅ Ver reportes
- ✅ Cambiar estados de tickets

### Flota
- ✅ Ver tickets asignados
- ✅ Actualizar estado de tickets
- ✅ Marcar como entregado

## 🛠️ Archivos de Integración

- `integracion_belgrano_tickets.py` - Cliente API
- `app.py` (línea ~1020) - Integración en procesar_pago
- `belgrano_tickets/app.py` - Servidor de tickets
- `belgrano_tickets/routes.py` - API endpoints

## 🔍 Verificación de Conexión

### Test Manual
```bash
python integracion_belgrano_tickets.py
```

### Verificación en Logs
- ✅ "Ticket enviado a Belgrano Tickets: PED-001"
- ⚠️ "Belgrano Tickets no está disponible"
- ❌ "Error en integración con Belgrano Tickets"

## 🚨 Solución de Problemas

### Belgrano Tickets no responde
1. Verificar que esté ejecutándose en puerto 5001
2. Revisar logs de error
3. Verificar dependencias instaladas

### Error de conexión
1. Verificar firewall
2. Comprobar que ambos servicios estén activos
3. Revisar configuración de red

### Tickets no se envían
1. Verificar formato de datos
2. Revisar logs de la aplicación principal
3. Comprobar que la API esté funcionando

## 📊 Monitoreo

### Logs a Revisar
- **Belgrano Ahorro**: Consola de la aplicación
- **Belgrano Tickets**: Consola de la aplicación

### Métricas Importantes
- Tickets enviados exitosamente
- Errores de conexión
- Tiempo de respuesta de la API

## 🔐 Seguridad

- La API de Belgrano Tickets está protegida
- Solo acepta POST requests
- Validación de datos en ambos extremos
- Logs de auditoría en ambas aplicaciones

---

**Estado**: ✅ Integración Funcional
**Última actualización**: 19/01/2025
