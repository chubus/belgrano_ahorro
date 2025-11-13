# 🚀 GUÍA COMPLETA: Configurar PostgreSQL y Migrar

## 📋 **PASO A PASO**

### **PASO 1: Crear Base de Datos PostgreSQL en Render**

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configuración:
   - **Name**: `belgrano-ahorro-db`
   - **Database**: `belgrano_ahorro`
   - **User**: `belgrano_ahorro_user`
   - **Region**: Elige la más cercana
   - **Plan**: **Free** (suficiente para empezar)
4. Click **"Create Database"**
5. Espera a que se cree (1-2 minutos)

### **PASO 2: Obtener Connection String**

1. Una vez creada, ve a la base de datos
2. En la pestaña **"Info"**, busca **"Internal Database URL"**
3. Copia la URL completa (algo como):
   ```
   postgresql://belgrano_ahorro_user:password@dpg-xxxxx-a/belgrano_ahorro
   ```
4. **IMPORTANTE**: Usa la **Internal Database URL**, NO la externa

### **PASO 3: Configurar Variable de Entorno en Render**

1. Ve a tu servicio web (Belgrano Ahorro) en Render
2. **Settings** → **Environment**
3. Click **"Add Environment Variable"**
4. Agregar:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la Internal Database URL que copiaste
5. Click **"Save Changes"**

### **PASO 4: Inicializar Tablas en PostgreSQL**

Tienes dos opciones:

#### **Opción A: Automático (Recomendado)**
Las tablas se crearán automáticamente cuando la aplicación inicie por primera vez con `DATABASE_URL` configurada.

#### **Opción B: Manual**
Si prefieres crear las tablas manualmente:

1. Conecta a tu base de datos PostgreSQL (puedes usar psql o un cliente)
2. Ejecuta el script `create_postgres_tables.sql`
3. O ejecuta el script Python:
   ```bash
   python init_postgres_db.py
   ```

### **PASO 5: Migrar Datos Existentes (Opcional)**

Si ya tienes datos en SQLite local y quieres migrarlos:

```bash
# Asegúrate de tener DATABASE_URL configurada
export DATABASE_URL="postgresql://..."

# Ejecutar migración
python migrate_sqlite_to_postgres.py

# Verificar migración
python migrate_sqlite_to_postgres.py --verify
```

### **PASO 6: Redeploy**

1. Render detectará el cambio en `DATABASE_URL` y hará redeploy automático
2. O manualmente: **Manual Deploy** → **Deploy latest commit**

### **PASO 7: Verificar**

Revisa los logs del servicio. Deberías ver:
```
✅ Configurado para usar PostgreSQL
✅ Tablas de API verificadas/creadas en PostgreSQL
```

---

## ✅ **VERIFICACIÓN**

### **1. Verificar que está usando PostgreSQL:**

En los logs deberías ver:
```
✅ Configurado para usar PostgreSQL
```

Si ves:
```
ℹ️ Usando SQLite (desarrollo)
```
Significa que `DATABASE_URL` no está configurada correctamente.

### **2. Verificar que las tablas existen:**

Puedes conectarte a PostgreSQL y ejecutar:
```sql
\dt
```

Deberías ver las tablas: `negocios`, `productos`, `categorias`, `sucursales`, `ofertas`, etc.

### **3. Probar crear un producto desde DevOps:**

1. Crear un producto desde DevOps
2. Verificar que aparece en Belgrano Ahorro
3. Hacer un redeploy
4. Verificar que el producto sigue ahí (persistencia)

---

## 🔧 **TROUBLESHOOTING**

### **Error: "psycopg2 not found"**
```bash
# Asegúrate de que requirements.txt incluye:
psycopg2-binary>=2.9.0

# Y que se instaló en Render
```

### **Error: "Connection refused"**
- Verifica que estás usando la **Internal Database URL** (no la externa)
- Verifica que la base de datos está activa en Render
- Verifica que el servicio web está en la misma región que la base de datos

### **Error: "Table does not exist"**
- Las tablas se crean automáticamente al iniciar
- Si no se crean, ejecuta `init_postgres_db.py` manualmente
- Revisa los logs para ver errores específicos

### **Error: "DATABASE_URL inválida"**
- Asegúrate de que la URL comienza con `postgresql://` o `postgres://`
- Verifica que no tiene espacios o caracteres especiales
- Usa la Internal Database URL de Render

---

## 📊 **ESTRUCTURA DE TABLAS**

Las siguientes tablas se crearán automáticamente:

- ✅ `usuarios` - Usuarios del sistema
- ✅ `negocios` - Negocios creados desde DevOps
- ✅ `categorias` - Categorías de productos
- ✅ `productos` - Productos creados desde DevOps
- ✅ `sucursales` - Sucursales creadas desde DevOps
- ✅ `ofertas` - Ofertas creadas desde DevOps
- ✅ `pedidos` - Pedidos realizados por clientes
- ✅ `pedido_items` - Items de cada pedido
- ✅ `carrito` - Carrito de compras

---

## 🎯 **RESULTADO ESPERADO**

Una vez configurado:

✅ **Los datos persisten** después de cada deploy
✅ **Los cambios desde DevOps se guardan permanentemente**
✅ **No se pierden datos** en reinicios o actualizaciones
✅ **Base de datos escalable** para producción
✅ **Backups automáticos** de Render

---

## 📝 **NOTAS IMPORTANTES**

- **Plan Free de Render**: 
  - 90 días de inactividad = base de datos pausada (pero datos se mantienen)
  - 1GB de almacenamiento (suficiente para empezar)
  - Backups automáticos incluidos

- **Migración de datos**:
  - Si tienes datos importantes en SQLite, migra antes de usar en producción
  - Si los datos vienen de DevOps, simplemente recrea desde DevOps después de configurar PostgreSQL

- **Desarrollo vs Producción**:
  - **Desarrollo local**: Usa SQLite (sin DATABASE_URL)
  - **Producción (Render)**: Usa PostgreSQL (con DATABASE_URL)

---

## ✅ **CHECKLIST FINAL**

- [ ] Base de datos PostgreSQL creada en Render
- [ ] Variable `DATABASE_URL` configurada en el servicio web
- [ ] `psycopg2-binary` en `requirements.txt`
- [ ] Redeploy realizado
- [ ] Logs muestran "✅ Configurado para usar PostgreSQL"
- [ ] Tablas creadas (verificar con `\dt` o logs)
- [ ] Crear un producto desde DevOps y verificar que persiste después de redeploy
- [ ] (Opcional) Datos migrados desde SQLite

---

## 🆘 **SOPORTE**

Si tienes problemas:

1. Revisa los logs del servicio en Render
2. Verifica que `DATABASE_URL` está configurada correctamente
3. Verifica que la base de datos está activa
4. Revisa `GUIA_PERSISTENCIA_POSTGRESQL.md` para más detalles

