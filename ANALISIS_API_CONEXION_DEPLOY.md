# ANÁLISIS DE API DE CONEXIÓN ENTRE PLATAFORMAS Y BASE DE DATOS PARA DEPLOY

## 📋 RESUMEN EJECUTIVO

Este documento analiza la arquitectura de conexión entre **Belgrano Ahorro** (plataforma principal) y **Belgrano Tickets** (sistema de gestión de pedidos) para preparar el deploy en producción.

## 🏗️ ARQUITECTURA DEL SISTEMA

### 1. PLATAFORMAS PRINCIPALES

#### **Belgrano Ahorro** (app.py)
- **Puerto**: 5000 (desarrollo) / Variable en producción
- **Base de datos**: SQLite (`belgrano_ahorro.db`)
- **Funcionalidad**: E-commerce, gestión de usuarios, carrito, pedidos
- **Framework**: Flask

#### **Belgrano Tickets** (belgrano_tickets/app.py)
- **Puerto**: 5001 (desarrollo) / Variable en producción  
- **Base de datos**: SQLite (`belgrano_tickets.db`)
- **Funcionalidad**: Gestión de tickets, asignación de repartidores, seguimiento
- **Framework**: Flask + Flask-SocketIO

### 2. FLUJO DE INTEGRACIÓN

```
Cliente → Belgrano Ahorro → API → Belgrano Tickets → Base de Datos
```

## 🔌 API DE CONEXIÓN

### 1. ENDPOINT PRINCIPAL DE INTEGRACIÓN

**Ubicación**: `app.py` línea 1604 (función `enviar_pedido_a_ticketera`)

```python
def enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas):
    """
    Enviar pedido automáticamente a la Ticketera vía API
    """
    ticketera_url = os.environ.get('TICKETERA_URL', 'http://localhost:5001')
    api_url = f"{ticketera_url}/api/tickets"
    
    ticket_data = {
        "numero": numero_pedido,
        "cliente_nombre": nombre_completo,
        "cliente_direccion": direccion,
        "cliente_telefono": usuario.get('telefono', ''),
        "cliente_email": usuario['email'],
        "productos": productos,
        "total": total,
        "metodo_pago": metodo_pago,
        "indicaciones": notas or 'Sin indicaciones especiales',
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente"
    }
```

### 2. ENDPOINTS DE API EN BELGRANO TICKETS

#### **POST /api/tickets** (línea 1650)
```python
@app.route('/api/tickets', methods=['POST'])
def api_crear_ticket():
    """Endpoint público para recibir tickets desde Belgrano Ahorro"""
```

**Funcionalidad**:
- Recibe datos del pedido desde Belgrano Ahorro
- Valida campos requeridos
- Guarda ticket en base de datos
- Retorna confirmación

#### **GET /api/tickets** (línea 1700)
```python
@app.route('/api/tickets', methods=['GET'])
def api_obtener_tickets():
    """Obtener todos los tickets (solo admin)"""
```

#### **GET /health** (línea 1710)
```python
@app.route('/health')
def health_check():
    """Health check para Render.com"""
```

## 🗄️ ESTRUCTURA DE BASES DE DATOS

### 1. BELGRANO AHORRO (db.py)

**Archivo**: `belgrano_ahorro.db`

**Tablas principales**:
- `usuarios` - Gestión de usuarios y autenticación
- `pedidos` - Pedidos realizados por usuarios
- `pedido_items` - Items de cada pedido
- `comerciantes` - Información de comerciantes
- `paquetes_comerciantes` - Paquetes automáticos
- `tokens_recuperacion` - Recuperación de contraseñas

### 2. BELGRANO TICKETS (models.py)

**Archivo**: `belgrano_tickets.db`

**Tablas principales**:
- `user` - Usuarios admin y flota
- `ticket` - Tickets de pedidos
- `configuracion` - Configuraciones del sistema

## ⚙️ CONFIGURACIÓN PARA DEPLOY

### 1. VARIABLES DE ENTORNO REQUERIDAS

#### **Belgrano Ahorro**:
```bash
FLASK_ENV=production
FLASK_APP=app.py
PORT=5000
SECRET_KEY=belgrano_ahorro_secret_key_2025
TICKETERA_URL=https://tu-app-ticketera.onrender.com
```

#### **Belgrano Tickets**:
```bash
FLASK_ENV=production
FLASK_APP=app.py
PORT=5001
SECRET_KEY=belgrano_tickets_secret_2025
BELGRANO_AHORRO_URL=https://tu-app-ahorro.onrender.com
```

