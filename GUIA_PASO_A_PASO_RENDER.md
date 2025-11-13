# 🎯 GUÍA PASO A PASO: Configurar PostgreSQL en Render

## ✅ **VERIFICACIÓN PREVIA**

Antes de empezar, verifica que tienes:
- [x] Acceso a https://dashboard.render.com
- [x] Tu servicio web de Belgrano Ahorro desplegado en Render
- [x] Permisos para crear bases de datos y modificar variables de entorno

---

## 📋 **PASO 1: CREAR BASE DE DATOS POSTGRESQL**

### **1.1. Acceder a Render Dashboard**
1. Abre tu navegador
2. Ve a: **https://dashboard.render.com**
3. Inicia sesión con tu cuenta

### **1.2. Crear Nueva Base de Datos**
1. En la esquina superior derecha, busca el botón **"New +"**
2. Click en **"New +"**
3. Del menú desplegable, selecciona **"PostgreSQL"**

### **1.3. Configurar la Base de Datos**
Completa el formulario con estos valores exactos:

```
┌─────────────────────────────────────────┐
│ Name: belgrano-ahorro-db                │
│ Database: belgrano_ahorro               │
│ User: belgrano_ahorro_user              │
│ Region: [Elige la más cercana]          │
│   - Oregon (US West)                    │
│   - Frankfurt (EU Central)              │
│   - Singapore (AP Southeast)            │
│ Plan: Free                              │
└─────────────────────────────────────────┘
```

**Nota importante:**
- El **Plan Free** incluye 1GB de almacenamiento (suficiente para empezar)
- Incluye backups automáticos
- La base de datos puede pausarse después de 90 días de inactividad (pero los datos se mantienen)

### **1.4. Crear la Base de Datos**
1. Revisa que todos los campos estén correctos
2. Click en el botón **"Create Database"** (verde, abajo)
3. Verás un mensaje: **"Creating..."**
4. Espera 1-2 minutos mientras Render crea la base de datos
5. Cuando esté lista, verás: **"Available"** (estado verde)

**✅ Paso 1 completado cuando veas "Available"**

---

## 📋 **PASO 2: OBTENER INTERNAL DATABASE URL**

### **2.1. Acceder a la Base de Datos**
1. Una vez que la base de datos esté "Available"
2. Click en el nombre: **"belgrano-ahorro-db"**
3. Esto te llevará a la página de detalles de la base de datos

### **2.2. Encontrar la Internal Database URL**
1. En la página de detalles, busca la sección **"Connections"**
2. Verás dos URLs:
   - ❌ **External Database URL** (NO uses esta)
   - ✅ **Internal Database URL** (USA ESTA)

### **2.3. Copiar la URL**
1. Busca el campo **"Internal Database URL"**
2. Debería verse algo como:
   ```
   postgresql://belgrano_ahorro_user:xxxxx@dpg-xxxxx-a.oregon-postgres.render.com/belgrano_ahorro
   ```
3. Click en el ícono de **copiar** (📋) o selecciona y copia toda la URL
4. **IMPORTANTE**: Copia la URL completa, incluyendo la contraseña

### **2.4. Guardar Temporalmente**
- Pega la URL en un bloc de notas o editor de texto
- La necesitarás en el siguiente paso
- **NO la compartas públicamente** (contiene credenciales)

**✅ Paso 2 completado cuando tengas la URL copiada**

---

## 📋 **PASO 3: CONFIGURAR VARIABLE DE ENTORNO**

### **3.1. Acceder a tu Servicio Web**
1. En el dashboard de Render, busca tu servicio web de **Belgrano Ahorro**
2. Click en el nombre del servicio para abrir sus detalles

### **3.2. Ir a Configuración de Entorno**
1. En el menú lateral izquierdo, busca **"Environment"**
2. Click en **"Environment"**
   - O ve directamente a: **Settings** → **Environment**

