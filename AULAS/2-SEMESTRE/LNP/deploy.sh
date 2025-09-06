#!/bin/bash

# FiapNet - Script de Deploy para VPS
# Configuração para produção com nginx + gunicorn

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do FiapNet - Suporte de Internet"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root"
   exit 1
fi

# Configurações
APP_NAME="fiapnet"
APP_DIR="/home/$USER/$APP_NAME"
SERVICE_NAME="fiapnet"
NGINX_SITE="fiapnet"

log "Configurando ambiente de produção..."

# 1. Atualizar sistema
log "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências do sistema
log "Instalando dependências do sistema..."
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# 3. Criar diretório da aplicação
log "Criando diretório da aplicação..."
mkdir -p $APP_DIR
cd $APP_DIR

# 4. Clonar código do GitHub
log "Clonando código do GitHub..."
if [ -d ".git" ]; then
    log "Atualizando código existente..."
    git pull origin master
else
    log "Clonando repositório..."
    git clone https://github.com/alansms/chatboot_dialogflow.git .
    cd AULAS/2-SEMESTRE/LNP
    cp -r * $APP_DIR/
    cd $APP_DIR
fi

# 5. Criar ambiente virtual
log "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependências Python
log "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Configurar variáveis de ambiente
log "Configurando variáveis de ambiente..."
cat > .env << EOF
# Configurações da aplicação
FLASK_ENV=production
DEBUG=False
PORT=5023

# Configurações do Dialogflow
PROJECT_ID=fiap-boot
LANG=pt-BR

# Configurações do Telegram (configure manualmente)
TELEGRAM_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=https://your-domain.com/telegram

# Configurações de segurança
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF

# 8. Criar diretório de logs
log "Criando diretório de logs..."
mkdir -p logs

# 9. Criar arquivo de serviço systemd
log "Configurando serviço systemd..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=FiapNet - Suporte de Internet
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5023 --timeout 120 app_web:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 10. Configurar Nginx
log "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Logs
    access_log /var/log/nginx/fiapnet_access.log;
    error_log /var/log/nginx/fiapnet_error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5023;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5023/health;
        access_log off;
    }
}
EOF

# 11. Habilitar site no Nginx
log "Habilitando site no Nginx..."
sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 12. Testar configuração do Nginx
log "Testando configuração do Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    success "Configuração do Nginx válida"
else
    error "Erro na configuração do Nginx"
    exit 1
fi

# 13. Recarregar systemd e iniciar serviços
log "Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME
sudo systemctl enable nginx
sudo systemctl restart nginx

# 14. Verificar status dos serviços
log "Verificando status dos serviços..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    success "Serviço $SERVICE_NAME está rodando"
else
    error "Erro ao iniciar serviço $SERVICE_NAME"
    sudo systemctl status $SERVICE_NAME
fi

if sudo systemctl is-active --quiet nginx; then
    success "Nginx está rodando"
else
    error "Erro ao iniciar Nginx"
    sudo systemctl status nginx
fi

# 15. Configurar firewall
log "Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 16. Obter IP público
PUBLIC_IP=$(curl -s ifconfig.me)

# 17. Criar script de configuração pós-deploy
log "Criando script de configuração..."
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

# 18. Instruções finais
success "Deploy concluído com sucesso!"
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
echo "- Aplicação: $APP_DIR"
echo "- Logs: journalctl -u $SERVICE_NAME -f"
echo "- Nginx: /var/log/nginx/fiapnet_*.log"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "• Status: sudo systemctl status $SERVICE_NAME"
echo "• Restart: sudo systemctl restart $SERVICE_NAME"
echo "• Logs: journalctl -u $SERVICE_NAME -f"
echo "• Configurar: ./configure.sh"
echo ""
echo "📱 Configure o webhook do Telegram após configurar o domínio!"
echo ""
success "Deploy do FiapNet concluído! 🎉"