#!/bin/bash

# Script para iniciar a aplicação com ngrok
# Permite testar o Telegram localmente

echo "🚀 Iniciando FiapNet com ngrok..."

# Verificar se o ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok não encontrado!"
    echo "📥 Instale o ngrok: https://ngrok.com/download"
    exit 1
fi

# Verificar se a aplicação está rodando
if ! curl -s http://localhost:5023/health > /dev/null; then
    echo "❌ Aplicação não está rodando na porta 5023!"
    echo "🔧 Execute primeiro: python app_web.py"
    exit 1
fi

echo "✅ Aplicação rodando na porta 5023"
echo "🌐 Iniciando ngrok..."

# Iniciar ngrok na porta 5023
ngrok http 5023 --log=stdout