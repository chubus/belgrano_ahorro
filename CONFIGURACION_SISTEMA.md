# ⚙️ CONFIGURACIÓN DEL SISTEMA - BELGRANO AHORRO

## 🎨 PERSONALIZACIÓN DE LA INTERFAZ

### 📝 Título Principal
**Archivo:** `templates/index.html` - Línea 33
```html
<h1 class="display-4 fw-bold text-black">🛒 Belgrano Ahorro</h1>
```
**Para cambiar:** Reemplazar "Belgrano Ahorro" con el nuevo nombre

### 🖼️ Logo del Banner
**Archivo:** `templates/index.html` - Línea 35
```html
<img src="{{ url_for('static', filename='images/logo_belgrano_ahorro.jpg') }}" alt="Belgrano Ahorro">
```
**Para cambiar:** Reemplazar `logo_belgrano_ahorro.jpg` con la nueva imagen

### 🎨 Colores del Sistema
**Archivo:** `static/style.css`
```css
:root {
    --color-primary: #28a745;      /* Verde principal */
    --color-secondary: #FFD700;    /* Dorado */
    --color-accent: #FFA500;       /* Naranja */
    --color-dark: #2c3e50;         /* Azul oscuro */
    --color-light: #f8f9fa;        /* Gris claro */
}
```

## 🏪 CONFIGURACIÓN DE NEGOCIOS

### 📝 Agregar Nuevo Negocio
**Archivo:** `productos.json` - Sección "negocios"
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

### 🗑️ Desactivar Negocio
Cambiar `"activo": false` en la sección del negocio

## 🏷️ CONFIGURACIÓN DE CATEGORÍAS

### 📝 Agregar Nueva Categoría
**Archivo:** `productos.json` - Sección "categorias"
```json
"nueva_categoria": {
    "id": 13,
    "nombre": "Nueva Categoría",
    "descripcion": "Descripción de la categoría",
    "icono": "🆕"
}
```

### 🎨 Cambiar Icono de Categoría
Modificar el campo `"icono"` con el nuevo emoji

## 🔥 CONFIGURACIÓN DE OFERTAS

### 📝 Crear Nueva Oferta
**Archivo:** `productos.json` - Sección "ofertas"
```json
"oferta_especial": {
    "id": "oferta_001",
    "nombre": "Oferta Especial",
    "descripcion": "Descripción de la oferta",
    "imagen": "/static/images/ofertas/oferta_especial.jpg",
    "fecha_inicio": "2025-01-01",
    "fecha_fin": "2025-03-31",
    "activa": true,
    "productos": ["producto_001", "producto_002"]
}
```

### 💰 Aplicar Oferta a Productos
En la sección "productos", modificar:
```json
{
    "precio": 150.00,        /* Precio con descuento */
    "precio_original": 200.00, /* Precio original */
    "oferta": true           /* Marcar como oferta */
}
```

## 🛍️ CONFIGURACIÓN DE PRODUCTOS

### 📝 Agregar Nuevo Producto
**Archivo:** `productos.json` - Sección "productos"
```json
{
    "id": "producto_001",
    "nombre": "Nombre del Producto",
    "descripcion": "Descripción del producto",
    "precio": 150.00,
    "precio_original": 200.00,  /* Solo si hay oferta */
    "negocio": "belgrano_ahorro",
    "categoria": "granos_cereales",
    "imagen": "/static/images/productos/belgrano_ahorro/nombre_producto.jpg",
    "stock": 50,
    "activo": true,
    "destacado": false,
    "oferta": false
}
```

### ⭐ Destacar Producto
Cambiar `"destacado": true` en el producto

### 🗑️ Desactivar Producto
Cambiar `"activo": false` en el producto

## 📁 ESTRUCTURA DE CARPETAS

### 🖼️ Organización de Imágenes
```
static/images/
├── productos/
│   ├── belgrano_ahorro/     # Productos de Belgrano Ahorro
│   ├── maxi_descuento/      # Productos de Maxi Descuento
│   └── super_mercado/       # Productos de Super Mercado
├── ofertas/                 # Imágenes de ofertas
├── categorias/              # Iconos de categorías
└── banners/                 # Banners promocionales
```

### 📝 Convenciones de Nombres
- **Productos:** `nombre_producto.jpg` (sin espacios, usar guiones)
- **Ofertas:** `oferta_nombre.jpg`
- **Categorías:** `categoria_nombre.png`
- **Banners:** `banner_nombre.jpg`

## 🔧 CONFIGURACIÓN TÉCNICA

### 🚀 Iniciar la Aplicación
```bash
python app.py
```

### 📊 Base de Datos
**Archivo:** `belgrano_ahorro.db`
- Usuarios registrados
- Pedidos realizados
- Historial de compras

### 🔐 Configuración de Seguridad
**Archivo:** `app.py` - Línea 25
```python
app.secret_key = 'belgrano_ahorro_secret_key_2025'
```

## 📱 CONFIGURACIÓN RESPONSIVE

### 📱 Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### 🎨 Estilos Adaptativos
**Archivo:** `templates/index.html` - Sección CSS
```css
@media (max-width: 768px) {
    .hero-section { padding: 2rem 0; }
    .display-4 { font-size: 2rem; }
    .producto-carrusel { width: 200px; }
}
```

## 🔄 MANTENIMIENTO RUTINARIO

### ✅ Checklist Diario
- [ ] Verificar que todos los productos estén activos
- [ ] Revisar precios actualizados
- [ ] Confirmar que las ofertas estén vigentes

### ✅ Checklist Semanal
- [ ] Actualizar stock de productos
- [ ] Revisar imágenes rotas
- [ ] Verificar enlaces de navegación

### ✅ Checklist Mensual
- [ ] Limpiar productos inactivos
- [ ] Optimizar imágenes
- [ ] Actualizar información de negocios
- [ ] Revisar ofertas expiradas

## 🚨 SOLUCIÓN DE PROBLEMAS

### ❌ Error: Producto no aparece
1. Verificar `"activo": true` en productos.json
2. Confirmar que el negocio esté activo
3. Verificar que la categoría exista

### ❌ Error: Imagen no se muestra
1. Verificar ruta en productos.json
2. Confirmar que el archivo existe
3. Verificar permisos del archivo

### ❌ Error: Oferta no funciona
1. Verificar fechas de inicio y fin
2. Confirmar `"activa": true`
3. Verificar que productos estén marcados como oferta

## 📞 SOPORTE TÉCNICO

### 🔧 Archivos Principales
- **`app.py`:** Lógica principal de la aplicación
- **`productos.json`:** Datos de productos, ofertas, categorías
- **`templates/`:** Plantillas HTML
- **`static/`:** Archivos CSS, JS e imágenes

### 📚 Documentación
- **`GUIA_MANTENIMIENTO.md`:** Guía completa de mantenimiento
- **`DOCUMENTACION.md`:** Documentación técnica
- **`CONFIGURACION_SISTEMA.md`:** Este archivo

---

**Última actualización:** 31 de Julio 2025
**Versión:** 1.0
**Mantenido por:** Equipo de Desarrollo Belgrano Ahorro 