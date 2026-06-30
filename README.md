# 🤖 Chatbot GenAI com Modelo Open Source na Oracle Cloud

> Aplicação de chatbot construída em **Python + Streamlit**, usando um modelo
> **open source da NVIDIA** (via NVIDIA NIM) e publicada numa máquina virtual da
> **Oracle Cloud**, acessível por IP público.
>
> _Trabalho da disciplina **Produtos de GenAI** — MBA em IA Generativa._

🔗 **Aplicação no ar:** http://136.248.110.70:8501

---

## ⚙️ Como instalar e executar

### Pré-requisitos
- Python 3.10 ou superior
- Uma API Key da NVIDIA — gere em [build.nvidia.com](https://build.nvidia.com)

### Passo a passo (local)
```bash
# 1. Clonar o repositório
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO

# 2. Criar e ativar um ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar a credencial
cp .env.example .env            # depois edite o .env e cole sua chave

# 5. Rodar a aplicação
streamlit run app.py
```
Acesse `http://localhost:8501` no navegador.

### Executando na VM (produção)
```bash
# Define a chave como variável de ambiente (não usar .env em produção)
export NVIDIA_API_KEY="nvapi-xxxxxxxx"

# Roda exposto na rede, na porta 8501
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

---

# 📰 Relatório

## 1. Introdução

### Objetivo da atividade
_Descreva em 2-3 linhas o objetivo: desenvolver e implantar um chatbot de IA
Generativa, com modelo open source, acessível publicamente na nuvem._

### Visão geral da solução desenvolvida
_Explique a arquitetura em uma frase: um app Streamlit rodando numa VM da Oracle
que consome a API da NVIDIA NIM, onde o modelo de fato é executado._

---

## 2. Infraestrutura

- **Provedor de nuvem:** Oracle Cloud Infrastructure (OCI) — _Always Free_
- **Configuração da máquina virtual:** _ex.: VM.Standard.A1.Flex_
- **Sistema operacional:** _ex.: Ubuntu 22.04 LTS_
- **Recursos computacionais:** _ex.: 1 OCPU (ARM Ampere), 6 GB RAM, 50 GB disco_
- **Porta exposta:** 8501 (Streamlit)

---

## 3. Modelo Escolhido

- **Nome do modelo:** `meta/llama-3.1-8b-instruct` _(ajuste se trocou)_
- **Justificativa da escolha:**
  - É open source e disponibilizado via NVIDIA NIM;
  - Bom desempenho em português;
  - Baixo custo de créditos e baixa latência, ideal para o free tier;
  - Como roda na infraestrutura da NVIDIA, não consome recursos da VM.
- **Principais características:** _nº de parâmetros (8B), janela de contexto,
  multilíngue, voltado a instrução/chat (instruct)._

---

## 4. Desenvolvimento

### Arquitetura da aplicação
```
Usuário (navegador) ──> VM Oracle [Streamlit / app.py] ──> API NVIDIA NIM [LLM] ──> resposta
```

### Bibliotecas utilizadas
- **Streamlit** — interface web do chat;
- **openai** — cliente compatível usado para chamar a API da NVIDIA;
- **python-dotenv** — leitura da chave a partir do `.env` em ambiente local.

### Estratégia de gerenciamento de credenciais
- A API Key **nunca** fica no código-fonte;
- Em desenvolvimento: lida de um arquivo `.env` (ignorado pelo Git via `.gitignore`);
- Em produção (VM): definida como **variável de ambiente** do sistema operacional;
- O arquivo `.env.example` documenta a variável esperada sem expor segredos.

### Tokens e modelos de raciocínio (*reasoning*)
O modelo adotado é do tipo **reasoning** — ele "raciocina" antes de responder. Um
ponto técnico importante que identificamos é que o parâmetro `max_tokens` (que limita
o tamanho da resposta) funciona como um **orçamento compartilhado** entre o
raciocínio interno do modelo (campo `reasoning_content`, que não é exibido ao usuário)
e a resposta final visível.

Como o assistente foi especializado em um tema específico (o universo de J.R.R.
Tolkien), as respostas tendem a ser mais detalhadas. Em testes empíricos, com
`max_tokens = 1024` o raciocínio sozinho consumia cerca de 650 tokens, deixando pouco
espaço para a resposta — que era **cortada no meio** (`finish_reason: length`).
Aumentamos o limite para **4096 tokens**, passando a obter respostas completas
(`finish_reason: stop`). **Lição aprendida:** modelos de *reasoning* exigem um
`max_tokens` mais generoso do que modelos *instruct* tradicionais, pois o "pensamento"
também consome parte desse orçamento.

---

## 5. Implantação

### Processo de publicação na Oracle Cloud
_Resuma os passos: criação da instância, configuração de rede (VCN, Security List
liberando a porta 8501), acesso via SSH, clone do repositório, instalação das
dependências e execução do Streamlit._

### Principais desafios encontrados
_Ex.: liberar a porta 8501 também no firewall interno do Ubuntu (iptables);
manter o app no ar após fechar o SSH (tmux/systemd); disponibilidade de shape ARM._

---

## 6. Discussão

### Lições aprendidas
_Ex.: a diferença entre rodar o modelo localmente vs. consumir uma API; a
importância de separar credenciais do código; conceitos de rede em nuvem._

### Possíveis melhorias futuras
_Ex.: autenticação de usuários; HTTPS com domínio próprio; troca de modelo via
menu na interface; histórico persistente em banco de dados; deploy automatizado._

---

## 📁 Estrutura do projeto
```
chatbot-genai-nvidia/
├── app.py               # Código do chatbot
├── requirements.txt     # Dependências
├── .gitignore           # Protege o .env
├── .env.example         # Modelo de credenciais
└── README.md            # Este relatório
```
