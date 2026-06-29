# =============================================================================
#  app.py  -  Chatbot com modelo Open Source (NVIDIA NIM) + Streamlit
# -----------------------------------------------------------------------------
#  Disciplina: Produtos de GenAI  |  MBA em IA Generativa
#
#  IDEIA GERAL (leia isto antes do codigo):
#  ----------------------------------------
#  Este programa NAO roda a Inteligencia Artificial dentro dele. Ele apenas:
#     1. Mostra uma tela de chat no navegador (graca ao Streamlit);
#     2. Pega o que voce digitou;
#     3. Envia pela internet para a API da NVIDIA, que roda o modelo de verdade;
#     4. Recebe a resposta e mostra na tela.
#
#  Por isso ele e leve e cabe numa VM pequena (free tier da Oracle): o trabalho
#  pesado acontece nos servidores da NVIDIA, nao na sua maquina.
# =============================================================================

# -----------------------------------------------------------------------------
# 1) IMPORTACOES
#    "import" = trazer uma biblioteca (codigo pronto de outras pessoas) para uso.
# -----------------------------------------------------------------------------
import os                          # Permite ler "variaveis de ambiente" do sistema
import streamlit as st            # A biblioteca da interface web. "as st" = apelido
from openai import OpenAI         # Cliente que sabe conversar com a API (estilo OpenAI)
from dotenv import load_dotenv    # Le o arquivo .env durante o teste local


# -----------------------------------------------------------------------------
# 2) CARREGAR A CHAVE SECRETA (API KEY)
#    A chave NUNCA fica escrita no codigo. Ela vem de "fora":
#      - No teste local: do arquivo .env (lido pelo load_dotenv abaixo)
#      - Na VM da Oracle: de uma variavel de ambiente do sistema
#    Assim o codigo pode ir para o GitHub sem expor o segredo.
# -----------------------------------------------------------------------------
load_dotenv()  # Procura um arquivo .env na pasta e carrega o que estiver nele

# os.getenv("NOME") busca o valor da variavel. Se nao existir, retorna None.
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


# -----------------------------------------------------------------------------
# 3) CONFIGURACAO DA PAGINA
#    Define o titulo da aba do navegador e o icone. Tem que ser a 1a chamada
#    de Streamlit do programa.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Chatbot GenAI - NVIDIA",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Chatbot GenAI")
st.caption("Modelo open source via NVIDIA NIM  •  MBA IA Generativa")


# -----------------------------------------------------------------------------
# 4) ESCOLHA DO MODELO
#    Esta string e o unico lugar que voce muda para trocar de modelo.
#    Veja a lista completa em https://build.nvidia.com
#    Usamos um modelo da PROPRIA NVIDIA (atende o requisito da tarefa). Ele e um
#    modelo "reasoning" (raciocina antes de responder), mas a API entrega esse
#    raciocinio num campo separado (reasoning_content) que NAO exibimos -> a tela
#    mostra so a resposta final, limpa. Escolhemos a versao "nano" (9B) por
#    equilibrar boa qualidade com respostas rapidas (chat mais fluido).
#      - "nvidia/nvidia-nemotron-nano-9b-v2"        -> modelo NVIDIA, rapido (ESCOLHIDO)
#      - "nvidia/llama-3.3-nemotron-super-49b-v1.5" -> NVIDIA, mais potente porem lento
#      - "meta/llama-3.1-8b-instruct"               -> alternativa leve (usada nos testes)
# -----------------------------------------------------------------------------
MODELO = "nvidia/nvidia-nemotron-nano-9b-v2"


# -----------------------------------------------------------------------------
# 5) CRIAR O "CLIENTE" QUE FALA COM A NVIDIA
#    A API da NVIDIA e compativel com o SDK da OpenAI: basta apontar a
#    "base_url" para o endereco da NVIDIA. Se a chave nao existir, avisamos
#    o usuario e paramos o app (st.stop) para evitar um erro feio.
# -----------------------------------------------------------------------------
if not NVIDIA_API_KEY:
    st.error(
        "A variavel NVIDIA_API_KEY nao foi encontrada.\n\n"
        "No teste local: crie um arquivo .env com a sua chave.\n"
        "Na VM: defina a variavel de ambiente antes de rodar."
    )
    st.stop()  # Interrompe a execucao aqui; nada abaixo roda sem a chave.

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",  # Endereco da API da NVIDIA
    api_key=NVIDIA_API_KEY,                          # Sua credencial
)


