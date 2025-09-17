from PIL import Image, ImageDraw, ImageFont
import os

# Lista de productos para crear imágenes
productos = [
    "arroz", "aceite", "fideos", "azucar", "leche", "pan", "huevos", "queso", 
    "yogur", "manteca", "harina", "sal", "cafe", "te", "galletas", "chocolate",
    "mermelada", "miel", "manzanas", "bananas", "tomates", "cebollas", "papas", "zanahorias"
]

# Crear directorio si no existe
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Crear imagen para cada producto
for producto in productos:
    # Crear imagen 300x300 con fondo blanco
    img = Image.new('RGB', (300, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Agregar borde
    draw.rectangle([0, 0, 299, 299], outline='#27ae60', width=3)
    
    # Agregar texto del producto
    try:
        # Intentar usar una fuente del sistema
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Si no encuentra la fuente, usar la por defecto
        font = ImageFont.load_default()
    
    # Centrar el texto
    text = producto.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (300 - text_width) // 2
    y = (300 - text_height) // 2
    
    # Dibujar el texto
    draw.text((x, y), text, fill='#2c3e50', font=font)
    
    # Guardar la imagen
    filename = f'static/images/{producto}.jpg'
    img.save(filename, 'JPEG', quality=85)
    print(f"✅ Creada imagen: {filename}")

print("\n🎉 ¡Todas las imágenes han sido creadas!")
print("📁 Ubicación: static/images/") 