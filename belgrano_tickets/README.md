# Proyecto B: Plataforma de gestión de tickets para Belgrano Ahorro

Este proyecto permite al equipo interno (admin y flota) gestionar los tickets de pedidos generados en la plataforma principal (Belgrano Ahorro).

## Estructura inicial
- Backend: Flask
- Base de datos: PostgreSQL
- Autenticación y roles: Flask-Login
- API REST para recibir tickets
- WebSocket para actualización en tiempo real
- Panel web con Bootstrap

## Instalación rápida
1. Instala dependencias:
   ```bash
   pip install flask flask_sqlalchemy flask_login flask_socketio psycopg2-binary
   ```
2. Configura la base de datos PostgreSQL en `.env` o en `config.py`.
3. Ejecuta la app:
   ```bash
   python app.py
   ```

## Roles
- **Admin:** Gestión total de tickets y usuarios flota.
- **Flota:** Acceso limitado, solo ve y actualiza estado de tickets.

## Conexión con Belgrano Ahorro
- Recibe tickets vía POST desde la plataforma principal.
- Actualización automática del panel con WebSocket.

---
