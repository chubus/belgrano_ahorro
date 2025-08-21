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
    sqlite3 \
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

# Crear directorios necesarios
RUN mkdir -p instance belgrano_tickets/instance

# Inicializar base de datos si no existe
RUN python -c "import os; import db; db.crear_base_datos() if not os.path.exists('belgrano_ahorro.db') else None"

# Inicializar base de datos de tickets si no existe
RUN python -c "import os; os.chdir('belgrano_tickets'); import crear_db_simple if not os.path.exists('belgrano_tickets.db') else None"

# Expone el puerto (5000 para Flask)
EXPOSE 5000

# Comando para ejecutar la aplicación directamente desde app.py
CMD ["python", "app.py"]