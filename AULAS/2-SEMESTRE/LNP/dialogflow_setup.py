#!/usr/bin/env python3
"""
Script para configurar o webhook do Dialogflow
"""

import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

def setup_dialogflow_webhook():
    """Configura o webhook do Dialogflow."""
    
    # Configurações
    CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
    PROJECT_ID = "fiap-boot"
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Arquivo de credenciais não encontrado: {CREDENTIALS_FILE}")
        return False
    
    # URL do webhook
    webhook_url = input("🌐 Digite a URL pública do seu webhook (ex: https://seu-dominio.com/dialogflow): ").strip()
    
    if not webhook_url:
        print("❌ URL do webhook é obrigatória")
        return False
    
    try:
        # Autenticação
        SCOPES = ["https://www.googleapis.com/auth/dialogflow"]
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        session = AuthorizedSession(credentials)
        
        # URL da API do Dialogflow
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent"
        
        # Dados do webhook
        webhook_data = {
            "webhook": {
                "url": webhook_url,
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        }
        
        print(f"🔧 Configurando webhook: {webhook_url}")
        
        # Fazer a requisição
        response = session.patch(url, json=webhook_data)
        
        if response.status_code == 200:
            print("✅ Webhook configurado com sucesso!")
            print(f"🌐 URL: {webhook_url}")
            print(f"📋 Projeto: {PROJECT_ID}")
            return True
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        return False

def list_intents():
    """Lista todas as intents do projeto."""
    
    CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
    PROJECT_ID = "fiap-boot"
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Arquivo de credenciais não encontrado: {CREDENTIALS_FILE}")
        return False
    
    try:
        # Autenticação
        SCOPES = ["https://www.googleapis.com/auth/dialogflow"]
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        session = AuthorizedSession(credentials)
        
        # URL da API
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
        
        print("📋 Listando intents...")
        
        response = session.get(url)
        
        if response.status_code == 200:
            result = response.json()
            intents = result.get("intents", [])
            
            if intents:
                print(f"✅ Encontradas {len(intents)} intents:")
                for intent in intents:
                    name = intent.get("displayName", "N/A")
                    webhook_enabled = intent.get("webhookState", "WEBHOOK_STATE_UNSPECIFIED")
                    print(f"   • {name} (Webhook: {webhook_enabled})")
            else:
                print("❌ Nenhuma intent encontrada")
            
            return True
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao listar intents: {e}")
        return False

def enable_webhook_for_intents():
    """Habilita webhook para todas as intents."""
    
    CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
    PROJECT_ID = "fiap-boot"
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Arquivo de credenciais não encontrado: {CREDENTIALS_FILE}")
        return False
    
    try:
        # Autenticação
        SCOPES = ["https://www.googleapis.com/auth/dialogflow"]
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        session = AuthorizedSession(credentials)
        
        # Listar intents
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
        response = session.get(url)
        
        if response.status_code != 200:
            print(f"❌ Erro ao listar intents: {response.text}")
            return False
        
        intents = response.json().get("intents", [])
        
        if not intents:
            print("❌ Nenhuma intent encontrada")
            return False
        
        print(f"🔧 Habilitando webhook para {len(intents)} intents...")
        
        success_count = 0
        
        for intent in intents:
            intent_name = intent.get("displayName", "")
            intent_id = intent.get("name", "").split("/")[-1]
            
            if not intent_name or not intent_id:
                continue
            
            # Atualizar intent para habilitar webhook
            update_data = {
                "webhookState": "WEBHOOK_STATE_ENABLED"
            }
            
            update_url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents/{intent_id}"
            update_response = session.patch(update_url, json=update_data)
            
            if update_response.status_code == 200:
                print(f"   ✅ {intent_name}")
                success_count += 1
            else:
                print(f"   ❌ {intent_name}: {update_response.text}")
        
        print(f"✅ Webhook habilitado para {success_count}/{len(intents)} intents")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao habilitar webhook: {e}")
        return False

def test_webhook():
    """Testa o webhook com uma mensagem de exemplo."""
    
    webhook_url = input("🌐 Digite a URL do webhook para testar: ").strip()
    
    if not webhook_url:
        print("❌ URL do webhook é obrigatória")
        return False
    
    # Payload de teste
    test_payload = {
        "queryResult": {
            "queryText": "Olá",
            "intent": {
                "displayName": "Saudacao_Identificacao"
            },
            "parameters": {
                "queryText": "Olá"
            }
        }
    }
    
    try:
        print(f"🧪 Testando webhook: {webhook_url}")
        
        response = requests.post(webhook_url, json=test_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            fulfillment_text = result.get("fulfillmentText", "")
            print("✅ Webhook funcionando!")
            print(f"📝 Resposta: {fulfillment_text[:100]}...")
            return True
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {e}")
        return False

def main():
    """Menu principal."""
    
    print("🤖 Configuração do Dialogflow - FiapNet")
    print("=" * 50)
    
    while True:
        print("\n📋 Opções:")
        print("1. Configurar webhook")
        print("2. Listar intents")
        print("3. Habilitar webhook para todas as intents")
        print("4. Testar webhook")
        print("5. Sair")
        
        choice = input("\n👉 Escolha uma opção (1-5): ").strip()
        
        if choice == "1":
            setup_dialogflow_webhook()
        elif choice == "2":
            list_intents()
        elif choice == "3":
            enable_webhook_for_intents()
        elif choice == "4":
            test_webhook()
        elif choice == "5":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
