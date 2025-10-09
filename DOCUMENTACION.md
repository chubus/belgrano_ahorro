# 📚 DOCUMENTACIÓN - BELGRANO AHORRO

## 🏗️ ESTRUCTURA DEL PROYECTO

```
Belgrano_ahorro/
├── app.py              # 🚀 Archivo principal (servidor Flask)
├── productos.json      # 📦 Datos de productos
├── static/
│   └── style.css      # 🎨 Estilos CSS personalizados
├── templates/
│   ├── base.html      # 📄 Plantilla base (header, footer)
│   └── index.html     # 🏠 Página principal (catálogo)
└── DOCUMENTACION.md   # 📖 Este archivo
```

## 📦 ESTRUCTURA DE DATOS (productos.json)

Cada producto tiene esta estructura:
```json
{
  "nombre": "Nombre del Producto",     // Texto que aparece en la tarjeta
  "precio": 1000,                      // Número (precio en pesos)
  "imagen": "https://url-de-la-imagen" // URL de la imagen del producto
}
```

### 🔧 CÓMO AGREGAR NUEVOS PRODUCTOS

1. **Abre** `productos.json`
2. **Copia** la estructura de un producto existente
3. **Cambia** los valores:
   - `nombre`: Nombre del producto
   - `precio`: Precio en pesos argentinos
   - `imagen`: URL de una imagen (puedes usar Unsplash)

### 📸 OBTENER IMÁGENES GRATIS

Para imágenes de productos, puedes usar:
- **Unsplash**: https://unsplash.com/s/photos/food
- **Pexels**: https://www.pexels.com/search/food/
- **Pixabay**: https://pixabay.com/images/search/food/

## 🎨 PERSONALIZACIÓN VISUAL

### Colores principales (en style.css):
- **Verde principal**: `#27ae60` (botones, navbar)
- **Verde hover**: `#229954` (efectos al pasar el mouse)
- **Texto oscuro**: `#2c3e50` (títulos)
- **Fondo**: `#f8f9fa` (gris claro)

### Para cambiar colores:
1. **Abre** `static/style.css`
2. **Busca** los códigos de color (ej: `#27ae60`)
3. **Reemplaza** con tu color preferido

## 🚀 FUNCIONES PRINCIPALES (app.py)

### Rutas disponibles:
- **`/`** - Página principal (catálogo de productos)
- **`/test`** - Página de prueba (para verificar que funciona)

### Para agregar nuevas páginas:
1. **Abre** `app.py`
2. **Agrega** una nueva función con `@app.route("/tu-pagina")`
3. **Crea** el template en `templates/tu-pagina.html`

## 📄 TEMPLATES (HTML)

### base.html
- **Header**: Barra de navegación verde
- **Footer**: Información de copyright
- **Bootstrap**: Framework CSS incluido
- **CSS personalizado**: Enlazado desde static/style.css

### index.html
- **Extiende** base.html
- **Bucle** para mostrar productos
- **Tarjetas** con imagen, nombre, precio y botón

## 🛠️ COMANDOS ÚTILES

### Ejecutar la aplicación:
```bash
python app.py
```

### Verificar que funciona:
- Abre: http://localhost:5000
- Página de prueba: http://localhost:5000/test

### Para detener:
- Presiona `Ctrl+C` en la terminal

## 🔧 MODIFICACIONES COMUNES

### Cambiar el título de la página:
1. **Abre** `templates/base.html`
2. **Busca** `<title>Belgrano Ahorro</title>`
3. **Cambia** el texto

### Agregar más productos:
1. **Abre** `productos.json`
2. **Copia** un producto existente
3. **Modifica** los valores

### Cambiar el logo/nombre:
1. **Abre** `templates/base.html`
2. **Busca** `<a class="navbar-brand">Belgrano Ahorro</a>`
3. **Cambia** el texto

### Modificar estilos:
1. **Abre** `static/style.css`
2. **Edita** las reglas CSS
3. **Guarda** y recarga la página

## 🐛 SOLUCIÓN DE PROBLEMAS

### La página no carga:
- Verifica que Flask esté instalado: `pip install flask`
- Revisa que no haya errores en la consola
- Asegúrate de que el puerto 5000 esté libre

### Las imágenes no aparecen:
- Verifica que las URLs sean válidas
- Prueba abrir las URLs en el navegador
- Considera usar imágenes locales

### Los estilos no se aplican:
- Verifica que `static/style.css` exista
- Revisa la consola del navegador (F12)
- Asegúrate de que no haya errores CSS

## 📈 PRÓXIMAS MEJORAS SUGERIDAS

1. **Carrito de compras** - Agregar funcionalidad para comprar
2. **Base de datos** - Reemplazar JSON con SQLite/MySQL
3. **Sistema de usuarios** - Login y registro
4. **Filtros** - Buscar por categoría o precio
5. **Responsive** - Mejorar diseño móvil
6. **Animaciones** - Efectos más suaves
7. **API** - Endpoints para aplicaciones móviles

---

**¡Listo para personalizar! 🎉** 