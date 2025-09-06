#!/bin/bash

# FiapNet - Deploy Rápido para Azure VPS
# Script simplificado para Azure (CentOS/RHEL)

set -e

echo "🚀 FiapNet - Deploy Rápido para Azure"
echo "===================================="

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

# 1. Atualizar sistema (Azure/CentOS)
echo "📦 Atualizando sistema..."
sudo yum update -y

# 2. Instalar dependências
echo "🔧 Instalando dependências..."
sudo yum install -y python3 python3-pip git curl wget

# Instalar nginx
sudo yum install -y epel-release
sudo yum install -y nginx

# Instalar certbot
sudo yum install -y certbot python3-certbot-nginx

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
sudo tee /etc/nginx/conf.d/fiapnet.conf > /dev/null <<EOF
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

# Testar e iniciar Nginx
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx

# 8. Configurar Gunicorn
echo "⚙️ Configurando Gunicorn..."
sudo tee /etc/systemd/system/fiapnet.service > /dev/null <<EOF
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
sudo systemctl enable fiapnet
sudo systemctl start fiapnet

# 10. Configurar firewall
echo "🔥 Configurando firewall..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 11. Obter IP público
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "IP não detectado")

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
sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/conf.d/fiapnet.conf

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
if sudo systemctl is-active --quiet fiapnet; then
    echo "✅ FiapNet: Ativo"
else
    echo "❌ FiapNet: Inativo"
    sudo systemctl status fiapnet
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
echo "- Logs: journalctl -u fiapnet -f"
echo "- Nginx: /var/log/nginx/error.log"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "• Status: sudo systemctl status fiapnet"
echo "• Restart: sudo systemctl restart fiapnet"
echo "• Logs: journalctl -u fiapnet -f"
echo "• Configurar: ./configure.sh"
echo ""
echo "📱 Configure o webhook do Telegram após configurar o domínio!"
echo ""
echo "✅ Deploy concluído! 🚀"
