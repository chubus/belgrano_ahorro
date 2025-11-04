# 🔒 Guía Segura para Configurar Variables en Render

## 📋 Pasos para Configurar DevOps en Render

### 1. Accede a Render Dashboard
- Ve a: https://dashboard.render.com
- Selecciona tu servicio **DevOps**

### 2. Configura las Variables de Entorno

Ve a **Environment** → **Add Environment Variable** y agrega:

#### Variables OBLIGATORIAS:

| KEY | VALUE |
|-----|-------|
| `BELGRANO_AHORRO_URL` | `https://belgranoahorro-aliq.onrender.com` |
| `BELGRANO_AHORRO_API_KEY` | `[La misma API key que está en Belgrano Ahorro]` |
| `FLASK_ENV` | `production` |
| `PORT` | `5000` |

#### Variables RECOMENDADAS:

| KEY | VALUE |
|-----|-------|
| `SECRET_KEY` | `[Genera un valor único y seguro]` |
| `SESSION_COOKIE_SECURE` | `true` |
| `REMEMBER_COOKIE_SECURE` | `true` |
| `SESSION_COOKIE_SAMESITE` | `Lax` |

#### Variables OPCIONALES (si necesitas conectarte a Ticketera):

| KEY | VALUE |
|-----|-------|
| `TICKETS_API_URL` | `https://ticketerabelgrano.onrender.com` |
| `TICKETS_API_KEY` | `[API key de Ticketera si aplica]` |

### 3. Generar SECRET_KEY Seguro

En Render, para el valor de `SECRET_KEY`, puedes usar:
- Un generador online: https://randomkeygen.com/
- O desde terminal: `openssl rand -hex 32`

**Ejemplo:** `devops_prod_2025_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

### 4. Obtener API Key de Belgrano Ahorro

1. Ve a **Belgrano Ahorro** en Render → Environment
2. Busca la variable `BELGRANO_AHORRO_API_KEY`
3. Copia ese valor
4. Pégalo en DevOps → `BELGRANO_AHORRO_API_KEY`

⚠️ **IMPORTANTE:** La API key debe ser **exactamente la misma** en ambos servicios.

### 5. Guardar y Reiniciar

1. Click en **Save Changes**
2. Render reiniciará automáticamente el servicio
3. Espera a que el deploy termine

### 6. Verificar

1. Accede a: https://devops-nsnc.onrender.com/devops/login
2. Intenta crear un negocio
3. Si funciona → ✅ Configuración correcta

---

## 🔐 Seguridad

### ✅ Buenas Prácticas:

- ✅ Nunca compartas tus API keys públicamente
- ✅ Usa SECRET_KEY únicos para cada servicio
- ✅ Habilita `SESSION_COOKIE_SECURE=true` en producción
- ✅ Usa contraseñas fuertes para login DevOps

### ❌ Evitar:

- ❌ No subir archivos con credenciales a Git
- ❌ No usar valores por defecto de contraseñas
- ❌ No compartir screenshots con variables visibles

---

## 📝 Checklist de Configuración

### DevOps:
- [ ] `BELGRANO_AHORRO_URL` configurada
- [ ] `BELGRANO_AHORRO_API_KEY` configurada (igual que en Belgrano Ahorro)
- [ ] `FLASK_ENV=production`
- [ ] `PORT=5000`
- [ ] `SECRET_KEY` único y seguro
- [ ] `SESSION_COOKIE_SECURE=true` (si usas HTTPS)

### Belgrano Ahorro:
- [ ] `BELGRANO_AHORRO_API_KEY` configurada
- [ ] `BELGRANO_AHORRO_URL` configurada

### Ticketera:
- [ ] `BELGRANO_AHORRO_URL` configurada (igual que en Belgrano Ahorro)
- [ ] `BELGRANO_AHORRO_API_KEY` configurada (igual que en Belgrano Ahorro)

---

## 🆘 Solución de Problemas

### Error: "Invalid API key"
- Verifica que `BELGRANO_AHORRO_API_KEY` sea **exactamente igual** en DevOps y Belgrano Ahorro
- Verifica que no haya espacios adicionales
- Reinicia ambos servicios

### Error: "Connection refused"
- Verifica que `BELGRANO_AHORRO_URL` sea correcta
- Verifica que Belgrano Ahorro esté corriendo
- Verifica que la URL no tenga `/` al final

### Error: "Service unavailable"
- Espera a que termine el deploy
- Revisa los logs en Render
- Verifica que todas las variables estén guardadas