# -----------------------------------------------------------------------------
# 6) MEMORIA DA CONVERSA (HISTORICO)
#    O Streamlit re-executa este arquivo inteiro a cada interacao. Para nao
#    "esquecer" a conversa, guardamos as mensagens em st.session_state, que
#    e uma memoria que sobrevive entre as interacoes do mesmo usuario.
#
#    Cada mensagem e um dicionario: {"role": quem falou, "content": o texto}.
#      - "system"    -> instrucao inicial que molda a personalidade do bot
#      - "user"      -> o que a pessoa digitou
#      - "assistant" -> o que o modelo respondeu
# -----------------------------------------------------------------------------
if "mensagens" not in st.session_state:
    # Roda apenas na primeira vez: cria o historico com a instrucao de sistema.
    st.session_state.mensagens = [
        {
            "role": "system",
            "content": (
                "Voce e um assistente prestativo e didatico. "
                "Responda sempre em portugues do Brasil, de forma clara e objetiva."
            ),
        }
    ]


# -----------------------------------------------------------------------------
# 7) MOSTRAR O HISTORICO NA TELA
#    Percorremos todas as mensagens guardadas e desenhamos cada uma como um
#    balao de chat. Pulamos a mensagem "system" porque ela e uma instrucao
#    interna, nao algo que o usuario precise ver.
# -----------------------------------------------------------------------------
for mensagem in st.session_state.mensagens:
    if mensagem["role"] == "system":
        continue  # nao exibe a instrucao interna
    with st.chat_message(mensagem["role"]):  # "user" ou "assistant"
        st.markdown(mensagem["content"])


# -----------------------------------------------------------------------------
# 8) CAMPO DE DIGITACAO + ENVIO PARA O MODELO
#    st.chat_input desenha a caixa de texto no rodape. Quando o usuario envia
#    algo, a variavel "pergunta" recebe o texto (senao fica None e o bloco
#    abaixo nao executa).
# -----------------------------------------------------------------------------
pergunta = st.chat_input("Digite sua mensagem...")

if pergunta:
    # 8.1) Guarda e mostra a mensagem do usuario
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # 8.2) Pede a resposta ao modelo e mostra "ao vivo" (streaming)
    with st.chat_message("assistant"):
        try:
            # Enviamos TODO o historico para o modelo ter contexto da conversa.
            # stream=True faz a resposta chegar em pedacinhos (efeito de digitacao).
            stream = client.chat.completions.create(
                model=MODELO,
                messages=st.session_state.mensagens,
                temperature=0.7,   # 0 = mais objetivo/repetitivo; 1 = mais criativo
                max_tokens=1024,   # Tamanho maximo da resposta
                stream=True,
            )
            # st.write_stream vai escrevendo na tela conforme os pedacos chegam
            # e, no final, devolve o texto completo para guardarmos no historico.
            resposta = st.write_stream(stream)
        except Exception as erro:
            # Se a internet, a chave ou a API falharem, mostramos um aviso amigavel
            resposta = f"❌ Ocorreu um erro ao falar com a API: {erro}"
            st.error(resposta)

    # 8.3) Guarda a resposta no historico para a proxima rodada lembrar dela
    st.session_state.mensagens.append({"role": "assistant", "content": resposta})


# -----------------------------------------------------------------------------
# 9) BARRA LATERAL: informacoes e botao de limpar conversa
#    Coisas secundarias ficam na "sidebar" para nao poluir o chat.
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("ℹ️ Sobre")
    st.write(f"**Modelo:** `{MODELO}`")
    st.write("**Infra:** VM Oracle Cloud (Always Free)")
    st.write("**Interface:** Streamlit")
    st.divider()
    # Botao que apaga o historico e recomeca a conversa do zero.
    if st.button("🗑️ Limpar conversa"):
        del st.session_state.mensagens  # apaga a memoria...
        st.rerun()                      # ...e recarrega a pagina
