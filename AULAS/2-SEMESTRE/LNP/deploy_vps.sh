#!/bin/bash

# FiapNet - Deploy Rápido para VPS
# Execute este script na sua VPS para instalar o FiapNet

set -e

echo "🚀 FiapNet - Deploy Rápido para VPS"
echo "=================================="

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Este script não deve ser executado como root"
   echo "💡 Execute como usuário normal (será solicitado sudo quando necessário)"
   exit 1
fi

# Configurações
APP_NAME="fiapnet"
APP_DIR="/home/$USER/$APP_NAME"
REPO_URL="https://github.com/alansms/chatboot_dialogflow.git"

echo "📋 Configurações:"
echo "   Usuário: $USER"
echo "   Diretório: $APP_DIR"
echo "   Repositório: $REPO_URL"
echo ""

# 1. Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
echo "🔧 Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# 3. Criar diretório e clonar
echo "📥 Clonando repositório..."
if [ -d "$APP_DIR" ]; then
    echo "⚠️  Diretório $APP_DIR já existe. Removendo..."
    rm -rf "$APP_DIR"
fi

git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR/AULAS/2-SEMESTRE/LNP"

# 4. Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# 5. Instalar dependências Python
echo "📚 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."
cp config_example.env .env

# Gerar chave secreta
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
sed -i "s/your_secret_key_here/$SECRET_KEY/" .env

echo "✅ Arquivo .env criado com chave secreta gerada"
echo "📝 Configure as outras variáveis manualmente:"
echo "   - TELEGRAM_TOKEN"
echo "   - DOMAIN"
echo "   - SSL_EMAIL"

# 7. Configurar Nginx
echo "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;

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
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 8. Configurar Gunicorn
echo "⚙️ Configurando Gunicorn..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=FiapNet - Suporte de Internet
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR/AULAS/2-SEMESTRE/LNP
Environment=PATH=$APP_DIR/AULAS/2-SEMESTRE/LNP/venv/bin
EnvironmentFile=$APP_DIR/AULAS/2-SEMESTRE/LNP/.env
ExecStart=$APP_DIR/AULAS/2-SEMESTRE/LNP/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5023 --timeout 120 app_web:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 9. Iniciar serviços
echo "🚀 Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl start $APP_NAME

# 10. Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 11. Obter IP público
PUBLIC_IP=$(curl -s ifconfig.me)

# 12. Criar script de configuração
echo "📋 Criando script de configuração..."
cat > configure.sh << 'EOF'
#!/bin/bash
# Script de configuração pós-deploy

echo "🔧 Configuração pós-deploy do FiapNet"
echo "====================================="

# Solicitar informações
read -p "🌐 Digite seu domínio (ex: fiapnet.com): " DOMAIN
read -p "📱 Digite o token do Telegram: " TELEGRAM_TOKEN
read -p "📧 Digite seu email para SSL: " EMAIL

# Atualizar configuração do Nginx
sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/fiapnet

# Configurar variáveis de ambiente
cat > .env << ENVEOF
FLASK_ENV=production
DEBUG=False
PORT=5023
PROJECT_ID=fiap-boot
LANG=pt-BR
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
WEBHOOK_URL=https://$DOMAIN/telegram
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
ENVEOF

# Recarregar Nginx
sudo systemctl reload nginx

# Configurar SSL
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

# Configurar webhook do Telegram
source venv/bin/activate
python telegram_setup.py setup

echo "✅ Configuração concluída!"
echo "🌐 Acesse: https://$DOMAIN"
echo "📱 Bot Telegram: @chat_fiap_bot"
EOF

chmod +x configure.sh

# 13. Verificar status
echo "🔍 Verificando status dos serviços..."
if sudo systemctl is-active --quiet $APP_NAME; then
    echo "✅ FiapNet: Ativo"
else
    echo "❌ FiapNet: Inativo"
    sudo systemctl status $APP_NAME
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Ativo"
else
    echo "❌ Nginx: Inativo"
    sudo systemctl status nginx
fi

# 14. Instruções finais
echo ""
echo "🎉 FiapNet instalado com sucesso!"
echo "================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Execute: ./configure.sh"
echo "2. Configure seu domínio e token do Telegram"
echo "3. Acesse: http://$PUBLIC_IP"
echo ""
echo "📁 Arquivos importantes:"
echo "- Aplicação: $APP_DIR/AULAS/2-SEMESTRE/LNP"
echo "- Logs: journalctl -u $APP_NAME -f"
echo "- Nginx: /var/log/nginx/error.log"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "• Status: sudo systemctl status $APP_NAME"
echo "• Restart: sudo systemctl restart $APP_NAME"
echo "• Logs: journalctl -u $APP_NAME -f"
echo "• Configurar: ./configure.sh"
echo ""
echo "📱 Configure o webhook do Telegram após configurar o domínio!"
echo ""
echo "✅ Deploy concluído! 🚀"
