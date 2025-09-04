# Script de prueba simple usando curl para probar la comunicacion bidireccional

$BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
$API_KEY = "belgrano_ahorro_api_key_2025"

function Write-Status {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    switch ($Type) {
        "SUCCESS" { Write-Host "[$timestamp] SUCCESS: $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "[$timestamp] ERROR: $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "[$timestamp] WARNING: $Message" -ForegroundColor Yellow }
        "INFO" { Write-Host "[$timestamp] INFO: $Message" -ForegroundColor Blue }
        default { Write-Host "[$timestamp] $Message" }
    }
}

function Test-BelgranoAhorroHealth {
    Write-Status "Probando salud de Belgrano Ahorro..." "INFO"
    
    try {
        $headers = @{
            'X-API-Key' = $API_KEY
            'X-Origin' = 'test_script'
        }
        
        $response = Invoke-RestMethod -Uri "$BELGRANO_AHORRO_URL/healthz" -Method GET -Headers $headers -TimeoutSec 10
        Write-Status "Belgrano Ahorro esta funcionando correctamente" "SUCCESS"
        return $true
    }
    catch {
        Write-Status "Error conectando con Belgrano Ahorro: $($_.Exception.Message)" "WARNING"
        return $false
    }
}

function Get-NegociosFromBelgranoAhorro {
    $headers = @{
        'X-API-Key' = $API_KEY
        'X-Origin' = 'test_script'
    }
    
    try {
        Write-Status "Obteniendo negocios desde Belgrano Ahorro..." "INFO"
        $response = Invoke-RestMethod -Uri "$BELGRANO_AHORRO_URL/api/v1/negocios" -Method GET -Headers $headers -TimeoutSec 10
        Write-Status "Negocios obtenidos exitosamente: $($response.Count) negocios encontrados" "SUCCESS"
        return $response
    }
    catch {
        Write-Status "Error obteniendo negocios desde Belgrano Ahorro: $($_.Exception.Message)" "WARNING"
        return @()
    }
}

function Test-CreateNegocio {
    $negocioId = [System.Guid]::NewGuid().ToString().Substring(0, 8)
    $negocioData = @{
        nombre = "Negocio Test $negocioId"
        descripcion = "Descripcion del negocio de prueba $negocioId"
        categoria = "Pruebas"
        direccion = "Direccion de prueba 123"
        telefono = "+54 11 1234-5678"
        email = "test$negocioId@ejemplo.com"
        activo = $true
    }
    
    Write-Status "Creando negocio de prueba: $($negocioData.nombre)" "INFO"
    
    $headers = @{
        'Content-Type' = 'application/json'
        'X-API-Key' = $API_KEY
        'X-Origin' = 'test_script'
    }
    
    try {
        $jsonData = $negocioData | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$BELGRANO_AHORRO_URL/api/v1/negocios" -Method POST -Headers $headers -Body $jsonData -TimeoutSec 15
        
        Write-Status "Negocio creado exitosamente en Belgrano Ahorro" "SUCCESS"
        Write-Status "Respuesta: $($response | ConvertTo-Json -Compress)" "INFO"
        return $negocioData, $true
    }
    catch {
        Write-Status "Error creando negocio en Belgrano Ahorro: $($_.Exception.Message)" "ERROR"
        if ($_.Exception.Response) {
            $errorResponse = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorResponse)
            $errorBody = $reader.ReadToEnd()
            Write-Status "Detalles del error: $errorBody" "ERROR"
        }
        return $negocioData, $false
    }
}

function Test-EndpointExists {
    param([string]$Endpoint)
    
    Write-Status "Probando endpoint: $Endpoint" "INFO"
    
    $headers = @{
        'X-API-Key' = $API_KEY
        'X-Origin' = 'test_script'
    }
    
    try {
        $response = Invoke-WebRequest -Uri "$BELGRANO_AHORRO_URL$Endpoint" -Method GET -Headers $headers -TimeoutSec 10
        Write-Status "Endpoint $Endpoint responde correctamente (Status: $($response.StatusCode))" "SUCCESS"
        return $true
    }
    catch {
        Write-Status "Endpoint $Endpoint no responde o no existe (Error: $($_.Exception.Message))" "WARNING"
        return $false
    }
}

# Funcion principal de prueba
function Test-APIEndpoints {
    Write-Status "============================================================" "INFO"
    Write-Status "INICIANDO PRUEBA DE ENDPOINTS DE BELGRANO AHORRO" "INFO"
    Write-Status "============================================================" "INFO"
    
    # 1. Verificar salud
    Write-Status "1. Verificando salud de Belgrano Ahorro..." "INFO"
    $healthOk = Test-BelgranoAhorroHealth
    
    # 2. Probar endpoints
    Write-Status "`n2. Probando endpoints disponibles..." "INFO"
    $endpoints = @(
        "/api/v1/negocios",
        "/api/negocios",
        "/api/v1/sucursales",
        "/api/sucursales",
        "/api/v1/ofertas",
        "/api/ofertas"
    )
    
    $workingEndpoints = @()
    foreach ($endpoint in $endpoints) {
        if (Test-EndpointExists -Endpoint $endpoint) {
            $workingEndpoints += $endpoint
        }
    }
    
    # 3. Obtener negocios existentes
    Write-Status "`n3. Obteniendo negocios existentes..." "INFO"
    $negocios = Get-NegociosFromBelgranoAhorro
    
    # 4. Intentar crear un negocio
    Write-Status "`n4. Probando creacion de negocio..." "INFO"
    $negocioData, $created = Test-CreateNegocio
    
    # 5. Resumen final
    Write-Status "`n============================================================" "INFO"
    Write-Status "RESUMEN DE LA PRUEBA" "INFO"
    Write-Status "============================================================" "INFO"
    
    Write-Status "Belgrano Ahorro funcionando: $(if ($healthOk) { 'Si' } else { 'No' })" $(if ($healthOk) { "SUCCESS" } else { "WARNING" })
    Write-Status "Endpoints funcionando: $($workingEndpoints.Count)/$($endpoints.Count)" $(if ($workingEndpoints.Count -gt 0) { "SUCCESS" } else { "ERROR" })
    Write-Status "Negocios existentes: $($negocios.Count)" "INFO"
    Write-Status "Negocio creado: $(if ($created) { 'Si' } else { 'No' })" $(if ($created) { "SUCCESS" } else { "ERROR" })
    
    Write-Status "`nEndpoints funcionando:" "INFO"
    foreach ($endpoint in $workingEndpoints) {
        Write-Status "  - $endpoint" "SUCCESS"
    }
    
    if ($workingEndpoints.Count -gt 0 -and $created) {
        Write-Status "`nPRUEBA EXITOSA: API de Belgrano Ahorro funcionando correctamente" "SUCCESS"
        return $true
    }
    else {
        Write-Status "`nPRUEBA FALLIDA: Hay problemas con la API de Belgrano Ahorro" "ERROR"
        return $false
    }
}

# Ejecutar la prueba
Write-Status "Script de prueba de endpoints de Belgrano Ahorro" "INFO"
Write-Status "Version: 1.0.0" "INFO"
Write-Status "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"

try {
    $success = Test-APIEndpoints
    if ($success) {
        exit 0
    }
    else {
        exit 1
    }
}
catch {
    Write-Status "Error inesperado: $($_.Exception.Message)" "ERROR"
    exit 1
}
