# 🚀 SISTEMAS SEPARADOS - Belgrano Ahorro + Belgrano Tickets

## 📋 Descripción

Este sistema consta de **dos aplicaciones independientes** que se comunican vía API:

1. **Belgrano Ahorro** - E-commerce principal
2. **Belgrano Tickets** - Sistema de gestión de pedidos

## 🔗 Flujo de Integración

```
Cliente hace pedido → Belgrano Ahorro → API POST → Belgrano Tickets → Panel de control
```

## 🏗️ Arquitectura

### **Belgrano Ahorro** (`app_unificado.py`)
- **Puerto**: 5000
- **URL**: `https://belgrano-ahorro-unificado.onrender.com`
- **Función**: E-commerce con carrito, checkout y procesamiento de pagos
- **API**: Envía pedidos a Belgrano Tickets vía `POST /api/tickets`

### **Belgrano Tickets** (`app_tickets.py`)
- **Puerto**: 5001
- **URL**: `https://belgrano-tickets.onrender.com`
- **Función**: Recibe y gestiona tickets de pedidos
- **API**: `POST /api/tickets` (público)
- **Panel**: `/tickets` (requiere login)

## 🔧 Configuración

### **Belgrano Ahorro**
```bash
# Archivos principales
app_unificado.py          # Aplicación principal
requirements.txt          # Dependencias (incluye requests)
render.yaml              # Configuración Render.com
```

### **Belgrano Tickets**
```bash
# Archivos principales
app_tickets.py           # Aplicación de tickets
requirements_tickets.txt # Dependencias específicas
render_tickets.yaml      # Configuración Render.com
templates_tickets/       # Plantillas HTML
```

## 🚀 Deploy

### **Paso 1: Deploy Belgrano Ahorro**
```bash
# En el repositorio principal
git add .
git commit -m "Sistema de integración API implementado"
git push origin main
```

### **Paso 2: Deploy Belgrano Tickets**
```bash
# Crear nuevo repositorio para tickets
# Subir archivos de tickets
git init
git add app_tickets.py requirements_tickets.txt render_tickets.yaml templates_tickets/
git commit -m "Sistema de tickets independiente"
git push origin main
```

## 🔐 Credenciales

### **Belgrano Tickets**
- **Admin**: `admin@belgranoahorro.com` / `admin123`
- **Flota**: `repartidor1@belgranoahorro.com` / `flota123`

## 📡 API Endpoints

### **POST /api/tickets** (Belgrano Tickets)
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

## 🎯 URLs de Acceso

### **En Producción**
- **Belgrano Ahorro**: `https://belgrano-ahorro-unificado.onrender.com`
- **Belgrano Tickets**: `https://belgrano-tickets.onrender.com`
- **Panel Tickets**: `https://belgrano-tickets.onrender.com/tickets`

### **En Desarrollo Local**
- **Belgrano Ahorro**: `http://localhost:5000`
- **Belgrano Tickets**: `http://localhost:5001`
- **Panel Tickets**: `http://localhost:5001/tickets`

## 🔄 Flujo de Prueba

1. **Hacer pedido** en Belgrano Ahorro
2. **Confirmar pago** → Se envía automáticamente a Belgrano Tickets
3. **Verificar** en panel de tickets (`/tickets`)
4. **Login** con credenciales de admin

## 🛠️ Características Técnicas

### **Manejo de Errores**
- ✅ Timeout de 10 segundos en requests
- ✅ Logs detallados de errores
- ✅ Fallback si la API no está disponible
- ✅ Validación de datos en ambos extremos

### **Seguridad**
- ✅ Autenticación con Flask-Login
- ✅ Contraseñas hasheadas
- ✅ Control de acceso por roles
- ✅ Validación de datos JSON

### **Escalabilidad**
- ✅ Aplicaciones independientes
- ✅ Base de datos separada para tickets
- ✅ API RESTful
- ✅ Configuración para Render.com

## 📊 Monitoreo

### **Health Checks**
- **Belgrano Ahorro**: `/health`
- **Belgrano Tickets**: `/health`

### **Logs**
- ✅ Logs de envío de pedidos
- ✅ Logs de recepción de tickets
- ✅ Logs de errores de conexión
- ✅ Logs de autenticación

## 🎉 Resultado Final

**Dos sistemas independientes que se comunican vía API HTTP, permitiendo escalabilidad y mantenimiento independiente.**
