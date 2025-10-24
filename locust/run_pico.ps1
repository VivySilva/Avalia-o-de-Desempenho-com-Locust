# ==========================
# Teste de Carga - CENARIO PICO
# 200 usuarios, 5 minutos, 30 repeticoes
# ==========================

param(
    # [CORRIGIDO] Renomeado de '$Host' para '$BaseUrl' para evitar conflito
    # com a variavel automatica $Host do PowerShell.
    [string]$BaseUrl = "http://localhost:8080",
    
    [int]$Repetitions = 5
)

# [MELHORIA] Usar '.\' e mais explicito para indicar o diretorio atual
$resultsDir = ".\results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
    Write-Host "[OK] Pasta 'results' criada"
}

Write-Host "=========================================="
Write-Host "CENARIO PICO - TESTE DE CARGA"
Write-Host "=========================================="
Write-Host "Configuracao:"
Write-Host "  - Usuarios: 200"
Write-Host "  - Spawn Rate: 20 usuarios/s"
Write-Host "  - Duracao: 5 minutos"
Write-Host "  - Repeticoes: $Repetitions"
Write-Host "  - Host: $BaseUrl"
Write-Host "  - Aquecimento: 30 segundos (desconsiderado na analise)"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

for ($i = 1; $i -le $Repetitions; $i++) {
    Write-Host "=============================="
    Write-Host "Execucao $i/$Repetitions do cenario PICO"
    Write-Host "==============================" -ForegroundColor Yellow

    # [MELHORIA] Usar Join-Path para construir caminhos de forma segura
    $csvPrefix = Join-Path $resultsDir "PICO_exec_$i"
    $htmlReport = Join-Path $resultsDir "PICO_exec_$i.html"

    try {
        & locust -f locustfile.py `
            --headless `
            -u 200 `
            -r 20 `
            -t 5m `
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
        Write-Host "[ERRO] Erro na execucao $i}: $_" -ForegroundColor Red
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
Write-Host "[OK] CENARIO PICO CONCLUIDO!"
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Tempo total: $($elapsed.ToString('hh\:mm\:ss'))"
Write-Host "Resultados salvos em: $resultsDir\PICO_exec_*_stats.csv"
Write-Host "==========================================`n"