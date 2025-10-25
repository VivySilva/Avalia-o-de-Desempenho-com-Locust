# ==========================
# Teste de Carga - CENARIO LEVE
# 50 usuarios, 10 minutos, 30 repeticoes
# ==========================

param(
    # Define o host-alvo para o teste
    [string]$BaseUrl = "http://localhost:8080",
    
    # Define o numero de repeticoes do cenario
    [int]$Repetitions = 5
)

# Define o diretorio de resultados na pasta atual
$resultsDir = ".\results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
    Write-Host "Pasta 'results' criada em $resultsDir"
}

Write-Host "=========================================="
Write-Host "CENARIO LEVE - TESTE DE CARGA"
Write-Host "=========================================="
Write-Host "Configuracao:"
Write-Host "  - Usuarios: 50"
Write-Host "  - Spawn Rate: 5 usuarios/s"
Write-Host "  - Duracao: 10 minutos"
Write-Host "  - Repeticoes: $Repetitions"
Write-Host "  - Host (Alvo): $BaseUrl" 
Write-Host "  - Aquecimento: 1 minuto (desconsiderado na analise)"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

for ($i = 1; $i -le $Repetitions; $i++) {
    Write-Host "=============================="
    Write-Host "Execucao $i/$Repetitions do cenario LEVE"
    Write-Host "==============================" -ForegroundColor Yellow

    $csvPrefix = Join-Path $resultsDir "LEVE_exec_$i"
    $htmlReport = Join-Path $resultsDir "LEVE_exec_$i.html"

    try {
        & locust -f locustfile.py `
            --headless `
            -u 50 `
            -r 5 `
            -t 10m `
            --csv $csvPrefix `
            --html $htmlReport `
            --host $BaseUrl 

        # $LASTEXITCODE armazena o codigo de saida do ultimo programa (locust)
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Execucao $i concluida com sucesso" -ForegroundColor Green
        } else {
            Write-Host "Execucao $i falhou (Codigo de Saida: $LASTEXITCODE)" -ForegroundColor Red
        }
    }
    catch {
        # $_ aqui captura o erro do PowerShell (ex: 'locust' nao encontrado)
        Write-Host "Erro na execucao {$i}: $_" -ForegroundColor Red
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
Write-Host "CENARIO LEVE CONCLUIDO!"
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Tempo total: $($elapsed.ToString('hh\:mm\:ss'))"
# Locust cria arquivos como _stats.csv, _failures.csv, etc.
Write-Host "Resultados salvos em: $resultsDir/LEVE_exec_*_stats.csv"
Write-Host "==========================================`n" # 