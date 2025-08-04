FROM python:3.12-slim
RUN apt-get update && apt-get install -y build-essential libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libwebp-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]