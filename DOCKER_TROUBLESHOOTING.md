# Solución de Problemas de Docker para Belgrano Ahorro

## Problemas Comunes y Soluciones

### 1. Error: "open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified"

Este error indica que Docker Desktop no está corriendo correctamente o hay un problema con la conexión.

**Soluciones:**

1. **Reiniciar Docker Desktop**:
   - Cierra Docker Desktop completamente
   - Reinicia Docker Desktop
   - Espera a que esté completamente iniciado antes de ejecutar comandos

2. **Verificar que Docker esté corriendo**:
   ```bash
   docker version
   ```

3. **Cambiar a Docker Desktop para Windows (si estás en Windows)**:
   - Abre Docker Desktop
   - Ve a Settings > General
   - Asegúrate de que "Use Docker Compose V2" esté activado
   - Si estás usando WSL2, asegúrate de que esté correctamente configurado

### 2. Error: "the attribute version is obsolete"

Este error ocurre porque en las versiones recientes de Docker Compose, el atributo `version` ya no es necesario.

**Solución:**
El archivo docker-compose.yml ya ha sido actualizado para eliminar esta línea.

### 3. Problemas al construir la imagen

Si la construcción de la imagen falla, intenta:

```bash
docker build --no-cache -t belgrano-ahorro .
```

### 4. Problemas de permisos con volúmenes

En Windows, puede haber problemas de permisos con los volúmenes. Si los datos no se persisten:

1. Verifica que los archivos existan en el directorio local:
   ```bash
   ls -la belgrano_ahorro.db
   ls -la productos.json
   ```

2. Si los archivos no existen, créalos primero:
   ```bash
   touch belgrano_ahorro.db
   touch productos.json
   ```

### 5. Problemas con dependencias

Si hay errores al instalar dependencias:

1. Limpia el caché de Docker:
   ```bash
   docker system prune -a
   ```

2. Reconstruye la imagen:
   ```bash
   docker-compose build --no-cache
   ```

## Comandos Útiles para Diagnóstico

### Verificar estado de Docker:
```bash
docker info
```

### Verificar contenedores en ejecución:
```bash
docker ps
```

### Verificar imágenes:
```bash
docker images
```

### Ver logs de un contenedor:
```bash
docker logs <nombre_del_contenedor>
```

### Ver logs de docker-compose:
```bash
docker-compose logs
```

## Configuración Recomendada para Windows

1. **Usar Docker Desktop con WSL2**:
   - Asegúrate de tener WSL2 instalado
   - Configura Docker Desktop para usar WSL2

2. **Permisos de archivos**:
   - En Windows, ejecuta el terminal como administrador si es necesario
   - Verifica que los archivos no estén bloqueados por el sistema

3. **Recursos suficientes**:
   - Asegúrate de que Docker Desktop tenga suficiente memoria asignada
   - Mínimo recomendado: 4GB de RAM

## Verificación Final

Una vez resueltos los problemas, prueba:

```bash
# Construir la imagen
docker build -t belgrano-ahorro .

# Ejecutar el contenedor
docker run -p 5000:5000 belgrano-ahorro

# O usar docker-compose
docker-compose up
```

La aplicación debería estar disponible en http://localhost:5000
