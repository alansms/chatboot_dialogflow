import streamlit as st
import pandas as pd
import os
import json
import random
import uuid
from datetime import datetime
from google.cloud import dialogflow
import google.auth.exceptions

# ===== CONFIGURAÇÃO DO STREAMLIT =====
# Define configuração para aceitar conexões de qualquer IP
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'      # Aceita conexões de qualquer IP
os.environ['STREAMLIT_SERVER_PORT'] = '8501'            # Porta padrão
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'false'       # Não abrir navegador automaticamente
os.environ['STREAMLIT_SERVER_ENABLECORS'] = 'true'      # Habilita CORS
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'  # Desativa coleta de estatísticas

# Configuração da página
st.set_page_config(
    page_title='Hamburgueria RPA-BOT',
    page_icon="🍔",
    layout='centered',
    initial_sidebar_state='collapsed'
)

# ===== INICIALIZAÇÃO DA SESSÃO =====
# Identificador único para esta sessão
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Histórico de chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Contexto da conversa (para tratamento inteligente de "Sim")
if 'context' not in st.session_state:
    st.session_state.context = {'last_action': None, 'last_intent': None}

# Carrinho de compras
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Cardápio
if 'cardapio' not in st.session_state:
    # Cardápio padrão
    st.session_state.cardapio = pd.DataFrame({
        'categoria': ['Burgers', 'Burgers', 'Burgers', 'Bebidas', 'Bebidas', 'Porções'],
        'item': ['Cheeseburger', 'Vegetariano', 'Duplo', 'Coca-Cola', 'Suco', 'Batata Frita'],
        'descricao': ['Hambúrguer com queijo', 'Hambúrguer de grão de bico', 'Hambúrguer duplo com queijo', 'Refrigerante lata', 'Suco natural de laranja', 'Batata frita crocante'],
        'preco': [18.90, 20.00, 25.00, 6.00, 7.50, 12.00],
        'vegetariano': ['não', 'sim', 'não', 'não', 'sim', 'sim'],
    })

# ===== FUNÇÕES DE PROCESSAMENTO DE LINGUAGEM NATURAL =====
def reconhecer_intent(texto):
    """Identifica a intenção do usuário baseado no texto."""
    if not texto:
        return "Default"

    texto = texto.lower().strip()

    # Detecta cumprimentos
    cumprimentos = ["olá", "ola", "oi", "boa tarde", "bom dia", "boa noite", "hello", "hi", "e ai", "eai"]
    if any(cumprimento in texto for cumprimento in cumprimentos):
        return "BoasVindas"

    # Detecta pedidos de cardápio
    if any(palavra in texto for palavra in ["cardápio", "cardapio", "menu", "opções", "opcoes", "quais são", "o que tem", "cardápios"]):
        return "Cardapio"

    # Detecta pedidos de ver itens detalhados
    if any(frase in texto for frase in ["ver opções", "mostrar itens", "detalhado", "itens", "lista", "listar"]):
        return "MostrarItens"

    # Detecta pedidos específicos
    categorias_comuns = ["burger", "hambúrguer", "hamburger", "burgers", "bebida", "bebidas", "porção", "porcao", "porções", "porcoes"]
    if any(palavra in texto for palavra in ["quero", "gostaria", "pedir", "queria", "me vê", "me dá", "pedido"]) or any(categoria in texto for categoria in categorias_comuns):
        return "FazerPedido"

    # Detecta confirmações
    if any(palavra in texto for palavra in ["sim", "yes", "isso", "confirmar", "confirmo", "certo", "ok", "pode ser", "claro"]):
        return "Confirmar"

    # Detecta negações
    if any(palavra in texto for palavra in ["não", "nao", "no", "não quero", "cancela", "cancelar"]):
        return "Negar"

    # Detecta despedidas
    if any(palavra in texto for palavra in ["tchau", "adeus", "até mais", "obrigado", "valeu"]):
        return "Despedida"

    # Intent padrão (fallback)
    return "Default"

