# 🛠️ GUÍA DE MANTENIMIENTO - BELGRANO AHORRO

## 📁 ESTRUCTURA DE CARPETAS DE IMÁGENES

### Organización de Imágenes
```
static/images/
├── productos/                    # 📦 Imágenes de productos por negocio
│   ├── belgrano_ahorro/         # 🏪 Productos de Belgrano Ahorro
│   ├── maxi_descuento/          # 🏪 Productos de Maxi Descuento
│   └── super_mercado/           # 🏪 Productos de Super Mercado
├── ofertas/                     # 🔥 Imágenes de ofertas especiales
├── categorias/                  # 🏷️ Iconos y banners de categorías
└── banners/                     # 🎨 Banners promocionales
```

## 🛍️ GESTIÓN DE PRODUCTOS

### 📝 Cómo Agregar un Nuevo Producto

1. **Preparar la imagen del producto:**
   - Tamaño recomendado: 400x400 píxeles
   - Formato: JPG o PNG
   - Nombre del archivo: `nombre_producto.jpg` (sin espacios, usar guiones)

2. **Colocar la imagen en la carpeta correcta:**
   ```
   static/images/productos/[NOMBRE_NEGOCIO]/nombre_producto.jpg
   ```

3. **Agregar el producto en `productos.json`:**
   ```json
   {
     "id": "producto_001",
     "nombre": "Nombre del Producto",
     "descripcion": "Descripción del producto",
     "precio": 150.00,
     "precio_original": 200.00,  // Solo si hay oferta
     "negocio": "belgrano_ahorro",  // ID del negocio
     "categoria": "granos_cereales", // ID de la categoría
     "imagen": "/static/images/productos/belgrano_ahorro/nombre_producto.jpg",
     "stock": 50,
     "activo": true,
     "destacado": false,
     "oferta": false
   }
   ```

### 🗑️ Cómo Eliminar un Producto

1. **Desactivar el producto (recomendado):**
   - Cambiar `"activo": false` en `productos.json`
   - La imagen permanece disponible por si se reactiva

2. **Eliminar completamente:**
   - Eliminar la entrada del producto en `productos.json`
   - Eliminar la imagen de la carpeta correspondiente

## 🏪 GESTIÓN DE NEGOCIOS

### 📝 Cómo Agregar un Nuevo Negocio

1. **Crear carpeta para las imágenes:**
   ```
   mkdir static/images/productos/[NUEVO_NEGOCIO]
   ```

2. **Agregar el negocio en `productos.json`:**
   ```json
   "nuevo_negocio": {
     "id": 4,
     "nombre": "Nombre del Negocio",
     "descripcion": "Descripción del negocio",
     "logo": "/static/images/logo_nuevo_negocio.jpg",
     "color": "#FF6B35",
     "activo": true
   }
   ```

3. **Agregar productos del nuevo negocio** (seguir pasos de productos)

### 🗑️ Cómo Eliminar un Negocio

1. **Desactivar el negocio:**
   - Cambiar `"activo": false` en `productos.json`
   - Los productos seguirán visibles pero marcados como inactivos

2. **Eliminar completamente:**
   - Eliminar la entrada del negocio en `productos.json`
   - Eliminar todos los productos asociados
   - Eliminar la carpeta de imágenes del negocio

## 🏷️ GESTIÓN DE CATEGORÍAS

### 📝 Cómo Agregar una Nueva Categoría

1. **Agregar la categoría en `productos.json`:**
   ```json
   "nueva_categoria": {
     "id": 13,
     "nombre": "Nueva Categoría",
     "descripcion": "Descripción de la categoría",
     "icono": "🆕"
   }
   ```

2. **Agregar icono personalizado (opcional):**
   - Colocar imagen en `static/images/categorias/`
   - Referenciar en la categoría: `"icono_img": "/static/images/categorias/icono.png"`

### 🗑️ Cómo Eliminar una Categoría

1. **Reasignar productos de la categoría** a otra categoría
2. **Eliminar la entrada** de la categoría en `productos.json`

## 🔥 GESTIÓN DE OFERTAS

### 📝 Cómo Crear una Nueva Oferta

1. **Preparar imagen de la oferta:**
   - Colocar en `static/images/ofertas/`
   - Tamaño recomendado: 800x400 píxeles

2. **Agregar la oferta en `productos.json`:**
   ```json
   "ofertas": {
     "oferta_verano": {
       "id": "oferta_001",
       "nombre": "Oferta de Verano",
       "descripcion": "Descuentos especiales en productos frescos",
       "imagen": "/static/images/ofertas/oferta_verano.jpg",
       "fecha_inicio": "2025-01-01",
       "fecha_fin": "2025-03-31",
       "activa": true,
       "productos": ["producto_001", "producto_002"]
     }
   }
   ```

3. **Marcar productos como oferta:**
   - Cambiar `"oferta": true` en los productos
   - Establecer `"precio_original"` y `"precio"` con descuento

### 🗑️ Cómo Eliminar una Oferta

1. **Desactivar la oferta:**
   - Cambiar `"activa": false` en `productos.json`

2. **Restaurar precios de productos:**
   - Eliminar `"precio_original"` de los productos
   - Cambiar `"oferta": false`

## 🎨 PERSONALIZACIÓN DE LA INTERFAZ

### 📝 Cambiar el Banner Principal

1. **Reemplazar la imagen:**
   - Colocar nueva imagen en `static/images/banners/`
   - Actualizar la referencia en `templates/index.html` línea 35

### 📝 Cambiar el Título "Belgrano Ahorro"

1. **Modificar en `templates/index.html` línea 33:**
   ```html
   <h1 class="display-4 fw-bold text-black">🛒 Belgrano Ahorro</h1>
   ```

### 📝 Personalizar Colores y Estilos

1. **Editar `static/style.css`:**
   - Cambiar variables CSS para colores principales
   - Modificar estilos de botones y elementos

## 🔧 MANTENIMIENTO RUTINARIO

### ✅ Checklist Semanal
- [ ] Verificar que todos los productos estén activos
- [ ] Revisar precios y ofertas vigentes
- [ ] Actualizar stock de productos
- [ ] Verificar que las imágenes se carguen correctamente

### ✅ Checklist Mensual
- [ ] Revisar y actualizar ofertas expiradas
- [ ] Limpiar productos inactivos
- [ ] Optimizar imágenes para mejor rendimiento
- [ ] Actualizar información de negocios

## 🚨 SOLUCIÓN DE PROBLEMAS

### ❌ Imagen no se muestra
1. Verificar que la ruta en `productos.json` sea correcta
2. Confirmar que el archivo existe en la carpeta correspondiente
3. Verificar permisos del archivo

### ❌ Producto no aparece
1. Verificar que `"activo": true` en `productos.json`
2. Confirmar que el negocio esté activo
3. Verificar que la categoría exista

### ❌ Oferta no se muestra
1. Verificar fechas de inicio y fin
2. Confirmar que `"activa": true`
3. Verificar que los productos estén marcados como oferta

## 📞 CONTACTO PARA SOPORTE

Si necesitas ayuda con el mantenimiento:
- Revisar esta guía primero
- Consultar la documentación técnica
- Contactar al equipo de desarrollo

---

**Última actualización:** 31 de Julio 2025
**Versión:** 1.0 