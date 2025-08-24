# Usa una imagen base de Python
FROM python:3.12-slim

# Instala las dependencias del sistema necesarias, incluyendo PortAudio
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    sqlite3 \
    libasound-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de la aplicación a la carpeta de trabajo
COPY belgrano_tickets/ ./belgrano_tickets/
COPY requirements_ticketera.txt ./
COPY start_ticketera.sh ./

# Instala las dependencias de Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements_ticketera.txt

# Asegúrate de que el script de inicio sea ejecutable
RUN chmod +x start_ticketera.sh

# El comando de inicio
CMD ["/bin/bash", "start_ticketera.sh"]