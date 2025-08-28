# 🔧 Variables de Entorno - Belgrano Ahorro

## 🎯 Objetivo
Configurar las variables de entorno necesarias para que Belgrano Ahorro se comunique automáticamente con la Ticketera en cada compra.

## 📋 Variables Requeridas

### **1. TICKETERA_URL** 🔗
**Propósito**: URL de la Ticketera para enviar pedidos automáticamente

#### **Valor de Producción (Render.com)**
```bash
TICKETERA_URL=https://ticketerabelgrano.onrender.com
```

#### **Valor de Desarrollo (Local)**
```bash
TICKETERA_URL=http://localhost:5001
```

#### **Ubicación en el código**
```python
# app.py línea 75-80
TICKETERA_URL = os.environ.get('TICKETERA_URL', 'http://localhost:5001')

# URLs de producción (Render.com)
if os.environ.get('RENDER_ENVIRONMENT') == 'production':
    TICKETERA_URL = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com')
```

### **2. BELGRANO_AHORRO_API_KEY** 🔑
**Propósito**: Clave de autenticación para la API de la Ticketera

#### **Valor**
```bash
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
```

#### **Ubicación en el código**
```python
# app.py línea 76-81
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

# URLs de producción (Render.com)
if os.environ.get('RENDER_ENVIRONMENT') == 'production':
    BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
```

### **3. RENDER_ENVIRONMENT** 🌍
**Propósito**: Indicar que estamos en producción

#### **Valor**
```bash
RENDER_ENVIRONMENT=production
```

## 🔄 Flujo de Comunicación

### **Cuando un usuario hace una compra:**

1. **Usuario completa compra** en Belgrano Ahorro
2. **Sistema valida** la información del pedido
3. **Función `enviar_pedido_a_ticketera()`** se ejecuta automáticamente
4. **Request POST** se envía a `{TICKETERA_URL}/api/tickets`
5. **Headers incluyen** `X-API-Key: {BELGRANO_AHORRO_API_KEY}`
6. **Ticketera recibe** el pedido y crea el ticket
7. **Respuesta** confirma la creación del ticket
8. **Belgrano Ahorro actualiza** su base de datos con la confirmación

### **Código que maneja la comunicación:**
```python
# app.py líneas 1630-1720
def enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas):
    api_url = f"{TICKETERA_URL}/api/tickets"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': BELGRANO_AHORRO_API_KEY,
        'User-Agent': 'BelgranoAhorro/1.0.0'
    }
    
    # Enviar request POST con reintentos
    response = requests.post(api_url, json=ticket_data, headers=headers, timeout=15)
```

## 🚀 Configuración en Render.com

### **Archivo `render_ahorro.yaml`**
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
      - key: BELGRANO_AHORRO_API_KEY
        value: belgrano_ahorro_api_key_2025
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /healthz
    autoDeploy: true
```

### **Variables en el Dashboard de Render**
1. Ir a **Dashboard de Render.com**
2. Seleccionar **belgrano-ahorro**
3. Ir a **Environment**
4. Configurar las variables:

| Key | Value |
|-----|-------|
| `TICKETERA_URL` | `https://ticketerabelgrano.onrender.com` |
| `BELGRANO_AHORRO_API_KEY` | `belgrano_ahorro_api_key_2025` |
| `RENDER_ENVIRONMENT` | `production` |

## 🔍 Verificación

### **Logs esperados al hacer una compra:**
```
🔗 Configuración API:
   TICKETERA_URL: https://ticketerabelgrano.onrender.com
   API_KEY: belgrano_a...

📤 Enviando datos a Ticketera:
   URL: https://ticketerabelgrano.onrender.com/api/tickets
   Datos: {
     "numero": "PED-001",
     "cliente_nombre": "Juan Pérez",
     "total": 1500,
     ...
   }

🔄 Intento 1/3 enviando a https://ticketerabelgrano.onrender.com/api/tickets
✅ Petición exitosa en intento 1
✅ Pedido enviado exitosamente a Ticketera: PED-001
```

### **Comando de prueba:**
```bash
# Verificar que las variables están configuradas
curl -X GET https://belgranoahorro-hp30.onrender.com/healthz

# Verificar que la comunicación funciona
curl -X POST https://ticketerabelgrano.onrender.com/api/tickets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{"numero":"TEST-001","cliente_nombre":"Test","total":100}'
```

## ⚠️ Consideraciones Importantes

### **Seguridad**
- ✅ **API Key** es la misma en ambos servicios
- ✅ **HTTPS** obligatorio en producción
- ✅ **Timeout** configurado (15 segundos)
- ✅ **Reintentos** automáticos (3 intentos)

### **Manejo de Errores**
- ✅ **Backoff exponencial** entre reintentos
- ✅ **Logs detallados** de cada intento
- ✅ **Rollback** si falla la comunicación
- ✅ **Notificación** al usuario si hay problemas

### **Rendimiento**
- ✅ **Timeout** configurado para evitar bloqueos
- ✅ **Headers optimizados** para la comunicación
- ✅ **JSON eficiente** en el payload
- ✅ **Conexiones reutilizadas** con requests.Session()

## 📝 Resumen de Configuración

### **Variables Clave:**
```bash
# Producción (Render.com)
TICKETERA_URL=https://ticketerabelgrano.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
RENDER_ENVIRONMENT=production

# Desarrollo (Local)
TICKETERA_URL=http://localhost:5001
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
RENDER_ENVIRONMENT=development
```

### **Estado:**
- ✅ **Variables configuradas** en render_ahorro.yaml
- ✅ **Código preparado** para usar las variables
- ✅ **Comunicación automática** en cada compra
- ✅ **Manejo de errores** robusto
- ✅ **Logs detallados** para debugging

---

**🎯 Resultado**: Cada compra en Belgrano Ahorro se enviará automáticamente a la Ticketera sin intervención manual.
