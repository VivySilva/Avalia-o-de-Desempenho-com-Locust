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

### 2. Clonar este Repositório de Testes

```bash
cd ..
git clone <seu-repositorio-de-testes>
cd <diretorio-testes>
```

### 3. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

**Arquivo `requirements.txt`:**
```
locust>=2.15.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
openpyxl>=3.1.0
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

### Passo 3: Popular o Banco de Dados

O Spring PetClinic já vem com dados iniciais, mas você pode adicionar mais:

**Script `popular_banco.py`:**

```python
import requests
import random

BASE_URL = "http://localhost:8080"

# Gerar 100 donos de exemplo
for i in range(1, 101):
    owner = {
        "firstName": f"TestOwner{i}",
        "lastName": f"LastName{i}",
        "address": f"Rua Teste {i}",
        "city": random.choice(["Picos", "São Paulo", "Rio de Janeiro", "Brasília"]),
        "telephone": f"88{random.randint(10000000, 99999999)}"
    }
    
    response = requests.post(f"{BASE_URL}/api/customer/owners", json=owner)
    if response.status_code == 201:
        print(f"✓ Dono {i} criado")
    else:
        print(f"✗ Erro ao criar dono {i}: {response.status_code}")

print("\n✓ Banco de dados populado!")
```

Execute:
```bash
python popular_banco.py
```

## 🧪 Execução dos Testes

### Opção 1: Executar Todos os Cenários (Recomendado)

**Windows:**
```powershell
.\executar_todos.ps1
```

**Linux/Mac:**
```bash
chmod +x executar_todos.sh
./executar_todos.sh
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
- **Cenário PICO**: 10 exec × 5 min = 25 min
- **TOTAL**: ~12.5 horas + análise

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
└── graficos/
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

### Indicadores de Problemas

- 🚨 Taxa de sucesso < 99%
- 🚨 Tempo médio > 500ms
- 🚨 Tempo máximo > 5000ms
- 🚨 Variação alta (desvio padrão > 50% da média)

## 🎥 Vídeo Demonstrativo

O vídeo deve mostrar:

1. **Ambiente em execução**
   - Docker Compose mostrando serviços ativos
   - Comandos de verificação da aplicação

2. **Execução de um teste**
   - Rodar um cenário completo
   - Mostrar console do Locust em ação

3. **Análise dos resultados**
   - Abrir Excel consolidado
   - Navegar pelos gráficos gerados
   - Destacar métricas principais

4. **Monitoramento (opcional)**
   - Docker stats mostrando CPU/memória
   - Logs da aplicação

## 📝 Artigo IEEE (6 páginas)

### Estrutura Sugerida

**1. Resumo (Abstract)**
- Contexto, objetivo, método, principais resultados

**2. Introdução**
- Importância dos testes de carga
- Apresentação do Spring PetClinic
- Objetivos do estudo

**3. Metodologia**
- Descrição da arquitetura testada
- Configuração do ambiente
- Cenários de teste (A, B, C)
- Ferramentas utilizadas (Locust)

**4. Resultados**
- Tabelas com as 6 métricas por cenário
- Gráficos comparativos
- Análise estatística

**5. Discussão**
- Interpretação dos resultados
- Comportamento sob diferentes cargas
- Identificação de gargalos
- Comparação com benchmarks (se disponível)

**6. Conclusões**
- Principais descobertas
- Limitações do estudo
- Trabalhos futuros

**7. Referências**
- Spring PetClinic
- Documentação Locust
- Artigos sobre performance testing

## ⚠️ Troubleshooting

### Problema: "Locust não encontrado"
```bash
pip install locust
# ou
pip install --upgrade locust
```

### Problema: "Connection refused"
- Verifique se o Docker está rodando: `docker ps`
- Aguarde a aplicação inicializar completamente (~2-3 min)
- Teste manualmente: `curl http://localhost:8080/api/customer/owners`

### Problema: "Port 8080 already in use"
```bash
# Pare outros serviços na porta 8080
docker-compose down
# ou altere a porta no docker-compose.yml
```

### Problema: "Muitos erros nos testes"
- Verifique recursos da máquina (CPU/RAM)
- Reduza número de usuários temporariamente
- Aumente timeout das requisições no Locust
- Verifique logs: `docker-compose logs -f`

### Problema: "Script PowerShell não executa"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📧 Contato e Suporte

Para dúvidas sobre este projeto:
- Abra uma issue no repositório
- Consulte a documentação oficial do Locust: https://docs.locust.io

## 📄 Licença

Este projeto de teste é fornecido como está para fins educacionais.

---

**Desenvolvido para avaliação de desempenho do Spring PetClinic Microservices**

**Data:** Outubro 2025  
**Ferramenta:** Locust  
**Metodologia:** 30 repetições por cenário com análise estatística