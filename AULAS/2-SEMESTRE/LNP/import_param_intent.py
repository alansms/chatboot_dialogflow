
import json
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# CONFIGURAÇÕES
CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
PROJECT_ID = "fiap-boot"
INTENT_FILE = "intent_PedidoDetalhado.json"

# Autenticação
scopes = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
session = AuthorizedSession(credentials)

# Carregar intent
with open(INTENT_FILE, "r", encoding="utf-8") as f:
    intents = json.load(f)

# URL da API
url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"

for intent in intents:
    training_phrases = []
    for phrase in intent["trainingPhrases"]:
        parts = []
        tokens = phrase.split()
        for token in tokens:
            if token.startswith("@") and ":" in token:
                ent, alias = token[1:].split(":")
                parts.append({
                    "text": token.replace(f"@{ent}:{alias}", alias),
                    "entityType": f"@{ent}",
                    "alias": alias,
                    "userDefined": True
                })
            else:
                parts.append({"text": token + " "})
        training_phrases.append({"type": "EXAMPLE", "parts": parts})

    parameters = [
        {
            "displayName": p["displayName"],
            "entityTypeDisplayName": p["entityTypeDisplayName"],
            "mandatory": p["mandatory"],
            "name": "",
            "value": f"${p['displayName']}"
        }
        for p in intent["parameters"]
    ]

    body = {
        "displayName": intent["displayName"],
        "trainingPhrases": training_phrases,
        "parameters": parameters,
        "messages": [
            {
                "text": {
                    "text": [intent["response"]]
                }
            }
        ]
    }

    response = session.post(url, json=body)
    print(f"[{intent['displayName']}] {response.status_code}")
    try:
        print(response.json())
    except:
        pass
