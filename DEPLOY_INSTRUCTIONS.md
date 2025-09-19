# 🚀 Instrucciones de Deploy - Belgrano Ahorro

## 📋 Archivos Necesarios para Deploy

### 1. **app.py** (Punto de entrada principal)
- ✅ Importa desde `app_unificado.py`
- ✅ Configura variables de entorno
- ✅ Manejo de errores robusto
- ✅ Fallback para casos de error

### 2. **render.yaml** (Configuración de Render)
- ✅ Comando de build optimizado
- ✅ Variables de entorno configuradas
- ✅ Comando de inicio correcto

### 3. **requirements.txt** (Dependencias)
- ✅ Todas las dependencias necesarias
- ✅ Versiones específicas

## 🔧 Pasos para Deploy

### 1. **Verificar Archivos Locales**
```bash
python -c "import app; print('✅ app.py OK')"
```

### 2. **Commit y Push**
```bash
git add .
git commit -m "Fix: Corregir app.py para deploy en Render"
git push origin main
```

### 3. **Configurar en Render**
- Usar `app.py` como punto de entrada
- Comando: `gunicorn app:app`
- Puerto: Automático (Render asigna)

## 🐛 Solución de Problemas

### Error: `IndentationError: expected an indented block`
**Causa**: Render está usando un archivo `app.py` anterior
**Solución**: 
1. Verificar que `app.py` local esté correcto
2. Hacer commit y push
3. Forzar redeploy en Render

### Error: `ModuleNotFoundError`
**Causa**: Dependencias faltantes
**Solución**: Verificar `requirements.txt`

### Error: Variables de entorno
**Causa**: Variables no configuradas
**Solución**: Usar `render.yaml` o configurar manualmente

## ✅ Verificación Post-Deploy

1. **Health Check**: `https://tu-app.onrender.com/health`
2. **Página Principal**: `https://tu-app.onrender.com/`
3. **Logs**: Revisar logs en Render Dashboard

## 📞 Soporte

Si hay problemas:
1. Revisar logs en Render
2. Verificar variables de entorno
3. Comprobar que `app.py` sea el archivo correcto
