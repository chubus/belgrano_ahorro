# SISTEMA INTEGRADO DEVOPS + TICKETERA

## ARQUITECTURA

```
🌐 Belgrano Ahorro: Puerto 5000 (independiente)
🎫 Ticketera + DevOps: Puerto 5001 (integrado)
```

## FUNCIONALIDADES

### ✅ IMPLEMENTADAS
- DevOps integrado en Ticketera
- Persistencia directa en belgrano_ahorro.db
- Fallback cuando DevOps Manager no está disponible
- Datos visibles inmediatamente en Belgrano Ahorro
- Sin problemas de codificación Unicode

### 🔧 CONFIGURACIÓN

**Variables de entorno:**
- FLASK_PORT: Puerto del servicio
- FLASK_ENV: development/production
- PYTHONIOENCODING: utf-8

**Base de datos:**
- belgrano_ahorro.db (SQLite)
- Tablas: negocios, productos, ofertas, categorias

## DESPLIEGUE

### Desarrollo
```bash
python desplegar_simple.py
```

### Producción
```bash
python desplegar_robusto.py
```

## ENDPOINTS

### Ticketera
- http://localhost:5001/

### DevOps (integrado)
- http://localhost:5001/devops/
- http://localhost:5001/devops/login
- http://localhost:5001/devops/negocios
- http://localhost:5001/devops/productos
- http://localhost:5001/devops/ofertas

### Belgrano Ahorro
- http://localhost:5000/

## FUNCIONALIDAD DEVOPS

### Creación de entidades
- Negocios: POST /devops/negocios
- Productos: POST /devops/productos  
- Ofertas: POST /devops/ofertas

### Fallback
Cuando DevOps Manager no está disponible:
- Inserción directa en belgrano_ahorro.db
- Lectura directa desde belgrano_ahorro.db
- Flash messages HTML en lugar de JSON

## ESTADO FINAL

✅ DevOps y Ticketera integrados correctamente
✅ Base de datos funcionando
✅ Persistencia real implementada
✅ Fallback funcional
✅ Sin errores de codificación
✅ Listo para post-deploy

## PRÓXIMOS PASOS

1. Ejecutar: python desplegar_simple.py
2. Verificar: http://localhost:5001/devops/
3. Crear entidades desde DevOps
4. Verificar en Belgrano Ahorro
