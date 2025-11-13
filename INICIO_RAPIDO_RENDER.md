# ⚡ INICIO RÁPIDO: Configurar PostgreSQL en Render (5 minutos)

## 🎯 **PASOS RÁPIDOS**

### **1. Crear PostgreSQL** (2 min)
```
Render Dashboard → New + → PostgreSQL
Name: belgrano-ahorro-db
Plan: Free
Create Database
```

### **2. Copiar URL** (30 seg)
```
Base de datos → Info → Internal Database URL
Copiar URL completa
```

### **3. Configurar Variable** (1 min)
```
Servicio Web → Settings → Environment
Add Environment Variable:
  Key: DATABASE_URL
  Value: [Pegar URL copiada]
Save Changes
```

### **4. Esperar Deploy** (1-2 min)
- Render hace deploy automático
- Esperar a que termine

### **5. Verificar** (30 seg)
```
Logs del servicio → Buscar:
✅ Configurado para usar PostgreSQL
✅ Tablas de API verificadas/creadas en PostgreSQL
```

---

## ✅ **LISTO!**

Si ves esos mensajes en los logs, **¡todo funciona!**

Los datos ahora persisten después de cada deploy.

---

## 📖 **GUÍA COMPLETA**

Para más detalles, ver: `GUIA_RENDER_POSTGRESQL_PASO_A_PASO.md`

---

## 🆘 **PROBLEMAS?**

1. **No ves "✅ Configurado para usar PostgreSQL"**
   - Verifica que `DATABASE_URL` está configurada
   - Verifica que es la Internal Database URL (no externa)

2. **Error de conexión**
   - Verifica que la base de datos está "Available" (no pausada)
   - Verifica que estás usando Internal Database URL

3. **Tablas no se crean**
   - Revisa los logs para ver errores específicos
   - Las tablas se crean automáticamente al iniciar

