# 🚀 INSTRUCCIONES DE DEPLOY - Belgrano Tickets

## 📋 Pasos para Deploy en Render.com

### **1. Crear Repositorio en GitHub**

1. Ve a [GitHub](https://github.com) y crea un nuevo repositorio
2. Nombre: `belgrano-tickets`
3. Descripción: "Sistema de gestión de tickets para Belgrano Ahorro"
4. **NO** inicialices con README (ya tenemos uno)

### **2. Subir Código a GitHub**

```bash
# En la carpeta belgrano-tickets
git remote add origin https://github.com/TU-USUARIO/belgrano-tickets.git
git branch -M main
git push -u origin main
```

### **3. Configurar Render.com**

1. Ve a [Render.com](https://render.com) y crea una cuenta
2. Haz clic en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio `belgrano-tickets`

### **4. Configuración Automática**

Render detectará automáticamente:
- ✅ `render_tickets.yaml` - Configuración del servicio
- ✅ `requirements_tickets.txt` - Dependencias
- ✅ `app_tickets.py` - Aplicación principal

### **5. Variables de Entorno**

Render configurará automáticamente:
- `PYTHON_VERSION`: 3.12.0
- `FLASK_ENV`: production
- `FLASK_APP`: app_tickets.py
- `PORT`: 5001
- `SECRET_KEY`: belgrano_tickets_secret_2025

### **6. Deploy**

1. Haz clic en "Create Web Service"
2. Render comenzará el deploy automáticamente
3. Espera 5-10 minutos para que termine

## 🔗 URLs Resultantes

Una vez completado el deploy:

- **URL Principal**: `https://belgrano-tickets.onrender.com`
- **API**: `https://belgrano-tickets.onrender.com/api/tickets`
- **Panel**: `https://belgrano-tickets.onrender.com/tickets`
- **Health Check**: `https://belgrano-tickets.onrender.com/health`

## 🔐 Credenciales

- **Admin**: `admin@belgranoahorro.com` / `admin123`
- **Flota**: `repartidor1@belgranoahorro.com` / `flota123`

## 🧪 Pruebas Post-Deploy

### **1. Health Check**
```bash
curl https://belgrano-tickets.onrender.com/health
```

### **2. Probar API**
```bash
curl -X POST https://belgrano-tickets.onrender.com/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": "Test User",
    "productos": ["Producto Test"],
    "total": 1000
  }'
```

### **3. Acceder al Panel**
1. Ve a `https://belgrano-tickets.onrender.com`
2. Login con credenciales de admin
3. Ve a `/tickets` para ver el panel

## 🔄 Integración con Belgrano Ahorro

Una vez que Belgrano Tickets esté desplegado:

1. **Actualizar URL** en `app_unificado.py`:
   ```python
   api_url = "https://belgrano-tickets.onrender.com/api/tickets"
   ```

2. **Hacer commit y push** del cambio:
   ```bash
   cd ../Belgrano_ahorro-back
   git add app_unificado.py
   git commit -m "Actualizar URL de API de tickets"
   git push origin main
   ```

3. **Probar integración completa**:
   - Hacer pedido en Belgrano Ahorro
   - Verificar que aparece en Belgrano Tickets

## 📊 Monitoreo

### **Logs en Render.com**
- Ve a tu servicio en Render
- Pestaña "Logs" para ver logs en tiempo real

### **Health Check**
- Render verificará automáticamente `/health`
- Si falla, reiniciará el servicio

### **Métricas**
- Render proporciona métricas básicas
- Uptime, response time, etc.

## 🛠️ Troubleshooting

### **Error: "Build failed"**
- Verifica que `requirements_tickets.txt` esté correcto
- Revisa logs de build en Render

### **Error: "Service failed to start"**
- Verifica que `app_tickets.py` tenga `if __name__ == "__main__"`
- Revisa logs de runtime

### **Error: "Database connection failed"**
- SQLite se crea automáticamente
- Verifica permisos de escritura

### **Error: "API not responding"**
- Verifica que el servicio esté "Live" en Render
- Revisa health check

## 🎯 Resultado Final

Una vez completado todo:

✅ **Belgrano Ahorro**: `https://belgrano-ahorro-unificado.onrender.com`
✅ **Belgrano Tickets**: `https://belgrano-tickets.onrender.com`
✅ **Integración**: Funcionando vía API HTTP
✅ **Panel**: Accesible con credenciales admin

**¡Sistema completamente funcional y desplegado!** 🚀
