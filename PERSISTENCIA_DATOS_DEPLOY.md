# ⚠️ PROBLEMA DE PERSISTENCIA POST-DEPLOY

## 🔴 **PROBLEMA ACTUAL**

**NO hay persistencia de datos post-deploy** porque:

1. **SQLite es efímero**: El archivo `belgrano_ahorro.db` se guarda en el sistema de archivos local
2. **Render.com borra el sistema de archivos** en cada:
   - Redeploy
   - Reinicio del servicio
   - Actualización del código
   - Cambio de configuración

**Resultado**: Todos los datos creados desde DevOps se pierden después de cada deploy.

---

## ✅ **SOLUCIONES DISPONIBLES**

### **Opción 1: PostgreSQL (RECOMENDADO) ⭐**

Render.com ofrece bases de datos PostgreSQL persistentes y gratuitas.

#### **Pasos para implementar:**

1. **Crear base de datos PostgreSQL en Render:**
   - Dashboard → New → PostgreSQL
   - Plan: Free (suficiente para empezar)
   - Copiar la `DATABASE_URL` interna

2. **Configurar variable de entorno:**
   ```bash
   DATABASE_URL=postgresql://usuario:password@host:5432/belgrano_ahorro
   ```

3. **Instalar dependencias:**
   ```bash
   pip install psycopg2-binary sqlalchemy
   ```

4. **Actualizar código para usar PostgreSQL** (ver siguiente sección)

---

### **Opción 2: Backups Automáticos a S3/Cloud Storage**

Crear backups periódicos de SQLite a un servicio de almacenamiento externo.

**Ventajas:**
- Mantiene SQLite (sin cambios de código)
- Backups automáticos

**Desventajas:**
- Requiere servicio externo (S3, Google Cloud Storage, etc.)
- No es tiempo real (solo backups)

---

### **Opción 3: Volúmenes Persistentes (Solo Docker)**

Si usas Docker con volúmenes montados, los datos persisten.

**Limitación:** Render.com no soporta volúmenes persistentes en el plan gratuito.

---

## 🚀 **IMPLEMENTACIÓN: PostgreSQL**

### **1. Actualizar `requirements.txt`:**
```txt
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
```

### **2. Crear módulo de base de datos compatible:**

El código actual usa SQLite directamente. Necesitamos crear una capa de abstracción que soporte tanto SQLite como PostgreSQL.

### **3. Configurar variable de entorno en Render:**

En el Dashboard de Render:
- Settings → Environment
- Agregar: `DATABASE_URL=postgresql://...` (la URL de tu base de datos PostgreSQL)

---

## 📋 **CHECKLIST DE MIGRACIÓN**

- [ ] Crear base de datos PostgreSQL en Render
- [ ] Instalar `psycopg2-binary` y `sqlalchemy`
- [ ] Actualizar código para usar SQLAlchemy (abstracción)
- [ ] Crear script de migración de SQLite → PostgreSQL
- [ ] Configurar `DATABASE_URL` en variables de entorno
- [ ] Probar en staging antes de producción
- [ ] Hacer backup de datos existentes antes de migrar

---

## 🔧 **CONFIGURACIÓN ACTUAL**

**Estado actual:**
- ✅ SQLite funcionando en desarrollo
- ❌ SQLite NO persiste en producción (Render.com)
- ⚠️ Datos se pierden en cada deploy

**Recomendación inmediata:**
1. **Usar PostgreSQL** para producción (gratis en Render)
2. **Mantener SQLite** para desarrollo local
3. **Migrar datos** existentes antes del deploy

---

## 📝 **NOTAS IMPORTANTES**

- Los datos creados desde DevOps **NO se guardan** actualmente en producción
- Cada vez que se hace deploy, se pierden todos los datos
- **Solución urgente**: Migrar a PostgreSQL antes de usar en producción

