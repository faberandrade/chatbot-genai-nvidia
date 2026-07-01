# 💍 Assistente Tolkien — Chatbot GenAI com Modelo Open Source da NVIDIA na Oracle Cloud

> Um chatbot de Inteligência Artificial Generativa construído em **Python + Streamlit**,
> usando um modelo **open source da NVIDIA** (via NVIDIA NIM) e publicado numa máquina
> virtual da **Oracle Cloud**, acessível publicamente por IP. Como personalização, o
> assistente foi especializado no universo de **J.R.R. Tolkien**.
>
> _Trabalho da disciplina **Produtos de GenAI** — MBA em IA Generativa._

🔗 **Aplicação no ar:** http://164.152.63.48:8501
📦 **Repositório:** https://github.com/faberandrade/chatbot-genai-nvidia

---

## ⚙️ Como instalar e executar

### Pré-requisitos
- Python 3.10 ou superior
- Uma API Key da NVIDIA — gere em [build.nvidia.com](https://build.nvidia.com)

### Passo a passo (local)
```bash
# 1. Clonar o repositório
git clone https://github.com/faberandrade/chatbot-genai-nvidia.git
cd chatbot-genai-nvidia

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
# Define a chave como variável de ambiente (ou em um arquivo .env na pasta do projeto)
export NVIDIA_API_KEY="nvapi-xxxxxxxx"

# Roda exposto na rede, na porta 8501
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
Em produção, a aplicação é mantida no ar 24h por um serviço **systemd** (ver seção 5).

---

# 📰 Relatório

## 1. Introdução

### Objetivo da atividade
O objetivo foi **desenvolver e implantar um chatbot de IA Generativa** utilizando um
modelo **open source disponibilizado pela NVIDIA**, com a aplicação escrita em **Python
+ Streamlit** e publicada em uma **máquina virtual na nuvem (Oracle Cloud)**, de modo
que qualquer usuário possa interagir com ela via navegador, através de um endereço IP
público.

### Visão geral da solução desenvolvida
A arquitetura é simples e eficiente: uma aplicação **Streamlit** roda na VM da Oracle e
funciona como uma "ponte". Ela recebe as mensagens do usuário e as encaminha, pela
internet, para a **API do NVIDIA NIM**, onde o modelo de linguagem é de fato executado.
A resposta volta e é exibida no chat.

O ponto-chave dessa escolha é que **o modelo NÃO roda na VM** — ele roda na
infraestrutura da NVIDIA. Isso torna a aplicação extremamente leve, cabendo
confortavelmente no *free tier* da Oracle, mesmo utilizando modelos grandes.

Como personalização, o chatbot foi transformado em um **assistente especializado em
J.R.R. Tolkien**, que responde com riqueza de detalhes sobre a vida, a obra e o universo
da Terra-Média do autor — e recusa educadamente perguntas fora desse tema.

---

## 2. Infraestrutura

- **Provedor de nuvem:** Oracle Cloud Infrastructure (OCI) — camada **Always Free**
- **Configuração da máquina virtual:** `VM.Standard.A1.Flex` (processadores **ARM Ampere**)
- **Recursos computacionais:** **4 OCPUs** e **24 GB de RAM**
- **Sistema operacional:** **Ubuntu 24.04 LTS**
- **Rede:** VCN dedicada com Internet Gateway; **porta 8501** exposta
- **Endereço público:** `164.152.63.48` (IP reservado/estático)

> Como o modelo é executado na NVIDIA, esses recursos são mais do que suficientes — a VM
> apenas hospeda a aplicação web, que consome pouquíssima memória e processamento.

---

## 3. Modelo Escolhido

- **Nome do modelo:** `nvidia/nvidia-nemotron-nano-9b-v2`
- **Justificativa da escolha:**
  - É um modelo **da própria NVIDIA** (família Nemotron), atendendo diretamente ao
    requisito de "modelo disponibilizado pela NVIDIA";
  - Roda na infraestrutura da NVIDIA (NIM), **não consumindo recursos da VM**;
  - Bom desempenho em **português**;
  - Entre os modelos da NVIDIA disponíveis na API gratuita, foi o que ofereceu o
    melhor equilíbrio entre **qualidade e velocidade**: em testes, respondeu em
    **~4,2 s**, contra **~17,6 s** de um modelo maior (Nemotron Super 49B). Para um
    chatbot interativo, a **responsividade** foi determinante.
- **Principais características:**
  - ~9 bilhões de parâmetros; amplo contexto (até ~128 mil tokens);
  - É um modelo de **raciocínio (*reasoning*)** — "pensa" antes de responder. Esse
    raciocínio vem em um campo separado (`reasoning_content`), que **não é exibido**,
    de modo que o usuário recebe apenas a resposta final, limpa.

> **Nota sobre a escolha do modelo (lição aprendida):** o catálogo da NVIDIA é enorme e
> repleto de termos técnicos (instruct vs. reasoning, MoE, número de parâmetros,
> "nano/super/ultra"), o que torna a escolha desafiadora. Além disso, descobri que
> vários modelos aparecem no catálogo mas retornam **erro 404 na API gratuita** — só
> alguns estão realmente disponíveis. Cheguei ao modelo final **testando via API** quais
> respondiam de fato (`client.models.list()` + chamadas reais).

---

## 4. Desenvolvimento

### Arquitetura da aplicação
```
Usuário (navegador) ──> VM Oracle [Streamlit / app.py] ──> API NVIDIA NIM [LLM] ──> resposta
```

### Bibliotecas utilizadas
- **Streamlit** — cria a interface web do chat sem necessidade de HTML/JS;
- **openai** — cliente compatível usado para chamar a API da NVIDIA (basta apontar a
  `base_url` para `https://integrate.api.nvidia.com/v1`);
- **httpx** (versão fixada) — usada internamente pelo `openai`;
- **python-dotenv** — leitura da chave a partir do `.env` no ambiente local.

### Estratégia de gerenciamento de credenciais
- A API Key **nunca** fica no código-fonte;
- Em desenvolvimento: lida de um arquivo `.env` (ignorado pelo Git via `.gitignore`);
- Em produção (VM): definida como **variável de ambiente** / `.env` no servidor;
- O arquivo `.env.example` documenta a variável esperada sem expor segredos.

### Personalização: *prompt engineering* e segurança
A "personalidade" do assistente é definida por uma **mensagem de sistema** (`system
prompt`). Para especializá-lo em Tolkien, essa mensagem instrui o modelo a atuar como um
especialista no tema e a **recusar** perguntas fora do escopo. Também foram adicionadas
**proteções contra tentativas de burlar** essas regras (*prompt injection / jailbreak*):
cenários hipotéticos/*role-play*, pedidos de "ignore as instruções", falsa autoridade e
"contrabando temático". As proteções foram testadas e resistiram aos ataques comuns.

### Tokens e modelos de raciocínio (*reasoning*)
O modelo adotado é do tipo **reasoning** — ele "raciocina" antes de responder. Um ponto
técnico importante que identificamos é que o parâmetro `max_tokens` (que limita o tamanho
da resposta) funciona como um **orçamento compartilhado** entre o raciocínio interno do
modelo (campo `reasoning_content`, não exibido) e a resposta final visível.

Como o assistente foi especializado em um tema específico, as respostas tendem a ser mais
detalhadas. Em testes empíricos, com `max_tokens = 1024` o raciocínio sozinho consumia
cerca de 650 tokens, deixando pouco espaço para a resposta — que era **cortada no meio**
(`finish_reason: length`). Aumentamos o limite para **4096 tokens**, passando a obter
respostas completas (`finish_reason: stop`). **Lição aprendida:** modelos de *reasoning*
exigem um `max_tokens` mais generoso do que modelos *instruct* tradicionais.

---

## 5. Implantação

### Processo de publicação na Oracle Cloud
1. **Criação da VM:** instância `VM.Standard.A1.Flex` (Always Free) com Ubuntu 24.04 e
   geração do par de chaves **SSH**;
2. **Rede:** criação de uma **VCN com conectividade de internet** (o assistente de rede
   monta o **Internet Gateway** necessário para o IP público funcionar);
3. **Firewall:** liberação da **porta 8501** em **dois níveis** — na *Security List* da
   nuvem e no *firewall interno* do Ubuntu (`iptables`);
4. **Acesso e código:** conexão via **SSH**; instalação de Python/pip/git; **`git clone`**
   do repositório público;
5. **Ambiente:** criação de `venv` e `pip install -r requirements.txt`;
6. **Credencial:** configuração da API Key da NVIDIA diretamente na VM;
7. **Execução permanente:** criação de um serviço **systemd** (`chatbot.service`) que
   mantém o app no ar 24h, reinicia em caso de falha e sobe automaticamente no boot.

### Principais desafios encontrados
- **IP público não habilitava:** o formulário rápido de criação não montava o
  **Internet Gateway** completo; resolvido criando a rede pelo *VCN Wizard*;
- **Firewall duplo:** além da *Security List* da nuvem, o Ubuntu bloqueia tudo (exceto
  SSH) via `iptables` — foi preciso abrir a porta 8501 **nos dois lugares**;
- **Conflito de dependências:** uma incompatibilidade entre `openai` e uma versão nova da
  `httpx` (erro do parâmetro `proxies`), resolvida **fixando a versão** da `httpx`;
- **Repositório acessível:** o repositório original era privado (o professor não
  conseguiria abri-lo); criei um **repositório público dedicado** só para o chatbot;
- **Escolha do modelo:** conforme descrito na seção 3, descobrir quais modelos da NVIDIA
  estavam realmente disponíveis na API gratuita exigiu testes.
- **A curva de aprendizado como iniciante:** este foi, sinceramente, um dos maiores
  desafios. Como estou **iniciando meus estudos em IA e desenvolvimento**, muitos
  conceitos aplicados aqui eram novos para mim — ambientes virtuais em Python, uso do Git,
  redes em nuvem, firewalls, deploy com `systemd` e *prompt engineering*, entre outros.
  Nesse contexto, o uso de um **assistente de IA como copiloto de aprendizado** foi
  fundamental: ele me ajudou a entender o *porquê* de cada etapa e a destravar os erros
  pelo caminho. Com sinceridade, sem esse auxílio dificilmente eu teria conseguido colocar
  o chatbot no ar e funcionando. Fica aqui, também, o registro de como essas ferramentas
  podem **acelerar e democratizar** o aprendizado técnico para quem está começando.

---

## 6. Discussão

### Lições aprendidas
- **A grande sacada da arquitetura:** separar "quem hospeda a interface" (a VM) de "quem
  executa o modelo" (a NVIDIA). Isso viabiliza usar modelos poderosos em uma máquina
  modesta;
- **Segurança de credenciais:** manter segredos fora do código e do Git é essencial e
  simples de fazer com `.env` + `.gitignore` + variáveis de ambiente;
- **Redes em nuvem:** conceitos como VCN, subnet, Internet Gateway e a diferença entre o
  firewall do provedor e o firewall do sistema operacional;
- **Prompt engineering e segurança de prompt:** a mensagem de sistema molda o
  comportamento do modelo, mas é uma "trava suave" — segurança robusta exige defesa em
  camadas;
- **Modelos de *reasoning*:** entender que o "pensamento" consome tokens e impacta
  latência e o dimensionamento do `max_tokens`.

### Possíveis melhorias futuras
- **Autenticação de usuários** e **HTTPS** com domínio próprio;
- Uma camada extra de *guardrails* (ex.: um classificador de tema antes do modelo, ou os
  modelos `nemoguard` da NVIDIA) para segurança em profundidade;
- **Histórico persistente** das conversas em banco de dados;
- **Seleção de modelo** pela própria interface;
- **Deploy automatizado** (CI/CD) e monitoramento.

---

## 📁 Estrutura do projeto
```
chatbot-genai-nvidia/
├── app.py               # Código do chatbot (comentado)
├── requirements.txt     # Dependências
├── .gitignore           # Protege o .env
├── .env.example         # Modelo de credenciais
└── README.md            # Este relatório
```
