# Changelog - DevOps & Backend Integration

## [2025-11-26] - Fixes Críticos de Imágenes y Base de Datos

### Backend (api_belgrano_ahorro.py)
- **Auto-Healing de Base de Datos**: Implementada lógica robusta en `execute_insert_returning_id` para detectar errores `UndefinedColumn`.
  - Si falta `image_url` o `imagen`, se crea una nueva conexión a la BD y se ejecuta `ALTER TABLE ... ADD COLUMN`.
  - Se reintenta la inserción automáticamente.
- **Persistencia de Imágenes**: Restaurado el guardado de `image_url` en los INSERT de `negocios`, `productos` y `sucursales`.

### DevOps Client (devops/manager_unified.py & devops/image_utils.py)
- **API Versioning**: Actualizados todos los endpoints para usar `/api/v1/` en lugar de `/api/`.
- **Cache Inteligente**: Mejorada la invalidación de caché (`clear_cache`) para limpiar tanto la lista como el detalle del item al actualizar.
- **Soporte Universal de Imágenes**:
  - Eliminada restricción de formatos (ahora acepta BMP, TIFF, GIF, etc.).
  - Conversión automática a **JPEG optimizado** para cualquier imagen subida.
  - Redimensionamiento automático (max 1200px) antes de guardar.

### Utilidades (belgrano_tickets/file_utils.py)
- **Optimización de Imágenes**: Implementado redimensionamiento automático con `Pillow`.
  - Max resolución: 800x800 px.
  - Calidad: 85%.
  - Formato: Optimizado para web.

### Base de Datos
- **Migración Automática**: Script `ensure_image_columns.py` se ejecuta al inicio (`wsgi.py`) como primera línea de defensa.
