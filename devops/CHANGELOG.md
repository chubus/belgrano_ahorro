# Changelog - DevOps & Backend Integration

## [2025-11-27] - Integración con Cloudinary

### File Storage (devops/image_utils_cloudinary.py)
- **Cloudinary Integration**: Implementado almacenamiento permanente en la nube usando Cloudinary. Las imágenes ahora se suben a Cloudinary en lugar de guardarse en disco local, resolviendo el problema de pérdida de imágenes al reiniciar servicios en Render.
- **Automatic Optimization**: Las imágenes se redimensionan automáticamente a máximo 1200x1200px y se optimizan con calidad 85%.
- **Permanent URLs**: Las URLs de Cloudinary son permanentes y se sirven desde CDN global para carga rápida.

### Dependencies (requirements.txt)
- **Added**: `cloudinary==1.41.0` para integración con servicio de almacenamiento en la nube.

## [2025-11-27] - Fix Crítico de Gunicorn en Python 3.13

### Deployment (render.yaml)
- **Gunicorn Worker Fix**: Especificado explícitamente `--worker-class sync` en el comando de inicio para evitar el uso de `eventlet`, que no es compatible con Python 3.13+. Esto resuelve el error `RuntimeError: do not call blocking functions from the mainloop`.

### Backend (app_unificado.py)
- **Upload Configuration Fix**: Agregada configuración de `UPLOAD_FOLDER`, `MAX_CONTENT_LENGTH` y `UPLOAD_EXTENSIONS` a `app.config`. Esto permite que DevOps guarde imágenes correctamente en disco y que se sirvan a través del endpoint `/media/`.

## [2025-11-26] - Fixes Críticos de Imágenes y Base de Datos

### Backend (api_belgrano_ahorro.py)
- **Auto-Healing de Base de Datos**: Implementada lógica robusta en `execute_insert_returning_id` para detectar errores `UndefinedColumn`.
  - Si falta `image_url` o `imagen`, se crea una nueva conexión a la BD y se ejecuta `ALTER TABLE ... ADD COLUMN`.
  - Se reintenta la inserción automáticamente.
- **Persistencia de Imágenes**: Restaurado el guardado de `image_url` en los INSERT de `negocios`, `productos` y `sucursales`.

### DevOps Client (devops/manager_unified.py & devops/image_utils.py)
- **API Routing Fix**: Corregidas las rutas de API de `/api/v1/` a `/api/` para coincidir con el blueprint real de Belgrano Ahorro. Esto resuelve los errores 400 "Failed to decode JSON".
- **Cache Inteligente**: Mejorada la invalidación de caché (`clear_cache`) para limpiar tanto la lista como el detalle del item al actualizar.
- **Soporte Universal de Imágenes**:
  - Eliminada restricción de formatos (ahora acepta BMP, TIFF, GIF, etc.).
  - Conversión automática a **JPEG optimizado** para cualquier imagen subida.
  - Redimensionamiento automático (max 1200px) antes de guardar.
  - **Cambio de Estrategia**: Se reemplazó el envío de imágenes en Base64 por **URLs públicas** (`/media/...`). Esto mejora drásticamente la velocidad de carga y asegura que las imágenes se vean correctamente en el frontend.

### Utilidades (belgrano_tickets/file_utils.py)
- **Optimización de Imágenes**: Implementado redimensionamiento automático con `Pillow`.
  - Max resolución: 800x800 px.
  - Calidad: 85%.
  - Formato: Optimizado para web.

### Base de Datos
- **Migración Automática**: Script `ensure_image_columns.py` se ejecuta al inicio (`wsgi.py`) como primera línea de defensa.
