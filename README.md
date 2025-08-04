# belgrano_ahorro
Web de belgrano ahorro

## Dockerización

Este proyecto ahora incluye soporte completo para Docker, lo que facilita su despliegue y ejecución en cualquier entorno.

### Archivos Docker incluidos:

- `Dockerfile`: Define cómo construir la imagen de la aplicación
- `docker-compose.yml`: Configuración para ejecutar la aplicación con Docker Compose
- `.dockerignore`: Archivos que se excluyen del contexto de construcción de Docker
- `start_docker.sh`: Script para Linux/macOS para iniciar la aplicación
- `start_docker.bat`: Script para Windows para iniciar la aplicación

### Instrucciones de uso:

1. **Con Docker Compose (recomendado):**
   ```bash
   docker-compose up
   ```

2. **Con scripts de inicio:**
   - En Linux/macOS: `./start_docker.sh`
   - En Windows: `start_docker.bat`

3. **Manualmente:**
   ```bash
   # Construir la imagen
   docker build -t belgrano-ahorro .
   
   # Ejecutar el contenedor
   docker run -p 5000:5000 belgrano-ahorro
   ```

La aplicación estará disponible en http://localhost:5000

### Documentación adicional:

- `README_DOCKER.md`: Instrucciones detalladas para usar Docker
- `DOCKER_GUIDE.md`: Guía completa de los cambios realizados
- `DOCKER_TROUBLESHOOTING.md`: Solución de problemas comunes

### Beneficios de usar Docker:

- **Portabilidad**: La aplicación se ejecuta de la misma manera en cualquier entorno
- **Persistencia de datos**: Los datos se conservan entre reinicios gracias a los volúmenes
- **Facilidad de despliegue**: Un solo comando para iniciar toda la aplicación
- **Aislamiento**: La aplicación se ejecuta en un entorno aislado sin afectar el sistema host
