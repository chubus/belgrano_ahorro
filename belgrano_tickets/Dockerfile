FROM python:3.12-slim

# Instala dependencias del sistema necesarias
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

# Copia los archivos de requisitos de la ticketera
COPY belgrano_tickets/requirements_ticketera.txt ./requirements_ticketera.txt

# Instala las dependencias de Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements_ticketera.txt

# Copia el código de la ticketera
COPY belgrano_tickets/ ./belgrano_tickets/
COPY static/ ./static/
COPY templates/ ./templates/
COPY app.py .
COPY db.py .
COPY config.py .
COPY productos.json .

# Crear directorios necesarios
RUN mkdir -p instance belgrano_tickets/instance

# Crear archivos de base de datos si no existen
RUN touch belgrano_ahorro.db belgrano_tickets/belgrano_tickets.db

# Configurar variables de entorno para la ticketera
ENV FLASK_APP=belgrano_tickets/app.py
ENV FLASK_ENV=production
ENV PORT=5001
ENV BELGRANO_AHORRO_URL=http://belgrano-ahorro:5000

# Expone el puerto de la ticketera
EXPOSE 5001

# Script de inicio que inicializa la BD y ejecuta la aplicación
COPY belgrano_tickets/start_ticketera.sh /start_ticketera.sh
RUN chmod +x /start_ticketera.sh

# Comando para ejecutar la ticketera
CMD ["/start_ticketera.sh"]
