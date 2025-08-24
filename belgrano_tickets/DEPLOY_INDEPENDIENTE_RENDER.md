# 🚀 Deploy Independiente de Belgrano Tickets en Render

## 📋 Estrategia de Deploy Independiente

### **Arquitectura Propuesta**

```
┌─────────────────────────────────┐
│ Belgrano Ahorro                 │
│ https://belgrano-ahorro.onrender.com │
│ Puerto: 5000                    │
└─────────────────┬───────────────┘
                  │
                  │ API Calls
                  │
┌─────────────────▼───────────────┐
│ Belgrano Tickets                │
│ https://belgrano-ticketera.onrender.com │
│ Puerto: 5001                    │
└─────────────────────────────────┘
```

## 🎯 Ventajas del Deploy Independiente

### **✅ Beneficios**
- **Escalabilidad independiente**: Cada servicio puede escalar según sus necesidades
- **Mantenimiento separado**: Actualizaciones independientes
- **Monitoreo específico**: Métricas separadas para cada servicio
- **Recursos optimizados**: Cada servicio usa solo lo que necesita
- **Desarrollo paralelo**: Equipos pueden trabajar independientemente

### **🔗 Conexión entre Servicios**
- **API REST**: Comunicación HTTP entre servicios
- **Bases de datos compartidas**: Acceso a datos comunes
- **Autenticación centralizada**: Sistema de usuarios compartido

## 🚀 Configuración para Render

### **Opción 1: Repositorio Separado (Recomendado)**

#### **Estructura del Repositorio**
```
belgrano-ticketera/
├── app.py
├── models.py
├── requirements_ticketera.txt
├── render.yaml
├── README.md
└── templates/
    └── ...
```

#### **Configuración de Render**
1. **Crear nuevo repositorio** en GitHub: `belgrano-ticketera`
2. **Conectar a Render** como nuevo Web Service
3. **Configurar variables de entorno** para conexión

### **Opción 2: Subcarpeta en Repositorio Principal**

#### **Estructura Actual**
```
belgrano_ahorro-back/
├── app.py (Belgrano Ahorro)
├── belgrano_tickets/
│   ├── app.py (Belgrano Tickets)
│   ├── render_ticketera.yaml
│   └── requirements_ticketera.txt
└── ...
```

#### **Configuración de Render**
- Usar `render_ticketera.yaml` existente
- Configurar como servicio independiente

## 🔧 Configuración Técnica

### **Variables de Entorno para Conexión**

```yaml
envVars:
  - key: BELGRANO_AHORRO_URL
    value: https://belgrano-ahorro.onrender.com
  - key: BELGRANO_AHORRO_API_KEY
    value: tu_api_key_secreta
  - key: SHARED_DATABASE_URL
    value: sqlite:///shared_data.db
```

### **Configuración de API**

#### **En Belgrano Ahorro (Servicio Principal)**
```python
# Agregar endpoints para la ticketera
@app.route('/api/tickets/usuarios', methods=['GET'])
def get_usuarios():
    # Retornar lista de usuarios para la ticketera
    pass

@app.route('/api/tickets/productos', methods=['GET'])
def get_productos():
    # Retornar productos para la ticketera
    pass
```

#### **En Belgrano Tickets (Servicio Independiente)**
```python
import requests

# Configuración de conexión
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL')

def obtener_usuarios():
    response = requests.get(f"{BELGRANO_AHORRO_URL}/api/tickets/usuarios")
    return response.json()

def obtener_productos():
    response = requests.get(f"{BELGRANO_AHORRO_URL}/api/tickets/productos")
    return response.json()
```

## 📁 Archivos de Configuración

### **render.yaml para Servicio Independiente**

```yaml
services:
  - type: web
    name: belgrano-ticketera
    env: python
    plan: free
    buildCommand: pip install -r requirements_ticketera.txt
    startCommand: python app.py
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
        value: https://belgrano-ahorro.onrender.com
      - key: DATABASE_URL
        value: sqlite:///belgrano_tickets.db
    healthCheckPath: /
    autoDeploy: true
```

### **requirements_ticketera.txt**

```txt
Flask==3.1.1
Flask-SocketIO==5.3.6
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
requests==2.32.3
python-socketio==5.11.1
eventlet==0.35.2
```

## 🔗 Configuración de Conexión

### **Método 1: API REST (Recomendado)**