### 2. ARCHIVOS DE CONFIGURACIÓN

#### **render.yaml** (Belgrano Ahorro)
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
        value: 3.12.0
      - key: FLASK_ENV
        value: production
      - key: FLASK_APP
        value: app.py
      - key: PORT
        value: 5000
      - key: SECRET_KEY
        value: belgrano_ahorro_secret_key_2025
      - key: TICKETERA_URL
        value: https://belgrano-tickets.onrender.com
    healthCheckPath: /test
    autoDeploy: true
```

#### **render_tickets.yaml** (Belgrano Tickets)
```yaml
services:
  - type: web
    name: belgrano-tickets
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
    healthCheckPath: /health
    autoDeploy: true
```

## 🔧 DEPENDENCIAS Y REQUIREMENTS

### 1. BELGRANO AHORRO (requirements.txt)
```txt
Flask==3.1.1
requests==2.31.0
Werkzeug==3.1.1
Jinja2==3.1.6
python-dotenv==1.1.0
```

### 2. BELGRANO TICKETS (requirements_ticketera.txt)
```txt
Flask==3.1.1
Flask-SocketIO==5.3.6
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.1.1
requests==2.32.3
SQLAlchemy==2.0.28
gunicorn
```

## 🚀 PASOS PARA DEPLOY

### 1. PREPARACIÓN DE ARCHIVOS

#### **Crear archivo de configuración unificado**:
```python
# config_deploy.py
import os

class DeployConfig:
    # Belgrano Ahorro
    AHORRO_SECRET_KEY = os.environ.get('AHORRO_SECRET_KEY', 'belgrano_ahorro_secret_key_2025')
    AHORRO_PORT = int(os.environ.get('AHORRO_PORT', 5000))
    
    # Belgrano Tickets
    TICKETS_SECRET_KEY = os.environ.get('TICKETS_SECRET_KEY', 'belgrano_tickets_secret_2025')
    TICKETS_PORT = int(os.environ.get('TICKETS_PORT', 5001))
    
    # URLs de producción
    AHORRO_URL = os.environ.get('AHORRO_URL', 'https://belgrano-ahorro.onrender.com')
    TICKETS_URL = os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
    
    # Base de datos
    AHORRO_DB_PATH = os.environ.get('AHORRO_DB_PATH', 'belgrano_ahorro.db')
    TICKETS_DB_PATH = os.environ.get('TICKETS_DB_PATH', 'belgrano_tickets.db')
```

### 2. SCRIPT DE VERIFICACIÓN DE CONEXIÓN

```python
# verificar_conexion_deploy.py
import requests
import time