def gerar_cardapio_completo(cardapio):
    """Gera a string completa do cardápio para exibição."""
    if cardapio.empty:
        return "Desculpe, nosso cardápio não está disponível no momento."

    # Gera lista de itens por categoria
    categorias = cardapio['categoria'].unique()
    resultado = "📋 **CARDÁPIO COMPLETO** 📋\n\n"

    for categoria in categorias:
        items_categoria = cardapio[cardapio['categoria'] == categoria]
        resultado += f"🍴 **{categoria.upper()}**\n"
        for _, item in items_categoria.iterrows():
            vegetariano = " 🌱" if item.get('vegetariano', '').lower() in ['sim', 'true', 'vegetariano'] else ""
            resultado += f"• **{item['item']}** - R$ {item['preco']:.2f}{vegetariano}\n"
            if 'descricao' in item and pd.notna(item['descricao']):
                resultado += f"  {item['descricao']}\n"
        resultado += "\n"

    resultado += "Digite o nome do item que deseja pedir ou 'voltar' para retornar ao menu principal."
    return resultado

def listar_itens_categoria(cardapio, categoria):
    """Lista os itens de uma categoria específica."""
    categoria_normalizada = categoria.lower().strip()

    # Verifica se a categoria existe no cardápio
    if categoria_normalizada not in cardapio['categoria'].str.lower().values:
        return "Categoria não encontrada no cardápio."

    # Filtra os itens pela categoria
    itens_categoria = cardapio[cardapio['categoria'].str.lower() == categoria_normalizada]
    items = [f"**{row['item']}** (R$ {row['preco']:.2f})" for _, row in itens_categoria.iterrows()]

    return f"Temos as seguintes opções em {categoria}:\n\n" + "\n".join(items) + "\n\nQual você gostaria de pedir?"

def processar_pedido_local(texto, cardapio, cart, context):
    """Processa o pedido usando lógica local (fallback do Dialogflow)."""
    # Verifica se há algum item do cardápio mencionado no texto
    item_encontrado = None

    # Normaliza o texto para comparação (remove acentos, converte para minúsculas)
    texto_normalizado = texto.lower().strip()

    # Primeiro tenta encontrar itens específicos do cardápio
    for _, row in cardapio.iterrows():
        item_nome = row['item'].lower()
        if item_nome in texto_normalizado:
            item_encontrado = row
            break

    # Verifica também para categorias específicas
    if not item_encontrado and ("burger" in texto_normalizado or "hambúrguer" in texto_normalizado
                               or "hamburger" in texto_normalizado or "burgers" in texto_normalizado):
        # Se mencionou a categoria de hambúrgueres
        burgers = cardapio[cardapio["categoria"].str.lower() == "burgers"]
        if not burgers.empty:
            items = [f"**{row['item']}** (R$ {row['preco']:.2f})" for _, row in burgers.iterrows()]
            return f"Temos os seguintes hambúrgueres:\n\n" + "\n".join(items) + "\n\nQual você gostaria de pedir?"

    elif not item_encontrado and ("bebida" in texto_normalizado or "bebidas" in texto_normalizado):
        # Se mencionou a categoria de bebidas
        bebidas = cardapio[cardapio["categoria"].str.lower() == "bebidas"]
        if not bebidas.empty:
            items = [f"**{row['item']}** (R$ {row['preco']:.2f})" for _, row in bebidas.iterrows()]
            return f"Temos as seguintes bebidas:\n\n" + "\n".join(items) + "\n\nQual você gostaria de pedir?"

    elif not item_encontrado and ("porção" in texto_normalizado or "porcao" in texto_normalizado
                                 or "porções" in texto_normalizado or "porcoes" in texto_normalizado):
        # Se mencionou a categoria de porções
        porcoes = cardapio[cardapio["categoria"].str.lower() == "porções"]
        if not porcoes.empty:
            items = [f"**{row['item']}** (R$ {row['preco']:.2f})" for _, row in porcoes.iterrows()]
            return f"Temos as seguintes porções:\n\n" + "\n".join(items) + "\n\nQual você gostaria de pedir?"

    # Se encontrou um item específico, adiciona ao carrinho
    if item_encontrado is not None:
        # Adiciona ao carrinho
        cart.append({
            'item': item_encontrado['item'],
            'preco': item_encontrado['preco'],
            'quantidade': 1
        })
        context['last_action'] = 'adicionou_item'
        return f"Adicionei 1x **{item_encontrado['item']}** (R$ {item_encontrado['preco']:.2f}) ao seu pedido. Deseja pedir mais alguma coisa ou confirmar o pedido?"

    # Se nada foi identificado
    context['last_action'] = 'pediu_nao_especifico'
    return "Qual item você gostaria de pedir? Você pode digitar 'ver opções' para ver o cardápio completo."

