# 🐾 Automação de Execução — Spring PetClinic Microservices

Este projeto utiliza **Docker Compose** para subir toda a infraestrutura da aplicação **Spring PetClinic Microservices** e um script PowerShell (`executar.ps1`) que executa automaticamente todos os testes de carga, além da análise final dos resultados.

---

## ⚙️ Estrutura do Processo

O processo automatizado segue as etapas abaixo:

1. **Subir os containers** da aplicação com `docker compose up -d`
2. **Aguardar** a inicialização dos serviços
3. **Executar os testes de carga**:
   - `run_leve.ps1`
   - `medio.ps1`
   - `pico.ps1`
4. **Analisar os resultados** com o script `analisar_dados.py`

---

## 🚀 Execução Automática

O script principal é **`executar.ps1`**, responsável por rodar todos os testes de carga e realizar a análise final.  
⚠️ **Antes de executá-lo, é necessário subir os containers com Docker Compose.**

---

### ▶️ Passo a passo

1. **Suba a infraestrutura da aplicação:**
   ```powershell
   docker compose up -d
   ```

2. **Após os containers estarem ativos, execute o script principal:**
   ```powershell
   .\executar.ps1
   ```

---

### 💡 O que acontece ao executar `executar.ps1`

1. O script aguarda o tempo necessário para que todos os serviços estejam ativos.  
2. Em seguida, executa automaticamente:
   ```powershell
   .\run_leve.ps1
   .\medio.ps1
   .\pico.ps1
   ```
3. Por fim, realiza a análise de desempenho:
   ```powershell
   python .\analisar_dados.py
   ```

---

## 🧩 Estrutura Recomendada de Arquivos

```
📦 projeto/
 ┣ 📜 docker-compose.yml
 ┣ 📜 executar.ps1
 ┣ 📜 run_leve.ps1
 ┣ 📜 medio.ps1
 ┣ 📜 pico.ps1
 ┣ 📜 analisar_dados.py
 ┗ 📜 README.md
```

---

## 🐳 Requisitos

Antes de iniciar o processo, verifique se possui instalado:

- **Docker** (ou Docker Desktop)
- **PowerShell 5.0+**
- **Python 3.x** com as bibliotecas necessárias (`pandas`, `matplotlib`, etc.)

---

## 🧠 Observações

- O comando `docker compose up -d` **deve ser executado antes** de rodar o `executar.ps1`.  
- O script `executar.ps1` automatiza apenas a parte dos **testes e análise**.  
- Todos os resultados são gerados e analisados automaticamente ao final.  

---

## 📊 Dicas úteis

Para verificar se os containers estão ativos:
```powershell
docker ps
```

Para acompanhar os logs:
```powershell
docker compose logs -f
```

Para encerrar e limpar tudo após os testes:
```powershell
docker compose down -v
```

---

## 🧩 Créditos

Baseado na arquitetura **Spring PetClinic Microservices**  
Automação de testes e análise por **Luis Gustavo Luz de Deus Ramos**
