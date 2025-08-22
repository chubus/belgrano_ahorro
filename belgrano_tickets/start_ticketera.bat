@echo off
REM Script para iniciar Belgrano Tickets con Docker en Windows

echo 🎫 Iniciando Belgrano Tickets con Docker...
echo.

REM Verificar si Docker está disponible
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está instalado o no está corriendo. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker está disponible
echo.

REM Verificar si la imagen ya existe, si no, construirla
docker images belgrano-ticketera:latest --format "{{.Repository}}" | findstr "belgrano-ticketera" >nul
if %errorlevel% neq 0 (
    echo 🏗️ Construyendo la imagen de Belgrano Tickets...
    docker build -f Dockerfile -t belgrano-ticketera ..
    
    if %errorlevel% neq 0 (
        echo ❌ Error al construir la imagen de Docker
        pause
        exit /b 1
    )
) else (
    echo ✅ La imagen de Belgrano Tickets ya existe
)

REM Verificar si los archivos de datos existen, si no, crearlos
if not exist belgrano_tickets.db (
    echo 📊 Creando archivo de base de datos de tickets...
    type nul > belgrano_tickets.db
)

if not exist ..\belgrano_ahorro.db (
    echo 📊 Creando archivo de base de datos principal...
    type nul > ..\belgrano_ahorro.db
)

REM Iniciar la aplicación con docker-compose
echo 🏃 Iniciando Belgrano Tickets...
echo 📱 La ticketera estará disponible en http://localhost:5001
echo 🔗 Conectada a Belgrano Ahorro en http://localhost:5000
echo ⏹️  Presiona Ctrl+C para detener
echo.

docker-compose up

echo 👋 Belgrano Tickets detenido
pause