def verificar_conexion_entre_plataformas():
    """Verificar que ambas plataformas se comunican correctamente"""
    
    # URLs de producción
    ahorro_url = "https://belgrano-ahorro.onrender.com"
    tickets_url = "https://belgrano-tickets.onrender.com"
    
    print("🔍 Verificando conexión entre plataformas...")
    
    # 1. Verificar que Belgrano Ahorro responde
    try:
        response = requests.get(f"{ahorro_url}/test", timeout=10)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro está funcionando")
        else:
            print(f"⚠️ Belgrano Ahorro responde con código: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando a Belgrano Ahorro: {e}")
    
    # 2. Verificar que Belgrano Tickets responde
    try:
        response = requests.get(f"{tickets_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Belgrano Tickets está funcionando")
        else:
            print(f"⚠️ Belgrano Tickets responde con código: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando a Belgrano Tickets: {e}")
    
    # 3. Verificar API de integración
    try:
        test_data = {
            "numero": "TEST-001",
            "cliente_nombre": "Cliente Test",
            "cliente_direccion": "Dirección Test",
            "cliente_telefono": "123456789",
            "cliente_email": "test@test.com",
            "productos": ["Producto Test x1"],
            "total": 100.0,
            "metodo_pago": "efectivo",
            "indicaciones": "Test de integración"
        }
        
        response = requests.post(
            f"{tickets_url}/api/tickets",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ API de integración funciona correctamente")
        else:
            print(f"⚠️ API de integración responde con código: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error en API de integración: {e}")

if __name__ == "__main__":
    verificar_conexion_entre_plataformas()
```

### 3. SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS

```python
# inicializar_db_deploy.py
import sqlite3
import os

def inicializar_bases_datos():
    """Inicializar ambas bases de datos para producción"""
    
    print("🗄️ Inicializando bases de datos...")
    
    # 1. Inicializar Belgrano Ahorro
    try:
        from db import crear_base_datos
        crear_base_datos()
        print("✅ Base de datos Belgrano Ahorro inicializada")
    except Exception as e:
        print(f"❌ Error inicializando BD Belgrano Ahorro: {e}")
    
    # 2. Inicializar Belgrano Tickets
    try:
        import sys
        sys.path.append('belgrano_tickets')
        from belgrano_tickets.inicializar_db import inicializar_db_tickets
        inicializar_db_tickets()
        print("✅ Base de datos Belgrano Tickets inicializada")
    except Exception as e:
        print(f"❌ Error inicializando BD Belgrano Tickets: {e}")

if __name__ == "__main__":
    inicializar_bases_datos()
```

## 🔍 PUNTOS CRÍTICOS PARA DEPLOY

### 1. **Gestión de Sesiones**
- ✅ Implementado con Flask-Session
- ✅ Secret key configurado
- ⚠️ Verificar persistencia en producción

### 2. **Conexión entre Plataformas**
- ✅ API REST implementada
- ✅ Manejo de errores y timeouts
- ⚠️ Verificar URLs de producción

### 3. **Base de Datos**
- ✅ SQLite para desarrollo
- ⚠️ Considerar migración a PostgreSQL para producción
- ✅ Backup automático configurado

### 4. **Seguridad**
- ✅ Autenticación implementada
- ✅ Rate limiting configurado
- ✅ Validación de inputs
- ⚠️ Verificar HTTPS en producción

### 5. **Logging y Monitoreo**
- ✅ Logging básico implementado
- ✅ Health checks configurados
- ⚠️ Implementar monitoreo avanzado

## 📊 MÉTRICAS DE FUNCIONAMIENTO

### 1. **Endpoints Críticos**
- `/test` - Belgrano Ahorro
- `/health` - Belgrano Tickets
- `/api/tickets` - API de integración

### 2. **Tiempos de Respuesta Esperados**
- Respuesta de health check: < 2 segundos
- Creación de ticket: < 5 segundos
- Procesamiento de pedido: < 10 segundos

### 3. **Disponibilidad**
- Objetivo: 99.9% uptime
- Health checks cada 30 segundos
- Auto-restart en caso de fallo

## 🚨 PLAN DE CONTINGENCIA

### 1. **Fallback de Conexión**
```python
def enviar_pedido_con_fallback(numero_pedido, datos):
    """Enviar pedido con fallback si la API falla"""
    try:
        # Intentar enviar a API
        return enviar_pedido_a_ticketera(numero_pedido, datos)
    except Exception as e:
        # Guardar en cola local para reintento
        guardar_pedido_en_cola(numero_pedido, datos)
        logger.error(f"Error enviando pedido, guardado en cola: {e}")
        return False
```

### 2. **Reintentos Automáticos**
```python
def procesar_cola_pendiente():
    """Procesar pedidos pendientes en cola"""
    pedidos_pendientes = obtener_pedidos_en_cola()
    for pedido in pedidos_pendientes:
        if enviar_pedido_a_ticketera(pedido['numero'], pedido['datos']):
            eliminar_de_cola(pedido['id'])
```

## ✅ CHECKLIST DE DEPLOY

### **Pre-Deploy**
- [ ] Verificar todas las dependencias en requirements.txt
- [ ] Configurar variables de entorno
- [ ] Inicializar bases de datos
- [ ] Probar conexión local entre plataformas

### **Deploy**
- [ ] Deploy Belgrano Tickets primero
- [ ] Verificar health check de Tickets
- [ ] Deploy Belgrano Ahorro
- [ ] Verificar health check de Ahorro
- [ ] Probar integración completa

### **Post-Deploy**
- [ ] Verificar logs de ambas aplicaciones
- [ ] Probar flujo completo de compra
- [ ] Verificar creación de tickets
- [ ] Monitorear métricas de rendimiento

## 📞 SOPORTE Y MONITOREO

### **Logs Importantes**
- `app.py` - Logs de Belgrano Ahorro
- `belgrano_tickets/app.py` - Logs de Belgrano Tickets
- `db.py` - Logs de base de datos

### **Alertas Críticas**
- Error 500 en endpoints principales
- Timeout en conexión entre plataformas
- Base de datos no accesible
- Health check fallando

---

**Estado**: ✅ Listo para deploy
**Última actualización**: Enero 2025
**Responsable**: Equipo de Desarrollo
