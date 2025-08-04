#!/bin/bash

# Script para iniciar la aplicación Belgrano Ahorro con Docker

echo "🚀 Iniciando Belgrano Ahorro con Docker..."

# Verificar si Docker está disponible
if ! command -v docker &> /dev/null
then
    echo "❌ Docker no está instalado. Por favor, instala Docker primero."
    exit 1
fi

# Verificar si docker-compose está disponible
if ! command -v docker-compose &> /dev/null
then
    echo "❌ docker-compose no está instalado. Por favor, instala docker-compose primero."
    exit 1
fi

# Verificar si la imagen ya existe, si no, construirla
if [[ "$(docker images -q belgrano-ahorro:latest 2> /dev/null)" == "" ]]; then
    echo "🏗️ Construyendo la imagen de Docker..."
    docker build -t belgrano-ahorro .
    
    if [ $? -ne 0 ]; then
        echo "❌ Error al construir la imagen de Docker"
        exit 1
    fi
else
    echo "✅ La imagen de Docker ya existe"
fi

# Verificar si los archivos de datos existen, si no, crearlos
if [ ! -f belgrano_ahorro.db ]; then
    echo "📊 Creando archivo de base de datos..."
    touch belgrano_ahorro.db
fi

if [ ! -f productos.json ]; then
    echo "📦 Creando archivo de productos..."
    touch productos.json
fi

# Iniciar la aplicación con docker-compose
echo "🏃 Iniciando la aplicación..."
echo "📱 La aplicación estará disponible en http://localhost:5000"
echo "⏹️  Presiona Ctrl+C para detener"

docker-compose up

echo "👋 Aplicación detenida"
