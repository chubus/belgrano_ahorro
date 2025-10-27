# 🚀 APLICACIONES LANZADAS PARA TESTING

## 🌐 **URLs DE ACCESO:**

### **🏪 Belgrano Ahorro**
- **URL Principal**: http://localhost:5000/
- **API Health**: http://localhost:5000/api/health
- **API Status**: http://localhost:5000/api/status
- **API Productos**: http://localhost:5000/api/productos
- **API Categorías**: http://localhost:5000/api/categorias
- **API Negocios**: http://localhost:5000/api/negocios

### **🎫 Ticketera**
- **URL Principal**: http://localhost:5001/
- **Sistema de gestión de pedidos**

### **⚙️ DevOps**
- **URL Principal**: http://localhost:5002/devops/
- **Usuario**: devops
- **Contraseña**: DevOps2025!Secure

## 📋 **GUÍA DE TESTING:**

### **1. Acceder a DevOps**
- Ir a: http://localhost:5002/devops/
- Usuario: `devops`
- Contraseña: `DevOps2025!Secure`

### **2. Crear un Producto desde DevOps**
- Ir a "Gestión de Productos"
- Crear nuevo producto
- Llenar los campos requeridos
- Guardar el producto

### **3. Verificar en Belgrano Ahorro**
- Ir a: http://localhost:5000/
- Buscar el producto creado
- Verificar que aparece en la lista
- Probar la funcionalidad de búsqueda

### **4. Probar Compra en Belgrano Ahorro**
- Agregar producto al carrito
- Proceder al checkout
- Completar el proceso de compra
- Verificar que se genera el pedido

### **5. Verificar Ticket en Ticketera**
- Ir a: http://localhost:5001/
- Verificar que se generó el ticket
- Revisar detalles del pedido
- Probar funcionalidades del sistema de tickets

## 🔍 **ENDPOINTS DE API PARA TESTING:**

### **Health Check**
```bash
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     http://localhost:5000/api/health
```

### **Status Detallado**
```bash
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     http://localhost:5000/api/status
```

### **Listar Productos**
```bash
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     http://localhost:5000/api/productos
```

### **Listar Categorías**
```bash
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     http://localhost:5000/api/categorias
```

### **Listar Negocios**
```bash
curl -H "Authorization: Bearer belgrano_ahorro_api_key_2025" \
     http://localhost:5000/api/negocios
```

## 🔐 **AUTENTICACIÓN API:**

### **Métodos Soportados:**
1. **Bearer Token**: `Authorization: Bearer belgrano_ahorro_api_key_2025`
2. **X-API-Key Header**: `X-API-Key: belgrano_ahorro_api_key_2025`
3. **Query Parameter**: `?api_key=belgrano_ahorro_api_key_2025`

## 📊 **DATOS DISPONIBLES:**

### **Base de Datos:**
- **Negocios**: 17 registros
- **Productos**: 60 registros
- **Categorías**: 8 registros
- **Ofertas**: 9 registros
- **Sucursales**: 7 registros

## ⚠️ **NOTAS IMPORTANTES:**

1. **Las aplicaciones están ejecutándose en modo desarrollo**
2. **Presiona Ctrl+C para detener todas las aplicaciones**
3. **Si alguna aplicación se detiene, se mostrará un mensaje de advertencia**
4. **Los datos se mantienen en la base de datos local**
5. **Las APIs están completamente funcionales con autenticación**

## 🎯 **FLUJO DE PRUEBA RECOMENDADO:**

1. **Crear producto en DevOps** → Verificar sincronización
2. **Probar APIs** → Verificar autenticación y respuestas
3. **Completar compra** → Verificar flujo completo
4. **Revisar tickets** → Verificar generación de pedidos
5. **Probar diferentes escenarios** → Verificar robustez del sistema

**¡Las aplicaciones están listas para testing!**
