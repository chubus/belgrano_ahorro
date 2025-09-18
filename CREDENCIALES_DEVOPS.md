# 🔐 CREDENCIALES DE DEVOPS - BELGRANO TICKETS

## 📋 CREDENCIALES DE ACCESO

**Usuario:** `devops`  
**Contraseña:** `DevOps2025!Secure`

## 🔗 ACCESO AL SISTEMA

- **URL de Login:** `/devops/login`
- **Panel Principal:** `/devops/`
- **Acceso desde Ticketera:** `http://localhost:5000/devops/login`

## 🔐 CARACTERÍSTICAS DE SEGURIDAD

### ✅ Autenticación Segura
- Contraseña con hash seguro (pbkdf2:sha256:150000)
- Autenticación independiente de ticketera
- Sesiones separadas y protegidas
- Logging de intentos de acceso

### ✅ Sistema de Autenticación
- Login propio de DevOps
- No interfiere con el sistema de ticketera
- Redirecciones correctas
- Manejo de errores robusto

## 🛠️ ENDPOINTS DISPONIBLES

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/devops/` | GET | Panel principal |
| `/devops/login` | GET/POST | Autenticación |
| `/devops/logout` | GET/POST | Cerrar sesión |
| `/devops/health` | GET | Health check |
| `/devops/status` | GET | Estado del sistema |
| `/devops/info` | GET | Información del servicio |
| `/devops/ofertas` | GET | Gestión de ofertas |
| `/devops/negocios` | GET | Gestión de negocios |
| `/devops/logs` | GET | Logs del sistema |
| `/devops/config` | GET | Configuración |
| `/devops/sync` | POST | Sincronización manual |

## 🚀 CONFIGURACIÓN

### Variables de Entorno
```bash
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=DevOps2025!Secure
```

### Implementación
- Hash de contraseña generado automáticamente
- Verificación segura con `check_password_hash()`
- Logging de accesos exitosos y fallidos
- Interfaz de login moderna y profesional

## 📊 ESTADO DEL SISTEMA

- ✅ **Autenticación:** Funcionando correctamente
- ✅ **Endpoints:** Todos operativos (9/9)
- ✅ **Seguridad:** Hash seguro implementado
- ✅ **Integración:** Funciona desde ticketera
- ✅ **Logging:** Sistema de monitoreo activo

## 🔧 MANTENIMIENTO

### Cambiar Contraseña
Para cambiar la contraseña, modificar la variable de entorno:
```bash
DEVOPS_PASSWORD=nueva_contraseña_segura
```

### Verificar Acceso
```bash
curl -X POST http://localhost:5000/devops/login \
  -d "username=devops&password=DevOps2025!Secure"
```

## 📝 NOTAS IMPORTANTES

1. **Seguridad:** Las credenciales están protegidas con hash seguro
2. **Independencia:** DevOps tiene su propio sistema de autenticación
3. **Integración:** Funciona perfectamente desde ticketera
4. **Monitoreo:** Todos los accesos son registrados en logs
5. **Configuración:** Fácil de configurar con variables de entorno

---
**Sistema DevOps v2.0 - Belgrano Tickets**  
*Implementado con seguridad y funcionalidad completa*
