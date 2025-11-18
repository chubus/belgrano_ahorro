# 🔒 Análisis de Seguridad - Belgrano Ahorro

## ✅ Aspectos de Seguridad Implementados Correctamente

### 1. **Protección contra SQL Injection**
- ✅ Uso de consultas parametrizadas con SQLAlchemy `text()` y parámetros nombrados
- ✅ Conversión automática de `?` a `:param` para compatibilidad PostgreSQL
- ✅ No hay concatenación directa de strings en queries SQL

### 2. **Autenticación de API**
- ✅ Decorador `@require_api_key` implementado
- ✅ Validación de API key en múltiples métodos (Bearer token, X-API-Key header)
- ✅ Logging de intentos de acceso no autorizados

### 3. **Protección de Rutas**
- ✅ Decoradores `@devops_login_required` para rutas administrativas
- ✅ Decoradores `@login_required` para rutas protegidas
- ✅ Validación de sesiones en DevOps

### 4. **Validación de Entrada Básica**
- ✅ Validación de campos requeridos en endpoints de API
- ✅ Validación de tipos de datos (listas, strings, números)
- ✅ Sanitización básica con `.strip()` en campos de texto

### 5. **Manejo de Errores**
- ✅ Try-catch en funciones críticas
- ✅ Logging de errores sin exponer información sensible
- ✅ Rollback de transacciones en caso de error

### 6. **Conexión Segura a Base de Datos**
- ✅ Uso de `sslmode=require` para PostgreSQL
- ✅ Variables de entorno para credenciales
- ✅ No hay credenciales hardcodeadas en el código

---

## ⚠️ Problemas de Seguridad Identificados

### 🔴 **CRÍTICO**

#### 1. **API Key en Query Parameters**
**Ubicación:** `api_belgrano_ahorro.py:86`
```python
api_key = request.args.get('api_key')
```
**Problema:** Las API keys en query parameters pueden quedar en:
- Logs del servidor
- Historial del navegador
- URLs compartidas
- Referrers HTTP

**Recomendación:** Eliminar soporte para query parameters, solo usar headers.

#### 2. **Hash de Contraseñas Débil**
**Ubicación:** `db.py:26-30`
```python
def hash_password(password):
    """Hash password usando SHA-256 con salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${password_hash}"
```
**Problema:** SHA-256 es rápido y vulnerable a ataques de fuerza bruta. No es adecuado para contraseñas.

**Recomendación:** Usar `bcrypt` o `argon2` con cost factor alto.

#### 3. **Secret Keys por Defecto**
**Ubicación:** Múltiples archivos
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'belgrano_ahorro_secret_key_2025')
```
**Problema:** Si no se configura la variable de entorno, se usa un valor por defecto conocido.

**Recomendación:** 
- En producción, fallar si no está configurado
- Generar automáticamente en desarrollo
- Usar valores únicos y aleatorios

#### 4. **API Key por Defecto**
**Ubicación:** `api_belgrano_ahorro.py:27`
```python
BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
```
**Problema:** API key por defecto conocida y débil.

**Recomendación:** Eliminar valor por defecto, requerir configuración explícita.

---

### 🟡 **MEDIO**

#### 5. **Rate Limiting No Implementado**
**Ubicación:** `auth_middleware.py:40-51`
```python
def rate_limit(f=None, max_requests=None, window=None):
    """Decorador de rate limiting (implementación básica)"""
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            return func(*args, **kwargs)  # No hace nada
```
**Problema:** El decorador existe pero no implementa rate limiting real.

**Recomendación:** Implementar rate limiting con Redis o memoria compartida.

#### 6. **Falta Validación de Longitud de Inputs**
**Problema:** No hay límites de longitud en campos de texto, permitiendo posibles DoS.

**Recomendación:** Agregar validación de longitud máxima en todos los campos.

#### 7. **Falta Sanitización de HTML/XSS**
**Problema:** Los datos ingresados por usuarios se muestran directamente en templates sin sanitización.

**Recomendación:** Usar `Markup.escape()` o `jinja2.escape()` en templates.

#### 8. **Falta Protección CSRF**
**Problema:** No hay protección CSRF para formularios.

**Recomendación:** Implementar Flask-WTF con CSRF tokens.

---

### 🟢 **BAJO**

#### 9. **Logging de Información Sensible**
**Problema:** Algunos logs pueden contener información sensible (aunque parcialmente oculta).

**Recomendación:** Revisar todos los logs y asegurar que no se expongan datos sensibles.

#### 10. **Headers de Seguridad HTTP**
**Problema:** No se configuran headers de seguridad (HSTS, CSP, X-Frame-Options, etc.).

**Recomendación:** Agregar Flask-Talisman o configurar headers manualmente.

---

## 📋 Plan de Acción Recomendado

### Prioridad Alta (Implementar Inmediatamente)

1. **Eliminar API key de query parameters**
   ```python
   # ELIMINAR esta línea:
   # api_key = request.args.get('api_key')
   ```

2. **Mejorar hash de contraseñas**
   ```python
   # Instalar: pip install bcrypt
   import bcrypt
   
   def hash_password(password):
       salt = bcrypt.gensalt(rounds=12)
       return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
   
   def verificar_password(password, hashed):
       return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
   ```

3. **Eliminar valores por defecto de secretos**
   ```python
   # En producción:
   SECRET_KEY = os.environ.get('SECRET_KEY')
   if not SECRET_KEY:
       raise ValueError("SECRET_KEY debe estar configurada en producción")
   
   BELGRANO_AHORRO_API_KEY = os.getenv('BELGRANO_AHORRO_API_KEY')
   if not BELGRANO_AHORRO_API_KEY:
       raise ValueError("BELGRANO_AHORRO_API_KEY debe estar configurada")
   ```

### Prioridad Media (Implementar Pronto)

4. **Implementar rate limiting real**
5. **Agregar validación de longitud de inputs**
6. **Implementar sanitización XSS**
7. **Agregar protección CSRF**

### Prioridad Baja (Mejoras Continuas)

8. **Revisar y mejorar logging**
9. **Agregar headers de seguridad HTTP**
10. **Implementar auditoría de accesos**

---

## ✅ Checklist de Seguridad para Producción

- [ ] API keys solo en headers (no en query params)
- [ ] Hash de contraseñas con bcrypt/argon2
- [ ] Secret keys únicos y aleatorios configurados
- [ ] Rate limiting implementado
- [ ] Validación de longitud de inputs
- [ ] Sanitización XSS en templates
- [ ] Protección CSRF en formularios
- [ ] Headers de seguridad HTTP configurados
- [ ] HTTPS forzado (HSTS)
- [ ] Logs sin información sensible
- [ ] Variables de entorno seguras en Render
- [ ] Backup y recuperación de base de datos
- [ ] Monitoreo de intentos de acceso no autorizados

---

## 🔐 Configuración Recomendada en Render

### Variables de Entorno Requeridas

```bash
# Generar valores seguros:
# SECRET_KEY: openssl rand -hex 32
# BELGRANO_AHORRO_API_KEY: openssl rand -hex 32

SECRET_KEY=<generar_valor_aleatorio_64_caracteres>
BELGRANO_AHORRO_API_KEY=<generar_valor_aleatorio_64_caracteres>
DATABASE_URL=<de_render_postgres>
TICKETERA_URL=https://ticketerabelgrano.onrender.com
FLASK_ENV=production
```

### Generar Valores Seguros

```bash
# En terminal:
openssl rand -hex 32  # Para SECRET_KEY
openssl rand -hex 32  # Para BELGRANO_AHORRO_API_KEY
```

---

## 📚 Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

