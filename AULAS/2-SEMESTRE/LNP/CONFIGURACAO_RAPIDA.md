# ⚡ Configuração Rápida - Telegram + FiapNet

## 🚀 **CONFIGURAÇÃO EM 5 MINUTOS**

### **1. Criar Bot no Telegram (2 min)**

1. **Abra o Telegram** e procure por `@BotFather`
2. **Envie**: `/newbot`
3. **Nome**: `FiapNet Suporte`
4. **Username**: `fiapnet_suporte_bot`
5. **Copie o TOKEN** fornecido

### **2. Configurar Variáveis (1 min)**

```bash
# Configure o token
export TELEGRAM_TOKEN="seu_token_aqui"

# Para desenvolvimento local
export WEBHOOK_URL="https://seu-ngrok-url.ngrok.io/telegram"
```

### **3. Iniciar Aplicação (1 min)**

```bash
# Terminal 1: Aplicação
python app_web.py

# Terminal 2: ngrok
./start_with_ngrok.sh
```

### **4. Configurar Webhook (1 min)**

```bash
# Configurar webhook
python telegram_setup.py setup
```

### **5. Testar (30 seg)**

1. **Procure**: `@fiapnet_suporte_bot` no Telegram
2. **Envie**: `Olá`
3. **Veja a mágica acontecer!** ✨

---

## 🎯 **COMANDOS ÚTEIS**

```bash
# Ver informações do bot
python telegram_setup.py info

# Testar webhook
python telegram_setup.py test

# Configurar webhook
python telegram_setup.py setup

# Iniciar com ngrok
./start_with_ngrok.sh
```

---

## 🔧 **SOLUÇÃO DE PROBLEMAS**

### **Erro: "TELEGRAM_TOKEN não encontrado"**
```bash
export TELEGRAM_TOKEN="seu_token_aqui"
```

### **Erro: "Aplicação não está rodando"**
```bash
python app_web.py
```

### **Erro: "ngrok não encontrado"**
- Instale: https://ngrok.com/download
- Ou use outro túnel (localtunnel, serveo, etc.)

### **Webhook não funciona**
1. Verifique se a aplicação está rodando
2. Verifique se o ngrok está ativo
3. Execute: `python telegram_setup.py test`

---

## 🎉 **PRONTO!**

Seu bot FiapNet está funcionando no Telegram! 🚀

**Teste estas mensagens:**
- `Olá`
- `Quero abrir um chamado`
- `Informações sobre planos`
- `Consultar status`
- `Horário de funcionamento`
