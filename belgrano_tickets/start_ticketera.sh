#!/bin/bash

# Script de inicio para Belgrano Tickets en producción
# Este script inicializa la base de datos y ejecuta la aplicación

gunicorn --bind 0.0.0.0:$PORT app:app


set -e  # Salir si hay algún error

echo "🚀 Iniciando Belgrano Tickets..."
echo "📊 Inicializando base de datos..."

# Cambiar al directorio de la ticketera
cd /app/belgrano_tickets

# Verificar que el archivo app.py existe
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py no encontrado en /app/belgrano_tickets/"
    exit 1
fi

# Inicializar la base de datos si no existe
echo "🔧 Inicializando base de datos..."
python -c "
import os
import sys
sys.path.append('/app/belgrano_tickets')

try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print('✅ Base de datos de tickets inicializada exitosamente')
except Exception as e:
    print(f'❌ Error al inicializar base de datos: {e}')
    sys.exit(1)
"

# Verificar conexión con Belgrano Ahorro
echo "🔗 Verificando conexión con Belgrano Ahorro..."
echo "   URL: $BELGRANO_AHORRO_URL"

# Verificar variables de entorno
echo "⚙️ Configuración:"
echo "   Puerto: $PORT"
echo "   Entorno: $FLASK_ENV"
echo "   App: $FLASK_APP"

# Iniciar la aplicación
echo "🏃 Iniciando aplicación en puerto $PORT..."
echo "📱 La ticketera estará disponible en http://localhost:$PORT"

# Ejecutar la aplicación con manejo de errores
exec python app.py
