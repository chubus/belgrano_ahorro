# 🔗 INTEGRACIÓN COMPLETA: BELGRANO AHORRO + BELGRANO TICKETS

## 🎯 Descripción

Este documento explica cómo funciona la integración automática entre **Belgrano Ahorro** (aplicación principal) y **Belgrano Tickets** (sistema de gestión de pedidos).

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
│ • Comerciantes      │                 │ • Asignación auto   │
└─────────────────────┘                 └─────────────────────┘
```

## 🚀 Cómo Iniciar el Sistema Completo

### Opción 1: Script Automático (Recomendado)

```bash
python iniciar_sistema_completo.py
```

Este script:
- ✅ Inicia ambas aplicaciones automáticamente
- ✅ Monitorea los procesos
- ✅ Reinicia automáticamente si se caen
- ✅ Maneja señales de interrupción (Ctrl+C)

### Opción 2: Iniciar Manualmente

**Terminal 1 - Belgrano Ahorro:**
```bash
python app.py
```

**Terminal 2 - Belgrano Tickets:**
```bash
cd belgrano_tickets
python app.py
```

## 📡 Flujo de Integración Automática

### 1. **Usuario Completa Compra en Belgrano Ahorro**
- Agrega productos al carrito
- Completa el checkout
- Procesa el pago

### 2. **Sistema Procesa el Pedido**
- Se guarda en la base de datos de Belgrano Ahorro
- Se genera número de pedido único
- Se preparan los datos para enviar a Belgrano Tickets

### 3. **Envío Automático a Belgrano Tickets**
- Se envía ticket via HTTP POST a `/api/tickets/recibir`
- Se incluyen todos los detalles del pedido
- Se asigna prioridad automática (alta para comerciantes)

### 4. **Belgrano Tickets Recibe y Procesa**
- Crea ticket en su base de datos
- Asigna repartidor automáticamente
- Emite evento WebSocket para actualización en tiempo real

### 5. **Gestión en Belgrano Tickets**
- Admin puede ver todos los tickets
- Flota ve solo sus tickets asignados
- Se pueden actualizar estados y prioridades

## 🔧 Configuración de Puertos

- **Belgrano Ahorro**: `http://localhost:5000`
- **Belgrano Tickets**: `http://localhost:5001`

## 📊 Datos que se Envían Automáticamente

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
  "indicaciones": "Entregar antes de las 18:00",
  "tipo_cliente": "cliente",
  "estado": "pendiente",
  "prioridad": "normal"
}
```

## 🎯 Características Especiales

### Prioridad Automática
- **Comerciantes**: Prioridad alta automáticamente
- **Clientes normales**: Prioridad normal
- **Información comercial**: Se incluye en indicaciones

### Asignación Automática de Repartidores
- Sistema inteligente que evita sobrecargar repartidores
- Prioriza repartidores sin tickets de prioridad alta
- Asignación aleatoria si todos están ocupados

### Logs Detallados
- Registro completo de tickets enviados
- Información de cliente y productos
- Estado de la integración

## 🔍 Verificación de la Integración

### Test Automático
```bash
python test_integracion_completa.py
```

### Test Manual
```bash
python integracion_belgrano_tickets.py
```

### Verificación en Logs
- ✅ "Ticket enviado a Belgrano Tickets: PED-001"
- ⚠️ "Belgrano Tickets no está disponible"
- ❌ "Error en integración con Belgrano Tickets"

## 🛠️ Archivos de Integración

### Belgrano Ahorro
- `integracion_belgrano_tickets.py` - Cliente API
- `app.py` (línea ~1100) - Integración en procesar_pago
- `iniciar_sistema_completo.py` - Script de inicio

### Belgrano Tickets
- `app.py` - Servidor principal
- `/api/tickets/recibir` - Endpoint de recepción
- `/health` - Health check para verificación

## 🔐 Credenciales de Acceso

### Belgrano Tickets
**👨‍💼 Administrador:**
- Email: `admin@belgranoahorro.com`
- Password: `admin123`

**🚚 Flota:**
- Email: `repartidor1@belgranoahorro.com`
- Password: `flota123`

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

### Problemas de credenciales
1. Ejecutar `python verificar_sistema.py` en belgrano_tickets
2. Usar ruta de reparación: `/debug/reparar_credenciales`
3. Verificar que las credenciales sean correctas

## 📊 Monitoreo

### Logs a Revisar
- **Belgrano Ahorro**: Consola de la aplicación
- **Belgrano Tickets**: Consola de la aplicación

### Métricas Importantes
- Tickets enviados exitosamente
- Errores de conexión
- Tiempo de respuesta de la API
- Estado de los servicios

## 🔄 Flujo de Trabajo Completo

1. **Usuario accede a Belgrano Ahorro**
   - Navega por productos
   - Agrega al carrito
   - Completa checkout

2. **Sistema procesa pedido**
   - Valida datos
   - Guarda en BD
   - Prepara ticket

3. **Integración automática**
   - Envía a Belgrano Tickets
   - Crea ticket automáticamente
   - Asigna repartidor

4. **Gestión en Belgrano Tickets**
   - Admin ve ticket
   - Puede modificar asignación
   - Flota actualiza estado

5. **Seguimiento**
   - Estados actualizados en tiempo real
   - Notificaciones automáticas
   - Reportes disponibles

## 🎉 Beneficios de la Integración

- ✅ **Automatización completa**: No requiere intervención manual
- ✅ **Tiempo real**: Actualizaciones instantáneas
- ✅ **Priorización inteligente**: Comerciantes tienen prioridad
- ✅ **Gestión centralizada**: Todo en un solo lugar
- ✅ **Escalabilidad**: Fácil agregar más funcionalidades
- ✅ **Monitoreo**: Logs detallados para debugging

---

**Estado**: ✅ Integración Completa y Funcional
**Última actualización**: 19/01/2025
**Versión**: 2.0.0
