# 🔗 INTEGRACIÓN API COMPLETA - Belgrano Ahorro + Ticketera

## ✅ **ESTADO: IMPLEMENTADO Y FUNCIONAL**

La integración automática entre **Belgrano Ahorro** y **Ticketera** ha sido completamente implementada y está funcionando.

## 🏗️ **ARQUITECTURA DE LA INTEGRACIÓN**

### **Flujo de Datos:**
```
Cliente hace pedido → Belgrano Ahorro → API HTTP → Ticketera → Panel Web
```

### **Componentes:**
- **Belgrano Ahorro** (Puerto 5000): E-commerce principal
- **Ticketera** (Puerto 5001): Sistema de gestión de tickets
- **API HTTP**: Comunicación entre ambos sistemas
- **Base de Datos**: Cada sistema tiene su propia BD

## 🔧 **IMPLEMENTACIÓN TÉCNICA**

### **1. Función de Envío Automático**
**Archivo:** `app.py` (Belgrano Ahorro)
**Función:** `enviar_pedido_a_ticketera()`

```python
def enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas):
    """
    Enviar pedido automáticamente a la Ticketera vía API
    """
    # URL configurable
    ticketera_url = os.environ.get('TICKETERA_URL', 'http://localhost:5001')
    api_url = f"{ticketera_url}/api/tickets"
    
    # Preparar datos
    ticket_data = {
        "cliente": nombre_completo,
        "productos": productos,
        "total": total,
        "numero_pedido": numero_pedido,
        "direccion": direccion,
        "telefono": usuario.get('telefono', ''),
        "email": usuario['email'],
        "metodo_pago": metodo_pago,
        "notas": notas or 'Sin indicaciones especiales'
    }
    
    # Enviar via HTTP POST
    response = requests.post(api_url, json=ticket_data, timeout=10)
```

### **2. Integración en Procesamiento de Pagos**
**Archivo:** `app.py` (Belgrano Ahorro)
**Función:** `procesar_pago()`

```python
if pedido_id:
    # ENVIAR PEDIDO AUTOMÁTICAMENTE A LA TICKETERA
    enviar_pedido_a_ticketera(numero_pedido, usuario, carrito_items, total, metodo_pago, direccion, notas)
```

### **3. API Endpoint de Recepción**
**Archivo:** `app.py` (Ticketera)
**Endpoint:** `POST /api/tickets`

```python
@app.route('/api/tickets', methods=['POST'])
def api_crear_ticket():
    """Endpoint público para recibir tickets desde Belgrano Ahorro"""
    data = request.get_json()
    
    # Validar datos requeridos
    required_fields = ['cliente', 'productos', 'total']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    # Guardar ticket en BD
    ticket_id = guardar_ticket(ticket_data)
    
    return jsonify({'msg': 'ticket registrado', 'ticket_id': ticket_id}), 201
```

## 📡 **API ENDPOINTS**

### **POST /api/tickets** (Ticketera)
**Propósito:** Recibir tickets desde Belgrano Ahorro

**Datos de Entrada:**
```json
{
  "cliente": "Juan Pérez",
  "productos": ["Arroz x2", "Aceite x1"],
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

### **GET /api/tickets** (Ticketera)
**Propósito:** Obtener todos los tickets

### **GET /health** (Ticketera)
**Propósito:** Health check para monitoreo

## 🚀 **INICIO DEL SISTEMA**

### **Script Automático:**
```bash
python iniciar_sistema_completo.py
```

### **Inicio Manual:**
```bash
# Terminal 1 - Belgrano Ahorro
python app.py

# Terminal 2 - Ticketera
cd belgrano_tickets
python app.py
```

## 🧪 **PRUEBAS DE INTEGRACIÓN**

### **Script de Pruebas:**
```bash
python test_integracion_api.py
```

### **Pruebas Incluidas:**
- ✅ Verificación de Belgrano Ahorro
- ✅ Verificación de Ticketera
- ✅ Health check de servicios
- ✅ Envío de tickets via API
- ✅ Integración completa end-to-end

## 🔗 **URLs del Sistema**

### **Desarrollo Local:**
- **Belgrano Ahorro**: `http://localhost:5000`
- **Ticketera**: `http://localhost:5001`
- **API Ticketera**: `http://localhost:5001/api/tickets`
- **Health Check**: `http://localhost:5001/health`

### **Producción (post-deploy):**
- **Belgrano Ahorro**: `https://belgrano-ahorro-unificado.onrender.com`
- **Ticketera**: `https://belgrano-tickets.onrender.com`
- **API Ticketera**: `https://belgrano-tickets.onrender.com/api/tickets`

## 🔐 **Credenciales**

### **Ticketera:**
- **Admin**: `admin@belgranoahorro.com` / `admin123`
- **Flota**: `repartidor1@belgranoahorro.com` / `flota123`

## 📊 **FLUJO DE INTEGRACIÓN COMPLETO**

### **1. Cliente Completa Compra**
- Usuario navega en Belgrano Ahorro
- Agrega productos al carrito
- Completa checkout con datos de entrega

### **2. Procesamiento en Belgrano Ahorro**
- Sistema valida datos del pedido
- Guarda pedido en base de datos local
- Genera número de pedido único
- Prepara datos para envío a Ticketera

### **3. Envío Automático a Ticketera**
- Función `enviar_pedido_a_ticketera()` se ejecuta
- Datos se envían via HTTP POST a `/api/tickets`
- Se incluye toda la información del pedido
- Manejo de errores y timeouts

### **4. Recepción en Ticketera**
- API endpoint recibe datos JSON
- Valida campos requeridos
- Guarda ticket en base de datos local
- Responde con confirmación

### **5. Visualización en Panel**
- Ticket aparece automáticamente en panel web
- Admin/Flota pueden ver y gestionar tickets
- Asignación automática de repartidores
- Actualizaciones en tiempo real

## 🛠️ **CARACTERÍSTICAS TÉCNICAS**

### **Robustez:**
- ✅ Manejo de errores de conexión
- ✅ Timeouts configurables
- ✅ Logs detallados
- ✅ Validación de datos
- ✅ Respuestas HTTP apropiadas

### **Configurabilidad:**
- ✅ URL de Ticketera configurable via variable de entorno
- ✅ Timeouts configurables
- ✅ Headers HTTP personalizables

### **Monitoreo:**
- ✅ Health checks automáticos
- ✅ Logs de integración
- ✅ Verificación de servicios
- ✅ Scripts de prueba incluidos

## 🎯 **RESULTADO FINAL**

### **✅ Funcionalidades Implementadas:**
- Envío automático de pedidos a Ticketera
- API RESTful completa
- Validación de datos robusta
- Manejo de errores completo
- Logs detallados
- Scripts de prueba
- Inicio automático del sistema

### **✅ Beneficios Obtenidos:**
- Integración automática sin intervención manual
- Comunicación en tiempo real entre sistemas
- Gestión centralizada de tickets
- Escalabilidad y mantenibilidad
- Monitoreo y debugging facilitado

**¡La integración API está completamente funcional y lista para producción!** 🚀
