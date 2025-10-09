# 🏪 Funcionalidad de Sucursales - Belgrano Ahorro

## 📋 Descripción

Se ha implementado una nueva funcionalidad que permite a los comerciantes seleccionar sucursales específicas y agregar productos particulares de cada sucursal a sus paquetes automáticos.

## ✨ Características Principales

### 1. **Selección de Sucursales**
- Los comerciantes pueden seleccionar primero un negocio
- Luego pueden elegir una sucursal específica de ese negocio
- Se muestra información detallada de la sucursal (dirección, horarios, teléfono)

### 2. **Productos por Sucursal**
- Cada sucursal tiene productos específicos disponibles
- Los productos se filtran automáticamente según la sucursal seleccionada
- Solo se muestran productos que están disponibles en esa sucursal específica

### 3. **Agregado Automático al Paquete**
- Al seleccionar un producto, se abre un modal de confirmación
- Se puede especificar la cantidad deseada
- El producto se agrega automáticamente al paquete del comerciante

## 🏗️ Estructura de Datos

### Sucursales en `productos.json`

```json
{
  "sucursales": {
    "belgrano_ahorro": {
      "sucursal_centro": {
        "id": 1,
        "nombre": "Sucursal Centro",
        "direccion": "Av. Belgrano 1234, Centro",
        "telefono": "011-1234-5678",
        "horarios": "Lun-Sáb 8:00-22:00, Dom 9:00-21:00",
        "activo": true
      },
      "sucursal_norte": {
        "id": 2,
        "nombre": "Sucursal Norte",
        "direccion": "Av. Corrientes 567, Norte",
        "telefono": "011-1234-5679",
        "horarios": "Lun-Sáb 8:00-22:00, Dom 9:00-21:00",
        "activo": true
      }
    }
  }
}
```

### Productos con Sucursales

```json
{
  "id": 1,
  "nombre": "Arroz 1kg",
  "precio": 950,
  "negocio": "belgrano_ahorro",
  "sucursales": ["sucursal_centro", "sucursal_norte", "sucursal_sur"],
  "activo": true
}
```

## 🔧 Funciones Implementadas

### En `app.py`

1. **`obtener_sucursales()`**
   - Obtiene todas las sucursales del sistema
   - Retorna diccionario organizado por negocio

2. **`obtener_sucursales_por_negocio(negocio_id)`**
   - Obtiene sucursales de un negocio específico
   - Filtra solo sucursales activas

3. **`obtener_productos_por_sucursal(negocio_id, sucursal_id)`**
   - Obtiene productos disponibles en una sucursal específica
   - Filtra por negocio, sucursal y estado activo

4. **`api_productos_por_sucursal()`**
   - Endpoint API para obtener productos de una sucursal
   - Recibe negocio_id y sucursal_id por POST
   - Retorna JSON con productos disponibles

## 🎨 Interfaz de Usuario

### Pantalla de Edición de Paquetes

La pantalla se divide en 3 secciones:

1. **📦 Productos en el Paquete** (izquierda)
   - Muestra productos ya agregados al paquete
   - Lista con nombre y cantidad de cada producto

2. **🏪 Seleccionar Sucursal** (centro)
   - Dropdown para seleccionar negocio
   - Dropdown para seleccionar sucursal (se habilita después de seleccionar negocio)
   - Información de la sucursal seleccionada

3. **🛍️ Productos de la Sucursal** (derecha)
   - Lista de productos disponibles en la sucursal seleccionada
   - Botón para agregar cada producto al paquete

### Modal de Confirmación

- Muestra imagen, nombre y precio del producto
- Campo para especificar cantidad
- Botones para confirmar o cancelar

## 🚀 Cómo Usar

### Para Comerciantes

1. **Acceder a la edición de paquetes**
   - Ir a Panel de Comerciantes → Paquetes
   - Hacer clic en "Editar" en el paquete deseado

2. **Seleccionar sucursal**
   - Elegir negocio del primer dropdown
   - Elegir sucursal del segundo dropdown
   - Ver información de la sucursal

3. **Agregar productos**
   - Ver productos disponibles en la sucursal
   - Hacer clic en ➕ para agregar un producto
   - Especificar cantidad en el modal
   - Confirmar para agregar al paquete

### Para Desarrolladores

1. **Agregar nuevas sucursales**
   - Editar `productos.json` sección "sucursales"
   - Agregar sucursal con estructura completa

2. **Asignar productos a sucursales**
   - Agregar campo "sucursales" a productos en `productos.json`
   - Lista de IDs de sucursales donde está disponible

3. **Probar funcionalidad**
   - Ejecutar `python test_sucursales.py`
   - Verificar que productos se filtran correctamente

## 📊 Estadísticas Actuales

- **Total de productos**: 137
- **Productos con sucursales asignadas**: 7 (5.1%)
- **Negocios con sucursales**: 3
- **Sucursales totales**: 6

## 🔄 Flujo de Datos

```
1. Usuario selecciona negocio
   ↓
2. Se cargan sucursales del negocio
   ↓
3. Usuario selecciona sucursal
   ↓
4. Se hace llamada API a /api/productos_por_sucursal
   ↓
5. Se filtran productos por sucursal
   ↓
6. Se muestran productos disponibles
   ↓
7. Usuario selecciona producto
   ↓
8. Se abre modal de confirmación
   ↓
9. Usuario confirma cantidad
   ↓
10. Se agrega producto al paquete
```

## 🛠️ Mantenimiento

### Agregar Nueva Sucursal

1. Editar `productos.json`
2. Agregar sucursal en sección correspondiente
3. Asignar productos a la nueva sucursal

### Modificar Productos por Sucursal

1. Editar campo "sucursales" del producto
2. Agregar o quitar IDs de sucursales según necesidad

### Desactivar Sucursal

1. Cambiar `"activo": false` en la sucursal
2. Los productos seguirán disponibles pero no se mostrará la sucursal

## ✅ Pruebas

Ejecutar el script de prueba:
```bash
python test_sucursales.py
```

Este script verifica:
- Carga correcta de datos
- Filtrado de productos por sucursal
- Estadísticas del sistema
- Funcionamiento de las funciones principales

## 🎯 Beneficios

1. **Especificidad**: Los comerciantes pueden crear paquetes con productos de sucursales específicas
2. **Flexibilidad**: Diferentes sucursales pueden tener diferentes productos
3. **Organización**: Mejor gestión de inventario por ubicación
4. **Experiencia de usuario**: Interfaz intuitiva y fácil de usar
5. **Escalabilidad**: Fácil agregar nuevas sucursales y productos

## 🔮 Próximas Mejoras

- [ ] Agregar más productos con información de sucursales
- [ ] Implementar gestión de stock por sucursal
- [ ] Agregar filtros por categoría en productos de sucursal
- [ ] Implementar búsqueda de productos por sucursal
- [ ] Agregar reportes de productos por sucursal
