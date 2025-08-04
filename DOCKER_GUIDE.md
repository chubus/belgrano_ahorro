# Guía Completa para Dockerizar Belgrano Ahorro

## Cambios Realizados

Hemos realizado los siguientes cambios para dockerizar la aplicación:

### 1. Actualización del Dockerfile

- Cambiamos el comando de ejecución de `python app.py` a `gunicorn` para una mejor gestión de procesos en producción
- Agregamos `gunicorn==23.0.0` al archivo `requirements.txt`
- Agregamos un paso para inicializar la base de datos durante la construcción de la imagen

### 2. Archivo docker-compose.yml

Creamos un archivo `docker-compose.yml` para facilitar la ejecución de la aplicación:

```yaml
services:
  belgrano-ahorro:
    build: .
    image: belgrano-ahorro:latest
    ports:
      - "5000:5000"
    volumes:
      - ./belgrano_ahorro.db:/app/belgrano_ahorro.db
      - ./productos.json:/app/productos.json
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### 3. Archivo .dockerignore

Creamos un archivo `.dockerignore` para excluir archivos innecesarios del contexto de construcción de Docker.

### 4. Actualización de requirements.txt

Agregamos `gunicorn==23.0.0` al archivo `requirements.txt` para usar un servidor WSGI más robusto en producción.

## Instrucciones de Uso

### Construir la imagen Docker

```bash
docker build -t belgrano-ahorro .
```

### Ejecutar con Docker Compose (Recomendado)

```bash
docker-compose up
```

Para ejecutar en segundo plano:

```bash
docker-compose up -d
```

Para detener:

```bash
docker-compose down
```

### Ejecutar con Docker directamente

```bash
docker run -p 5000:5000 belgrano-ahorro
```

## Beneficios de los Cambios

1. **Mejor rendimiento**: Gunicorn es un servidor WSGI de producción que maneja mejor las solicitudes concurrentes
2. **Persistencia de datos**: Los volúmenes en docker-compose.yml aseguran que los datos se conserven entre reinicios
3. **Facilidad de despliegue**: Docker Compose simplifica la ejecución de la aplicación con un solo comando
4. **Configuración de producción**: Variables de entorno y reinicio automático para mayor estabilidad

## Solución de Problemas

Para problemas comunes con Docker, consulta el archivo `DOCKER_TROUBLESHOOTING.md` que contiene soluciones detalladas para:

- Errores de conexión con Docker Desktop
- Problemas al construir imágenes
- Errores de permisos con volúmenes
- Problemas con dependencias

### Comandos útiles para diagnóstico:

```bash
# Verificar estado de Docker
docker info

# Verificar contenedores en ejecución
docker ps

# Verificar imágenes
docker images

# Ver logs de un contenedor
docker logs <nombre_del_contenedor>

# Ver logs de docker-compose
docker-compose logs
```

## Personalización

Puedes modificar el `docker-compose.yml` para:

1. Cambiar el puerto de exposición
2. Ajustar los volúmenes
3. Modificar las variables de entorno
4. Agregar más servicios (por ejemplo, una base de datos separada)

## Notas Importantes

- La base de datos se inicializa automáticamente durante la construcción de la imagen
- Los datos se persisten gracias a los volúmenes configurados en docker-compose.yml
- En entornos de producción, considera usar un proxy inverso como Nginx
