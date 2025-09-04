# Script de prueba simple para comunicacion bidireccional DevOps - Belgrano Ahorro

$DEVOPS_BASE_URL = "http://127.0.0.1:10000"
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

function Test-DevOpsHealth {
    Write-Status "Probando salud de DevOps..." "INFO"
    
    try {
        $response = Invoke-RestMethod -Uri "$DEVOPS_BASE_URL/devops/health" -Method GET -TimeoutSec 10
        Write-Status "DevOps esta funcionando correctamente" "SUCCESS"
        return $true
    }
    catch {
        Write-Status "Error conectando con DevOps: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-BelgranoAhorroHealth {
    Write-Status "Probando salud de Belgrano Ahorro..." "INFO"
    
    $headers = @{
        'X-API-Key' = $API_KEY
        'X-Origin' = 'test_script'
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BELGRANO_AHORRO_URL/healthz" -Method GET -Headers $headers -TimeoutSec 10
        Write-Status "Belgrano Ahorro esta funcionando correctamente" "SUCCESS"
        return $true
    }
    catch {
        Write-Status "Error conectando con Belgrano Ahorro: $($_.Exception.Message)" "WARNING"
        return $false
    }
}

function New-NegocioFromDevOps {
    $negocioId = [System.Guid]::NewGuid().ToString().Substring(0, 8)
    $negocioData = @{
        nombre = "Negocio Test $negocioId"
        descripcion = "Descripcion del negocio de prueba $negocioId"
        categoria = "Pruebas"
        direccion = "Direccion de prueba 123"
        telefono = "+54 11 1234-5678"
        email = "test$negocioId@ejemplo.com"
    }
    
    Write-Status "Creando negocio desde DevOps: $($negocioData.nombre)" "INFO"
    
    $headers = @{
        'Content-Type' = 'application/json'
        'Accept' = 'application/json'
    }
    
    try {
        $jsonData = $negocioData | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$DEVOPS_BASE_URL/devops/agregar_negocio" -Method POST -Headers $headers -Body $jsonData -TimeoutSec 15
        
        if ($response.status -eq "success") {
            Write-Status "Negocio creado exitosamente desde DevOps" "SUCCESS"
            return $negocioData, $true
        }
        else {
            Write-Status "Error en respuesta de DevOps: $($response.message)" "ERROR"
            return $negocioData, $false
        }
    }
    catch {
        Write-Status "Error creando negocio desde DevOps: $($_.Exception.Message)" "ERROR"
        return $negocioData, $false
    }
}

function Get-NegociosFromBelgranoAhorro {
    $headers = @{
        'X-API-Key' = $API_KEY
        'X-Origin' = 'test_script'
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BELGRANO_AHORRO_URL/api/v1/negocios" -Method GET -Headers $headers -TimeoutSec 10
        return $response
    }
    catch {
        Write-Status "Error obteniendo negocios desde Belgrano Ahorro: $($_.Exception.Message)" "WARNING"
        return @()
    }
}

function Test-NegocioSync {
    param(
        [hashtable]$NegocioData,
        [int]$MaxAttempts = 3,
        [int]$DelaySeconds = 3
    )
    
    Write-Status "Verificando sincronizacion con Belgrano Ahorro..." "INFO"
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Start-Sleep -Seconds $DelaySeconds
        $negocios = Get-NegociosFromBelgranoAhorro
        
        foreach ($negocio in $negocios) {
            if ($negocio.nombre -eq $NegocioData.nombre) {
                Write-Status "Negocio encontrado en Belgrano Ahorro: $($negocio.nombre)" "SUCCESS"
                return $true, $negocio
            }
        }
        
        Write-Status "Intento $attempt/$MaxAttempts : Negocio no encontrado aun..." "WARNING"
    }
    
    Write-Status "Negocio no se sincronizo con Belgrano Ahorro despues de varios intentos" "ERROR"
    return $false, $null
}

# Funcion principal de prueba
function Test-BidirectionalSync {
    Write-Status "============================================================" "INFO"
    Write-Status "INICIANDO PRUEBA DE COMUNICACION BIDIRECCIONAL" "INFO"
    Write-Status "============================================================" "INFO"
    
    # 1. Verificar salud de los servicios
    Write-Status "1. Verificando salud de los servicios..." "INFO"
    $devopsOk = Test-DevOpsHealth
    $belgranoOk = Test-BelgranoAhorroHealth
    
    if (-not $devopsOk) {
        Write-Status "DevOps no esta disponible. Abortando prueba." "ERROR"
        return $false
    }
    
    # 2. Crear negocio desde DevOps
    Write-Status "2. Creando negocio desde DevOps..." "INFO"
    $negocioData, $created = New-NegocioFromDevOps
    
    if (-not $created) {
        Write-Status "No se pudo crear el negocio desde DevOps" "ERROR"
        return $false
    }
    
    # 3. Verificar sincronizacion con Belgrano Ahorro
    Write-Status "3. Verificando sincronizacion con Belgrano Ahorro..." "INFO"
    $synced, $negocioSynced = Test-NegocioSync -NegocioData $negocioData
    
    # 4. Resumen final
    Write-Status "============================================================" "INFO"
    Write-Status "RESUMEN DE LA PRUEBA" "INFO"
    Write-Status "============================================================" "INFO"
    
    Write-Status "DevOps funcionando: $(if ($devopsOk) { 'Si' } else { 'No' })" $(if ($devopsOk) { "SUCCESS" } else { "ERROR" })
    Write-Status "Belgrano Ahorro funcionando: $(if ($belgranoOk) { 'Si' } else { 'No' })" $(if ($belgranoOk) { "SUCCESS" } else { "WARNING" })
    Write-Status "Negocio creado desde DevOps: $(if ($created) { 'Si' } else { 'No' })" $(if ($created) { "SUCCESS" } else { "ERROR" })
    Write-Status "Sincronizacion con Belgrano Ahorro: $(if ($synced) { 'Si' } else { 'No' })" $(if ($synced) { "SUCCESS" } else { "ERROR" })
    
    # Determinar resultado general
    if ($created -and $synced) {
        Write-Status "PRUEBA EXITOSA: Comunicacion bidireccional funcionando" "SUCCESS"
        return $true
    }
    else {
        Write-Status "PRUEBA FALLIDA: Hay problemas en la comunicacion bidireccional" "ERROR"
        return $false
    }
}

# Ejecutar la prueba
Write-Status "Script de prueba de comunicacion bidireccional DevOps - Belgrano Ahorro" "INFO"
Write-Status "Version: 1.0.0" "INFO"
Write-Status "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"

try {
    $success = Test-BidirectionalSync
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