#### **Endpoints en Belgrano Ahorro**
```python
# app.py en Belgrano Ahorro
@app.route('/api/tickets/usuarios', methods=['GET'])
@login_required
def api_usuarios():
    usuarios = db.obtener_usuarios()
    return jsonify(usuarios)

@app.route('/api/tickets/productos', methods=['GET'])
def api_productos():
    productos = cargar_productos()
    return jsonify(productos)

@app.route('/api/tickets/verificar_usuario', methods=['POST'])
def api_verificar_usuario():
    data = request.get_json()
    usuario = db.verificar_usuario(data['email'], data['password'])
    return jsonify({'usuario': usuario})
```

#### **Cliente en Belgrano Tickets**
```python
# app.py en Belgrano Tickets
import requests

class BelgranoAhorroClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def obtener_usuarios(self):
        response = requests.get(f"{self.base_url}/api/tickets/usuarios")
        return response.json()
    
    def verificar_usuario(self, email, password):
        response = requests.post(f"{self.base_url}/api/tickets/verificar_usuario", 
                               json={'email': email, 'password': password})
        return response.json()

# Uso
client = BelgranoAhorroClient(os.environ.get('BELGRANO_AHORRO_URL'))
```

### **Método 2: Base de Datos Compartida**

```python
# Configuración de BD compartida
SHARED_DB_URL = os.environ.get('SHARED_DATABASE_URL', 'sqlite:///shared_data.db')

# En ambos servicios
from sqlalchemy import create_engine
engine = create_engine(SHARED_DB_URL)
```

## 🚀 Pasos para Deploy

### **Opción 1: Repositorio Separado**

1. **Crear repositorio separado**:
   ```bash
   git clone https://github.com/tu-usuario/belgrano-ticketera.git
   cd belgrano-ticketera
   ```

2. **Copiar archivos de la ticketera**:
   ```bash
   cp -r ../belgrano_ahorro-back/belgrano_tickets/* .
   ```

3. **Configurar Render**:
   - Crear nuevo Web Service
   - Conectar repositorio
   - Configurar variables de entorno

### **Opción 2: Subcarpeta Actual**

1. **Usar configuración existente**:
   ```bash
   # El archivo render_ticketera.yaml ya está configurado
   ```

2. **Deploy en Render**:
   - Crear nuevo Web Service
   - Usar `render_ticketera.yaml`
   - Configurar variables de entorno

## 🔍 Verificación de Conexión

### **Test de Conectividad**

```python
# Script de prueba
import requests
import os

def test_conexion():
    url = os.environ.get('BELGRANO_AHORRO_URL')
    try:
        response = requests.get(f"{url}/api/tickets/productos")
        if response.status_code == 200:
            print("✅ Conexión exitosa con Belgrano Ahorro")
            return True
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
```

### **Health Check**

```python
@app.route('/health')
def health_check():
    # Verificar conexión con Belgrano Ahorro
    try:
        response = requests.get(f"{BELGRANO_AHORRO_URL}/api/tickets/productos")
        belgrano_status = "connected" if response.status_code == 200 else "disconnected"
    except:
        belgrano_status = "error"
    
    return jsonify({
        'status': 'healthy',
        'belgrano_ahorro': belgrano_status,
        'timestamp': datetime.now().isoformat()
    })
```

## 📊 Monitoreo y Logs

### **Variables de Entorno para Monitoreo**

```yaml
envVars:
  - key: LOG_LEVEL
    value: INFO
  - key: ENABLE_METRICS
    value: true
  - key: BELGRANO_AHORRO_TIMEOUT
    value: 30
```

### **Logs de Conexión**

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_conexion(service, status, details=None):
    logger.info(f"🔗 Conexión {service}: {status}")
    if details:
        logger.info(f"   Detalles: {details}")
```

## ✅ Estado Final

### **Servicios Independientes**
- ✅ **Belgrano Ahorro**: https://belgrano-ahorro.onrender.com
- ✅ **Belgrano Tickets**: https://belgrano-ticketera.onrender.com
- ✅ **Conexión API**: Configurada y funcional
- ✅ **Monitoreo**: Separado para cada servicio

### **Beneficios Logrados**
- 🚀 **Deploy independiente**: Cada servicio se despliega por separado
- 🔗 **Conexión mantenida**: Comunicación API entre servicios
- 📊 **Monitoreo separado**: Métricas independientes
- 🔧 **Mantenimiento independiente**: Actualizaciones separadas

**La ticketera puede funcionar completamente independiente y conectada a Belgrano Ahorro.**
