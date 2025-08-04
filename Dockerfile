FROM python:3.12-slim

# Instala dependencias del sistema necesarias para Pillow y PyAudio
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto (5000 para Flask)
EXPOSE 5000

# Comando para ejecutar la aplicación directamente desde app.py
CMD ["python", "app.py"]