def processar_confirmacao(context, cart):
    """Processa a confirmação do pedido."""
    last_action = context.get('last_action')

    # Se confirmou após mostrar menu, mostra o cardápio detalhado diretamente
    if last_action == 'mostrou_menu':
        context['last_action'] = 'mostrou_itens'  # Muda o contexto para evitar loops

        return gerar_cardapio_completo(st.session_state.cardapio)

    # Se confirmou após adicionar um item, finaliza o pedido
    elif last_action == 'adicionou_item':
        if not cart:
            return "Seu carrinho está vazio. O que você gostaria de pedir?"

        # Confirma o pedido
        total = sum(item['preco'] * item['quantidade'] for item in cart)
        itens = [f"{item['quantidade']}x {item['item']} (R${item['preco'] * item['quantidade']:.2f})" for item in cart]

        # Limpa o carrinho e o contexto
        st.session_state.cart = []
        context['last_action'] = 'confirmou_pedido'

        return f"🎉 Pedido confirmado com sucesso!\n\nItens: {', '.join(itens)}\nTotal: R${total:.2f}\n\nSeu pedido será preparado em breve. Obrigado pela preferência!"

    # Fallback para qualquer outro "Sim"
    else:
        context['last_action'] = 'sim_generico'
        return "Certo! O que você gostaria de fazer? Você pode pedir para ver o cardápio digitando 'cardápio' ou fazer um pedido diretamente."

def processar_negacao(context, cart):
    """Processa a negação de um pedido."""
    last_action = context.get('last_action')

    # Se negou após adicionar item (cancelando pedido)
    if last_action == 'adicionou_item':
        st.session_state.cart = []  # Limpa o carrinho
        context['last_action'] = 'cancelou_pedido'
        return "Pedido cancelado. Posso ajudar com mais alguma coisa?"

    # Fallback para "Não" genérico
    context['last_action'] = 'nao_generico'
    return "Sem problemas. Como posso ajudar então?"

def processar_mensagem(texto):
    """Processa a mensagem do usuário usando Dialogflow API ou processamento local"""
    context = st.session_state.context
    cart = st.session_state.cart
    cardapio = st.session_state.cardapio

    # Tenta usar o Dialogflow primeiro
    dialogflow_response = st.session_state.dialogflow_bot.detect_intent(texto)

    if dialogflow_response and dialogflow_response['confidence'] > 0.6:
        # Usa a resposta do Dialogflow se a confiança for alta
        intent = dialogflow_response['intent']
        parameters = dialogflow_response['parameters']

        # Registra a intent para contexto
        context['last_intent'] = intent

        # Processa conforme a intenção detectada pelo Dialogflow
        if intent in ['Default Welcome Intent', 'BoasVindas', 'cumprimentos']:
            context['last_action'] = 'boas_vindas'
            return dialogflow_response['text'] or "Olá! Bem-vindo à nossa hamburgueria virtual! 🍔 Como posso ajudar você hoje?"

        elif intent in ['Cardapio', 'mostrar.cardapio', 'ver.menu']:
            context['last_action'] = 'mostrou_menu'
            return dialogflow_response['text'] or "Temos hambúrgueres artesanais, porções e bebidas geladas. Deseja ver o cardápio detalhado?"

        elif intent in ['MostrarItens', 'listar.itens', 'ver.opcoes']:
            context['last_action'] = 'mostrou_itens'
            return gerar_cardapio_completo(cardapio)

        elif intent in ['FazerPedido', 'pedir.item', 'adicionar.carrinho']:
            # Extrai parâmetros do Dialogflow
            item_solicitado = parameters.get('item', '')
            categoria_solicitada = parameters.get('categoria', '')

            if item_solicitado:
                # Procura item específico
                item_encontrado = None
                for _, row in cardapio.iterrows():
                    if row['item'].lower() == item_solicitado.lower():
                        item_encontrado = row
                        break

                if item_encontrado is not None:
                    cart.append({
                        'item': item_encontrado['item'],
                        'preco': item_encontrado['preco'],
                        'quantidade': 1
                    })
                    context['last_action'] = 'adicionou_item'
                    return f"Adicionei 1x **{item_encontrado['item']}** (R$ {item_encontrado['preco']:.2f}) ao seu pedido. Deseja pedir mais alguma coisa ou confirmar o pedido?"

            elif categoria_solicitada:
                return listar_itens_categoria(cardapio, categoria_solicitada)

            # Fallback para processamento local se não conseguiu extrair parâmetros
            return processar_pedido_local(texto, cardapio, cart, context)

        elif intent in ['Confirmar', 'sim', 'confirmar.pedido']:
            return processar_confirmacao(context, cart)

        elif intent in ['Negar', 'nao', 'cancelar']:
            return processar_negacao(context, cart)

        elif intent in ['Despedida', 'tchau', 'finalizar']:
            context['last_action'] = 'despedida'
            return dialogflow_response['text'] or "Obrigado por visitar nossa hamburgueria virtual! Volte sempre! 👋"

        else:
            # Usa resposta padrão do Dialogflow para intents não mapeadas
            return dialogflow_response['text']

    # Fallback para processamento local se Dialogflow não está disponível ou confiança baixa
    return processar_pedido_local(texto, cardapio, cart, context)

