import os
import io
import pandas as pd
import requests
from flask import Flask, request, render_template_string, redirect
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# CONFIGURAÇÕES
# Arquivo de credenciais da conta de serviço Dialogflow
CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
# ID do projeto Dialogflow
PROJECT_ID = "fiap-boot"
# Código de idioma utilizado nas requisições
LANG = "pt-BR"

# Inicializa a aplicação Flask
app = Flask(__name__)

# Variáveis globais
# DataFrame que armazena o cardápio carregado
MENU_DF: pd.DataFrame | None = None
# Carrinhos de compra por sessão (chat)
CARTS: dict[str, list[dict]] = {}

# Autenticação com a API Dialogflow
SCOPES = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
GSESSION = AuthorizedSession(credentials)

# HTML simples para a página de upload do cardápio
HTML = """
<!doctype html>
<title>Cardápio</title>
<h2>Upload CSV/XLSX do Cardápio</h2>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file accept=".csv,.xlsx"/>
  <button type=submit>Enviar</button>
</form>
<hr>
<a href="/menu">Ver cardápio carregado</a>
"""


@app.route("/")
def home():
    """Página de health check."""
    return "Bot online", 200


@app.route("/admin")
def admin():
    """Página de administração para upload de cardápio."""
    return render_template_string(HTML)


@app.route("/upload", methods=["POST"])
def upload():
    """Recebe planilha CSV/XLSX e carrega no DataFrame global."""
    global MENU_DF
    f = request.files.get("file")
    if not f:
        return "Arquivo não enviado.", 400
    content = f.read()
    try:
        # Detecta extensão para leitura
        if f.filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        return f"Erro ao ler planilha: {e}", 400

    # Normaliza colunas para minúsculas e sem espaços
    df.columns = [c.strip().lower() for c in df.columns]
    required = ["categoria", "item", "descricao", "preco"]
    # Verifica se todas as colunas obrigatórias existem
    if not set(required).issubset(set(df.columns)):
        return f"Colunas obrigatórias ausentes: {', '.join(required)}", 400
    # Coluna vegetariano padrão "não" caso não exista
    df["vegetariano"] = df.get("vegetariano", "não").astype(str).str.lower()
    # Converte preços para float com duas casas decimais
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce").round(2)
    MENU_DF = df
    # Persiste em disco para uso posterior
    df.to_csv("cardapio_cache.csv", index=False)
    return redirect("/menu")


@app.route("/menu")
def show_menu():
    """Exibe o cardápio carregado em formato HTML."""
    global MENU_DF
    if MENU_DF is None and os.path.exists("cardapio_cache.csv"):
        MENU_DF = pd.read_csv("cardapio_cache.csv")
    if MENU_DF is None:
        return "Nenhum cardápio carregado. Vá em /admin", 200
    # Gera tabela HTML sem índice
    return MENU_DF.to_html(index=False)


def ensure_menu_loaded() -> bool:
    """Garante que o DataFrame do cardápio esteja carregado na memória."""
    global MENU_DF
    if MENU_DF is None and os.path.exists("cardapio_cache.csv"):
        MENU_DF = pd.read_csv("cardapio_cache.csv")
    return MENU_DF is not None


def push_session_entities(session_id: str) -> None:
    """
    Envia entidades dinâmicas para a sessão do Dialogflow.
    Cada item do cardápio vira um valor em @Item com sinônimos opcionais.
    """
    if not ensure_menu_loaded():
        return
    import pandas as pd  # Import local para tipagem
    # Lista de entidades
    items_entities = []
    for _, row in MENU_DF.iterrows():
        value = str(row["item"]).strip()
        synonyms = [value]
        # Se houver coluna de sinônimos, separa por |
        if "sinonimos" in MENU_DF.columns:
            raw = row.get("sinonimos", "")
            if pd.notna(raw) and str(raw).strip() != "":
                parts = str(raw).split("|")
                synonyms += [p.strip() for p in parts if p.strip()]
        items_entities.append({"value": value, "synonyms": synonyms})
    # Monta payload do session entity type
    url = (
        f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/"
        f"{session_id}/entityTypes/Item"
    )
    payload = {
        "entityOverrideMode": "ENTITY_OVERRIDE_MODE_OVERRIDE",
        "entities": items_entities,
    }
    try:
        # Utiliza PUT para criar/atualizar o SessionEntityType
        GSESSION.put(url, json=payload)
    except Exception as e:
        # Em caso de falha, apenas registra no log (não interrompe fluxo)
        print("Falha ao enviar entidades dinâmicas:", e)


