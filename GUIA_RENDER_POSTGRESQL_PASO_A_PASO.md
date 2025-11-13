# 🚀 GUÍA PASO A PASO: Configurar PostgreSQL en Render

## 📋 **PASO 1: Crear Base de Datos PostgreSQL**

### **1.1. Acceder a Render Dashboard**
1. Ve a https://dashboard.render.com
2. Inicia sesión con tu cuenta

### **1.2. Crear Nueva Base de Datos**
1. En el dashboard, click en el botón **"New +"** (esquina superior derecha)
2. Selecciona **"PostgreSQL"** del menú desplegable

### **1.3. Configurar Base de Datos**
Completa el formulario con estos valores:

```
Name: belgrano-ahorro-db
Database: belgrano_ahorro
User: belgrano_ahorro_user
Region: [Elige la región más cercana a tu ubicación]
  - Ejemplos: Oregon (US West), Frankfurt (EU Central), etc.
Plan: Free
  - 1GB de almacenamiento (suficiente para empezar)
  - Backups automáticos incluidos
```

### **1.4. Crear Base de Datos**
1. Click en **"Create Database"**
2. Espera 1-2 minutos mientras Render crea la base de datos
3. Verás un mensaje de "Creating..." que cambiará a "Available" cuando esté lista

---

## 📋 **PASO 2: Obtener Connection String**

### **2.1. Acceder a la Base de Datos**
1. Una vez creada, click en el nombre de la base de datos (`belgrano-ahorro-db`)
2. Esto te llevará a la página de detalles

### **2.2. Encontrar Internal Database URL**
1. En la página de detalles, busca la sección **"Connections"**
2. Busca **"Internal Database URL"** (NO uses la "External Database URL")
3. Debería verse algo como:
   ```
   postgresql://belgrano_ahorro_user:xxxxx@dpg-xxxxx-a.oregon-postgres.render.com/belgrano_ahorro
   ```
4. **IMPORTANTE**: Copia esta URL completa (incluye la contraseña)

### **2.3. Guardar la URL**
- Guárdala en un lugar seguro temporalmente
- La necesitarás en el siguiente paso

---

## 📋 **PASO 3: Configurar Variable de Entorno en el Servicio Web**

### **3.1. Acceder a tu Servicio Web**
1. En el dashboard de Render, busca tu servicio web de Belgrano Ahorro
2. Click en el nombre del servicio para abrir sus detalles

### **3.2. Ir a Configuración de Entorno**
1. En el menú lateral, click en **"Environment"**
2. O ve directamente a: **Settings** → **Environment**

### **3.3. Agregar Variable DATABASE_URL**
1. Scroll hasta la sección **"Environment Variables"**
2. Click en **"Add Environment Variable"** o el botón **"+ Add"**
3. Completa:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la Internal Database URL que copiaste en el Paso 2
4. **IMPORTANTE**: 
   - No agregues espacios antes o después
   - Copia la URL completa tal como está
   - Debe comenzar con `postgresql://` o `postgres://`

### **3.4. Guardar Cambios**
1. Click en **"Save Changes"** o **"Update"**
2. Render mostrará un mensaje de confirmación

---

## 📋 **PASO 4: Redeploy Automático**

### **4.1. Render Detecta el Cambio**
- Render detectará automáticamente el cambio en las variables de entorno
- Verás un mensaje como "New deploy triggered" o "Redeploying..."

### **4.2. Esperar el Deploy**
1. Ve a la pestaña **"Events"** o **"Logs"** de tu servicio
2. Verás el proceso de deploy en tiempo real
3. Espera 2-3 minutos mientras:
   - Render instala dependencias (`psycopg2-binary`)
   - La aplicación se inicia
   - Las tablas se crean automáticamente

### **4.3. Verificar el Deploy**
- El deploy está completo cuando ves:
  - Estado: **"Live"** (verde)
  - Mensaje: "Your service is live at https://..."

---

## 📋 **PASO 5: Verificar que Funciona**

### **5.1. Revisar Logs**
1. En tu servicio web, ve a la pestaña **"Logs"**
2. Busca estas líneas (deberían aparecer al inicio):
   ```
   ✅ Configurado para usar PostgreSQL
   ✅ Tablas de API verificadas/creadas en PostgreSQL
   ```

### **5.2. Si NO ves esas líneas:**
- Busca: `ℹ️ Usando SQLite (desarrollo)`
- Esto significa que `DATABASE_URL` no está configurada correctamente
- Verifica:
  - Que la variable se llama exactamente `DATABASE_URL` (mayúsculas)
  - Que el valor es la Internal Database URL completa
  - Que guardaste los cambios

### **5.3. Probar la API**
Puedes probar que funciona haciendo un request:
```bash
curl https://tu-app.onrender.com/api/health
```

Debería responder con status 200.

---

## 📋 **PASO 6: Probar Persistencia**

### **6.1. Crear un Producto desde DevOps**
1. Accede a tu panel de DevOps
2. Crea un nuevo producto
3. Verifica que aparece en Belgrano Ahorro

### **6.2. Hacer Redeploy Manual**
1. En Render, ve a tu servicio web
2. Click en **"Manual Deploy"** → **"Deploy latest commit"**
3. Espera a que termine el deploy

### **6.3. Verificar que el Producto Sigue Ahí**
1. Recarga Belgrano Ahorro
2. El producto que creaste debería seguir visible
3. ✅ **¡Persistencia funcionando!**

---

## 🔧 **TROUBLESHOOTING**

### **Problema: "psycopg2 not found"**
**Solución:**
1. Verifica que `requirements.txt` incluye `psycopg2-binary>=2.9.0`
2. Si no está, agrégalo y haz commit
3. Render reinstalará las dependencias automáticamente

### **Problema: "Connection refused"**
**Solución:**
1. Verifica que estás usando la **Internal Database URL** (no la externa)
2. Verifica que la base de datos está en estado "Available" (no pausada)
3. Verifica que el servicio web está en la misma región que la base de datos

### **Problema: "Table does not exist"**
**Solución:**
1. Las tablas se crean automáticamente al iniciar
2. Si no se crean, revisa los logs para ver errores específicos
3. Puedes ejecutar manualmente el script SQL si es necesario

### **Problema: "DATABASE_URL inválida"**
**Solución:**
1. Verifica que la URL comienza con `postgresql://` o `postgres://`
2. Verifica que no tiene espacios al inicio o final
3. Verifica que es la Internal Database URL (no la externa)
4. Copia la URL nuevamente desde Render

---

## ✅ **CHECKLIST DE VERIFICACIÓN**

Marca cada paso cuando lo completes:

- [ ] Base de datos PostgreSQL creada en Render
- [ ] Internal Database URL copiada
- [ ] Variable `DATABASE_URL` agregada al servicio web
- [ ] Cambios guardados
- [ ] Deploy completado
- [ ] Logs muestran "✅ Configurado para usar PostgreSQL"
- [ ] Tablas creadas (verificar en logs)
- [ ] Producto creado desde DevOps
- [ ] Redeploy realizado
- [ ] Producto sigue visible después del redeploy

---

## 🎯 **RESULTADO ESPERADO**

Una vez completados todos los pasos:

✅ **Los datos persisten** después de cada deploy
✅ **Los cambios desde DevOps se guardan permanentemente**
✅ **No se pierden datos** en reinicios o actualizaciones
✅ **Base de datos escalable** lista para producción

---

## 📞 **SIGUIENTE PASO**

Una vez que hayas completado estos pasos, avísame y:
1. Verificaremos juntos que todo funciona
2. Probaremos crear productos desde DevOps
3. Verificaremos que persisten después de redeploy

