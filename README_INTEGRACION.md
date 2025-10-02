# Integración DevOps ↔ Belgrano Ahorro (APIs REST bidireccionales)

## Autenticación
- Usar header: Authorization: Bearer <BELGRANO_AHORRO_API_KEY>
- Variables en DevOps: BELGRANO_AHORRO_URL, BELGRANO_AHORRO_API_KEY

## Endpoints disponibles (alias ES + EN)
- Negocios: GET/POST /api/negocios (/api/businesses), GET/PUT/DELETE /api/negocios/<id>
- Sucursales: GET/POST /api/sucursales (/api/branches), GET/PUT/DELETE /api/sucursales/<id>
- Productos: GET/POST /api/productos (/api/products), GET/PUT/DELETE /api/productos/<id>
- Ofertas: GET/POST /api/ofertas (/api/offers), GET/PUT/DELETE /api/ofertas/<id>
- Precios: GET /api/precios, PUT /api/precios/<producto_id>
- Salud: GET /api/health

## Consumo desde DevOps
- Paneles:
  - /devops/negocios → lista/alta (templates/devops/negocios.html)
  - /devops/productos → lista/alta (templates/devops/productos.html)
- Cliente: belgrano_client.py (get_/create_/update_/delete_ para businesses, products, branches, offers; health_check)

## Ejemplos curl
- Listar productos:
  curl -H "Authorization: Bearer $BELGRANO_AHORRO_API_KEY" "$BELGRANO_AHORRO_URL/api/productos"
- Crear negocio:
  curl -X POST -H "Authorization: Bearer $BELGRANO_AHORRO_API_KEY" -H "Content-Type: application/json" -d '{"nombre":"Nuevo"}' "$BELGRANO_AHORRO_URL/api/negocios"
- Actualizar precio:
  curl -X PUT -H "Authorization: Bearer $BELGRANO_AHORRO_API_KEY" -H "Content-Type: application/json" -d '{"precio": 123.45}' "$BELGRANO_AHORRO_URL/api/precios/1"

## Notas
- No se modificó la UI existente; solo se agregaron endpoints y vistas mínimas.
- La base se asegura al iniciar la API (ensure_tables).
- Cambios en DevOps impactan en belgrano_ahorro.db y se reflejan en la app.
