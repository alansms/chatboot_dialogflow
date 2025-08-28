import json
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# CONFIGURAÇÕES
CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
PROJECT_ID = "fiap-boot"
ENTITIES_FILE = "entities_hamburgueria.json"

# Autenticação
scopes = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
session = AuthorizedSession(credentials)

# Carregar entidades
with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
    entities = json.load(f)

# URL da API
url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/entityTypes"

# Enviar entidades
for entity in entities:
    body = {
        "displayName": entity["displayName"],
        "kind": entity["kind"],
        "autoExpansionMode": entity.get("autoExpansionMode", "AUTO_EXPANSION_MODE_DEFAULT"),
        "entities": entity["entities"]
    }

    response = session.post(url, json=body)
    print(f"[{entity['displayName']}] {response.status_code}")
    try:
        print(response.json())
    except:
        pass