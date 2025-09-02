#!/bin/bash
# Script de deploy optimizado para BELGRANO AHORRO
# =================================================================

set -e  # Salir si hay algún error

echo "🚀 INICIANDO DEPLOY OPTIMIZADO - BELGRANO AHORRO"
echo "=================================================="

# Configurar variables de entorno para evitar BuildKit
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

echo "✅ BuildKit deshabilitado para evitar problemas de conexión"

# Limpiar recursos Docker
echo "🧹 Limpiando recursos Docker..."
docker system prune -f
docker builder prune -f

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p data logs
mkdir -p instance belgrano_tickets/instance

# Verificar que productos.json existe
if [ ! -f "productos.json" ]; then
    echo "📝 Creando archivo productos.json inicial..."
    cat > productos.json << EOF
{
  "productos": [],
  "sucursales": [],
  "ofertas": [],
  "negocios": {},
  "categorias": {}
}
EOF
    echo "✅ productos.json creado exitosamente"
else
    echo "✅ productos.json ya existe"
fi

# Construir imagen sin BuildKit
echo "🔨 Construyendo imagen Docker (sin BuildKit)..."
docker build --no-cache --progress=plain \
    --build-arg DOCKER_BUILDKIT=0 \
    -t belgrano-ahorro:latest .

# Verificar que la imagen se construyó correctamente
if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente"
else
    echo "❌ Error construyendo imagen"
    exit 1
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down --remove-orphans

# Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose up -d

# Esperar a que el servicio esté listo
echo "⏳ Esperando a que el servicio esté listo..."
sleep 10

# Verificar salud del servicio
echo "🏥 Verificando salud del servicio..."
for i in {1..10}; do
    if curl -f http://localhost:10000/devops/health > /dev/null 2>&1; then
        echo "✅ Servicio funcionando correctamente"
        break
    else
        echo "⏳ Intento $i/10 - Esperando servicio..."
        sleep 5
    fi
done

# Mostrar logs del servicio
echo "📋 Mostrando logs del servicio..."
docker-compose logs app

echo ""
echo "🎉 DEPLOY COMPLETADO EXITOSAMENTE!"
echo "=================================="
echo "🌐 URL del servicio: http://localhost:10000"
echo "🔧 Health check: http://localhost:10000/devops/health"
echo "📊 Status: http://localhost:10000/devops/status"
echo ""
echo "📝 Para ver logs en tiempo real:"
echo "   docker-compose logs -f app"
echo ""
echo "🛑 Para detener servicios:"
echo "   docker-compose down"
