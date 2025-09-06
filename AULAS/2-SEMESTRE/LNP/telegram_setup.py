#!/usr/bin/env python3
"""
Script para configurar o webhook do Telegram
"""

import os
import requests
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def setup_telegram_webhook():
    """Configura o webhook do Telegram."""
    
    # Verificar se o token está configurado
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        print("❌ ERRO: TELEGRAM_TOKEN não encontrado!")
        print("📝 Configure a variável de ambiente TELEGRAM_TOKEN")
        print("   export TELEGRAM_TOKEN='seu_token_aqui'")
        return False
    
    # URL do webhook (você precisa configurar com sua URL pública)
    webhook_url = os.getenv("WEBHOOK_URL", "https://seu-dominio.com/telegram")
    
    print(f"🤖 Configurando webhook do Telegram...")
    print(f"📡 Token: {telegram_token[:10]}...")
    print(f"🌐 Webhook URL: {webhook_url}")
    
    # URL da API do Telegram
    telegram_api_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook"
    
    # Dados do webhook
    webhook_data = {
        "url": webhook_url,
        "allowed_updates": ["message"]
    }
    
    try:
        # Configurar webhook
        response = requests.post(telegram_api_url, json=webhook_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook configurado com sucesso!")
                print(f"📋 Resultado: {result.get('description', 'OK')}")
                return True
            else:
                print(f"❌ Erro ao configurar webhook: {result.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        return False

def get_bot_info():
    """Obtém informações do bot."""
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        print("❌ ERRO: TELEGRAM_TOKEN não encontrado!")
        return False
    
    try:
        # URL da API do Telegram
        telegram_api_url = f"https://api.telegram.org/bot{telegram_token}/getMe"
        
        response = requests.get(telegram_api_url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                print("🤖 Informações do Bot:")
                print(f"   Nome: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                print(f"   ID: {bot_info.get('id', 'N/A')}")
                print(f"   Pode ingressar em grupos: {bot_info.get('can_join_groups', False)}")
                print(f"   Pode ler mensagens: {bot_info.get('can_read_all_group_messages', False)}")
                return True
            else:
                print(f"❌ Erro ao obter informações: {result.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")
        return False

def test_webhook():
    """Testa o webhook configurado."""
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        print("❌ ERRO: TELEGRAM_TOKEN não encontrado!")
        return False
    
    try:
        # URL da API do Telegram
        telegram_api_url = f"https://api.telegram.org/bot{telegram_token}/getWebhookInfo"
        
        response = requests.get(telegram_api_url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                webhook_info = result.get("result", {})
                print("🔍 Informações do Webhook:")
                print(f"   URL: {webhook_info.get('url', 'N/A')}")
                print(f"   Tem certificado personalizado: {webhook_info.get('has_custom_certificate', False)}")
                print(f"   Número de atualizações pendentes: {webhook_info.get('pending_update_count', 0)}")
                
                if webhook_info.get('last_error_date'):
                    print(f"   Último erro: {webhook_info.get('last_error_message', 'N/A')}")
                    print(f"   Data do último erro: {webhook_info.get('last_error_date', 'N/A')}")
                
                return True
            else:
                print(f"❌ Erro ao obter informações: {result.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")
        return False

def main():
    """Função principal."""
    
    print("🚀 Configuração do Telegram Bot - FiapNet")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "info":
            get_bot_info()
        elif command == "test":
            test_webhook()
        elif command == "setup":
            setup_telegram_webhook()
        else:
            print("❌ Comando inválido!")
            print("📝 Comandos disponíveis:")
            print("   python telegram_setup.py info    - Obter informações do bot")
            print("   python telegram_setup.py test    - Testar webhook")
            print("   python telegram_setup.py setup   - Configurar webhook")
    else:
        print("📝 Comandos disponíveis:")
        print("   python telegram_setup.py info    - Obter informações do bot")
        print("   python telegram_setup.py test    - Testar webhook")
        print("   python telegram_setup.py setup   - Configurar webhook")
        print()
        print("🔧 Configuração necessária:")
        print("   1. Configure a variável TELEGRAM_TOKEN")
        print("   2. Configure a variável WEBHOOK_URL (sua URL pública)")
        print("   3. Execute: python telegram_setup.py setup")

if __name__ == "__main__":
    main()