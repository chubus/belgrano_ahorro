# 🗄️ Configuración PostgreSQL para Belgrano Ahorro

## 📋 **RESUMEN**

Este proyecto ahora soporta **PostgreSQL** para persistencia de datos en producción (Render.com), manteniendo **SQLite** para desarrollo local.

## ✅ **ESTADO ACTUAL**

- ✅ Código preparado para PostgreSQL
- ✅ Detección automática SQLite/PostgreSQL
- ✅ Scripts de migración creados
- ✅ Documentación completa

## 🚀 **CONFIGURACIÓN RÁPIDA (5 minutos)**

### **Paso 1: Crear PostgreSQL en Render**
1. Dashboard → New + → PostgreSQL
2. Name: `belgrano-ahorro-db`
3. Plan: Free
4. Create Database

### **Paso 2: Configurar DATABASE_URL**
1. Servicio Web → Settings → Environment
2. Agregar: `DATABASE_URL` = (Internal Database URL)
3. Save Changes

### **Paso 3: Verificar**
Revisa logs para ver:
```
✅ Configurado para usar PostgreSQL
```

**¡Listo!** Los datos ahora persisten.

---

## 📚 **DOCUMENTACIÓN**

- **`INICIO_RAPIDO_RENDER.md`** - Guía rápida (5 min)
- **`GUIA_RENDER_POSTGRESQL_PASO_A_PASO.md`** - Guía detallada paso a paso
- **`GUIA_CONFIGURACION_POSTGRESQL.md`** - Guía técnica completa
- **`PERSISTENCIA_DATOS_DEPLOY.md`** - Explicación del problema

---

## 🔧 **ARCHIVOS IMPORTANTES**

### **Infraestructura**
- `db_abstraction.py` - Capa de abstracción SQLite/PostgreSQL
- `create_postgres_tables.sql` - Script SQL para crear tablas
- `init_postgres_db.py` - Script de inicialización
- `migrate_sqlite_to_postgres.py` - Script de migración

### **Código Actualizado**
- `api_belgrano_ahorro.py` - Funciones compatibles con PostgreSQL
- `requirements.txt` - Incluye `psycopg2-binary`

---

## 🎯 **CÓMO FUNCIONA**

### **Detección Automática**
El código detecta automáticamente qué base de datos usar:

- **Sin `DATABASE_URL`** → Usa SQLite (desarrollo)
- **Con `DATABASE_URL` (PostgreSQL)** → Usa PostgreSQL (producción)

### **Funciones Helper**
Se crearon funciones helper para compatibilidad:

- `execute_insert_returning_id()` - INSERT con retorno de ID
- `execute_select()` - SELECT compatible
- `execute_update_delete()` - UPDATE/DELETE compatible

---

## 🔄 **MIGRACIÓN DE DATOS**

Si tienes datos en SQLite local:

```bash
export DATABASE_URL="postgresql://..."
python migrate_sqlite_to_postgres.py
python migrate_sqlite_to_postgres.py --verify
```

---

## ✅ **VERIFICACIÓN**

### **1. Logs del Servicio**
Deberías ver:
```
✅ Configurado para usar PostgreSQL
✅ Tablas de API verificadas/creadas en PostgreSQL
```

### **2. Probar Persistencia**
1. Crear producto desde DevOps
2. Hacer redeploy
3. Verificar que el producto sigue ahí

---

## 🆘 **TROUBLESHOOTING**

### **No veo "✅ Configurado para usar PostgreSQL"**
- Verifica que `DATABASE_URL` está configurada
- Verifica que es la Internal Database URL

### **Error de conexión**
- Verifica que la base de datos está "Available"
- Verifica que usas Internal Database URL

### **Tablas no se crean**
- Revisa logs para errores específicos
- Las tablas se crean automáticamente al iniciar

---

## 📞 **SIGUIENTE PASO**

Sigue la guía: **`GUIA_RENDER_POSTGRESQL_PASO_A_PASO.md`**

