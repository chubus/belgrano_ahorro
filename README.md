# 🎫 Belgrano Tickets - Sistema de Gestión de Pedidos

## 📋 Descripción

Sistema independiente para la gestión de tickets de pedidos recibidos desde Belgrano Ahorro vía API HTTP.

## 🏗️ Arquitectura

- **Framework**: Flask
- **Base de Datos**: SQLite
- **Autenticación**: Flask-Login
- **Deploy**: Render.com
- **API**: RESTful

## 🚀 Deploy

### **Render.com**
1. Conectar repositorio a Render.com
2. Configuración automática desde `render_tickets.yaml`
3. URL: `https://belgrano-tickets.onrender.com`

### **Local**
```bash
pip install -r requirements_tickets.txt
python app_tickets.py
```

## 📡 API Endpoints

### **POST /api/tickets**
Recibe tickets desde Belgrano Ahorro

**Datos esperados:**
```json
{
  "cliente": "Juan Pérez",
  "productos": ["Arroz", "Aceite"],
  "total": 3500,
  "numero_pedido": "PED-20241201-ABC123",
  "direccion": "Av. Belgrano 123",
  "telefono": "1234567890",
  "email": "juan@email.com",
  "metodo_pago": "efectivo",
  "notas": "Entregar antes de las 18:00"
}
```

**Respuestas:**
- `201 Created`: `{"msg": "ticket registrado", "ticket_id": 123}`
- `400 Bad Request`: `{"error": "Campo requerido: cliente"}`

### **GET /api/tickets** (Admin)
Obtiene todos los tickets (requiere autenticación admin)

### **GET /health**
Health check para Render.com

## 🔐 Credenciales

- **Admin**: `admin@belgranoahorro.com` / `admin123`
- **Flota**: `repartidor1@belgranoahorro.com` / `flota123`

## 📱 URLs

- **Login**: `/login`
- **Panel de Tickets**: `/tickets`
- **API**: `/api/tickets`
- **Health Check**: `/health`

## 🔄 Flujo de Integración

```
Belgrano Ahorro → POST /api/tickets → Belgrano Tickets → Panel Web
```

## 🛠️ Características

- ✅ Recepción automática de tickets vía API
- ✅ Panel web para visualización
- ✅ Autenticación y autorización
- ✅ Base de datos SQLite
- ✅ Health checks
- ✅ Logs detallados
- ✅ Validación de datos
- ✅ Manejo de errores

## 📊 Estructura del Proyecto

```
belgrano-tickets/
├── app_tickets.py              # Aplicación principal
├── requirements_tickets.txt     # Dependencias
├── render_tickets.yaml         # Configuración Render
├── templates_tickets/          # Plantillas HTML
│   ├── login.html
│   └── tickets.html
└── README.md                   # Este archivo
```

## 🎯 Estado del Sistema

- **Versión**: 1.0.0
- **Estado**: Listo para producción
- **Integración**: API HTTP con Belgrano Ahorro

# devops
