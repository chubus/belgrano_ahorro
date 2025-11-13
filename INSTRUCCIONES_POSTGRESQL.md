# 🚀 INSTRUCCIONES RÁPIDAS: Configurar PostgreSQL

## ✅ **LO QUE YA ESTÁ LISTO**

- ✅ Código preparado para PostgreSQL
- ✅ Detección automática SQLite/PostgreSQL
- ✅ Scripts de migración creados
- ✅ Documentación completa

## 🎯 **LO QUE TÚ DEBES HACER (5 minutos)**

### **PASO 1: Crear Base de Datos PostgreSQL** (2 min)

1. Ve a https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configura:
   - **Name**: `belgrano-ahorro-db`
   - **Database**: `belgrano_ahorro`
   - **Plan**: **Free**
4. Click **"Create Database"**

### **PASO 2: Copiar Connection String** (1 min)

1. Una vez creada, ve a la base de datos
2. Pestaña **"Info"**
3. Copia **"Internal Database URL"** (algo como):
   ```
   postgresql://user:pass@host:5432/dbname
   ```

### **PASO 3: Configurar Variable de Entorno** (1 min)

1. Ve a tu servicio web (Belgrano Ahorro) en Render
2. **Settings** → **Environment**
3. Click **"Add Environment Variable"**
4. Agregar:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la Internal Database URL
5. **Save Changes**

### **PASO 4: Esperar Redeploy** (1 min)

Render hará redeploy automáticamente. Espera 1-2 minutos.

### **PASO 5: Verificar** (30 seg)

Revisa los logs. Deberías ver:
```
✅ Configurado para usar PostgreSQL
✅ Tablas de API verificadas/creadas en PostgreSQL
```

---

## ✅ **LISTO!**

Una vez configurado, los datos persisten después de cada deploy.

---

## 🔄 **MIGRAR DATOS EXISTENTES (Opcional)**

Si tienes datos en SQLite local:

```bash
# Configurar DATABASE_URL
export DATABASE_URL="postgresql://..."

# Migrar
python migrate_sqlite_to_postgres.py

# Verificar
python migrate_sqlite_to_postgres.py --verify
```

---

## 🆘 **SI ALGO FALLA**

1. Verifica que `DATABASE_URL` está configurada
2. Usa la **Internal Database URL** (no la externa)
3. Revisa los logs del servicio
4. Ver `GUIA_CONFIGURACION_POSTGRESQL.md` para más ayuda

