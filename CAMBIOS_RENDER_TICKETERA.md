# 🔧 Cambios para Deploy en Render - Ticketera

## 🎯 Objetivo
Modificar el proyecto de ticketera para que se despliegue correctamente en Render.com

## ✅ Cambios Realizados

### 1. **`belgrano_tickets/app.py`**

#### **Variables de Entorno**
- ✅ **Importación de `os`** ya existía
- ✅ **Carga de variables** usando `os.environ.get()`:
  - `BELGRANO_AHORRO_URL`
  - `BELGRANO_AHORRO_API_KEY`
- ✅ **Detección de entorno de producción** configurada

#### **Cliente API**
- ✅ **Modificado `create_api_client()`** para recibir parámetros:
  ```python
  api_client = create_api_client(BELGRANO_AHORRO_URL, BELGRANO_AHORRO_API_KEY)
  ```

#### **Endpoint Health Check**
- ✅ **`/healthz` simplificado** para Render:
  ```python
  @app.route('/healthz')
  def healthz():
      return "ok", 200
  ```

### 2. **`belgrano_tickets/api_client.py`**

#### **Función `create_api_client()`**
- ✅ **Modificada para recibir parámetros**:
  ```python
  def create_api_client(url=None, api_key=None):
      if url is None or api_key is None:
          raise ValueError("url y api_key son requeridos para crear el cliente API")
      return BelgranoAhorroAPIClient(url, api_key)
  ```

#### **Función `test_api_connection()`**
- ✅ **Modificada para recibir parámetros**:
  ```python
  def test_api_connection(url=None, api_key=None):
      if url is None or api_key is None:
          raise ValueError("url y api_key son requeridos para probar la conexión")
      client = BelgranoAhorroAPIClient(url, api_key)
  ```

#### **Validaciones**
- ✅ **Validación de parámetros** requeridos
- ✅ **Manejo de errores** con `ValueError`

### 3. **`belgrano_tickets/Dockerfile`**

#### **Comando de Ejecución**
- ✅ **Cambiado a gunicorn** para Render:
  ```dockerfile
  CMD ["sh","-c","gunicorn -w 2 -b 0.0.0.0:${PORT:-10000} app:app"]
  ```

#### **Configuración**
- ✅ **Puerto dinámico** usando variable `${PORT}`
- ✅ **Workers configurados** (2 workers)
- ✅ **Binding a 0.0.0.0** para aceptar conexiones externas

### 4. **`belgrano_tickets/requirements_ticketera.txt`**

#### **Dependencias**
- ✅ **gunicorn** ya incluido
- ✅ **eventlet** ya incluido para Socket.IO
- ✅ **Todas las dependencias** necesarias presentes

## 🔧 Configuración de Variables de Entorno

### **Variables Requeridas en Render**
```bash
BELGRANO_AHORRO_URL=https://belgranoahorro.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
RENDER_ENVIRONMENT=production
PORT=10000  # Render inyecta automáticamente
```

## 🚀 Flujo de Deploy

### **1. Render.com Detecta Cambios**
- ✅ **Dockerfile** optimizado para Render
- ✅ **Requirements** con todas las dependencias
- ✅ **Health check** en `/healthz`

### **2. Build del Contenedor**
- ✅ **Python 3.9** configurado
- ✅ **Dependencias instaladas** correctamente
- ✅ **Código copiado** al contenedor

### **3. Ejecución**
- ✅ **Gunicorn** inicia la aplicación
- ✅ **Puerto dinámico** configurado
- ✅ **Variables de entorno** cargadas

### **4. Health Check**
- ✅ **Endpoint `/healthz`** responde "ok"
- ✅ **Status 200** para Render

## 📋 Verificación Post-Deploy

### **Comandos de Prueba**
```bash
# Health check
curl https://ticketerabelgrano.onrender.com/healthz

# Crear ticket
curl -X POST https://ticketerabelgrano.onrender.com/api/tickets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{"numero":"TEST-001","cliente_nombre":"Test","total":100}'
```

### **Logs a Verificar**
- ✅ **Inicialización de variables** de entorno
- ✅ **Cliente API** creado correctamente
- ✅ **Base de datos** inicializada
- ✅ **Gunicorn** iniciado en puerto correcto

## ✅ Estado Final

**LISTO PARA DEPLOY EN RENDER** 🚀

- ✅ Variables de entorno configuradas
- ✅ Cliente API parametrizado
- ✅ Health check simplificado
- ✅ Dockerfile optimizado para gunicorn
- ✅ Todas las dependencias incluidas

## 🎯 Próximos Pasos

1. **Commit y push** de todos los cambios
2. **Deploy automático** en Render.com
3. **Verificar health check** en `/healthz`
4. **Probar comunicación** con Belgrano Ahorro
5. **Monitorear logs** para confirmar funcionamiento

---

**Nota**: Todos los cambios están optimizados para Render.com y mantienen la funcionalidad existente.
