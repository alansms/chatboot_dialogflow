# 🚀 Guia de Deploy - FiapNet

## 📋 Pré-requisitos

### **VPS/Servidor:**
- Ubuntu 20.04+ ou similar
- 1GB RAM mínimo
- 10GB espaço em disco
- Acesso root ou sudo

### **Domínio:**
- Domínio configurado apontando para o IP da VPS
- Certificado SSL (Let's Encrypt)

### **Contas:**
- Google Cloud Platform (Dialogflow)
- Telegram Bot (via @BotFather)

## 🔧 Deploy Automático

### **1. Conectar na VPS:**
```bash
ssh root@seu-ip-da-vps
```

### **2. Executar script de deploy:**
```bash
# Baixar e executar o script
curl -sSL https://raw.githubusercontent.com/alansms/chatboot_dialogflow/master/AULAS/2-SEMESTRE/LNP/deploy.sh | bash
```

### **3. Configurar aplicação:**
```bash
cd /home/ubuntu/fiapnet
./configure.sh
```

## 🛠️ Deploy Manual

### **1. Preparar servidor:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl
```

### **2. Clonar repositório:**
```bash
# Criar usuário
sudo useradd -m -s /bin/bash fiapnet
sudo usermod -aG sudo fiapnet

# Clonar código
sudo -u fiapnet git clone https://github.com/alansms/chatboot_dialogflow.git /home/fiapnet/app
cd /home/fiapnet/app/AULAS/2-SEMESTRE/LNP
```

### **3. Configurar aplicação:**
```bash
# Criar ambiente virtual
sudo -u fiapnet python3 -m venv /home/fiapnet/venv
sudo -u fiapnet /home/fiapnet/venv/bin/pip install -r requirements.txt

# Configurar variáveis
sudo -u fiapnet cp config_example.env .env
sudo -u fiapnet nano .env  # Configure as variáveis
```

### **4. Configurar Nginx:**
```bash
# Criar configuração
sudo tee /etc/nginx/sites-available/fiapnet > /dev/null <<EOF
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5023;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/fiapnet /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### **5. Configurar Gunicorn:**
```bash
# Criar serviço
sudo tee /etc/systemd/system/fiapnet.service > /dev/null <<EOF
[Unit]
Description=FiapNet
After=network.target

[Service]
User=fiapnet
Group=fiapnet
WorkingDirectory=/home/fiapnet/app/AULAS/2-SEMESTRE/LNP
Environment=PATH=/home/fiapnet/venv/bin
ExecStart=/home/fiapnet/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5023 app_web:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable fiapnet
sudo systemctl start fiapnet
```

### **6. Configurar SSL:**
```bash
# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com --non-interactive --agree-tos --email seu-email@exemplo.com
```

## 🔧 Configuração Pós-Deploy

### **1. Configurar Telegram:**
```bash
# Configurar webhook
cd /home/fiapnet/app/AULAS/2-SEMESTRE/LNP
sudo -u fiapnet /home/fiapnet/venv/bin/python telegram_setup.py setup
```

### **2. Configurar Dialogflow:**
```bash
# Configurar webhook do Dialogflow
sudo -u fiapnet /home/fiapnet/venv/bin/python dialogflow_setup.py
```

### **3. Testar aplicação:**
```bash
# Verificar status
sudo systemctl status fiapnet
sudo systemctl status nginx

# Verificar logs
sudo journalctl -u fiapnet -f
```

## 📊 Monitoramento

### **Comandos úteis:**
```bash
# Status dos serviços
sudo systemctl status fiapnet nginx

# Logs da aplicação
sudo journalctl -u fiapnet -f

# Logs do Nginx
sudo tail -f /var/log/nginx/fiapnet_error.log

# Reiniciar serviços
sudo systemctl restart fiapnet
sudo systemctl restart nginx

# Verificar portas
sudo netstat -tlnp | grep :5023
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### **Health Check:**
```bash
# Verificar se aplicação está respondendo
curl -s http://localhost:5023/health
curl -s https://seu-dominio.com/health
```

## 🔒 Segurança

### **Firewall:**
```bash
# Configurar UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### **Atualizações:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Atualizar aplicação
cd /home/fiapnet/app
sudo -u fiapnet git pull origin master
sudo systemctl restart fiapnet
```

## 🚨 Troubleshooting

### **Aplicação não inicia:**
```bash
# Verificar logs
sudo journalctl -u fiapnet -f

# Verificar configuração
sudo -u fiapnet /home/fiapnet/venv/bin/python -c "import app_web"

# Verificar dependências
sudo -u fiapnet /home/fiapnet/venv/bin/pip list
```

### **Nginx não funciona:**
```bash
# Verificar configuração
sudo nginx -t

# Verificar logs
sudo tail -f /var/log/nginx/error.log

# Verificar portas
sudo netstat -tlnp | grep nginx
```

### **SSL não funciona:**
```bash
# Renovar certificado
sudo certbot renew

# Verificar certificado
sudo certbot certificates
```

## 📱 Configuração do Telegram

### **1. Criar bot:**
1. Acesse @BotFather no Telegram
2. Execute `/newbot`
3. Escolha um nome e username
4. Copie o token

### **2. Configurar webhook:**
```bash
# Usar o script de configuração
python telegram_setup.py setup

# Ou manualmente
curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://seu-dominio.com/telegram"}'
```

### **3. Testar bot:**
1. Acesse @seu_bot no Telegram
2. Envie uma mensagem
3. Verifique se recebe resposta

## 🌐 URLs Importantes

Após o deploy, você terá acesso a:

- **Interface Web:** `https://seu-dominio.com`
- **Chat:** `https://seu-dominio.com/chat`
- **Admin:** `https://seu-dominio.com/admin`
- **Gerenciar Intents:** `https://seu-dominio.com/intent-manager`
- **Gerenciar Entidades:** `https://seu-dominio.com/entity-manager`
- **Webhook Telegram:** `https://seu-dominio.com/telegram`
- **Webhook Dialogflow:** `https://seu-dominio.com/dialogflow`
- **Health Check:** `https://seu-dominio.com/health`

## 🎉 Conclusão

Após seguir este guia, você terá:

✅ **Aplicação web funcionando**  
✅ **Bot Telegram ativo**  
✅ **Dialogflow integrado**  
✅ **SSL configurado**  
✅ **Monitoramento ativo**  

**FiapNet está pronto para produção! 🚀**
