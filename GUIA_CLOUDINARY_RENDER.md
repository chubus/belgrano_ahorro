# Guía de Configuración de Cloudinary en Render

## Resumen

Esta guía explica cómo configurar Cloudinary en Render Dashboard para que las imágenes funcionen correctamente en producción.

## Variables Agregadas a render.yaml

Los archivos `render.yaml` y `devops/render_devops.yaml` ya incluyen las variables de Cloudinary:

```yaml
- key: CLOUDINARY_CLOUD_NAME
  value: dc2n1p5wx
- key: CLOUDINARY_API_KEY
  value: "882162797341932"
- key: CLOUDINARY_API_SECRET
  sync: false  # Configurar manualmente
```

## Configuración Manual en Render Dashboard

Aunque `CLOUDINARY_CLOUD_NAME` y `CLOUDINARY_API_KEY` están en el YAML, **DEBES configurar manualmente** `CLOUDINARY_API_SECRET` por seguridad.

### Para Belgrano Ahorro

1. Ir a: https://dashboard.render.com
2. Seleccionar servicio: **belgrano-ahorro**
3. **Environment** (menú izquierdo)
4. **Add Environment Variable**
5. Agregar:
   - Key: `CLOUDINARY_API_SECRET`
   - Value: `Flf1YKomyxORM1aMnGL7YFr3Ea0`
6. **Save Changes**

### Para DevOps

1. Ir a: https://dashboard.render.com
2. Seleccionar servicio: **devops-service** (o el nombre que tengas)
3. **Environment** (menú izquierdo)
4. **Add Environment Variable**
5. Agregar:
   - Key: `CLOUDINARY_API_SECRET`
   - Value: `Flf1YKomyxORM1aMnGL7YFr3Ea0`
6. **Save Changes**

## Verificación

Después de configurar y redeploy:

1. **Ver logs del servicio**:
   - Services → [tu servicio] → Logs
   - Buscar: "Cloudinary configurado" o similar

2. **Probar subida de imagen**:
   - Login en DevOps
   - Crear producto con imagen
   - Verificar que `image_url` tenga URL de Cloudinary

3. **Verificar en frontend**:
   - Ir a Belgrano Ahorro
   - Buscar el producto
   - La imagen debería mostrarse correctamente

## Migración de Productos Existentes

Después de configurar Cloudinary, ejecutar el script de migración:

```bash
# Conectar a Render Shell o ejecutar localmente con DATABASE_URL de producción
python migrar_imagenes_a_cloudinary.py
```

Este script:
- Busca productos con `imagen` pero sin `image_url`
- Descarga las imágenes (si son URLs)
- Las sube a Cloudinary
- Actualiza el campo `image_url`

## Notas Importantes

- **No commitear secretos**: `CLOUDINARY_API_SECRET` está marcado como `sync: false` para que NO se incluya en el repositorio
- **Redeploy automático**: Al guardar variables en Render Dashboard, el servicio se redeploya automáticamente
- **Tiempo de redeploy**: ~2-5 minutos por servicio

## Troubleshooting

### Las imágenes siguen sin mostrarse

1. Verificar que `CLOUDINARY_API_SECRET` esté configurado en Render Dashboard
2. Ver logs del servicio para errores de Cloudinary
3. Ejecutar `python verificar_productos_api.py` para ver si `image_url` tiene valores
4. Si `image_url` sigue vacío, ejecutar script de migración

### Error "Cloudinary not configured"

- Verificar que las 3 variables estén configuradas en Render Dashboard
- Redeploy el servicio manualmente si es necesario

### Imágenes antiguas no se muestran

- Ejecutar script de migración: `python migrar_imagenes_a_cloudinary.py`
- O re-subir las imágenes manualmente desde DevOps
