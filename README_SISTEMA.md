# 🚀 SISTEMA BELGRANO AHORRO - GUÍA COMPLETA

## 📋 Descripción
Sistema completo de gestión de productos y tickets para Belgrano Ahorro, compuesto por:
- **Aplicación Principal**: Gestión de productos, carrito y pedidos (Puerto 5000)
- **Ticketera**: Sistema de gestión de tickets y repartidores (Puerto 5001)

## 🎯 Acceso Rápido

### 🌐 Aplicación Principal
- **URL**: http://localhost:5000
- **Funcionalidades**: Productos, carrito, pedidos, comerciantes

### 🎫 Ticketera (Sistema de Tickets)
- **URL**: http://localhost:5001
- **Acceso directo**: http://localhost:5000/ticketera
- **Acceso admin**: http://localhost:5000/admin

## 🔐 Credenciales Ticketera

### 👨‍💼 Administrador
- **Email**: `admin@belgranoahorro.com`
- **Password**: `admin123`
- **Funciones**: Ver todos los tickets, gestionar usuarios, asignar repartidores

### 🚚 Flota (Repartidores)
- **Email**: `repartidor1@belgranoahorro.com`
- **Password**: `flota123`
- **Funciones**: Ver tickets asignados, cambiar estados

**Otros repartidores**: `repartidor2@belgranoahorro.com` hasta `repartidor5@belgranoahorro.com`

## 🚀 Inicio Rápido

### Opción 1: Sistema Completo (Recomendado)
```bash
python iniciar_sistema.py
```
Este comando inicia automáticamente ambas aplicaciones.

### Opción 2: Inicio Manual

#### Aplicación Principal
```bash
python app.py
```
- Puerto: 5000
- URL: http://localhost:5000

#### Ticketera
```bash
cd belgrano_tickets
python app_simple.py
```
- Puerto: 5001
- URL: http://localhost:5001

## 📁 Estructura del Proyecto

```
Belgrano_ahorro-back/
├── app.py                          # Aplicación principal
├── iniciar_sistema.py              # Script de inicio completo
├── productos.json                  # Datos de productos
├── belgrano_ahorro.db             # Base de datos principal
├── belgrano_tickets/
│   ├── app_simple.py              # Ticketera simplificada
│   ├── models.py                  # Modelos de datos
│   ├── belgrano_tickets.db        # Base de datos ticketera
│   ├── templates/                 # Plantillas ticketera
│   └── static/                    # Archivos estáticos
└── templates/                     # Plantillas aplicación principal
```

## 🔧 Solución de Problemas

### ❌ "Usuario no encontrado" en Ticketera
1. Asegúrate de estar en http://localhost:5001 (no 5000)
2. Usa las credenciales exactas mostradas arriba
3. Verifica que la ticketera esté ejecutándose

### ❌ Error de dependencias
- La ticketera usa `app_simple.py` que evita problemas de WebSocket
- Si hay errores, usa `python app_simple.py` en lugar de `app.py`

### ❌ Puerto ocupado
- Aplicación principal: Puerto 5000
- Ticketera: Puerto 5001
- Verifica que no haya otras aplicaciones usando estos puertos

## 📞 Soporte

### Logs de Debug
- La aplicación principal muestra logs detallados
- La ticketera muestra información de login en consola

### Verificación de Estado
```bash
# Verificar puertos en uso
netstat -an | findstr :5000
netstat -an | findstr :5001
```

## 🚀 Deploy en Producción

### 🌐 URLs de Producción
- **Aplicación Principal**: https://belgrano-ahorro.onrender.com
- **Ticketera**: https://belgrano-ticketera.onrender.com
- **Acceso directo**: https://belgrano-ahorro.onrender.com/ticketera

### 🔧 Configuración de Deploy
El sistema está configurado para deploy automático en Render:
- **render.yaml**: Configuración completa para ambas aplicaciones
- **Variables de entorno**: Configuradas para producción
- **Base de datos**: SQLite persistente en producción

### 🔐 Credenciales de Producción
- **Admin**: admin@belgranoahorro.com / admin123
- **Flota**: repartidor1@belgranoahorro.com / flota123

### 📋 Verificación de Deploy
```bash
python verificar_deploy_produccion.py
```

## 🎉 ¡Listo para Usar!

### Desarrollo Local
Una vez iniciado el sistema:
1. **Aplicación Principal**: http://localhost:5000
2. **Ticketera**: http://localhost:5001
3. **Acceso directo**: http://localhost:5000/ticketera

### Producción
1. **Aplicación Principal**: https://belgrano-ahorro.onrender.com
2. **Ticketera**: https://belgrano-ticketera.onrender.com
3. **Acceso directo**: https://belgrano-ahorro.onrender.com/ticketera

¡El sistema está completamente funcional en desarrollo y producción!
