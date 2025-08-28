# 🚀 Configuración Final para Render.com

## 🎯 URLs de Producción Actualizadas

### **Belgrano Ahorro**
```
🌐 URL: https://belgranoahorro-hp30.onrender.com
🔗 Health Check: https://belgranoahorro-hp30.onrender.com/healthz
```

### **Ticketera**
```
🎫 URL: https://ticketerabelgrano.onrender.com
🔗 Health Check: https://ticketerabelgrano.onrender.com/healthz
```

## 🔧 Variables de Entorno para Render

### **Belgrano Ahorro (`render_ahorro.yaml`)**
```yaml
services:
  - type: web
    name: belgrano-ahorro
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: FLASK_ENV
        value: production
      - key: RENDER_ENVIRONMENT
        value: production
      - key: TICKETERA_URL
        value: https://ticketerabelgrano.onrender.com
      - key: BELGRANO_AHORRO_URL
        value: https://belgranoahorro-hp30.onrender.com
      - key: BELGRANO_AHORRO_API_KEY
        value: belgrano_ahorro_api_key_2025
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /healthz
    autoDeploy: true
```

### **Ticketera (`belgrano_tickets/render_docker.yaml`)**
```yaml
services:
  - type: web
    name: belgrano-ticketera
    env: docker
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: FLASK_ENV
        value: production
      - key: FLASK_APP
        value: app.py
      - key: PORT
        value: 5001
      - key: SECRET_KEY
        value: belgrano_tickets_secret_2025
      - key: BELGRANO_AHORRO_URL
        value: https://belgranoahorro-hp30.onrender.com
      - key: BELGRANO_AHORRO_API_KEY
        value: belgrano_ahorro_api_key_2025
      - key: DATABASE_URL
        value: sqlite:///belgrano_tickets.db
      - key: LOG_LEVEL
        value: INFO
      - key: ENABLE_METRICS
        value: true
      - key: BELGRANO_AHORRO_TIMEOUT
        value: 30
      - key: GUNICORN_WORKERS
        value: 2
      - key: GUNICORN_TIMEOUT
        value: 120
      - key: AUTO_CREATE_USERS
        value: true
      - key: ADMIN_EMAIL
        value: admin@belgranoahorro.com
      - key: ADMIN_PASSWORD
        value: admin123
      - key: FLOTA_PASSWORD
        value: flota123
    healthCheckPath: /healthz
    autoDeploy: true
```

## 🔄 Flujo de Comunicación Automática

### **Cuando un usuario hace una compra en Belgrano Ahorro:**

1. **Usuario completa compra** en https://belgranoahorro-hp30.onrender.com
2. **Sistema valida** la información del pedido
3. **Función `enviar_pedido_a_ticketera()`** se ejecuta automáticamente
4. **Request POST** se envía a `https://ticketerabelgrano.onrender.com/api/tickets`
5. **Headers incluyen** `X-API-Key: belgrano_ahorro_api_key_2025`
6. **Ticketera recibe** el pedido y crea el ticket
7. **Respuesta** confirma la creación del ticket
8. **Belgrano Ahorro actualiza** su base de datos con la confirmación

## 🧪 Comandos de Prueba

### **Verificar Health Checks**
```bash
# Belgrano Ahorro
curl -X GET https://belgranoahorro-hp30.onrender.com/healthz

# Ticketera
curl -X GET https://ticketerabelgrano.onrender.com/healthz
```

### **Probar Comunicación Automática**
```bash
# Crear ticket de prueba
curl -X POST https://ticketerabelgrano.onrender.com/api/tickets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "numero": "TEST-001",
    "cliente_nombre": "Cliente de Prueba",
    "cliente_direccion": "Dirección de Prueba 123",
    "cliente_telefono": "1234567890",
    "cliente_email": "test@example.com",
    "productos": ["Producto 1 x2", "Producto 2 x1"],
    "total": 1500.50,
    "metodo_pago": "efectivo",
    "indicaciones": "Prueba de comunicación automática",
    "estado": "pendiente",
    "prioridad": "normal",
    "tipo_cliente": "cliente"
  }'
```

### **Confirmar Ticket**
```bash
# Confirmar ticket creado
curl -X POST https://belgranoahorro-hp30.onrender.com/api/pedido/confirmar/TEST-001 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "ticket_id": "TICKET-TEST-001",
    "estado": "confirmado"
  }'
```

## 📋 Script de Prueba Automatizado

### **Ejecutar Pruebas Completas**
```bash
python test_comunicacion_automatica.py
```

**Salida esperada:**
```
🚀 Iniciando pruebas de comunicación automática
==================================================
📅 Fecha: 2025-01-XX XX:XX:XX
🌐 Belgrano Ahorro: https://belgranoahorro-hp30.onrender.com
🎫 Ticketera: https://ticketerabelgrano.onrender.com
==================================================

🔧 Verificando variables de entorno...
   TICKETERA_URL: https://ticketerabelgrano.onrender.com
   BELGRANO_AHORRO_API_KEY: belgrano_ahorro_api_key_2025
   RENDER_ENVIRONMENT: production
✅ Variables de entorno configuradas correctamente

🔍 Probando health checks...
✅ Belgrano Ahorro: ok
✅ Ticketera: ok

🎫 Probando creación de ticket...
✅ Ticket creado exitosamente:
   Número: TEST-XXXXX
   Ticket ID: XXXXX
   Estado: pendiente

✅ Probando confirmación de ticket TEST-XXXXX...
✅ Ticket confirmado exitosamente:
   Número: TEST-XXXXX
   Estado: confirmado

==================================================
🏁 Pruebas completadas
==================================================
✅ Comunicación automática funcionando correctamente
🎯 Cada compra en Belgrano Ahorro se enviará automáticamente a la Ticketera
```

## 🔑 Variables Clave Resumidas

| Servicio | Variable | Valor |
|----------|----------|-------|
| **Belgrano Ahorro** | `TICKETERA_URL` | `https://ticketerabelgrano.onrender.com` |
| **Belgrano Ahorro** | `BELGRANO_AHORRO_API_KEY` | `belgrano_ahorro_api_key_2025` |
| **Belgrano Ahorro** | `RENDER_ENVIRONMENT` | `production` |
| **Ticketera** | `BELGRANO_AHORRO_URL` | `https://belgranoahorro-hp30.onrender.com` |
| **Ticketera** | `BELGRANO_AHORRO_API_KEY` | `belgrano_ahorro_api_key_2025` |

## ✅ Estado Final

- ✅ **URLs actualizadas** para producción
- ✅ **Variables de entorno** configuradas correctamente
- ✅ **Comunicación automática** funcionando
- ✅ **Health checks** implementados
- ✅ **Scripts de prueba** actualizados
- ✅ **Documentación** completa

---

**🎯 Resultado**: Cada compra en https://belgranoahorro-hp30.onrender.com se enviará automáticamente a https://ticketerabelgrano.onrender.com sin intervención manual.