# ===== CONFIGURAÇÃO DO DIALOGFLOW =====
class DialogflowBot:
    def __init__(self, project_id, session_id, language_code='pt-BR'):
        self.project_id = project_id
        self.session_id = session_id
        self.language_code = language_code
        self.dialogflow_enabled = False

        # Tenta configurar as credenciais do Google Cloud
        try:
            # Verifica se existe um arquivo de credenciais como variável de ambiente no Streamlit
            if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in st.secrets:
                # Para Streamlit Cloud - credenciais via secrets
                credentials_info = json.loads(st.secrets['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                self.session_client = dialogflow.SessionsClient(credentials=credentials)
                self.dialogflow_enabled = True
            elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                # Para ambiente local - credenciais via arquivo
                self.session_client = dialogflow.SessionsClient()
                self.dialogflow_enabled = True
            else:
                st.warning("⚠️ Credenciais do Dialogflow não configuradas. Usando processamento local.")
                self.dialogflow_enabled = False
                return

            self.session_path = self.session_client.session_path(project_id, session_id)

        except Exception as e:
            st.warning(f"⚠️ Erro ao conectar com Dialogflow: {str(e)}. Usando processamento local.")
            self.dialogflow_enabled = False

    def detect_intent(self, text_input):
        """Envia mensagem para o Dialogflow e retorna a resposta"""
        if not self.dialogflow_enabled:
            return None

        try:
            # Prepara o input de texto
            text_input_obj = dialogflow.TextInput(text=text_input, language_code=self.language_code)
            query_input = dialogflow.QueryInput(text=text_input_obj)

            # Faz a chamada para a API do Dialogflow
            response = self.session_client.detect_intent(
                request={"session": self.session_path, "query_input": query_input}
            )

            return {
                'text': response.query_result.fulfillment_text,
                'intent': response.query_result.intent.display_name,
                'confidence': response.query_result.intent_detection_confidence,
                'parameters': dict(response.query_result.parameters)
            }

        except Exception as e:
            st.error(f"Erro na comunicação com Dialogflow: {str(e)}")
            return None

# Inicializa o bot do Dialogflow
if 'dialogflow_bot' not in st.session_state:
    # Configuração do projeto (ajuste conforme necessário)
    PROJECT_ID = st.secrets.get('DIALOGFLOW_PROJECT_ID', 'fiap-boot')  # ou use seu project ID
    st.session_state.dialogflow_bot = DialogflowBot(
        project_id=PROJECT_ID,
        session_id=st.session_state.session_id
    )

# ===== INTERFACE STREAMLIT =====
st.title("🍔 Hamburgueria Virtual")

# Abas de navegação
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Cardápio", "⚙️ Admin"])

# Aba de Chat
with tab1:
    st.header("Chat com o Bot")

    # Container para histórico (com scroll automático)
    chat_container = st.container()
    with chat_container:
        for mensagem in st.session_state.chat_history:
            if mensagem['tipo'] == 'usuario':
                st.markdown(f"**Você:** {mensagem['texto']}")
            else:
                st.markdown(f"**Bot:** {mensagem['texto']}")

    # Barra de separação
    st.markdown("---")

    # Entrada de texto e botão
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Digite sua mensagem:", key="input_message")
    with col2:
        enviar = st.button("Enviar")

    # Processar mensagem quando o botão for clicado
    if enviar and user_input.strip():
        # Adiciona mensagem do usuário ao histórico
        st.session_state.chat_history.append({
            'tipo': 'usuario',
            'texto': user_input,
            'timestamp': datetime.now().isoformat()
        })

        # Processa e adiciona resposta do bot
        resposta = processar_mensagem(user_input)
        st.session_state.chat_history.append({
            'tipo': 'bot',
            'texto': resposta,
            'timestamp': datetime.now().isoformat()
        })

        # Limpa o campo de entrada
        st.rerun()

# Aba de Cardápio
with tab2:
    st.header("Cardápio Atual")

    if not st.session_state.cardapio.empty:
        # Mostra o cardápio formatado
        for categoria in st.session_state.cardapio['categoria'].unique():
            st.subheader(f"🍴 {categoria}")
            itens_categoria = st.session_state.cardapio[st.session_state.cardapio['categoria'] == categoria]

            for _, item in itens_categoria.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    titulo = f"{item['item']}"
                    if 'vegetariano' in item and item['vegetariano'].lower() == 'sim':
                        titulo += " 🌱"
                    st.markdown(f"**{titulo}**")
                    if 'descricao' in item and pd.notna(item['descricao']):
                        st.write(item['descricao'])
                with col2:
                    st.markdown(f"**R$ {item['preco']:.2f}**")
                st.markdown("---")
    else:
        st.warning("Nenhum cardápio carregado.")

# Aba de Admin
with tab3:
    st.header("Administração")

    # Upload de cardápio
    st.subheader("Upload de Cardápio")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            # Lê o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Normaliza colunas
            df.columns = [c.strip().lower() for c in df.columns]

            # Verifica colunas obrigatórias
            required = ["categoria", "item", "descricao", "preco"]
            if not set(required).issubset(set(df.columns)):
                st.error(f"Colunas obrigatórias ausentes: {', '.join(required)}")
            else:
                # Coluna vegetariano padrão "não" se não existir
                df["vegetariano"] = df.get("vegetariano", "não").astype(str).str.lower()

                # Converte preços para numérico
                df["preco"] = pd.to_numeric(df["preco"], errors="coerce").round(2)

                # Atualiza o cardápio
                st.session_state.cardapio = df
                st.success("Cardápio carregado com sucesso!")

                # Mostra preview
                st.dataframe(df)
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

    # Botão para gerar cardápio de exemplo
    if st.button("Gerar Cardápio de Exemplo"):
        exemplo = pd.DataFrame({
            'categoria': ['Burgers', 'Burgers', 'Burgers', 'Bebidas', 'Bebidas', 'Porções'],
            'item': ['Cheeseburger', 'Vegetariano', 'Duplo', 'Coca-Cola', 'Suco', 'Batata Frita'],
            'descricao': ['Hambúrguer com queijo', 'Hambúrguer de grão de bico', 'Hambúrguer duplo com queijo', 'Refrigerante lata', 'Suco natural de laranja', 'Batata frita crocante'],
            'preco': [18.90, 20.00, 25.00, 6.00, 7.50, 12.00],
            'vegetariano': ['não', 'sim', 'não', 'não', 'sim', 'sim']
        })
        st.session_state.cardapio = exemplo
        st.success("Cardápio de exemplo gerado!")
        st.dataframe(exemplo)

    # Configurações e informações do sistema
    st.subheader("Informações do Sistema")
    st.info(f"""
    - ID da Sessão: {st.session_state.session_id}
    - Número de mensagens: {len(st.session_state.chat_history)}
    - Itens no carrinho: {len(st.session_state.cart)}
    - URL de acesso: http://172.21.101.185:8501 ou http://localhost:8501
    """)

    # Botão para limpar histórico
    if st.button("Limpar Histórico de Chat"):
        st.session_state.chat_history = []
        st.session_state.context = {'last_action': None, 'last_intent': None}
        st.session_state.cart = []
        st.success("Histórico limpo com sucesso!")
        st.rerun()

# Rodapé
st.markdown("---")
st.caption("Hamburgueria Virtual RPA-BOT - Desenvolvido com Streamlit")