### **3.3. Agregar Variable DATABASE_URL**
1. Scroll hasta la sección **"Environment Variables"**
2. Verás una lista de variables existentes (si las hay)
3. Busca el botón **"Add Environment Variable"** o **"+ Add"**
4. Click en ese botón

### **3.4. Completar el Formulario**
En el formulario que aparece, completa:

```
┌─────────────────────────────────────────┐
│ Key: DATABASE_URL                       │
│                                         │
│ Value: [Pega aquí la URL que copiaste] │
│                                         │
│ Ejemplo:                                │
│ postgresql://user:pass@host/dbname     │
└─────────────────────────────────────────┘
```

**IMPORTANTE:**
- **Key** debe ser exactamente: `DATABASE_URL` (mayúsculas, sin espacios)
- **Value** debe ser la Internal Database URL completa que copiaste
- No agregues espacios antes o después
- No agregues comillas
- Debe comenzar con `postgresql://` o `postgres://`

### **3.5. Guardar Cambios**
1. Revisa que todo esté correcto
2. Click en **"Save Changes"** o **"Update"**
3. Verás un mensaje de confirmación
4. Render mostrará: **"New deploy triggered"** o **"Redeploying..."**

**✅ Paso 3 completado cuando veas "Save Changes" exitoso**

---

## 📋 **PASO 4: ESPERAR EL DEPLOY**

### **4.1. Render Detecta el Cambio**
- Render detectará automáticamente el cambio en `DATABASE_URL`
- Iniciará un nuevo deploy automáticamente
- Verás un mensaje: **"New deploy triggered"**

### **4.2. Monitorear el Deploy**
1. Ve a la pestaña **"Events"** o **"Logs"** de tu servicio
2. Verás el proceso de deploy en tiempo real:
   ```
   Building...
   Installing dependencies...
   Starting application...
   ```

### **4.3. Tiempo de Espera**
- El deploy puede tardar 2-3 minutos
- Durante este tiempo:
  - Render instala `psycopg2-binary` (driver de PostgreSQL)
  - La aplicación se inicia
  - Las tablas se crean automáticamente en PostgreSQL

### **4.4. Deploy Completado**
El deploy está completo cuando ves:
- Estado: **"Live"** (verde)
- Mensaje: **"Your service is live at https://..."**

**✅ Paso 4 completado cuando veas "Live"**

---

## 📋 **PASO 5: VERIFICAR QUE FUNCIONA**

### **5.1. Revisar los Logs**
1. En tu servicio web, ve a la pestaña **"Logs"**
2. Scroll hacia arriba para ver los logs de inicio
3. Busca estas líneas específicas:

```
✅ Configurado para usar PostgreSQL
✅ Tablas de API verificadas/creadas en PostgreSQL
```

### **5.2. ¿Qué Buscar?**

**✅ CORRECTO - Si ves:**
```
✅ Configurado para usar PostgreSQL
✅ Tablas de API verificadas/creadas en PostgreSQL
```
**¡Perfecto! Todo funciona correctamente.**

**❌ INCORRECTO - Si ves:**
```
ℹ️ Usando SQLite (desarrollo)
```
**Esto significa que `DATABASE_URL` no está configurada correctamente.**

### **5.3. Si NO Ves los Mensajes Correctos**

**Problema:** Ves "Usando SQLite" en lugar de "PostgreSQL"

**Solución:**
1. Verifica que la variable se llama exactamente `DATABASE_URL` (mayúsculas)
2. Verifica que el valor es la Internal Database URL completa
3. Verifica que guardaste los cambios
4. Si todo está bien, espera 1 minuto más y revisa los logs nuevamente

**✅ Paso 5 completado cuando veas "✅ Configurado para usar PostgreSQL"**

---

## 📋 **PASO 6: PROBAR PERSISTENCIA (OPCIONAL PERO RECOMENDADO)**

