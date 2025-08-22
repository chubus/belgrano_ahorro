# Usa una imagen base de Python
FROM python:3.12-slim

# Instala las dependencias del sistema necesarias
# Esto se hace primero para aprovechar el cache de Docker.
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de la aplicación a la carpeta de trabajo
# Esta es la línea más importante. Copia todos los archivos de la carpeta
# "belgrano_tickets" a la raíz del contenedor.
COPY belgrano_tickets/ ./

# Instala las dependencias de Python
# La carpeta "belgrano_tickets" ya está copiada, así que el archivo de requisitos
# se encuentra en la raíz del contenedor.
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements_ticketera.txt

# Asegúrate de que el script de inicio sea ejecutable
RUN chmod +x start_ticketera.sh

# El comando de inicio
CMD ["/bin/bash", "start_ticketera.sh"]