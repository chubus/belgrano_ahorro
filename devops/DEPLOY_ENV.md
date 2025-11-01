# Variables de Entorno para Deploy

## 📋 DEVops

### Variables Requeridas
```bash
# Conexión con Belgrano Ahorro API
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=tu_api_key_aqui

# Configuración de API (opcionales, con defaults)
API_TIMEOUT_SECS=15
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=0.5

# Base de datos local (si se usa manager.py en lugar de manager_unified.py)
BELGRANO_AHORRO_DB_PATH=belgrano_ahorro.db

# Flask
FLASK_ENV=production
SECRET_KEY=tu_secret_key_segura_aqui
PORT=5000

# Cookies de sesión (para producción con HTTPS)
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=true
REMEMBER_COOKIE_SECURE=true
```

### Valores de Ejemplo para DevOps
```bash
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
API_TIMEOUT_SECS=15
FLASK_ENV=production
SECRET_KEY=devops_secret_key_2025_prod_segura
PORT=5000
SESSION_COOKIE_SECURE=true
```

---

## 🏪 BELGRANO AHORRO

### Variables Requeridas
```bash
# Flask Core
FLASK_ENV=production
SECRET_KEY=tu_secret_key_segura_aqui
PORT=5000
HOST=0.0.0.0

# Base de datos
DATABASE_URL=sqlite:///belgrano_ahorro.db
# O para PostgreSQL/MySQL:
# DATABASE_URL=postgresql://user:pass@host:port/dbname

# API Keys para comunicación
BELGRANO_AHORRO_API_KEY=tu_api_key_aqui
DEVOPS_API_KEY=devops_api_key_aqui

# URLs de servicios
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
DEVOPS_API_URL=http://localhost:5000/devops
# O alternativamente:
# TICKETERA_URL=http://localhost:5002
```

### Valores de Ejemplo para Belgrano Ahorro
```bash
FLASK_ENV=production
SECRET_KEY=belgrano_ahorro_secret_key_2025
PORT=5000
HOST=0.0.0.0
DATABASE_URL=sqlite:///belgrano_ahorro.db
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
DEVOPS_API_KEY=devops_api_key_2025
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
DEVOPS_API_URL=https://tudominio.com/devops
```

---

## 🎫 TICKETERA (Belgrano Tickets)

### Variables Requeridas
```bash
# Flask Core
FLASK_ENV=production
SECRET_KEY=tu_secret_key_segura_aqui
PORT=5002
HOST=0.0.0.0

# Base de datos
DATABASE_URL=sqlite:///belgrano_tickets.db
# O alternativamente:
# TICKETS_DB_PATH=belgrano_tickets.db

# API de Belgrano Ahorro
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=tu_api_key_belgrano_aqui

# API de DevOps/Ticketera (para comunicación bidireccional)
DEVOPS_API_URL=https://tudominio.com/devops
DEVOPS_API_KEY=devops_api_key_aqui
# O alternativamente (nombres legados):
# TICKETERA_URL=https://tudominio.com/ticketera
# TICKETERA_API_KEY=ticketera_api_key_aqui
# TICKETS_API_URL=https://tudominio.com/ticketera
# TICKETS_API_KEY=ticketera_api_key_aqui

# Autenticación Ticketera (alternativa a API Key)
TICKETS_API_USERNAME=admin
TICKETS_API_PASSWORD=password_segura_aqui
# O alternativamente:
# TICKETERA_USER=admin
# TICKETERA_PASSWORD=password_segura_aqui

# Configuración de API
BELGRANO_AHORRO_TIMEOUT=30
API_REQUEST_TIMEOUT=30
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=0.5

# Credenciales de login DevOps (dentro de Ticketera)
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=DevOps2025!Secure

# Cookies de sesión (para producción con HTTPS)
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=true
REMEMBER_COOKIE_SECURE=true
```

### Valores de Ejemplo para Ticketera
```bash
FLASK_ENV=production
SECRET_KEY=belgrano_tickets_secret_2025
PORT=5002
HOST=0.0.0.0
DATABASE_URL=sqlite:///belgrano_tickets.db
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
DEVOPS_API_URL=https://tudominio.com/devops
DEVOPS_API_KEY=devops_api_key_2025
BELGRANO_AHORRO_TIMEOUT=30
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=DevOps2025!Secure
SESSION_COOKIE_SECURE=true
```

---

## 🔗 Variables Compartidas entre Servicios

### URLs Base
```bash
# Belgrano Ahorro
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com

# Ticketera/DevOps
TICKETERA_URL=https://tudominio.com/ticketera
DEVOPS_API_URL=https://tudominio.com/devops
```