def handle_intent(intent_name: str, params: dict, session_id: str) -> str:
    """
    Manipula as intents customizadas com base no cardápio e estado da sessão.
    """
    ensure_menu_loaded()
    if MENU_DF is None:
        return "Cardápio não carregado. Por favor, faça upload do cardápio em /admin."

    # Fallback inteligente - detecta cumprimentos e confirmações diretamente no texto
    user_text = params.get("queryText", "").lower().strip()

    # Detecta cumprimentos se o Dialogflow não reconheceu
    if intent_name in [None, "", "Default Fallback Intent"]:
        cumprimentos = ["olá", "oi", "ola", "boa noite", "bom dia", "e aí", "hello", "hi"]
        if any(c in user_text for c in cumprimentos):
            intent_name = "BoasVindas"

    # Contexto simples para última ação
    if 'last_action' not in CARTS:
        CARTS['last_action'] = {}
    last_action = CARTS['last_action'].get(session_id)

    # Tratamento especial para "Sim" baseado no contexto
    if intent_name == "ConfirmarPedido" and user_text in ["sim", "yes"]:
        cart = CARTS.get(session_id)
        if not cart:
            last = CARTS['last_action'].get(session_id)
            if last == 'show_menu':
                return "Ótimo! Qual item você gostaria de pedir? Digite 'ver opções' para o cardápio completo."
            elif last == 'show_category' or last == 'show_items':
                return "Perfeito! Digite o nome do item que deseja pedir."
            else:
                return "Você gostaria de fazer um pedido? Posso mostrar o cardápio ou tirar dúvidas!"
        # Se há carrinho, confirma pedido normalmente
        total = sum(itm['price'] * itm['qty'] for itm in cart)
        itens = [
            f"{itm['qty']}x {itm['item']} (R${itm['price'] * itm['qty']:.2f})"
            for itm in cart
        ]
        CARTS[session_id] = []  # Limpa carrinho
        CARTS['last_action'][session_id] = 'pedido_confirmado'
        return "Pedido confirmado: " + ", ".join(itens) + f". Total R${total:.2f}. Obrigado!"

    # Intents de categoria
    if intent_name == "ItensCategoria":
        categoria = params.get("categoria") or params.get("Categoria")
        if categoria:
            cat = str(categoria).strip().lower()
            df = MENU_DF[MENU_DF["categoria"].str.lower() == cat]
            if df.empty:
                return f"Não encontrei itens na categoria {categoria}."
            items = [f"{row['item']} (R${row['preco']:.2f})" for _, row in df.iterrows()]
            CARTS['last_action'][session_id] = 'show_category'
            return f"Itens de {categoria}: " + ", ".join(items)
        return "Qual categoria você deseja ver? Por exemplo: Burgers, Bebidas."
    # Intents de preço
    elif intent_name == "PrecoItem":
        item = params.get("item") or params.get("Item")
        if item:
            item_name = str(item).strip().lower()
            row = MENU_DF[MENU_DF["item"].str.lower() == item_name]
            if row.empty:
                return f"Não encontrei o item {item}."
            price = row.iloc[0]["preco"]
            return f"{item} custa R${price:.2f}."
        return "Sobre qual item você deseja saber o preço?"
    # Intents de detalhes
    elif intent_name == "DetalheItem":
        item = params.get("item") or params.get("Item")
        if item:
            item_name = str(item).strip().lower()
            row = MENU_DF[MENU_DF["item"].str.lower() == item_name]
            if row.empty:
                return f"Não encontrei o item {item}."
            desc = row.iloc[0]["descricao"]
            return f"{item}: {desc}."
        return "Qual item você deseja detalhes?"
    # Intents de listar vegetarianos
    elif intent_name == "ItensVegetarianos":
        df = MENU_DF[MENU_DF["vegetariano"].isin(["sim", "true", "vegano", "vegetariano"])]
        if df.empty:
            return "Nenhum item vegetariano disponível."
        items = [f"{row['item']} (R${row['preco']:.2f})" for _, row in df.iterrows()]
        return "Opções vegetarianas: " + ", ".join(items)
    # Intents para adicionar pedido
    elif intent_name == "FazerPedido":
        item = params.get("item") or params.get("Item")
        quantidade = params.get("quantidade") or params.get("number")

        # Se não há item específico, sugere opções
        if not item:
            # Verifica se a mensagem do usuário menciona uma categoria
            user_text = params.get("queryText", "").lower()
            if "hambúrguer" in user_text or "burger" in user_text:
                burgers = MENU_DF[MENU_DF["categoria"].str.lower() == "burgers"]
                if not burgers.empty:
                    items = [f"{row['item']} (R${row['preco']:.2f})" for _, row in burgers.iterrows()]
                    return f"Temos estes hambúrgueres: {', '.join(items)}. Qual você gostaria de pedir?"
            elif "bebida" in user_text:
                bebidas = MENU_DF[MENU_DF["categoria"].str.lower() == "bebidas"]
                if not bebidas.empty:
                    items = [f"{row['item']} (R${row['preco']:.2f})" for _, row in bebidas.iterrows()]
                    return f"Temos estas bebidas: {', '.join(items)}. Qual você gostaria de pedir?"
            elif "porção" in user_text or "porcao" in user_text:
                porcoes = MENU_DF[MENU_DF["categoria"].str.lower() == "porções"]
                if not porcoes.empty:
                    items = [f"{row['item']} (R${row['preco']:.2f})" for _, row in porcoes.iterrows()]
                    return f"Temos estas porções: {', '.join(items)}. Qual você gostaria de pedir?"

            return "Qual item você deseja pedir? Digite 'ver opções' para ver o cardápio completo."

        item_name = str(item).strip().lower()
        row = MENU_DF[MENU_DF["item"].str.lower() == item_name]
        if row.empty:
            # Busca por correspondência parcial
            matches = MENU_DF[MENU_DF["item"].str.lower().str.contains(item_name, na=False)]
            if not matches.empty:
                items = [f"{row['item']} (R${row['preco']:.2f})" for _, row in matches.iterrows()]
                return f"Encontrei: {', '.join(items)}. Qual especificamente você quer?"
            return f"Não encontrei o item '{item}'. Digite 'ver opções' para ver o cardápio."

        price = row.iloc[0]["preco"]
        try:
            qty = int(quantidade) if quantidade else 1
        except Exception:
            qty = 1
        total_price = price * qty
        # Adiciona no carrinho
        cart = CARTS.setdefault(session_id, [])
        cart.append({"item": item, "qty": qty, "price": price})
        CARTS['last_action'][session_id] = 'pedido_iniciado'
        return (
            f"Pedido adicionado: {qty}x {item} (R${total_price:.2f}). "
            "Deseja pedir mais alguma coisa ou confirmar?"
        )
    # Intents de confirmação de pedido
    elif intent_name == "ConfirmarPedido":
        cart = CARTS.get(session_id)
        if not cart:
            # Resposta mais amigável e contextual
            last = CARTS['last_action'].get(session_id)
            if last == 'show_menu' or last == 'show_category':
                return "Ótimo! Qual item você gostaria de pedir?"
            return "Você gostaria de fazer um pedido? Posso mostrar o cardápio ou tirar dúvidas!"
        total = sum(itm['price'] * itm['qty'] for itm in cart)
        itens = [
            f"{itm['qty']}x {itm['item']} (R${itm['price'] * itm['qty']:.2f})"
            for itm in cart
        ]
        CARTS[session_id] = []  # Limpa carrinho
        CARTS['last_action'][session_id] = 'pedido_confirmado'
        return "Pedido confirmado: " + ", ".join(itens) + f". Total R${total:.2f}. Obrigado!"
    elif intent_name == "NegarPedido":
        CARTS[session_id] = []  # Limpa carrinho
        CARTS['last_action'][session_id] = 'pedido_cancelado'
        return "Pedido cancelado. Se precisar de algo, estou à disposição!"
    # Intents simples (cumprimento, cardápio, horário, endereço, despedida)
    if intent_name == "BoasVindas":
        CARTS['last_action'][session_id] = 'boasvindas'
        return "Olá! Bem-vindo à nossa hamburgueria! Como posso te ajudar hoje?"
    elif intent_name == "Cardapio":
        CARTS['last_action'][session_id] = 'show_menu'
        return "Temos hambúrgueres artesanais, porções e bebidas geladas. Deseja ver as opções?"
    elif intent_name == "MostrarItens":
        # Mostra o cardápio detalhado com todos os itens
        CARTS['last_action'][session_id] = 'show_items'
        if MENU_DF is None or MENU_DF.empty:
            return "Cardápio não disponível no momento."

        # Agrupa por categoria e lista os itens
        categorias = MENU_DF['categoria'].unique()
        resultado = "📋 **CARDÁPIO COMPLETO** 📋\n\n"

        for categoria in categorias:
            items_categoria = MENU_DF[MENU_DF['categoria'] == categoria]
            resultado += f"🍴 **{categoria.upper()}**\n"
            for _, item in items_categoria.iterrows():
                vegetariano = " 🌱" if item.get('vegetariano', '').lower() in ['sim', 'true', 'vegetariano'] else ""
                resultado += f"• {item['item']} - R${item['preco']:.2f}{vegetariano}\n"
                if pd.notna(item.get('descricao', '')):
                    resultado += f"  {item['descricao']}\n"
            resultado += "\n"

        resultado += "💬 Digite o nome do item que deseja pedir!"
        return resultado
    elif intent_name == "HorarioFuncionamento":
        return "Funcionamos de terça a domingo, das 18h às 23h."
    elif intent_name == "Endereco":
        return "Estamos na Rua das Delícias, nº 123 – Centro."
    elif intent_name == "Despedida":
        return "Obrigado pela visita! Esperamos vê-lo em breve! 🍔"
    # Qualquer outra intent cai no fallback
    return "Desculpe, não entendi. Posso listar o cardápio ou informar preços."


