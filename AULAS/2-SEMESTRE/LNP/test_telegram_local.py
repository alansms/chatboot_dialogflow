#!/usr/bin/env python3
"""
Script para testar o bot do Telegram localmente
Simula mensagens do Telegram para testar a integração
"""

import requests
import json
import time
import os

def test_telegram_webhook():
    """Testa o webhook do Telegram localmente."""
    
    # URL do webhook local
    webhook_url = "http://localhost:5023/telegram"
    
    # Mensagens de teste
    test_messages = [
        {
            "message": {
                "text": "Olá",
                "chat": {"id": 123456789},
                "from": {"id": 123456789, "first_name": "Teste"}
            }
        },
        {
            "message": {
                "text": "Quero abrir um chamado",
                "chat": {"id": 123456789},
                "from": {"id": 123456789, "first_name": "Teste"}
            }
        },
        {
            "message": {
                "text": "Informações sobre planos",
                "chat": {"id": 123456789},
                "from": {"id": 123456789, "first_name": "Teste"}
            }
        },
        {
            "message": {
                "text": "Consultar status",
                "chat": {"id": 123456789},
                "from": {"id": 123456789, "first_name": "Teste"}
            }
        }
    ]
    
    print("🤖 Testando Bot FiapNet - Telegram")
    print("=" * 50)
    
    for i, message_data in enumerate(test_messages, 1):
        print(f"\n📱 Teste {i}: '{message_data['message']['text']}'")
        
        try:
            response = requests.post(
                webhook_url,
                json=message_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Webhook respondeu: OK")
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Pausa entre testes
        time.sleep(1)
    
    print("\n🎉 Testes concluídos!")
    print("\n📝 Para testar no Telegram real:")
    print("1. Configure o webhook com ngrok ou servidor público")
    print("2. Execute: python telegram_setup.py setup")
    print("3. Teste com @chat_fiap_bot")

def test_bot_info():
    """Testa as informações do bot."""
    
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN não configurado!")
        return
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print("🤖 Informações do Bot:")
                print(f"   Nome: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                print(f"   ID: {bot_info.get('id', 'N/A')}")
                print(f"   Link: https://t.me/{bot_info.get('username', 'N/A')}")
            else:
                print(f"❌ Erro: {data.get('description')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal."""
    
    print("🚀 Teste do Bot FiapNet - Telegram")
    print("=" * 50)
    
    # Verificar se a aplicação está rodando
    try:
        response = requests.get("http://localhost:5023/health", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicação rodando na porta 5023")
        else:
            print("❌ Aplicação não está respondendo")
            return
    except:
        print("❌ Aplicação não está rodando!")
        print("🔧 Execute: python app_web.py")
        return
    
    # Testar informações do bot
    print("\n📋 Informações do Bot:")
    test_bot_info()
    
    # Testar webhook
    print("\n🧪 Testando Webhook:")
    test_telegram_webhook()

if __name__ == "__main__":
    main()
