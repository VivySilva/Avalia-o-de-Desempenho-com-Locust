# ==========================
# Teste de Carga - CENARIO MEDIO
# 100 usuarios, 10 minutos, 30 repeticoes
# ==========================

param(
    [string]$BaseUrl = "http://localhost:8080",
    
    [int]$Repetitions = 5
)

$resultsDir = ".\results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
    Write-Host "[OK] Pasta 'results' criada"
}

Write-Host "=========================================="
Write-Host "CENARIO MEDIO - TESTE DE CARGA"
Write-Host "=========================================="
Write-Host "Configuracao:"
Write-Host "  - Usuarios: 100"
Write-Host "  - Spawn Rate: 10 usuarios/s"
Write-Host "  - Duracao: 10 minutos"
Write-Host "  - Repeticoes: $Repetitions"
Write-Host "  - Host: $BaseUrl"
Write-Host "  - Aquecimento: 1 minuto (desconsiderado na analise)"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

for ($i = 1; $i -le $Repetitions; $i++) {
    Write-Host "=============================="
    Write-Host "Execucao $i/$Repetitions do cenario MEDIO"
    Write-Host "==============================" -ForegroundColor Yellow

    $csvPrefix = Join-Path $resultsDir "MEDIO_exec_$i"
    $htmlReport = Join-Path $resultsDir "MEDIO_exec_$i.html"

    try {
        & locust -f locustfile.py `
            --headless `
            -u 100 `
            -r 10 `
            -t 10m `
            --csv $csvPrefix `
            --html $htmlReport `
            --host $BaseUrl 

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Execucao $i concluida com sucesso" -ForegroundColor Green
        } else {
            Write-Host "[ERRO] Execucao $i falhou (Codigo de Saida: $LASTEXITCODE)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "[ERRO] Erro na execucao {$i}: $_" -ForegroundColor Red
    }

    # Pausa entre execucoes
    if ($i -lt $Repetitions) {
        Write-Host "Aguardando 10 segundos antes da proxima execucao..."
        Write-Host "------------------------------`n"
        Start-Sleep -Seconds 10
    }
}

$endTime = Get-Date
$elapsed = $endTime - $startTime

Write-Host "`n=========================================="
Write-Host "[OK] CENARIO MEDIO CONCLUIDO!"
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Tempo total: $($elapsed.ToString('hh\:mm\:ss'))"
Write-Host "Resultados salvos em: $resultsDir\MEDIO_exec_*_stats.csv"
Write-Host "==========================================`n"