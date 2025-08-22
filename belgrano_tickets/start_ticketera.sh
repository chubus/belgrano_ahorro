#!/bin/bash

echo "🚀 Iniciando Belgrano Tickets..."
echo "📊 Inicializando base de datos..."

# Cambiar al directorio de la ticketera
cd /app/belgrano_tickets

# Inicializar la base de datos si no existe
if [ ! -f "belgrano_tickets.db" ]; then
    echo "📋 Creando base de datos de tickets..."
    python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Base de datos de tickets creada exitosamente')
"
else
    echo "✅ Base de datos de tickets ya existe"
fi

# Verificar conexión con Belgrano Ahorro
echo "🔗 Verificando conexión con Belgrano Ahorro..."
echo "   URL: $BELGRANO_AHORRO_URL"

# Iniciar la aplicación
echo "🏃 Iniciando aplicación en puerto $PORT..."
echo "📱 La ticketera estará disponible en http://localhost:$PORT"

# Ejecutar la aplicación
python app.py
