# ========================================
# Avaliacao de Desempenho - Spring PetClinic (Locust)
# Executa os 3 cenarios (Leve, Medio, Pico)
# ========================================

param(
    [string]$BaseUrl = "http://localhost:8080",
    
    [int]$Repetitions = 5
)

$resultsDir = ".\results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
    Write-Host "[OK] Pasta 'results' criada"
}

function Run-Scenario {
    param(
        [string]$Name,
        [int]$Users,
        [int]$SpawnRate,
        [string]$Duration,
        [int]$Repetitions,
        [string]$TargetHost
    )
    
    Write-Host "`n=========================================="
    Write-Host "CENARIO $Name"
    Write-Host "Usuarios: $Users | Spawn Rate: $SpawnRate/s | Duracao: $Duration"
    Write-Host "Repeticoes: $Repetitions"
    Write-Host "==========================================" -ForegroundColor Cyan
    
    $startTime = Get-Date
    
    for ($i = 1; $i -le $Repetitions; $i++) {
        Write-Host "`n[Execucao $i/$Repetitions do cenario $Name]" -ForegroundColor Yellow
        
        $csvPrefix = Join-Path $resultsDir "${Name}_exec_${i}"
        $htmlReport = "${csvPrefix}.html"
        
        try {
            & locust -f locustfile.py `
                --headless `
                -u $Users `
                -r $SpawnRate `
                -t $Duration `
                --csv $csvPrefix `
                --host $TargetHost `
                --html $htmlReport
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] Execucao $i concluida com sucesso" -ForegroundColor Green
            } else {
                Write-Host "  [ERRO] Execucao $i falhou (codigo: $LASTEXITCODE)" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "  [ERRO] Erro na execucao {$i}: $_" -ForegroundColor Red
        }
        
        if ($i -lt $Repetitions) {
            Write-Host "  Aguardando 10s antes da proxima execucao..."
            Start-Sleep -Seconds 10
        }
    }
    
    $endTime = Get-Date
    $elapsed = $endTime - $startTime
    
    Write-Host "`n[OK] Cenario $Name concluido!" -ForegroundColor Green
    Write-Host "  Tempo total: $($elapsed.ToString('hh\:mm\:ss'))"
    Write-Host "  Resultados em: $resultsDir\${Name}_exec_*.csv"
    Write-Host "==========================================`n"
}

# --- Verificacoes Iniciais ---
Write-Host "Verificando dependencias..." -ForegroundColor Cyan
try {
    $locustCmd = Get-Command locust -ErrorAction Stop
    Write-Host "[OK] Locust encontrado: $($locustCmd.Source)" -ForegroundColor Green
}
catch {
    Write-Host "[ERRO] Locust nao encontrado! Instale com: pip install locust" -ForegroundColor Red
    exit 1
}

Write-Host "`nVerificando conectividade com $BaseUrl..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/customer/owners" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Sistema respondendo (Status: $($response.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "[ERRO] Sistema nao esta respondendo em $BaseUrl" -ForegroundColor Red
    Write-Host "  Certifique-se de que o Spring PetClinic esta rodando!" -ForegroundColor Yellow
    $continue = Read-Host "Deseja continuar mesmo assim? (s/n)"
    if ($continue -ne "s") {
        exit 1
    }
}

# --- Sumario da Execucao ---
Write-Host "`n=========================================="
Write-Host "INICIANDO BATERIA DE TESTES"
Write-Host "=========================================="
Write-Host "Total de cenarios: 3"
Write-Host "Repeticoes por cenario: $Repetitions"
Write-Host "Total de execucoes: $($Repetitions * 3)"
$totalMin = $Repetitions * (10 + 10 + 5)
$totalHours = [Math]::Round($totalMin / 60, 2)
Write-Host "Tempo estimado (Locust): ~$totalHours horas"
Write-Host "==========================================`n"

Write-Host "!!! IMPORTANTE !!!" -ForegroundColor Yellow
Write-Host "Abra um segundo terminal e execute 'docker stats' AGORA para monitorar a CPU/Memoria."
$continue = Read-Host "Pressione ENTER para iniciar ou Ctrl+C para cancelar"

$globalStart = Get-Date

# --- Execucao dos Cenarios ---
Run-Scenario -Name "LEVE" -Users 50 -SpawnRate 5 -Duration "10m" `
    -Repetitions $Repetitions -TargetHost $BaseUrl

Run-Scenario -Name "MEDIO" -Users 100 -SpawnRate 10 -Duration "10m" `
    -Repetitions $Repetitions -TargetHost $BaseUrl

Run-Scenario -Name "PICO" -Users 200 -SpawnRate 20 -Duration "5m" `
    -Repetitions $Repetitions -TargetHost $BaseUrl

$globalEnd = Get-Date
$totalElapsed = $globalEnd - $globalStart

Write-Host "`n=========================================="
Write-Host "TODOS OS TESTES CONCLUIDOS!" -ForegroundColor Green
Write-Host "=========================================="
Write-Host "Tempo total: $($totalElapsed.ToString('hh\:mm\:ss'))"
Write-Host "Resultados salvos em: $resultsDir"
Write-Host "==========================================`n"

# --- Analise Final ---
if (Test-Path ".\analisar_dados.py") {
    Write-Host "Gerando analise consolidada dos resultados..." -ForegroundColor Cyan
    try {
        & python .\analisar_dados.py
        Write-Host "[OK] Analise consolidada gerada com sucesso!" -ForegroundColor Green
        Write-Host "Verifique os arquivos em: $resultsDir"
    }
    catch {
        Write-Host "[ERRO] Erro ao gerar analise: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "[AVISO] Script 'analisar_dados.py' nao encontrado" -ForegroundColor Yellow
    Write-Host "  Execute-o manualmente para gerar a analise consolidada."
}