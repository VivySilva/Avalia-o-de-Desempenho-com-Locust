# Avaliação de Desempenho - Spring PetClinic Microservices

Projeto de teste de carga e análise de desempenho do Spring PetClinic (versão microservices) utilizando Locust.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração do Sistema](#configuração-do-sistema)
- [Execução dos Testes](#execução-dos-testes)
- [Análise dos Resultados](#análise-dos-resultados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Métricas Coletadas](#métricas-coletadas)

## 🎯 Visão Geral

Este projeto realiza uma avaliação sistemática de desempenho do Spring PetClinic Microservices através de testes de carga automatizados usando Locust.

### Objetivos

- Medir tempo de resposta (médio e máximo)
- Avaliar throughput (requisições/segundo)
- Identificar taxa de erros e sucesso
- Comparar comportamento sob diferentes cargas

### Cenários de Teste

| Cenário | Usuários | Duração | Aquecimento | Repetições |
|---------|----------|---------|-------------|------------|
| **LEVE** | 50 | 10 min | 1 min | 5 |
| **MÉDIO** | 100 | 10 min | 1 min | 5 |
| **PICO** | 200 | 5 min | 30 s | 5 |

### Mix de Requisições

- **40%** - `GET /api/customer/owners` (listar donos)
- **30%** - `GET /api/customer/owners/{id}` (buscar dono específico)
- **20%** - `GET /api/vet/vets` (listar veterinários)
- **10%** - `POST /api/customer/owners` (criar novo dono)

## 📦 Requisitos

### Software Necessário

- **Docker** e **Docker Compose** (versão 20.10+)
- **Python** 3.8+ 
- **PowerShell** 7+ (Windows) ou Bash (Linux/Mac)
- **Git**

### Bibliotecas Python

```bash
pip install locust pandas numpy matplotlib seaborn openpyxl
```

## 🚀 Instalação

### 1. Clonar o Spring PetClinic Microservices

```bash
git clone https://github.com/spring-petclinic/spring-petclinic-microservices.git
cd spring-petclinic-microservices
```

### 2. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração do Sistema

### Passo 1: Subir o Spring PetClinic

No diretório do Spring PetClinic:

```bash
docker-compose up -d
```

Aguarde alguns minutos até todos os serviços estarem prontos. Verifique com:

```bash
docker-compose ps
```

### Passo 2: Verificar Conectividade

Teste se a aplicação está respondendo:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/api/customer/owners" -Method GET
```

**Linux/Mac:**
```bash
curl http://localhost:8080/api/customer/owners
```

## 🧪 Execução dos Testes

### Opção 1: Executar Todos os Cenários (Recomendado)

**Windows:**
```powershell
.\executar.ps1
```

**Com parâmetros personalizados:**
```powershell
.\executar_todos.ps1 -Host "http://localhost:8080" -Repetitions 30
```

### Opção 2: Executar Cenários Individuais

#### Cenário LEVE (50 usuários, 10 min)
```powershell
.\run_leve.ps1
```

#### Cenário MÉDIO (100 usuários, 10 min)
```powershell
.\run_medio.ps1
```

#### Cenário PICO (200 usuários, 5 min)
```powershell
.\run_pico.ps1
```

### Opção 3: Execução Manual com Locust

```bash
locust -f locustfile.py \
    --headless \
    -u 50 \
    -r 5 \
    -t 10m \
    --csv results/teste_manual \
    --host http://localhost:8080
```

### ⏱️ Tempo Estimado

- **Cenário LEVE**: 5 exec × 10 min = ~50 min
- **Cenário MÉDIO**: 5 exec × 10 min = ~50 min  
- **Cenário PICO**: 10 exec × 5 min = ~25 min
- **TOTAL**: ~2.05 horas + análise

**💡 Dica:** Execute overnight ou em lotes menores.

## 📊 Análise dos Resultados

### Gerar Análise Consolidada

Após executar os testes:

```bash
python analisar_dados.py
```

### Arquivos Gerados

```
results/
├── LEVE_exec_1_stats.csv          # Dados brutos (90 arquivos)
├── LEVE_exec_1_failures.csv
├── LEVE_exec_1.html
├── ...
├── analise_consolidada.xlsx       # Relatório Excel
└── graficos e imagens/
    ├── comparacao_cenarios.png    # Gráficos comparativos
    └── distribuicoes.png          # Box plots
```

### Estrutura do Excel

**Aba 1 - Resumo:**
- Comparação rápida dos 3 cenários
- Métricas principais com média ± desvio padrão

**Aba 2-4 - Dados Detalhados:**
- Dados brutos de cada execução por cenário

**Aba 5 - Estatísticas:**
- Análise estatística completa (média, desvio, min, max)

## 📁 Estrutura do Projeto

```
projeto-teste-carga/
│
├── locustfile.py              # Definição das tarefas do Locust
├── executar_todos.ps1         # Script principal (todos cenários)
├── run_leve.ps1               # Script cenário LEVE
├── run_medio.ps1              # Script cenário MÉDIO
├── run_pico.ps1               # Script cenário PICO
├── analisar_dados.py          # Análise consolidada
├── popular_banco.py           # Popular banco de dados
├── requirements.txt           # Dependências Python
├── README.md                  # Esta documentação
│
└── results/                   # Resultados dos testes
    ├── LEVE_exec_*.csv
    ├── MEDIO_exec_*.csv
    ├── PICO_exec_*.csv
    ├── analise_consolidada.xlsx
    └── graficos/
        ├── comparacao_cenarios.png
        └── distribuicoes.png
```

## 📈 Métricas Coletadas

### 1. Tempo de Resposta
- **Tempo Médio (ms)**: Média de todas as requisições
- **Tempo Máximo (ms)**: Pior caso observado
- Inclui média ± desvio padrão de 30 execuções

### 2. Throughput
- **Requisições/segundo**: Capacidade do sistema
- Comparação entre cenários

### 3. Confiabilidade
- **Taxa de Sucesso (%)**: Percentual de requisições bem-sucedidas
- **Total de Erros**: Contagem de falhas (4xx/5xx)

### 4. Volume
- **Total de Requisições**: Quantidade total processada por cenário

## 🔍 Interpretação dos Resultados

### Análise Esperada

**Cenário LEVE (50 usuários):**
- ✅ Tempo de resposta baixo (<100ms)
- ✅ Taxa de sucesso próxima de 100%
- ✅ Sistema opera confortavelmente

**Cenário MÉDIO (100 usuários):**
- ⚠️ Tempo de resposta aumenta moderadamente
- ⚠️ Taxa de sucesso ainda alta (>99%)
- ⚠️ Sistema começa a mostrar estresse

**Cenário PICO (200 usuários):**
- ⚠️ Tempo de resposta pode degradar significativamente
- ⚠️ Possível aparecimento de erros
- ⚠️ Identifica limites do sistema

**Desenvolvido para avaliação de desempenho do Spring PetClinic Microservices**

**Data:** Outubro 2025  
**Ferramenta:** Locust  
**Metodologia:** 5 repetições por cenário com análise estatística

**link video:** https://youtu.be/Ru67gmDR25w

