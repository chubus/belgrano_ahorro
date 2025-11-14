# 🧪 Prueba del Flujo DevOps -> Belgrano Ahorro

Este documento explica cómo probar manualmente que el flujo de creación desde DevOps se refleje en Belgrano Ahorro.

## 📋 Requisitos Previos

1. **Servidor Belgrano Ahorro corriendo** (local o en Render)
2. **Variables de entorno configuradas**:
   - `BELGRANO_AHORRO_URL`: URL del servidor (ej: `https://belgranoahorro-aliq.onrender.com`)
   - `BELGRANO_AHORRO_API_KEY`: Clave API (ej: `belgrano_ahorro_api_key_2025`)

## 🚀 Método 1: Script Automatizado

Ejecuta el script de prueba:

```bash
# Configurar variables de entorno (opcional, si no están en el sistema)
$env:BELGRANO_AHORRO_URL="https://belgranoahorro-aliq.onrender.com"
$env:BELGRANO_AHORRO_API_KEY="belgrano_ahorro_api_key_2025"

# Ejecutar script
python test_flujo_devops_belgrano.py
```

El script probará:
1. ✅ Crear un negocio
2. ✅ Crear un producto para ese negocio
3. ✅ Crear una oferta para ese producto
4. ✅ Verificar que todos los items se listan correctamente

## 🔧 Método 2: Prueba Manual con cURL

### 1. Crear Negocio

```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/negocios" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "nombre": "Negocio Test Manual",
    "descripcion": "Negocio creado manualmente",
    "direccion": "Calle Test 123",
    "telefono": "123456789",
    "email": "test@example.com",
    "activo": true
  }'
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Negocio creado exitosamente",
  "data": {"id": 1},
  "timestamp": "2025-11-04T..."
}
```

**Guarda el `id` del negocio para el siguiente paso.**

### 2. Crear Producto

```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/productos" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "nombre": "Producto Test Manual",
    "descripcion": "Producto creado manualmente",
    "precio": 199.99,
    "negocio_id": 1,
    "categoria": "Test",
    "stock": 10,
    "activo": true
  }'
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Producto creado exitosamente",
  "data": {"id": 1},
  "timestamp": "2025-11-04T..."
}
```

**Guarda el `id` del producto para el siguiente paso.**

### 3. Crear Oferta

```bash
curl -X POST "https://belgranoahorro-aliq.onrender.com/api/ofertas" \
  -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: belgrano_ahorro_api_key_2025" \
  -d '{
    "titulo": "Oferta Test Manual",
    "descripcion": "Oferta creada manualmente",
    "descuento": 15.0,
    "producto_id": 1,
    "negocio_id": 1,
    "fecha_inicio": "2025-11-04",
    "fecha_fin": "2025-12-04",
    "activa": true
  }'
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Oferta creada exitosamente",
  "data": {"id": 1},
  "timestamp": "2025-11-04T..."
}
```

### 4. Verificar Items Creados

```bash
# Listar negocios
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     -H "X-API-Key: belgrano_ahorro_api_key_2025" \
     "https://belgranoahorro-aliq.onrender.com/api/negocios"

# Listar productos
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     -H "X-API-Key: belgrano_ahorro_api_key_2025" \
     "https://belgranoahorro-aliq.onrender.com/api/productos"

# Listar ofertas
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     -H "X-API-Key: belgrano_ahorro_api_key_2025" \
     "https://belgranoahorro-aliq.onrender.com/api/ofertas"
```

## 🎯 Método 3: Desde la Interfaz DevOps

1. **Iniciar servidor DevOps** (si no está corriendo):
   ```bash
   cd devops
   python app.py
   # O si está en Render, acceder a la URL de DevOps
   ```

2. **Acceder a DevOps**:
   - URL: `http://localhost:5000/devops` (local) o URL de Render
   - Login con credenciales DevOps

3. **Crear Negocio**:
   - Ir a `/devops/negocios`
   - Click en "Crear Negocio"
   - Llenar formulario y guardar
   - ✅ Verificar que aparece en la lista

4. **Crear Producto**:
   - Ir a `/devops/productos`
   - Click en "Crear Producto"
   - Seleccionar el negocio creado
   - Llenar formulario y guardar
   - ✅ Verificar que aparece en la lista

5. **Crear Oferta**:
   - Ir a `/devops/ofertas`
   - Click en "Crear Oferta"
   - Seleccionar el producto creado
   - Llenar formulario y guardar
   - ✅ Verificar que aparece en la lista

6. **Verificar en Belgrano Ahorro**:
   - Acceder a la página principal de Belgrano Ahorro
   - ✅ El negocio debe aparecer en "Nuestros Negocios"
   - ✅ El producto debe aparecer en la sección del negocio
   - ✅ La oferta debe estar activa

## ✅ Verificación Final

Para confirmar que todo funciona:

1. **Dashboard DevOps**: Debe mostrar los contadores actualizados
2. **Página Principal Belgrano Ahorro**: Debe mostrar el negocio, producto y oferta
3. **API Belgrano Ahorro**: Los endpoints GET deben retornar los items creados

## 🔍 Troubleshooting

### Error 401 (Unauthorized)
- Verificar que `BELGRANO_AHORRO_API_KEY` sea correcta
- Verificar que el header `Authorization: Bearer ...` esté presente

### Error 400 (Bad Request)
- Verificar que todos los campos requeridos estén presentes
- Verificar tipos de datos (precio debe ser número, activo debe ser booleano)

### Error 500 (Internal Server Error)
- Revisar logs del servidor Belgrano Ahorro
- Verificar que la base de datos esté accesible
- Verificar que las tablas existan (se crean automáticamente)

### Items no aparecen en la página principal
- Verificar que `obtener_negocios_desde_db()` esté funcionando
- Verificar que los items tengan `activo = 1` en la base de datos
- Limpiar cache si existe

## 📝 Notas

- Los items creados desde DevOps se guardan en la base de datos SQLite de Belgrano Ahorro
- La página principal combina datos de la base de datos con datos del JSON local
- Los cambios se reflejan inmediatamente en la API, pero pueden requerir recarga de página en la UI





