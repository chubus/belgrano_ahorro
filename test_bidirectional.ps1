# Script de prueba para comunicación bidireccional DevOps ↔ Belgrano Ahorro
# PowerShell script para probar la sincronización

$DEVOPS_BASE_URL = "http://127.0.0.1:10000"
$BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
$API_KEY = "belgrano_ahorro_api_key_2025"

# Función para imprimir mensajes con colores
function Write-Status {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    switch ($Type) {
        "SUCCESS" { Write-Host "✅ [$timestamp] $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "❌ [$timestamp] $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "⚠️  [$timestamp] $Message" -ForegroundColor Yellow }
        "INFO" { Write-Host "ℹ️  [$timestamp] $Message" -ForegroundColor Blue }
        default { Write-Host "[$timestamp] $Message" }
    }
}

# Función para probar salud de DevOps
function Test-DevOpsHealth {
    Write-Status "Probando salud de DevOps..." "INFO"
    
    try {
        $response = Invoke-RestMethod -Uri "$DEVOPS_BASE_URL/devops/health" -Method GET -TimeoutSec 10
        Write-Status "DevOps está funcionando correctamente" "SUCCESS"
        return $true
    }
    catch {
        Write-Status "Error conectando con DevOps: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Función para probar salud de Belgrano Ahorro
function Test-BelgranoAhorroHealth {
    Write-Status "Probando salud de Belgrano Ahorro..." "INFO"
    
    $headers = @{
        'X-API-Key' = $API_KEY
        'X-Origin' = 'test_script'
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BELGRANO_AHORRO_URL/healthz" -Method GET -Headers $headers -TimeoutSec 10
        Write-Status "Belgrano Ahorro está funcionando correctamente" "SUCCESS"
        return $true
    }
    catch {
        Write-Status "Error conectando con Belgrano Ahorro: $($_.Exception.Message)" "WARNING"
        return $false
    }
}

# Función para obtener negocios desde DevOps
function Get-NegociosFromDevOps {
    try {
        $response = Invoke-RestMethod -Uri "$DEVOPS_BASE_URL/devops/negocios" -Method GET -TimeoutSec 10
        if ($response.status -eq "success") {
            return $response.data
        }
        return @()
    }
    catch {
        Write-Status "Error obteniendo negocios desde DevOps: $($_.Exception.Message)" "WARNING"
        return @()
    }
}

# Función para obtener negocios desde Belgrano Ahorro
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

# Función para crear negocio desde DevOps
function New-NegocioFromDevOps {
    $negocioId = [System.Guid]::NewGuid().ToString().Substring(0, 8)
    $negocioData = @{
        nombre = "Negocio Test $negocioId"
        descripcion = "Descripción del negocio de prueba $negocioId"
        categoria = "Pruebas"
        direccion = "Dirección de prueba 123"
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

# Función para verificar sincronización
function Test-NegocioSync {
    param(
        [hashtable]$NegocioData,
        [int]$MaxAttempts = 5,
        [int]$DelaySeconds = 2
    )
    
    Write-Status "Verificando sincronización con Belgrano Ahorro..." "INFO"
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Start-Sleep -Seconds $DelaySeconds
        $negocios = Get-NegociosFromBelgranoAhorro
        
        foreach ($negocio in $negocios) {
            if ($negocio.nombre -eq $NegocioData.nombre) {
                Write-Status "✅ Negocio encontrado en Belgrano Ahorro: $($negocio.nombre)" "SUCCESS"
                return $true, $negocio
            }
        }
        
        Write-Status "Intento $attempt/$MaxAttempts : Negocio no encontrado aún..." "WARNING"
    }
    
    Write-Status "❌ Negocio no se sincronizó con Belgrano Ahorro después de varios intentos" "ERROR"
    return $false, $null
}

# Función principal de prueba
function Test-BidirectionalSync {
    Write-Status "=" * 60 "INFO"
    Write-Status "INICIANDO PRUEBA DE COMUNICACIÓN BIDIRECCIONAL" "INFO"
    Write-Status "=" * 60 "INFO"
    
    # 1. Verificar salud de los servicios
    Write-Status "`n1. Verificando salud de los servicios..." "INFO"
    $devopsOk = Test-DevOpsHealth
    $belgranoOk = Test-BelgranoAhorroHealth
    
    if (-not $devopsOk) {
        Write-Status "❌ DevOps no está disponible. Abortando prueba." "ERROR"
        return $false
    }
    
    # 2. Obtener estado inicial
    Write-Status "`n2. Obteniendo estado inicial de negocios..." "INFO"
    $negociosBelgranoInicial = Get-NegociosFromBelgranoAhorro
    $negociosDevOpsInicial = Get-NegociosFromDevOps
    
    Write-Status "Negocios en Belgrano Ahorro (inicial): $($negociosBelgranoInicial.Count)" "INFO"
    Write-Status "Negocios en DevOps (inicial): $($negociosDevOpsInicial.Count)" "INFO"
    
    # 3. Crear negocio desde DevOps
    Write-Status "`n3. Creando negocio desde DevOps..." "INFO"
    $negocioData, $created = New-NegocioFromDevOps
    
    if (-not $created) {
        Write-Status "❌ No se pudo crear el negocio desde DevOps" "ERROR"
        return $false
    }
    
    # 4. Verificar sincronización con Belgrano Ahorro
    Write-Status "`n4. Verificando sincronización con Belgrano Ahorro..." "INFO"
    $synced, $negocioSynced = Test-NegocioSync -NegocioData $negocioData
    
    if (-not $synced) {
        Write-Status "❌ La sincronización falló" "ERROR"
        return $false
    }
    
    # 5. Verificar que DevOps puede leer el negocio sincronizado
    Write-Status "`n5. Verificando lectura desde DevOps..." "INFO"
    $negociosDevOpsFinal = Get-NegociosFromDevOps
    
    $negocioEncontrado = $false
    foreach ($negocio in $negociosDevOpsFinal) {
        if ($negocio.nombre -eq $negocioData.nombre) {
            $negocioEncontrado = $true
            Write-Status "✅ Negocio encontrado en DevOps: $($negocio.nombre)" "SUCCESS"
            break
        }
    }
    
    if (-not $negocioEncontrado) {
        Write-Status "⚠️  Negocio no encontrado en la lista de DevOps" "WARNING"
    }
    
    # 6. Resumen final
    Write-Status "`n" + "=" * 60 "INFO"
    Write-Status "RESUMEN DE LA PRUEBA" "INFO"
    Write-Status "=" * 60 "INFO"
    
    Write-Status "✅ DevOps funcionando: $(if ($devopsOk) { 'Sí' } else { 'No' })" $(if ($devopsOk) { "SUCCESS" } else { "ERROR" })
    Write-Status "✅ Belgrano Ahorro funcionando: $(if ($belgranoOk) { 'Sí' } else { 'No' })" $(if ($belgranoOk) { "SUCCESS" } else { "WARNING" })
    Write-Status "✅ Negocio creado desde DevOps: $(if ($created) { 'Sí' } else { 'No' })" $(if ($created) { "SUCCESS" } else { "ERROR" })
    Write-Status "✅ Sincronización con Belgrano Ahorro: $(if ($synced) { 'Sí' } else { 'No' })" $(if ($synced) { "SUCCESS" } else { "ERROR" })
    Write-Status "✅ Lectura desde DevOps: $(if ($negocioEncontrado) { 'Sí' } else { 'No' })" $(if ($negocioEncontrado) { "SUCCESS" } else { "WARNING" })
    
    # Determinar resultado general
    if ($created -and $synced) {
        Write-Status "`n🎉 PRUEBA EXITOSA: Comunicación bidireccional funcionando" "SUCCESS"
        return $true
    }
    else {
        Write-Status "`n❌ PRUEBA FALLIDA: Hay problemas en la comunicación bidireccional" "ERROR"
        return $false
    }
}

# Ejecutar la prueba
Write-Status "Script de prueba de comunicación bidireccional DevOps ↔ Belgrano Ahorro" "INFO"
Write-Status "Versión: 1.0.0" "INFO"
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
