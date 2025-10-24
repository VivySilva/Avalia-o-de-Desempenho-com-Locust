"""
Análise Consolidada dos Resultados dos Testes de Carga
Processa todos os CSVs gerados pelo Locust e gera:
- Tabelas consolidadas com médias e desvios padrão
- Gráficos comparativos
- Relatório em Excel

**Versão 2: Lida com o descarte do período de aquecimento**
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
GRAFICOS_DIR = RESULTS_DIR / "graficos"
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
    Lê o arquivo _stats_history.csv do Locust, descarta o aquecimento
    e extrai as métricas principais do período de teste.
    """
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            print(f"⚠ Arquivo vazio: {filepath}")
            return None
        
        # 1. Obter duração do aquecimento em segundos
        warmup_str = SCENARIOS[scenario_name]['warmup_str']
        warmup_seconds = parse_duration_to_seconds(warmup_str)
        
        # 2. Encontrar o timestamp de início e o fim do aquecimento
        start_time_ts = df['Timestamp'].min()
        warmup_end_ts = start_time_ts + warmup_seconds
        
        # 3. Filtrar o DataFrame para o período pós-aquecimento
        df_period = df[df['Timestamp'] >= warmup_end_ts]
        
        if df_period.empty:
            print(f"⚠ Nenhum dado após aquecimento em: {filepath}. O teste pode ter sido curto demais.")
            return None
            
        # 4. Encontrar a última linha *antes* do período de teste começar
        # Isso nos dá os totais acumulados durante o aquecimento
        df_warmup = df[df['Timestamp'] < warmup_end_ts]
        
        if df_warmup.empty:
            # Caso o teste comece direto (sem aquecimento gravado)
            requests_before = 0
            failures_before = 0
        else:
            last_warmup_row = df_warmup.iloc[-1]
            requests_before = last_warmup_row['Total Request Count']
            failures_before = last_warmup_row['Total Failure Count']
            
        # 5. Encontrar a última linha do teste
        last_test_row = df.iloc[-1]

        # 6. Calcular os totais *apenas* para o período de teste
        total_requests = last_test_row['Total Request Count'] - requests_before
        total_failures = last_test_row['Total Failure Count'] - failures_before
        
        if total_requests == 0:
            print(f"⚠ Zero requisições após aquecimento em: {filepath}")
            return None

        # 7. Calcular as métricas do período
        # A média do "Average Response Time" do histórico é a média das médias por segundo
        avg_response_time = df_period['Average Response Time'].mean()
        # O "Max Response Time" é o máximo de todo o período
        max_response_time = df_period['Max Response Time'].max()
        # "Requests/s" é a média das taxas por segundo
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
    print(f"\n📊 Analisando cenário: {scenario_name} (descartando {SCENARIOS[scenario_name]['warmup_str']} de aquecimento)")
    
    # [MODIFICADO] Buscar arquivos _stats_history.csv
    pattern = str(RESULTS_DIR / f"{scenario_name}_exec_*_stats_history.csv")
    files = glob.glob(pattern)
    
    if not files:
        print(f"   ✗ Nenhum arquivo *_stats_history.csv encontrado para {scenario_name}")
        return None
    
    print(f"  ✓ Encontrados {len(files)} arquivos de histórico")
    
    results = []
    for filepath in sorted(files):
        # [MODIFICADO] Passar o nome do cenário para o parser
        stats = parse_stats_file(filepath, scenario_name)
        if stats:
            results.append(stats)
    
    if not results:
        print(f"  ✗ Nenhum dado válido para {scenario_name}")
        return None
    
    # [RENOMEADO] Converter para DataFrame
    raw_data = pd.DataFrame(results)
    
    # [RENOMEADO] Calcular estatísticas
    summary = {
        'scenario': scenario_name,
        'executions': len(raw_data),
        'users': SCENARIOS[scenario_name]['users'],
        
        # Tempo de resposta médio
        'avg_resp_mean': raw_data['avg_response_time'].mean(),
        'avg_resp_std': raw_data['avg_response_time'].std(),
        'avg_resp_min': raw_data['avg_response_time'].min(),
        'avg_resp_max': raw_data['avg_response_time'].max(),
        
        # Tempo de resposta máximo
        'max_resp_mean': raw_data['max_response_time'].mean(),
        'max_resp_std': raw_data['max_response_time'].std(),
        'max_resp_min': raw_data['max_response_time'].min(),
        'max_resp_max': raw_data['max_response_time'].max(),
        
        # Requisições por segundo
        'rps_mean': raw_data['requests_per_sec'].mean(),
        'rps_std': raw_data['requests_per_sec'].std(),
        'rps_min': raw_data['requests_per_sec'].min(),
        'rps_max': raw_data['requests_per_sec'].max(),
        
        # Total de requisições
        'total_req_mean': raw_data['total_requests'].mean(),
        'total_req_std': raw_data['total_requests'].std(),
        
        # Taxa de sucesso
        'success_rate_mean': raw_data['success_rate'].mean(),
        'success_rate_std': raw_data['success_rate'].std(),
        'success_rate_min': raw_data['success_rate'].min(),
        
        # Erros
        'failures_mean': raw_data['failure_count'].mean(),
        'failures_total': raw_data['failure_count'].sum()
    }
    
    print(f"  ✓ Análise concluída: {len(raw_data)} execuções processadas")
    
    return summary, raw_data


