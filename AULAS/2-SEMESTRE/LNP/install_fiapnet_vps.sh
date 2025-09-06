#!/bin/bash

# FiapNet - Instalação Completa na VPS Azure
# Script completo para instalar e configurar o FiapNet

set -e

echo "🚀 FiapNet - Instalação Completa na VPS Azure"
echo "============================================="

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
   echo "💡 Execute como usuário normal (será solicitado sudo quando necessário)"
   exit 1
fi

# Configurações
APP_NAME="fiapnet"
APP_DIR="/home/$USER/$APP_NAME"
REPO_URL="https://github.com/alansms/chatboot_dialogflow.git"
TELEGRAM_TOKEN="7212197110:AAG1-u66vrSq0RnhOT4tCxVCBxy7ym87Rkg"

echo "📋 Configurações:"
echo "   Usuário: $USER"
echo "   Diretório: $APP_DIR"
echo "   Repositório: $REPO_URL"
echo "   Token Telegram: $TELEGRAM_TOKEN"
echo ""

# 1. Atualizar sistema
log "📦 Atualizando sistema..."
sudo yum update -y

# 2. Instalar dependências
log "🔧 Instalando dependências..."
sudo yum install -y python3 python3-pip git curl wget

# Instalar nginx
sudo yum install -y epel-release
sudo yum install -y nginx

# Instalar certbot
sudo yum install -y certbot python3-certbot-nginx

# 3. Criar diretório e clonar
log "📥 Clonando repositório..."
if [ -d "$APP_DIR" ]; then
    warning "Diretório $APP_DIR já existe. Removendo..."
    rm -rf "$APP_DIR"
fi

git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR/AULAS/2-SEMESTRE/LNP"

# 4. Criar ambiente virtual
log "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# 5. Instalar dependências Python
log "📚 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Configurar variáveis de ambiente
log "⚙️ Configurando variáveis de ambiente..."
cat > .env << EOF
FLASK_ENV=production
DEBUG=False
PORT=5023
PROJECT_ID=fiap-boot
LANG=pt-BR
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
WEBHOOK_URL=http://20.197.224.249/telegram
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF

success "Arquivo .env configurado com token do Telegram"

# 7. Configurar Nginx
log "🌐 Configurando Nginx..."
sudo tee /etc/nginx/conf.d/fiapnet.conf > /dev/null <<EOF
server {
    listen 80;
    server_name 20.197.224.249;

    # Logs
    access_log /var/log/nginx/fiapnet_access.log;
    error_log /var/log/nginx/fiapnet_error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Static files
    location /static/ {
        alias $APP_DIR/AULAS/2-SEMESTRE/LNP/static/;
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

# Testar configuração do Nginx
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx

# 8. Configurar Gunicorn
log "⚙️ Configurando Gunicorn..."
sudo tee /etc/systemd/system/fiapnet.service > /dev/null <<EOF
[Unit]
Description=FiapNet - Suporte de Internet
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR/AULAS/2-SEMESTRE/LNP
Environment=PATH=$APP_DIR/AULAS/2-SEMESTRE/LNP/venv/bin
ExecStart=$APP_DIR/AULAS/2-SEMESTRE/LNP/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5023 --timeout 120 app_web:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 9. Configurar permissões
log "🔐 Configurando permissões..."
sudo chown -R $USER:$USER $APP_DIR
chmod -R 755 $APP_DIR
chmod 600 $APP_DIR/AULAS/2-SEMESTRE/LNP/.env

# 10. Iniciar serviços
log "🚀 Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable fiapnet
sudo systemctl start fiapnet

# 11. Configurar firewall
log "🔥 Configurando firewall..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 12. Aguardar serviços iniciarem
log "⏳ Aguardando serviços iniciarem..."
sleep 10

# 13. Verificar status
log "🔍 Verificando status dos serviços..."
if sudo systemctl is-active --quiet fiapnet; then
    success "FiapNet: Ativo"
else
    error "FiapNet: Inativo"
    sudo systemctl status fiapnet --no-pager
fi

if sudo systemctl is-active --quiet nginx; then
    success "Nginx: Ativo"
else
    error "Nginx: Inativo"
    sudo systemctl status nginx --no-pager
fi

# 14. Testar aplicação
log "🧪 Testando aplicação..."
sleep 5
if curl -s http://localhost:5023/health > /dev/null; then
    success "Aplicação respondendo em localhost:5023"
else
    warning "Aplicação não está respondendo em localhost:5023"
    echo "📋 Verificando logs..."
    sudo journalctl -u fiapnet --no-pager -n 20
fi

# 15. Configurar webhook do Telegram
log "📱 Configurando webhook do Telegram..."
cd $APP_DIR/AULAS/2-SEMESTRE/LNP
source venv/bin/activate

# Configurar webhook
python telegram_setup.py setup

# 16. Testar webhook
log "🧪 Testando webhook do Telegram..."
python telegram_setup.py test

# 17. Instruções finais
echo ""
echo "🎉 FiapNet instalado com sucesso!"
echo "================================="
echo ""
echo "🌐 URLs de acesso:"
echo "   • Interface Web: http://20.197.224.249/"
echo "   • Chat: http://20.197.224.249/chat"
echo "   • Admin: http://20.197.224.249/admin"
echo "   • Gerenciar Intents: http://20.197.224.249/intent-manager"
echo "   • Gerenciar Entidades: http://20.197.224.249/entity-manager"
echo "   • Health Check: http://20.197.224.249/health"
echo ""
echo "📱 Bot Telegram:"
echo "   • Username: @chat_fiap_bot"
echo "   • Webhook: http://20.197.224.249/telegram"
echo ""
echo "🔧 Comandos úteis:"
echo "   • Status: sudo systemctl status fiapnet"
echo "   • Restart: sudo systemctl restart fiapnet"
echo "   • Logs: sudo journalctl -u fiapnet -f"
echo "   • Testar: curl http://20.197.224.249/health"
echo ""
echo "📁 Arquivos importantes:"
echo "   • Aplicação: $APP_DIR/AULAS/2-SEMESTRE/LNP"
echo "   • Logs: journalctl -u fiapnet -f"
echo "   • Nginx: /var/log/nginx/fiapnet_*.log"
echo ""
echo "✅ Instalação concluída! 🚀"
echo ""
echo "🎯 Próximos passos:"
echo "1. Acesse: http://20.197.224.249/"
echo "2. Teste o bot: @chat_fiap_bot"
echo "3. Configure SSL se necessário"
echo ""
echo "🌐 FiapNet está funcionando! Conectando você ao futuro! 🌐"