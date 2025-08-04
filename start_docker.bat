@echo off
REM Script para iniciar la aplicacin Belgrano Ahorro con Docker en Windows

echo 🚀 Iniciando Belgrano Ahorro con Docker...

REM Verificar si Docker est disponible
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no est instalado o no est corriendo. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker est disponible

REM Verificar si la imagen ya existe, si no, construirla
docker images belgrano-ahorro:latest --format "{{.Repository}}" | findstr "belgrano-ahorro" >nul
if %errorlevel% neq 0 (
    echo 🏗️ Construyendo la imagen de Docker...
    docker build -t belgrano-ahorro .
    
    if %errorlevel% neq 0 (
        echo ❌ Error al construir la imagen de Docker
        pause
        exit /b 1
    )
) else (
    echo ✅ La imagen de Docker ya existe
)

REM Verificar si los archivos de datos existen, si no, crearlos
if not exist belgrano_ahorro.db (
    echo 📊 Creando archivo de base de datos...
    type nul > belgrano_ahorro.db
)

if not exist productos.json (
    echo 📦 Creando archivo de productos...
    type nul > productos.json
)

REM Iniciar la aplicacin con docker-compose
echo 🏃 Iniciando la aplicacin...
echo 📱 La aplicacin estar disponible en http://localhost:5000
echo ⏹️  Presiona Ctrl+C para detener

docker-compose up

echo 👋 Aplicacin detenida
pause
