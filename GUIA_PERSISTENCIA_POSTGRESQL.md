# 🗄️ GUÍA: Configurar PostgreSQL para Persistencia Post-Deploy

## ⚠️ PROBLEMA ACTUAL

**SQLite NO persiste en Render.com** - Los datos se pierden en cada deploy.

## ✅ SOLUCIÓN: PostgreSQL

### **Paso 1: Crear Base de Datos PostgreSQL en Render**

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New +"** → **"PostgreSQL"**
3. Configuración:
   - **Name**: `belgrano-ahorro-db`
   - **Database**: `belgrano_ahorro`
   - **User**: `belgrano_ahorro_user`
   - **Region**: Elige la más cercana
   - **Plan**: **Free** (suficiente para empezar)
4. Click **"Create Database"**

### **Paso 2: Obtener Connection String**

1. Una vez creada la base de datos, ve a **"Info"**
2. Copia la **"Internal Database URL"** (algo como):
   ```
   postgresql://belgrano_ahorro_user:password@dpg-xxxxx-a/belgrano_ahorro
   ```

### **Paso 3: Configurar Variable de Entorno**

1. Ve a tu servicio web en Render (Belgrano Ahorro)
2. **Settings** → **Environment**
3. Agregar nueva variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la Internal Database URL que copiaste
4. Click **"Save Changes"**

### **Paso 4: Redeploy**

1. Render detectará el cambio y hará redeploy automático
2. O manualmente: **Manual Deploy** → **Deploy latest commit**

---

## 🔧 **VERIFICACIÓN**

### **Verificar que está usando PostgreSQL:**

Revisa los logs del servicio. Deberías ver:
```
✅ Configurado para usar PostgreSQL
✅ Tablas verificadas/creadas en PostgreSQL
```

### **Si ves:**
```
ℹ️ Usando SQLite (desarrollo)
```
Significa que `DATABASE_URL` no está configurada correctamente.

---

## 📋 **MIGRACIÓN DE DATOS (Opcional)**

Si ya tienes datos en SQLite local y quieres migrarlos:

### **Opción 1: Script de Migración Automática**

```python
# migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

# Conectar a SQLite
sqlite_conn = sqlite3.connect('belgrano_ahorro.db')
sqlite_cursor = sqlite_conn.cursor()

# Conectar a PostgreSQL
postgres_url = os.getenv('DATABASE_URL')
postgres_conn = psycopg2.connect(postgres_url)
postgres_cursor = postgres_conn.cursor()

# Migrar negocios
sqlite_cursor.execute('SELECT * FROM negocios')
negocios = sqlite_cursor.fetchall()
# ... insertar en PostgreSQL

# Repetir para productos, ofertas, sucursales, etc.
```

### **Opción 2: Recrear desde DevOps**

Si los datos vienen de DevOps, simplemente:
1. Configurar PostgreSQL
2. Crear los datos nuevamente desde DevOps
3. Los datos se guardarán permanentemente

---

## 🎯 **RESULTADO**

Una vez configurado PostgreSQL:

✅ **Los datos persisten** después de cada deploy
✅ **Los cambios desde DevOps se guardan permanentemente**
✅ **No se pierden datos** en reinicios o actualizaciones
✅ **Base de datos escalable** para producción

---

## 📝 **NOTAS IMPORTANTES**

- **Plan Free de Render**: 90 días de inactividad = base de datos pausada (pero datos se mantienen)
- **Backups**: Render hace backups automáticos de PostgreSQL
- **Límites Free**: 1GB de almacenamiento (suficiente para empezar)

---

## 🆘 **TROUBLESHOOTING**

### **Error: "psycopg2 not found"**
```bash
# Asegúrate de que requirements.txt incluye:
psycopg2-binary>=2.9.0
```

### **Error: "Connection refused"**
- Verifica que estás usando la **Internal Database URL** (no la externa)
- Verifica que la base de datos está activa en Render

### **Error: "Table does not exist"**
- Las tablas se crean automáticamente al iniciar
- Si no se crean, revisa los logs para ver errores

---

## ✅ **CHECKLIST**

- [ ] Base de datos PostgreSQL creada en Render
- [ ] Variable `DATABASE_URL` configurada en el servicio web
- [ ] `psycopg2-binary` en `requirements.txt`
- [ ] Redeploy realizado
- [ ] Logs muestran "✅ Configurado para usar PostgreSQL"
- [ ] Crear un producto desde DevOps y verificar que persiste después de redeploy