### **6.1. Crear un Producto desde DevOps**
1. Accede a tu panel de DevOps
2. Crea un nuevo producto (o negocio, categoría, etc.)
3. Verifica que aparece en Belgrano Ahorro

### **6.2. Hacer Redeploy Manual**
1. En Render, ve a tu servicio web
2. Click en **"Manual Deploy"** (menú superior)
3. Selecciona **"Deploy latest commit"**
4. Espera a que termine el deploy (1-2 minutos)

### **6.3. Verificar que el Producto Sigue Ahí**
1. Recarga Belgrano Ahorro en tu navegador
2. El producto que creaste debería seguir visible
3. **¡Persistencia funcionando!** ✅

**✅ Paso 6 completado cuando el producto persiste después del redeploy**

---

## ✅ **CHECKLIST FINAL**

Marca cada paso cuando lo completes:

- [ ] Paso 1: Base de datos PostgreSQL creada (estado "Available")
- [ ] Paso 2: Internal Database URL copiada
- [ ] Paso 3: Variable `DATABASE_URL` agregada al servicio web
- [ ] Paso 4: Deploy completado (estado "Live")
- [ ] Paso 5: Logs muestran "✅ Configurado para usar PostgreSQL"
- [ ] Paso 6: (Opcional) Producto persiste después de redeploy

---

## 🎯 **RESULTADO ESPERADO**

Una vez completados todos los pasos:

✅ **Los datos persisten** después de cada deploy
✅ **Los cambios desde DevOps se guardan permanentemente**
✅ **No se pierden datos** en reinicios o actualizaciones
✅ **Base de datos escalable** lista para producción

---

## 🆘 **TROUBLESHOOTING**

### **Problema 1: "psycopg2 not found"**
**Síntoma:** Error en logs sobre psycopg2

**Solución:**
1. Verifica que `requirements.txt` incluye `psycopg2-binary>=2.9.0`
2. Si no está, agrégalo y haz commit
3. Render reinstalará las dependencias automáticamente

### **Problema 2: "Connection refused"**
**Síntoma:** Error de conexión a la base de datos

**Solución:**
1. Verifica que estás usando la **Internal Database URL** (no la externa)
2. Verifica que la base de datos está en estado "Available" (no pausada)
3. Verifica que el servicio web está en la misma región que la base de datos

### **Problema 3: "Table does not exist"**
**Síntoma:** Error sobre tablas que no existen

**Solución:**
1. Las tablas se crean automáticamente al iniciar
2. Si no se crean, revisa los logs para ver errores específicos
3. Puedes ejecutar manualmente `init_postgres_db.py` si es necesario

### **Problema 4: "DATABASE_URL inválida"**
**Síntoma:** La aplicación no detecta PostgreSQL

**Solución:**
1. Verifica que la URL comienza con `postgresql://` o `postgres://`
2. Verifica que no tiene espacios al inicio o final
3. Verifica que es la Internal Database URL (no la externa)
4. Copia la URL nuevamente desde Render

---

## 📞 **SIGUIENTE PASO**

Una vez que hayas completado estos pasos:

1. ✅ Verifica que los logs muestran "✅ Configurado para usar PostgreSQL"
2. ✅ Prueba crear un producto desde DevOps
3. ✅ Haz redeploy y verifica que persiste
4. ✅ ¡Disfruta de la persistencia de datos!

---

## 💡 **CONSEJOS**

- **Guarda la Internal Database URL** en un lugar seguro (gestor de contraseñas)
- **No compartas la URL públicamente** (contiene credenciales)
- **El plan Free es suficiente** para empezar (1GB de almacenamiento)
- **Los backups son automáticos** en Render
- **La base de datos puede pausarse** después de 90 días de inactividad, pero los datos se mantienen

---

## 🎉 **¡FELICIDADES!**

Si llegaste hasta aquí y todo funciona, **¡has configurado PostgreSQL exitosamente!**

Tus datos ahora persisten permanentemente. 🚀

