# 🚀 GUÍA DE DEPLOY

## 🐳 Docker (Recomendado)

```bash
# Iniciar ambas aplicaciones
docker-compose up --build

# URLs:
# Belgrano Ahorro: http://localhost:5000
# La Ticketera: http://localhost:5001
```

## ☁️ Render

1. **Conectar repositorio** a Render
2. **Usar `render.yaml`** para configuración automática
3. **Render desplegará** ambos servicios automáticamente

## 🖥️ Local

```bash
# Opción 1: Script automático
python start_both_apps.py

# Opción 2: Manual
# Terminal 1:
python inicializar_db.py
python app.py

# Terminal 2:
cd belgrano_tickets
python crear_db_simple.py
python app.py
```

## 🔐 Credenciales

- **Admin**: admin@belgranoahorro.com / admin123
- **Flota**: repartidor1@belgranoahorro.com / repartidor123