@app.route("/dialogflow", methods=["POST"])
def dialogflow_webhook():
    """Endpoint de Fulfillment para Dialogflow e interface web."""
    body = request.json or {}
    # Suporte a payload simples: {"text": "mensagem"}
    if 'text' in body:
        user_message = body['text']
        session_id = "usuario-streamlit"
        push_session_entities(session_id)
        url = (
            f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/"
            f"{session_id}:detectIntent"
        )
        payload = {
            "queryInput": {
                "text": {
                    "text": user_message,
                    "languageCode": LANG,
                }
            }
        }
        df_response = GSESSION.post(url, json=payload).json()
        intent = df_response.get("queryResult", {}).get("intent", {}).get("displayName")
        params = df_response.get("queryResult", {}).get("parameters", {})
        # Adiciona o texto original do usuário aos parâmetros para fallback inteligente
        params["queryText"] = user_message
        print(f"[DEBUG] detectIntent: texto='{user_message}' intent='{intent}' params={params}")
        response = handle_intent(intent, params, session_id)
        return {"fulfillmentText": response}
    # Suporte legado (payload Dialogflow)
    session = body.get("session", "")
    session_id = session.split("/")[-1] if session else "unknown"
    push_session_entities(session_id)
    intent = body.get("queryResult", {}).get("intent", {}).get("displayName")
    params = body.get("queryResult", {}).get("parameters", {})
    response = handle_intent(intent, params, session_id)
    return {"fulfillmentText": response}


if __name__ == "__main__":
    # Define porta diferente para não conflitar com outros serviços
    app.run(host="0.0.0.0", port=5008)