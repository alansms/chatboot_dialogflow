from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# Dados
PROJECT_ID = "fiap-boot"
CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"

# Autenticação
scopes = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
authed_session = AuthorizedSession(credentials)

# JSON da intent
intent = {
    "displayName": "Cumprimento",
    "trainingPhrases": [
        {
            "type": "EXAMPLE",
            "parts": [{"text": "Olá"}]
        },
        {
            "type": "EXAMPLE",
            "parts": [{"text": "Oi"}]
        }
    ],
    "messages": [
        {
            "text": {
                "text": ["Olá! Como posso te ajudar?"]
            }
        }
    ]
}

# Requisição para criar a intent
url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
response = authed_session.post(url, json=intent)

# Resultado
print(response.status_code)
print(response.json())