"""
Análise Consolidada dos Resultados dos Testes de Carga
Processa todos os CSVs gerados pelo Locust e gera:
- Tabelas consolidadas com médias e desvios padrão
- Gráficos comparativos
- Relatório em Excel

**Versão 4.0: Corrigido para filtrar pela coluna 'Name'**
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob
import warnings

warnings.filterwarnings('ignore')

# Configurações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

RESULTS_DIR = Path("results")
GRAFICOS_DIR = RESULTS_DIR / "graficos e imagens"
GRAFICOS_DIR.mkdir(exist_ok=True)

# Configurações dos cenários (com aquecimento)
SCENARIOS = {
    'LEVE': {'users': 50, 'duration': '10m', 'warmup_str': '1m'},
    'MEDIO': {'users': 100, 'duration': '10m', 'warmup_str': '1m'},
    'PICO': {'users': 200, 'duration': '5m', 'warmup_str': '30s'}
}

def parse_duration_to_seconds(duration_str):
    """Converte strings como '1m' ou '30s' para segundos"""
    if 'm' in duration_str:
        return int(duration_str.replace('m', '')) * 60
    if 's' in duration_str:
        return int(duration_str.replace('s', ''))
    return 0

def parse_stats_file(filepath, scenario_name):
    """
    Le o arquivo _stats_history.csv do Locust,
    descarta o aquecimento e extrai as métricas.
    """
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            print(f"⚠ Arquivo vazio: {filepath}")
            return None
        
        df_agg = df[df['Name'] == 'Aggregated'].copy()
        
        if df_agg.empty:
            print(f"⚠ Nenhuma linha 'Aggregated' encontrada em: {filepath} (verifique a coluna 'Name')")
            return None
            
        # 1. Obter duracao do aquecimento em segundos
        warmup_str = SCENARIOS[scenario_name]['warmup_str']
        warmup_seconds = parse_duration_to_seconds(warmup_str)
        
        # 2. Encontrar o timestamp de início e o fim do aquecimento
        start_time_ts = df_agg['Timestamp'].min()
        warmup_end_ts = start_time_ts + warmup_seconds
        
        # 3. Filtrar o DataFrame para o período pós-aquecimento
        df_period = df_agg[df_agg['Timestamp'] >= warmup_end_ts]
        
        if df_period.empty:
            print(f"⚠ Nenhum dado apos aquecimento em: {filepath}. O teste pode ter sido curto demais.")
            return None
            
        # 4. Encontrar a última linha *antes* do período de teste começar
        df_warmup = df_agg[df_agg['Timestamp'] < warmup_end_ts]
        
        requests_before = 0
        failures_before = 0
        total_response_time_before = 0.0 # (Media * Contagem)
        
        if not df_warmup.empty:
            last_warmup_row = df_warmup.iloc[-1]
            requests_before = last_warmup_row['Total Request Count']
            failures_before = last_warmup_row['Total Failure Count']
            
            total_response_time_before = last_warmup_row['Total Average Response Time'] * requests_before
            
        # 5. Encontrar a última linha do teste
        last_test_row = df_agg.iloc[-1]

        # 6. Calcular os totais *apenas* para o período de teste
        total_requests = last_test_row['Total Request Count'] - requests_before
        total_failures = last_test_row['Total Failure Count'] - failures_before
        
        if total_requests == 0:
            print(f"⚠ Zero requisicoes apos aquecimento em: {filepath}")
            return None

        # 7. Calcular as métricas do período
        
        total_response_time_all = last_test_row['Total Average Response Time'] * last_test_row['Total Request Count']
        total_response_time_period = total_response_time_all - total_response_time_before
        avg_response_time = total_response_time_period / total_requests
        
        max_response_time = df_period['100%'].max() 
        
        requests_per_sec = df_period['Requests/s'].mean() 
        
        success_rate = (1 - total_failures / total_requests) * 100
        
        return {
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'requests_per_sec': requests_per_sec,
            'total_requests': total_requests,
            'failure_count': total_failures,
            'success_rate': success_rate
        }
    except Exception as e:
        print(f"⚠ Erro ao processar {filepath}: {e}")
        return None


def analyze_scenario(scenario_name):
    """Analisa todas as execuções de um cenário específico"""
    print(f"\n📊 Analisando cenario: {scenario_name} (descartando {SCENARIOS[scenario_name]['warmup_str']} de aquecimento)")
    
    pattern = str(RESULTS_DIR / f"{scenario_name}_exec_*_stats_history.csv")
    files = glob.glob(pattern)
    
    if not files:
        print(f"   ✗ Nenhum arquivo *_stats_history.csv encontrado para {scenario_name}")
        return None
    
    print(f"  ✓ Encontrados {len(files)} arquivos de historico")
    
    results = []
    for filepath in sorted(files):
        stats = parse_stats_file(filepath, scenario_name)
        if stats:
            results.append(stats)
    
    if not results:
        print(f"  ✗ Nenhum dado valido para {scenario_name}")
        return None
    
    raw_data = pd.DataFrame(results)
    
    summary = {
        'scenario': scenario_name,
        'executions': len(raw_data),
        'users': SCENARIOS[scenario_name]['users'],
        
        'avg_resp_mean': raw_data['avg_response_time'].mean(),
        'avg_resp_std': raw_data['avg_response_time'].std(),
        'avg_resp_min': raw_data['avg_response_time'].min(),
        'avg_resp_max': raw_data['avg_response_time'].max(),
        
        'max_resp_mean': raw_data['max_response_time'].mean(),
        'max_resp_std': raw_data['max_response_time'].std(),
        'max_resp_min': raw_data['max_response_time'].min(),
        'max_resp_max': raw_data['max_response_time'].max(),
        
        'rps_mean': raw_data['requests_per_sec'].mean(),
        'rps_std': raw_data['requests_per_sec'].std(),
        'rps_min': raw_data['requests_per_sec'].min(),
        'rps_max': raw_data['requests_per_sec'].max(),
        
        'total_req_mean': raw_data['total_requests'].mean(),
        'total_req_std': raw_data['total_requests'].std(),
        
        'success_rate_mean': raw_data['success_rate'].mean(),
        'success_rate_std': raw_data['success_rate'].std(),
        'success_rate_min': raw_data['success_rate'].min(),
        
        'failures_mean': raw_data['failure_count'].mean(),
        'failures_total': raw_data['failure_count'].sum()
    }
    
    print(f"  ✓ Analise concluida: {len(raw_data)} execucoes processadas")
    
    return summary, raw_data


def create_comparison_plots(all_data):
    """Cria gráficos comparativos entre cenários"""
    print("\n📈 Gerando graficos comparativos...")
    
    scenarios = list(all_data.keys())
    if not scenarios:
        print("  ✗ Sem dados para plotar.")
        return
        
    # Figura 1: Tempo de Resposta Médio
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comparacao de Desempenho entre Cenarios (Pos-Aquecimento)', fontsize=16, fontweight='bold')
    
    # 1.1 Tempo Médio de Resposta
    ax = axes[0, 0]
    means = [all_data[s]['summary']['avg_resp_mean'] for s in scenarios]
    stds = [all_data[s]['summary']['avg_resp_std'] for s in scenarios]
    users = [all_data[s]['summary']['users'] for s in scenarios]
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=5, alpha=0.7, color=['green', 'orange', 'red'])
    ax.set_ylabel('Tempo Medio (ms)', fontweight='bold')
    ax.set_xlabel('Cenario', fontweight='bold')
    ax.set_title('Tempo Medio de Resposta')
    ax.grid(axis='y', alpha=0.3)
    
    for i, (bar, user) in enumerate(zip(bars, users)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{means[i]:.1f}ms\n({user} users)',
                ha='center', va='bottom', fontsize=9)
    
    # 1.2 Requisições por Segundo
    ax = axes[0, 1]
    means = [all_data[s]['summary']['rps_mean'] for s in scenarios]
    stds = [all_data[s]['summary']['rps_std'] for s in scenarios]
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=5, alpha=0.7, color=['green', 'orange', 'red'])
    ax.set_ylabel('Requisicoes/segundo', fontweight='bold')
    ax.set_xlabel('Cenario', fontweight='bold')
    ax.set_title('Throughput (Requisicoes/s)')
    ax.grid(axis='y', alpha=0.3)
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{means[i]:.1f} req/s',
                ha='center', va='bottom', fontsize=9)
    
    # 1.3 Taxa de Sucesso
    ax = axes[1, 0]
    means = [all_data[s]['summary']['success_rate_mean'] for s in scenarios]
    stds = [all_data[s]['summary']['success_rate_std'] for s in scenarios]
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=5, alpha=0.7, color=['green', 'orange', 'red'])
    ax.set_ylabel('Taxa de Sucesso (%)', fontweight='bold')
    ax.set_xlabel('Cenario', fontweight='bold')
    ax.set_title('Taxa de Sucesso')
    ax.set_ylim([0, 105])
    ax.axhline(y=99, color='blue', linestyle='--', alpha=0.5, label='SLA: 99%')
    ax.grid(axis='y', alpha=0.3)
    ax.legend()
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{means[i]:.2f}%',
                ha='center', va='bottom', fontsize=9)
    
    # 1.4 Tempo Máximo de Resposta
    ax = axes[1, 1]
    means = [all_data[s]['summary']['max_resp_mean'] for s in scenarios]
    stds = [all_data[s]['summary']['max_resp_std'] for s in scenarios]
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=5, alpha=0.7, color=['green', 'orange', 'red'])
    ax.set_ylabel('Tempo Maximo (ms)', fontweight='bold')
    ax.set_xlabel('Cenario', fontweight='bold')
    ax.set_title('Tempo Maximo de Resposta')
    ax.grid(axis='y', alpha=0.3)
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{means[i]:.0f}ms',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / 'comparacao_cenarios.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Salvo: comparacao_cenarios.png")
    plt.close()
    
    # Figura 2: Box plots para distribuições
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Distribuicao de Metricas por Cenario (Pos-Aquecimento)', fontsize=16, fontweight='bold')
    
    # 2.1 Box plot - Tempo Médio
    ax = axes[0]
    data_to_plot = [all_data[s]['raw_data']['avg_response_time'] for s in scenarios]
    bp = ax.boxplot(data_to_plot, labels=scenarios, patch_artist=True)
    for patch, color in zip(bp['boxes'], ['lightgreen', 'lightyellow', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Tempo Medio de Resposta (ms)', fontweight='bold')
    ax.set_title('Distribuicao - Tempo Medio')
    ax.grid(axis='y', alpha=0.3)
    
    # 2.2 Box plot - RPS
    ax = axes[1]
    data_to_plot = [all_data[s]['raw_data']['requests_per_sec'] for s in scenarios]
    bp = ax.boxplot(data_to_plot, labels=scenarios, patch_artist=True)
    for patch, color in zip(bp['boxes'], ['lightgreen', 'lightyellow', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Requisicoes/segundo', fontweight='bold')
    ax.set_title('Distribuicao - Throughput')
    ax.grid(axis='y', alpha=0.3)
    
    # 2.3 Box plot - Taxa de Sucesso
    ax = axes[2]
    data_to_plot = [all_data[s]['raw_data']['success_rate'] for s in scenarios]
    bp = ax.boxplot(data_to_plot, labels=scenarios, patch_artist=True)
    for patch, color in zip(bp['boxes'], ['lightgreen', 'lightyellow', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Taxa de Sucesso (%)', fontweight='bold')
    ax.set_title('Distribuicao - Taxa de Sucesso')
    ax.axhline(y=99, color='red', linestyle='--', alpha=0.5, label='SLA: 99%')
    ax.grid(axis='y', alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / 'distribuicoes.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Salvo: distribuicoes.png")
    plt.close()


def generate_excel_report(all_data):
    """Gera relatório consolidado em Excel"""
    print("\n📄 Gerando relatorio Excel...")
    
    output_file = RESULTS_DIR / 'analise_consolidada.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Aba 1: Resumo Executivo
        summary_data = []
        for scenario in ['LEVE', 'MEDIO', 'PICO']:
            if scenario in all_data:
                s = all_data[scenario]['summary']
                summary_data.append({
                    'Cenario': scenario,
                    'Usuarios': s['users'],
                    'Execucoes': s['executions'],
                    'Tempo Medio (ms)': f"{s['avg_resp_mean']:.2f} ± {s['avg_resp_std']:.2f}",
                    'Tempo Max (ms)': f"{s['max_resp_mean']:.0f} ± {s['max_resp_std']:.0f}",
                    'Req/s': f"{s['rps_mean']:.2f} ± {s['rps_std']:.2f}",
                    'Total Req (por exec)': f"{s['total_req_mean']:.0f}",
                    'Taxa Sucesso (%)': f"{s['success_rate_mean']:.2f}%",
                    'Total Erros (global)': int(s['failures_total'])
                })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Resumo', index=False)
        
        # Aba 2: Detalhes por Cenário
        for scenario in ['LEVE', 'MEDIO', 'PICO']:
            if scenario in all_data:
                raw_data = all_data[scenario]['raw_data'].copy()
                raw_data.to_excel(writer, sheet_name=f'Dados_{scenario}', index=False)
        
        # Aba 3: Estatísticas Detalhadas
        detailed_data = []
        for scenario in ['LEVE', 'MEDIO', 'PICO']:
            if scenario in all_data:
                s = all_data[scenario]['summary']
                detailed_data.extend([
                    {'Cenario': scenario, 'Metrica': 'Tempo Medio (ms)', 
                     'Media': s['avg_resp_mean'], 'Desvio Padrao': s['avg_resp_std'],
                     'Minimo': s['avg_resp_min'], 'Maximo': s['avg_resp_max']},
                    {'Cenario': scenario, 'Metrica': 'Tempo Maximo (ms)',
                     'Media': s['max_resp_mean'], 'Desvio Padrao': s['max_resp_std'],
                     'Minimo': s['max_resp_min'], 'Maximo': s['max_resp_max']},
                    {'Cenario': scenario, 'Metrica': 'Req/s',
                     'Media': s['rps_mean'], 'Desvio Padrao': s['rps_std'],
                     'Minimo': s['rps_min'], 'Maximo': s['rps_max']},
                    {'Cenario': scenario, 'Metrica': 'Taxa Sucesso (%)',
                     'Media': s['success_rate_mean'], 'Desvio Padrao': s['success_rate_std'],
                     'Minimo': s['success_rate_min'], 'Maximo': 100.0}
                ])
        
        df_detailed = pd.DataFrame(detailed_data)
        df_detailed.to_excel(writer, sheet_name='Estatisticas', index=False)
    
    print(f"  ✓ Relatorio salvo: {output_file}")


def main():
    print("=" * 60)
    print("ANALISE CONSOLIDADA - TESTES DE CARGA SPRING PETCLINIC")
    print("Versao 4.0 (Corrigido para coluna 'Name')")
    print("=" * 60)
    
    all_data = {}
    
    # Processar cada cenário
    for scenario in ['LEVE', 'MEDIO', 'PICO']:
        if scenario not in SCENARIOS:
            print(f"⚠ Cenario '{scenario}' nao definido. Pulando.")
            continue
            
        result = analyze_scenario(scenario)
        if result:
            summary, raw_data = result
            if summary and raw_data is not None:
                all_data[scenario] = {
                    'summary': summary,
                    'raw_data': raw_data
                }
    
    if not all_data:
        print("\n✗ Nenhum dado encontrado para analise!")
        print("  Verifique os logs de erro acima.")
        return
    
    # Gerar gráficos
    create_comparison_plots(all_data)
    
    # Gerar relatório Excel
    generate_excel_report(all_data)
    
    # Imprimir resumo no console
    print("\n" + "=" * 60)
    print("RESUMO DOS RESULTADOS (Pos-Aquecimento)")
    print("=" * 60)
    
    for scenario in ['LEVE', 'MEDIO', 'PICO']:
        if scenario in all_data:
            s = all_data[scenario]['summary']
            print(f"\n📊 {scenario} ({s['users']} usuarios, {s['executions']} execucoes):")
            print(f"  • Tempo Medio: {s['avg_resp_mean']:.2f} ms (±{s['avg_resp_std']:.2f})")
            print(f"  • Tempo Maximo: {s['max_resp_mean']:.0f} ms (±{s['max_resp_std']:.0f})")
            print(f"  • Throughput: {s['rps_mean']:.2f} req/s (±{s['rps_std']:.2f})")
            print(f"  • Taxa Sucesso: {s['success_rate_mean']:.2f}%")
            print(f"  • Total Erros (global): {int(s['failures_total'])}")
    
    print("\n" + "=" * 60)
    print("✓ ANALISE CONCLUIDA COM SUCESSO!")
    print("=" * 60)
    print(f"\nArquivos gerados:")
    print(f"  • {RESULTS_DIR / 'analise_consolidada.xlsx'}")
    print(f"  • {GRAFICOS_DIR / 'comparacao_cenarios.png'}")
    print(f"  • {GRAFICOS_DIR / 'distribuicoes.png'}")
    print()


if __name__ == "__main__":
    main()