### API Keys Compartidas
```bash
# Para comunicación entre servicios
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025
DEVOPS_API_KEY=devops_api_key_2025
```

---

## 📝 Notas Importantes

### Seguridad
- ⚠️ **NUNCA** subas las variables reales a repositorios públicos
- 🔒 Usa secrets management de tu plataforma (Render, Heroku, AWS, etc.)
- 🔐 Genera `SECRET_KEY` únicos y seguros para cada servicio
- 🛡️ En producción, usa `SESSION_COOKIE_SECURE=true` solo si tienes HTTPS

### Prioridad de Variables
Algunas variables tienen alias/alternativas:
- `DEVOPS_API_URL` tiene prioridad sobre `TICKETERA_URL`
- `TICKETS_API_KEY` tiene prioridad sobre `TICKETERA_API_KEY`
- Para autenticación Ticketera: primero se intenta API Key, luego user/password

### Base de Datos
- En desarrollo: SQLite es suficiente (`sqlite:///archivo.db`)
- En producción: considera PostgreSQL o MySQL (`postgresql://user:pass@host:port/db`)

---

## 🚀 Ejemplo de Deploy en Render.com

### DevOps Service

#### Archivos Necesarios:
- ✅ `devops/app.py` - Aplicación Flask principal
- ✅ `devops/wsgi.py` - Entry point para Gunicorn
- ✅ `devops/requirements.txt` - Dependencias
- ✅ `devops/routes.py` - Rutas de DevOps
- ✅ `devops/manager_unified.py` - Gestor de APIs

#### Configuración de Render:

**Build Command:**
```bash
cd devops && pip install -r requirements.txt
```

**Start Command (Recomendado):**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 5 wsgi_devops:application
```

**Alternativa si ejecutas desde el directorio devops:**
```bash
cd devops && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 5 wsgi:application
```

**O usando Python directamente:**
```bash
cd devops && python app.py
```

**Environment Variables en Render:**
```bash
FLASK_ENV=production
SECRET_KEY=<genera-uno-seguro>
PORT=5000
HOST=0.0.0.0
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=<tu-api-key>
API_TIMEOUT_SECS=15
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=0.5
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax
REMEMBER_COOKIE_SECURE=true

# Opcional - para comunicación con Ticketera
TICKETS_API_URL=https://tu-ticketera.onrender.com
TICKETS_API_KEY=<ticketera-api-key>
```

### Belgrano Ahorro Service
```bash
FLASK_ENV=production
SECRET_KEY=<genera-uno-seguro>
PORT=5000
HOST=0.0.0.0
DATABASE_URL=<postgres-url-si-usas-postgres>
BELGRANO_AHORRO_API_KEY=<tu-api-key>
DEVOPS_API_KEY=<devops-api-key>
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
DEVOPS_API_URL=https://tu-devos-service.onrender.com/devops
```

### Ticketera Service
```bash
FLASK_ENV=production
SECRET_KEY=<genera-uno-seguro>
PORT=5002
HOST=0.0.0.0
DATABASE_URL=<postgres-url-si-usas-postgres>
BELGRANO_AHORRO_URL=https://belgranoahorro-hp30.onrender.com
BELGRANO_AHORRO_API_KEY=<belgrano-api-key>
DEVOPS_API_URL=https://tu-devos-service.onrender.com/devops
DEVOPS_API_KEY=<devops-api-key>
BELGRANO_AHORRO_TIMEOUT=30
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=<password-segura>
SESSION_COOKIE_SECURE=true
```

---

## ✅ Checklist de Configuración

### DevOps
- [ ] `BELGRANO_AHORRO_URL` configurada
- [ ] `BELGRANO_AHORRO_API_KEY` configurada
- [ ] `SECRET_KEY` configurada (única)
- [ ] `SESSION_COOKIE_SECURE=true` (si usas HTTPS)

### Belgrano Ahorro
- [ ] `SECRET_KEY` configurada (única)
- [ ] `DATABASE_URL` configurada
- [ ] `BELGRANO_AHORRO_API_KEY` configurada
- [ ] `DEVOPS_API_URL` apunta a servicio DevOps
- [ ] `DEVOPS_API_KEY` configurada

### Ticketera
- [ ] `SECRET_KEY` configurada (única)
- [ ] `DATABASE_URL` configurada
- [ ] `BELGRANO_AHORRO_URL` y ` exacta`
- [ ] `BELGRANO_AHORRO_API_KEY` configurada
- [ ] `DEVOPS_API_URL` y `DEVOPS_API_KEY` configuradas
- [ ] `DEVOPS_USERNAME` y `DEVOPS_PASSWORD` configuradas
- [ ] `SESSION_COOKIE_SECURE=true` (si usas HTTPS)




