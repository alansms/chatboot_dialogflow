import json
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# CONFIGURAÇÕES
CREDENTIALS_FILE = "/Users/alansms/PycharmProjects/Fiap/AULAS/2-SEMESTRE/LNP/fiap-boot-a239f7750ffc.json"
PROJECT_ID = "fiap-boot"
INTENTS_FILE = "/Users/alansms/PycharmProjects/Fiap/AULAS/2-SEMESTRE/LNP/intents_hamburgueria.json"

# Autenticação
scopes = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
session = AuthorizedSession(credentials)

# Carregar intents
with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    intents = json.load(f)

# URL da API
url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"

# Enviar intents
for intent in intents:
    body = {
        "displayName": intent["displayName"],
        "trainingPhrases": [
            {
                "type": "EXAMPLE",
                "parts": [{"text": phrase}]
            } for phrase in intent["trainingPhrases"]
        ],
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