def create_comparison_plots(all_data):
    """Cria gráficos comparativos entre cenários"""
    print("\n📈 Gerando gráficos comparativos...")
    
    scenarios = list(all_data.keys())
    
    # Figura 1: Tempo de Resposta Médio
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comparação de Desempenho entre Cenários (Pós-Aquecimento)', fontsize=16, fontweight='bold')
    
    # 1.1 Tempo Médio de Resposta
    ax = axes[0, 0]
    means = [all_data[s]['summary']['avg_resp_mean'] for s in scenarios]
    stds = [all_data[s]['summary']['avg_resp_std'] for s in scenarios]
    users = [all_data[s]['summary']['users'] for s in scenarios]
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=5, alpha=0.7, color=['green', 'orange', 'red'])
    ax.set_ylabel('Tempo Médio (ms)', fontweight='bold')
    ax.set_xlabel('Cenário', fontweight='bold')
    ax.set_title('Tempo Médio de Resposta')
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
    ax.set_ylabel('Requisições/segundo', fontweight='bold')
    ax.set_xlabel('Cenário', fontweight='bold')
    ax.set_title('Throughput (Requisições/s)')
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
    ax.set_xlabel('Cenário', fontweight='bold')
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
    ax.set_ylabel('Tempo Máximo (ms)', fontweight='bold')
    ax.set_xlabel('Cenário', fontweight='bold')
    ax.set_title('Tempo Máximo de Resposta')
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
    fig.suptitle('Distribuição de Métricas por Cenário (Pós-Aquecimento)', fontsize=16, fontweight='bold')
    
    # 2.1 Box plot - Tempo Médio
    ax = axes[0]
    # [RENOMEADO]
    data_to_plot = [all_data[s]['raw_data']['avg_response_time'] for s in scenarios]
    bp = ax.boxplot(data_to_plot, labels=scenarios, patch_artist=True)
    for patch, color in zip(bp['boxes'], ['lightgreen', 'lightyellow', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Tempo Médio de Resposta (ms)', fontweight='bold')
    ax.set_title('Distribuição - Tempo Médio')
    ax.grid(axis='y', alpha=0.3)
    
    # 2.2 Box plot - RPS
    ax = axes[1]
    # [RENOMEADO]
    data_to_plot = [all_data[s]['raw_data']['requests_per_sec'] for s in scenarios]
    bp = ax.boxplot(data_to_plot, labels=scenarios, patch_artist=True)
    for patch, color in zip(bp['boxes'], ['lightgreen', 'lightyellow', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Requisições/segundo', fontweight='bold')
    ax.set_title('Distribuição - Throughput')
    ax.grid(axis='y', alpha=0.3)
    
    # 2.3 Box plot - Taxa de Sucesso
    ax = axes[2]
    # [RENOMEADO]
    data_to_plot = [all_data[s]['raw_data']['success_rate'] for s in scenarios]
    bp = ax.boxplot(data_to_plot, labels=scenarios, patch_artist=True)
    for patch, color in zip(bp['boxes'], ['lightgreen', 'lightyellow', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Taxa de Sucesso (%)', fontweight='bold')
    ax.set_title('Distribuição - Taxa de Sucesso')
    ax.axhline(y=99, color='red', linestyle='--', alpha=0.5, label='SLA: 99%')
    ax.grid(axis='y', alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / 'distribuicoes.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Salvo: distribuicoes.png")
    plt.close()


def generate_excel_report(all_data):
    """Gera relatório consolidado em Excel"""
    print("\n📄 Gerando relatório Excel...")
    
    output_file = RESULTS_DIR / 'analise_consolidada.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Aba 1: Resumo Executivo
        summary_data = []
        for scenario in ['LEVE', 'MEDIO', 'PICO']:
            if scenario in all_data:
                s = all_data[scenario]['summary']
                summary_data.append({
                    'Cenário': scenario,
                    'Usuários': s['users'],
                    'Execuções': s['executions'],
                    'Tempo Médio (ms)': f"{s['avg_resp_mean']:.2f} ± {s['avg_resp_std']:.2f}",
                    'Tempo Máx (ms)': f"{s['max_resp_mean']:.0f} ± {s['max_resp_std']:.0f}",
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
                # [RENOMEADO]
                raw_data = all_data[scenario]['raw_data'].copy()
                raw_data.to_excel(writer, sheet_name=f'Dados_{scenario}', index=False)
        
        # Aba 3: Estatísticas Detalhadas
        detailed_data = []
        for scenario in ['LEVE', 'MEDIO', 'PICO']:
            if scenario in all_data:
                s = all_data[scenario]['summary']
                detailed_data.extend([
                    {'Cenário': scenario, 'Métrica': 'Tempo Médio (ms)', 
                     'Média': s['avg_resp_mean'], 'Desvio Padrão': s['avg_resp_std'],
                     'Mínimo': s['avg_resp_min'], 'Máximo': s['avg_resp_max']},
                    {'Cenário': scenario, 'Métrica': 'Tempo Máximo (ms)',
                     'Média': s['max_resp_mean'], 'Desvio Padrão': s['max_resp_std'],
                     'Mínimo': s['max_resp_min'], 'Máximo': s['max_resp_max']},
                    {'Cenário': scenario, 'Métrica': 'Req/s',
                     'Média': s['rps_mean'], 'Desvio Padrão': s['rps_std'],
                     'Mínimo': s['rps_min'], 'Máximo': s['rps_max']},
                    {'Cenário': scenario, 'Métrica': 'Taxa Sucesso (%)',
                     'Média': s['success_rate_mean'], 'Desvio Padrão': s['success_rate_std'],
                     'Mínimo': s['success_rate_min'], 'Máximo': 100.0}
                ])
        
        df_detailed = pd.DataFrame(detailed_data)
        df_detailed.to_excel(writer, sheet_name='Estatísticas', index=False)
    
    print(f"  ✓ Relatório salvo: {output_file}")


def main():
    print("=" * 60)
    print("ANÁLISE CONSOLIDADA - TESTES DE CARGA SPRING PETCLINIC")
    print("Versão 2.0 (Com descarte de aquecimento)")
    print("=" * 60)
    
    all_data = {}
    
    # Processar cada cenário
    for scenario in ['LEVE', 'MEDIO', 'PICO']:
        if scenario not in SCENARIOS:
            print(f"⚠ Cenário '{scenario}' não definido. Pulando.")
            continue
            
        summary, raw_data = analyze_scenario(scenario)
        if summary and raw_data is not None:
            all_data[scenario] = {
                'summary': summary,
                'raw_data': raw_data
            }
    
    if not all_data:
        print("\n✗ Nenhum dado encontrado para análise!")
        print("  Certifique-se de executar os testes primeiro e que os arquivos")
        print("  *_stats_history.csv existem em ./results/")
        return
    
    # Gerar gráficos
    create_comparison_plots(all_data)
    
    # Gerar relatório Excel
    generate_excel_report(all_data)
    
    # Imprimir resumo no console
    print("\n" + "=" * 60)
    print("RESUMO DOS RESULTADOS (Pós-Aquecimento)")
    print("=" * 60)
    
    for scenario in ['LEVE', 'MEDIO', 'PICO']:
        if scenario in all_data:
            s = all_data[scenario]['summary']
            print(f"\n📊 {scenario} ({s['users']} usuários, {s['executions']} execuções):")
            print(f"  • Tempo Médio: {s['avg_resp_mean']:.2f} ms (±{s['avg_resp_std']:.2f})")
            print(f"  • Tempo Máximo: {s['max_resp_mean']:.0f} ms (±{s['max_resp_std']:.0f})")
            print(f"  • Throughput: {s['rps_mean']:.2f} req/s (±{s['rps_std']:.2f})")
            print(f"  • Taxa Sucesso: {s['success_rate_mean']:.2f}%")
            print(f"  • Total Erros (global): {int(s['failures_total'])}")
    
    print("\n" + "=" * 60)
    print("✓ ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print(f"\nArquivos gerados:")
    print(f"  • {RESULTS_DIR / 'analise_consolidada.xlsx'}")
    print(f"  • {GRAFICOS_DIR / 'comparacao_cenarios.png'}")
    print(f"  • {GRAFICOS_DIR / 'distribuicoes.png'}")
    print()


if __name__ == "__main__":
    main()