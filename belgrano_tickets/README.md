# 🎫 Belgrano Tickets - Servicio Independiente

## 🚀 Deploy en Render

### **Configuración Lista: 5/5 ✅**

**Archivos esenciales:**
- ✅ `app.py` - Aplicación principal
- ✅ `models.py` - Modelos de datos
- ✅ `config_ticketera.py` - Configuración
- ✅ `requirements_ticketera.txt` - Dependencias
- ✅ `start_ticketera.sh` - Script de inicio
- ✅ `belgrano_client.py` - Cliente API

### **Opciones de Deploy:**

#### **Opción 1: Docker (Recomendado)**
```yaml
# Usar: render_docker.yaml
services:
  - type: web
    name: belgrano-ticketera
    env: docker
    plan: free
```

#### **Opción 2: Python Nativo**
```yaml
# Usar: render_independiente.yaml
services:
  - type: web
    name: belgrano-ticketera
    env: python
    plan: free
    buildCommand: pip install -r requirements_ticketera.txt
    startCommand: python app.py
```

### **Variables de Entorno:**
```bash
FLASK_APP=app.py
FLASK_ENV=production
PORT=5001
SECRET_KEY=belgrano_tickets_secret_2025
BELGRANO_AHORRO_URL=https://belgrano-ahorro.onrender.com
```

### **Verificación:**
```bash
python verificar_deploy.py
```

### **URLs de Producción:**
- **Belgrano Ahorro**: https://belgrano-ahorro.onrender.com
- **Belgrano Tickets**: https://belgrano-ticketera.onrender.com

**¡Listo para deploy independiente en Render!**
