import os
import json
import requests
import pandas as pd
from flask import Flask, request
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

"""
Webhook para integrar Telegram a Dialogflow.
Recebe mensagens do bot do Telegram, sincroniza entidades dinâmicas
(@Item) com base no cardápio e repassa a mensagem para o Dialogflow.
Em seguida, envia a resposta do Dialogflow de volta ao usuário no Telegram.
"""

# Configurações principais
CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
PROJECT_ID = "fiap-boot"
LANG = "pt-BR"
# Token do bot fornecido pelo BotFather
TELEGRAM_TOKEN = "8390986037:AAGnbcFuL_DRRxaUX7ZUjTRxWlxv3shrwEI"

app = Flask(__name__)

# Sessão autenticada para Dialogflow
SCOPES = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
df_session = AuthorizedSession(credentials)

# DataFrame em cache com cardápio
MENU_DF: pd.DataFrame | None = None


def ensure_menu_loaded() -> bool:
    """Carrega o cardápio salvo em cache (cardapio_cache.csv) se ainda não estiver carregado."""
    global MENU_DF
    if MENU_DF is None and os.path.exists("cardapio_cache.csv"):
        try:
            MENU_DF = pd.read_csv("cardapio_cache.csv")
        except Exception:
            MENU_DF = None
    return MENU_DF is not None


def push_session_entities(session_id: str) -> None:
    """
    Publica um SessionEntityType @Item na sessão do Dialogflow para reconhecer itens do cardápio.
    Lê nomes e sinônimos da coluna 'item' e opcional 'sinonimos' do arquivo de cardápio.
    """
    if not ensure_menu_loaded():
        return
    items_entities = []
    # Constrói entidades
    for _, row in MENU_DF.iterrows():
        value = str(row["item"]).strip()
        synonyms = [value]
        if "sinonimos" in MENU_DF.columns:
            raw = row.get("sinonimos", "")
            if pd.notna(raw) and str(raw).strip() != "":
                parts = str(raw).split("|")
                synonyms += [p.strip() for p in parts if p.strip()]
        items_entities.append({"value": value, "synonyms": synonyms})
    url = (
        f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/"
        f"{session_id}/entityTypes/Item"
    )
    payload = {
        "entityOverrideMode": "ENTITY_OVERRIDE_MODE_OVERRIDE",
        "entities": items_entities,
    }
    # Atualiza usando PUT
    try:
        df_session.put(url, json=payload)
    except Exception as e:
        print("Falha ao publicar SessionEntityType:", e)


@app.post("/webhook")
def telegram_webhook():
    """
    Endpoint que recebe atualizações do Telegram.
    Extrai a mensagem de texto, envia para o Dialogflow e devolve a resposta ao usuário.
    """
    data = request.json or {}
    msg = data.get("message") or data.get("edited_message") or {}
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    user_message = msg.get("text", "")
    # Ignora mensagens sem texto ou sem chat_id
    if not chat_id or not user_message:
        return "skip", 200

    session_id = str(chat_id)
    # Atualiza entidades dinâmicas para esta sessão
    try:
        push_session_entities(session_id)
    except Exception as e:
        print("Erro ao atualizar entidades:", e)
    # Envia a mensagem para o detectIntent
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
    df_response = df_session.post(url, json=payload).json()
    reply = df_response.get("queryResult", {}).get("fulfillmentText", "Desculpe, não entendi.")
    # Envia resposta via Telegram
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(send_url, json={"chat_id": chat_id, "text": reply})
    except Exception as e:
        print("Falha ao enviar mensagem para Telegram:", e)
    return "ok", 200


if __name__ == "__main__":
    # Define a porta padrão para o webhook do Telegram
    app.run(host="0.0.0.0", port=5007)