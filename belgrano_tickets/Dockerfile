# Usa una imagen base de Python
FROM python:3.12-slim

# Instala las dependencias del sistema necesarias para Pillow
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

# Copia solo la carpeta de la ticketera
COPY belgrano_tickets/ ./

# Instala las dependencias de Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements_ticketera.txt

# Configura la variable de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5001

# Expone el puerto de la ticketera
EXPOSE 5001

# Asegúrate de que el script de inicio sea ejecutable
RUN chmod +x start_ticketera.sh

# El comando de inicio
CMD ["/bin/bash", "start_ticketera.sh"]
