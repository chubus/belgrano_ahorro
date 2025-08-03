# Usa una imagen base de Python 3.12
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto (ajústalo según tu app, por ejemplo 5000 para Flask)
EXPOSE 5000

# Comando para ejecutar la aplicación (ajústalo según tu app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
