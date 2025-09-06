#!/bin/bash

# FiapNet - Deploy Universal para VPS (Ubuntu/Debian/CentOS/RHEL/Azure)
# Detecta automaticamente a distribuição e usa o gerenciador de pacotes correto

set -e

echo "🚀 FiapNet - Deploy Universal para VPS"
echo "====================================="

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

# Detectar distribuição Linux
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
        VERSION=$(cat /etc/redhat-release | grep -oE '[0-9]+\.[0-9]+' | head -1)
    else
        DISTRO="unknown"
        VERSION="unknown"
    fi
    
    log "Distribuição detectada: $DISTRO $VERSION"
}

# Instalar dependências baseado na distribuição
install_dependencies() {
    log "Instalando dependências para $DISTRO..."
    
    case $DISTRO in
        ubuntu|debian)
            sudo apt update && sudo apt upgrade -y
            sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl
            ;;
        centos|rhel|fedora|rocky|almalinux)
            if command -v dnf &> /dev/null; then
                sudo dnf update -y
                sudo dnf install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl
            elif command -v yum &> /dev/null; then
                sudo yum update -y
                sudo yum install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl
            fi
            ;;
        *)
            error "Distribuição não suportada: $DISTRO"
            echo "💡 Distribuições suportadas: Ubuntu, Debian, CentOS, RHEL, Fedora, Rocky Linux, AlmaLinux"
            exit 1
            ;;
    esac
    
    success "Dependências instaladas com sucesso"
}

# Configurações
APP_NAME="fiapnet"
APP_DIR="/home/$USER/$APP_NAME"
REPO_URL="https://github.com/alansms/chatboot_dialogflow.git"

echo "📋 Configurações:"
echo "   Usuário: $USER"
echo "   Diretório: $APP_DIR"
echo "   Repositório: $REPO_URL"
echo ""

# 1. Detectar distribuição
detect_distro

# 2. Instalar dependências
install_dependencies

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
log "🌐 Configurando Nginx..."

# Detectar localização do nginx baseado na distribuição
case $DISTRO in
    ubuntu|debian)
        NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
        NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
        ;;
    centos|rhel|fedora|rocky|almalinux)
        NGINX_SITES_AVAILABLE="/etc/nginx/conf.d"
        NGINX_SITES_ENABLED="/etc/nginx/conf.d"
        ;;
esac

sudo tee $NGINX_SITES_AVAILABLE/$APP_NAME.conf > /dev/null <<EOF
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

# Para Ubuntu/Debian, criar link simbólico
if [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
    sudo ln -sf $NGINX_SITES_AVAILABLE/$APP_NAME.conf $NGINX_SITES_ENABLED/
    sudo rm -f $NGINX_SITES_ENABLED/default
fi

# Testar configuração do Nginx
sudo nginx -t
sudo systemctl restart nginx

# 8. Configurar Gunicorn
log "⚙️ Configurando Gunicorn..."

# Detectar localização do systemd baseado na distribuição
case $DISTRO in
    ubuntu|debian)
        SYSTEMD_DIR="/etc/systemd/system"
        ;;
    centos|rhel|fedora|rocky|almalinux)
        SYSTEMD_DIR="/etc/systemd/system"
        ;;
esac

sudo tee $SYSTEMD_DIR/$APP_NAME.service > /dev/null <<EOF
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
log "🚀 Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl start $APP_NAME

# 10. Configurar firewall
log "🔥 Configurando firewall..."

# Detectar e configurar firewall baseado na distribuição
if command -v ufw &> /dev/null; then
    # Ubuntu/Debian com UFW
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL/Fedora com firewalld
    sudo systemctl enable firewalld
    sudo systemctl start firewalld
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
elif command -v iptables &> /dev/null; then
    # Fallback para iptables
    sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    sudo iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
fi

# 11. Obter IP público
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "IP não detectado")

# 12. Criar script de configuração
log "📋 Criando script de configuração..."
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
sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/conf.d/fiapnet.conf 2>/dev/null || \
sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/fiapnet.conf 2>/dev/null

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
log "🔍 Verificando status dos serviços..."
if sudo systemctl is-active --quiet $APP_NAME; then
    success "FiapNet: Ativo"
else
    error "FiapNet: Inativo"
    sudo systemctl status $APP_NAME
fi

if sudo systemctl is-active --quiet nginx; then
    success "Nginx: Ativo"
else
    error "Nginx: Inativo"
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
echo "- Nginx: /var/log/nginx/fiapnet_*.log"
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
