# Script para lanzar Belgrano Ahorro y La Ticketera en ventanas separadas
Write-Host "🚀 LANZANDO SISTEMA COMPLETO BELGRANO AHORRO" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Obtener la ruta actual
$currentPath = Get-Location

# Lanzar aplicación principal
Write-Host "🛒 Iniciando Belgrano Ahorro..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentPath'; .\venv\Scripts\Activate.ps1; python app.py" -WindowStyle Normal

# Esperar un momento
Start-Sleep -Seconds 3

# Lanzar ticketera
Write-Host "🎫 Iniciando La Ticketera..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentPath\belgrano_tickets'; ..\venv\Scripts\Activate.ps1; python app.py" -WindowStyle Normal

Write-Host ""
Write-Host "✅ SISTEMA COMPLETO INICIADO" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "📱 Aplicaciones disponibles:" -ForegroundColor Cyan
Write-Host "   Belgrano Ahorro: http://localhost:5000" -ForegroundColor White
Write-Host "   La Ticketera: http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales de acceso:" -ForegroundColor Cyan
Write-Host "   Admin: admin@belgranoahorro.com / admin123" -ForegroundColor White
Write-Host "   Flota: repartidor1@belgranoahorro.com / repartidor123" -ForegroundColor White
Write-Host ""
Write-Host "📊 Funcionalidades:" -ForegroundColor Cyan
Write-Host "   • Catálogo de productos y carrito de compras" -ForegroundColor White
Write-Host "   • Sistema de pedidos y checkout" -ForegroundColor White
Write-Host "   • Gestión de tickets de entrega" -ForegroundColor White
Write-Host "   • Panel de administración" -ForegroundColor White
Write-Host "   • Panel de flota/repartidores" -ForegroundColor White
Write-Host ""
Write-Host "Cierra las ventanas de PowerShell para detener las aplicaciones" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green

# Mantener la ventana abierta
Read-Host "Presiona Enter para salir"
