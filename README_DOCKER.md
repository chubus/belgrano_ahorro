# Belgrano Ahorro - Docker

Este documento explica cómo dockerizar y ejecutar la aplicación Belgrano Ahorro usando Docker.

## Requisitos previos

- Docker instalado en tu sistema
- Docker Compose (opcional pero recomendado)

## Estructura de archivos Docker

El proyecto incluye los siguientes archivos para Docker:

1. `Dockerfile` - Define cómo construir la imagen de la aplicación
2. `docker-compose.yml` - Configuración para ejecutar la aplicación con Docker Compose
3. `.dockerignore` - Archivos que se excluyen del contexto de construcción de Docker

## Construir la imagen Docker

Para construir la imagen Docker manualmente:

```bash
docker build -t belgrano-ahorro .
```

## Ejecutar con Docker Compose (Recomendado)

La forma más fácil de ejecutar la aplicación es con Docker Compose:

```bash
docker-compose up
```

Esto iniciará la aplicación y la expondrá en http://localhost:5000

Para ejecutar en segundo plano (modo detached):

```bash
docker-compose up -d
```

Para detener la aplicación:

```bash
docker-compose down
```

## Ejecutar con Docker directamente

Si prefieres ejecutar con Docker directamente:

```bash
docker run -p 5000:5000 belgrano-ahorro
```

## Persistencia de datos

La base de datos (`belgrano_ahorro.db`) y el archivo de productos (`productos.json`) se montan como volúmenes en el docker-compose.yml, lo que significa que los datos se conservarán entre reinicios del contenedor.

## Variables de entorno

Puedes configurar las siguientes variables de entorno:

- `FLASK_ENV` - Establecer a "development" o "production"

## Solución de problemas

### Si el contenedor no inicia:

1. Verifica que los puertos no estén ocupados:
   ```bash
   docker-compose down
   docker-compose up
   ```

2. Verifica los logs:
   ```bash
   docker-compose logs
   ```

### Si hay problemas con las dependencias:

1. Reconstruye la imagen:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

## Personalización

Puedes modificar el `docker-compose.yml` para:

1. Cambiar el puerto de exposición
2. Ajustar los volúmenes
3. Modificar las variables de entorno
4. Agregar más servicios (por ejemplo, una base de datos separada)

## Seguridad

- En producción, considera usar un proxy inverso como Nginx
- No expongas la aplicación directamente a internet sin protección adicional
- Usa variables de entorno para configuraciones sensibles
