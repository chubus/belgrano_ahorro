# Usa una imagen base de Python
FROM python:3.12-slim

# Instala las dependencias del sistema
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements_ticketera.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación
COPY belgrano_tickets/ ./

# Instala las dependencias de Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements_ticketera.txt

# Asegúrate de que el script de inicio sea ejecutable
RUN chmod +x start_ticketera.sh

# El comando de inicio
CMD ["/bin/bash", "start_ticketera.sh"]

