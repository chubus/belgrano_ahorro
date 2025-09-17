#!/bin/bash

echo "🚀 INICIANDO BELGRANO AHORRO Y LA TICKETERA"
echo "=========================================="

# Inicializar base de datos de tickets
echo "📊 Inicializando base de datos de tickets..."
cd belgrano_tickets
python crear_db_simple.py
cd ..

# Inicializar base de datos de Belgrano Ahorro
echo "📊 Inicializando base de datos de Belgrano Ahorro..."
python inicializar_db.py

# Iniciar Belgrano Ahorro en segundo plano
echo "🛒 Iniciando Belgrano Ahorro en puerto 5000..."
python app.py &
BELGRANO_PID=$!

# Esperar un momento
sleep 2

# Iniciar La Ticketera en segundo plano
echo "🎫 Iniciando La Ticketera en puerto 5001..."
cd belgrano_tickets
python app.py &
TICKETERA_PID=$!
cd ..

echo "✅ Servicios iniciados:"
echo "   🛒 Belgrano Ahorro: http://localhost:5000"
echo "   🎫 La Ticketera: http://localhost:5001"
echo ""
echo "🔐 Credenciales:"
echo "   👑 Admin: admin@belgranoahorro.com / admin123"
echo "   🚚 Flota: repartidor1@belgranoahorro.com / repartidor123"
echo ""
echo "📝 Presiona Ctrl+C para detener"

# Esperar a que ambos procesos terminen
wait $BELGRANO_PID $TICKETERA_PID
