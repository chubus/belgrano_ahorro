# 🚀 Configuración Final de Comunicación entre Aplicaciones

## 🎯 Objetivo
Establecer una comunicación sólida y confiable entre Belgrano Ahorro y la Ticketera, asegurando que ambas aplicaciones operen en puertos diferentes y se comuniquen correctamente.

## 📋 Configuración de Puertos

### **Belgrano Ahorro**
```
🌐 URL: https://belgranoahorro-hp30.onrender.com
🔗 Puerto: 10000 (Render.com asigna automáticamente)
🔗 Health Check: /healthz
```

### **Ticketera**
```
🎫 URL: https://ticketerabelgrano.onrender.com
🔗 Puerto: 10000 (Render.com asigna automáticamente)
🔗 Health Check: /healthz
```

## 🔧 Variables de Entorno Configuradas

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
        value: 10000
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

## 🧪 Scripts de Verificación

### **1. Diagnóstico Completo**
```bash
python diagnostico_comunicacion_completo.py
```

### **2. Test de Corrección**
```bash
python test_correccion_comunicacion.py
```

### **3. Test Rápido**
```bash
python test_endpoint_rapido.py
```

### **4. Test de Comunicación Automática**
```bash
python test_comunicacion_automatica.py
```

## 🔑 Comandos de Prueba Manual

### **Verificar Health Checks**
```bash
# Belgrano Ahorro
curl -X GET https://belgranoahorro-hp30.onrender.com/healthz

# Ticketera
curl -X GET https://ticketerabelgrano.onrender.com/healthz
```

### **Crear Ticket de Prueba**
```bash
curl -X POST https://ticketerabelgrano.onrender.com/api/tickets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "numero": "TEST-001",
    "cliente_nombre": "Cliente Test",
    "cliente_direccion": "Dirección Test 123",
    "cliente_telefono": "1234567890",
    "cliente_email": "test@example.com",
    "productos": ["Arroz 1kg x2", "Aceite 900ml x1"],
    "total": 1500.00,
    "metodo_pago": "efectivo",
    "indicaciones": "Test de comunicación",
    "estado": "pendiente",
    "prioridad": "normal",
    "tipo_cliente": "cliente"
  }'
```

### **Confirmar Ticket**
```bash
curl -X POST https://belgranoahorro-hp30.onrender.com/api/pedido/confirmar/TEST-001 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "ticket_id": "TICKET-TEST-001",
    "estado": "confirmado"
  }'
```

## ✅ Correcciones Implementadas

### **1. Función `get_db_connection` Agregada**
```python
# app.py - Agregada función faltante
def get_db_connection():
    """Obtener conexión a la base de datos"""
    import sqlite3
    conn = sqlite3.connect('belgrano_ahorro.db')
    conn.row_factory = sqlite3.Row
    return conn
```

### **2. Modelo Ticket Corregido**
```python
# belgrano_tickets/models.py - Campo total agregado
class Ticket(db.Model):
    # ... campos existentes ...
    total = db.Column(db.Float, nullable=False, default=0.0)  # ✅ AGREGADO
    # ... resto de campos ...
```

### **3. Script de Actualización de Base de Datos**
```python
# belgrano_tickets/actualizar_db.py - Nuevo script
def actualizar_base_datos():
    """Actualizar la base de datos para agregar el campo total"""
    # Verificar y agregar columna total si no existe
```

### **4. Script de Inicio Mejorado**
```bash
# belgrano_tickets/run.sh - Incluye actualización automática
init_database() {
    # Actualizar esquema de base de datos primero
    python3 actualizar_db.py
    # Continuar con inicialización normal...
}
```

## 📊 Estado Final de la Comunicación

### **✅ Funcionando Correctamente:**
- ✅ **Health checks** de ambas aplicaciones
- ✅ **Endpoint `/api/tickets`** de la Ticketera
- ✅ **Creación de tickets** desde Belgrano Ahorro
- ✅ **Validación de API keys**
- ✅ **Asignación automática** de repartidores
- ✅ **Base de datos** actualizada con campo `total`

### **✅ Flujo de Comunicación:**
- ✅ **Belgrano Ahorro → Ticketera**: Envío de tickets
- ✅ **Ticketera → Belgrano Ahorro**: Confirmación de tickets
- ✅ **Manejo de errores** robusto
- ✅ **Reintentos automáticos** con backoff exponencial
- ✅ **Logs detallados** para debugging

## 🎯 Resultado Final

**🎉 La comunicación entre ambas aplicaciones está completamente funcional:**

1. **Belgrano Ahorro** opera en `https://belgranoahorro-hp30.onrender.com`
2. **Ticketera** opera en `https://ticketerabelgrano.onrender.com`
3. **Cada compra** en Belgrano Ahorro se envía automáticamente a la Ticketera
4. **Los tickets** se crean y asignan automáticamente a repartidores
5. **Las confirmaciones** se procesan correctamente en ambas direcciones

---

**🚀 Las aplicaciones están listas para operar en producción con comunicación sólida y confiable!**
