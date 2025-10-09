# Dockerfile optimizado para deploy - SIN BuildKit
# =================================================================
# BELGRANO AHORRO - TICKETERA
# =================================================================

# Usar imagen base estable y soportada por Render
FROM python:3.9-bullseye

# Deshabilitar BuildKit para evitar problemas de conexión
ENV DOCKER_BUILDKIT=0
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python de forma optimizada
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para logs y datos
RUN mkdir -p /app/logs && \
    mkdir -p /app/data && \
    chmod 755 /app/logs && \
    chmod 755 /app/data

# Crear archivo productos.json inicial si no existe
RUN python -c "import json, os; datos={'productos':[],'sucursales':[],'ofertas':[],'negocios':{},'categorias':{}}; open('productos.json','w').write(json.dumps(datos,indent=2)) if not os.path.exists('productos.json') else None; print('Archivo productos.json verificado')"

# Exponer puerto
EXPOSE 10000

# Comando de inicio optimizado con verificaciones
# Usar gunicorn para producción
CMD ["sh", "-c", "python test_imports.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 app_unificado:app"]