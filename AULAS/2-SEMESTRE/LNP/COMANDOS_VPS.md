# 🖥️ Comandos para VPS - FiapNet

## 🚀 Deploy Rápido

### **1. Conectar na VPS:**
```bash
ssh root@seu-ip-da-vps
# ou
ssh usuario@seu-ip-da-vps
```

### **2. Executar deploy automático:**
```bash
# Baixar e executar o script de deploy
curl -sSL https://raw.githubusercontent.com/alansms/chatboot_dialogflow/master/AULAS/2-SEMESTRE/LNP/deploy_vps.sh | bash
```

### **3. Configurar aplicação:**
```bash
cd /home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP
./configure.sh
```

## 🔧 Comandos de Gerenciamento

### **Status dos Serviços:**
```bash
# Verificar status do FiapNet
sudo systemctl status fiapnet

# Verificar status do Nginx
sudo systemctl status nginx

# Verificar status de ambos
sudo systemctl status fiapnet nginx
```

### **Reiniciar Serviços:**
```bash
# Reiniciar FiapNet
sudo systemctl restart fiapnet

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar ambos
sudo systemctl restart fiapnet nginx
```

### **Parar/Iniciar Serviços:**
```bash
# Parar FiapNet
sudo systemctl stop fiapnet

# Iniciar FiapNet
sudo systemctl start fiapnet

# Habilitar na inicialização
sudo systemctl enable fiapnet

# Desabilitar da inicialização
sudo systemctl disable fiapnet
```

## 📊 Monitoramento e Logs

### **Logs da Aplicação:**
```bash
# Ver logs em tempo real
sudo journalctl -u fiapnet -f

# Ver logs das últimas 100 linhas
sudo journalctl -u fiapnet -n 100

# Ver logs de hoje
sudo journalctl -u fiapnet --since today

# Ver logs de um período específico
sudo journalctl -u fiapnet --since "2024-01-01" --until "2024-01-02"
```

### **Logs do Nginx:**
```bash
# Logs de erro
sudo tail -f /var/log/nginx/error.log

# Logs de acesso
sudo tail -f /var/log/nginx/access.log

# Logs específicos do FiapNet
sudo tail -f /var/log/nginx/fiapnet_error.log
sudo tail -f /var/log/nginx/fiapnet_access.log
```

### **Verificar Portas:**
```bash
# Verificar se a aplicação está rodando na porta 5023
sudo netstat -tlnp | grep :5023

# Verificar portas do Nginx
sudo netstat -tlnp | grep nginx

# Verificar todas as portas abertas
sudo netstat -tlnp
```

## 🌐 Testes de Conectividade

### **Health Check:**
```bash
# Testar localmente
curl -s http://localhost:5023/health

# Testar via IP público
curl -s http://seu-ip-publico/health

# Testar via domínio
curl -s https://seu-dominio.com/health
```

### **Testar Endpoints:**
```bash
# Página principal
curl -s http://localhost:5023/

# Chat
curl -s http://localhost:5023/chat

# Admin
curl -s http://localhost:5023/admin

# API de intents
curl -s http://localhost:5023/api/intents
```

## 🔒 SSL e Certificados

### **Verificar Certificados:**
```bash
# Listar certificados
sudo certbot certificates

# Verificar expiração
sudo certbot certificates | grep -A 2 "Certificate Name"
```

### **Renovar Certificados:**
```bash
# Renovar todos os certificados
sudo certbot renew

# Renovar certificado específico
sudo certbot renew --cert-name seu-dominio.com

# Testar renovação (dry run)
sudo certbot renew --dry-run
```

### **Configurar Renovação Automática:**
```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar esta linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔥 Firewall

### **Configurar UFW:**
```bash
# Ver status
sudo ufw status

# Habilitar firewall
sudo ufw enable

# Permitir portas
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Bloquear porta
sudo ufw deny 8080/tcp

# Resetar firewall
sudo ufw --force reset
```

## 📱 Configuração do Telegram

### **Configurar Webhook:**
```bash
# Usar script de configuração
cd /home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP
source venv/bin/activate
python telegram_setup.py setup

# Ou configurar manualmente
export TELEGRAM_TOKEN="seu_token"
export WEBHOOK_URL="https://seu-dominio.com/telegram"
python telegram_setup.py setup
```

### **Testar Bot:**
```bash
# Ver informações do bot
python telegram_setup.py info

# Testar webhook
python telegram_setup.py test
```

## 🔄 Atualizações

### **Atualizar Sistema:**
```bash
# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Atualizar apenas segurança
sudo apt upgrade -y --only-upgrade
```

### **Atualizar Aplicação:**
```bash
# Ir para diretório da aplicação
cd /home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP

# Fazer backup
cp -r . ../backup-$(date +%Y%m%d)

# Atualizar código
git pull origin master

# Reiniciar aplicação
sudo systemctl restart fiapnet
```

## 🗂️ Gerenciamento de Arquivos

### **Estrutura de Diretórios:**
```bash
# Diretório principal
/home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP/

# Arquivos importantes
.env                    # Configurações
app_web.py             # Aplicação principal
requirements.txt       # Dependências
deploy.sh             # Script de deploy
configure.sh          # Script de configuração

# Diretórios
templates/            # Templates HTML
static/              # Arquivos estáticos
logs/                # Logs da aplicação
venv/                # Ambiente virtual Python
```

### **Backup:**
```bash
# Backup completo
tar -czf fiapnet-backup-$(date +%Y%m%d).tar.gz \
    --exclude=venv \
    --exclude=logs \
    --exclude=__pycache__ \
    .

# Restaurar backup
tar -xzf fiapnet-backup-20240101.tar.gz
```

## 🚨 Troubleshooting

### **Aplicação não inicia:**
```bash
# Verificar logs
sudo journalctl -u fiapnet -f

# Verificar configuração
sudo -u usuario /home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP/venv/bin/python -c "import app_web"

# Verificar dependências
sudo -u usuario /home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP/venv/bin/pip list
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
# Verificar certificados
sudo certbot certificates

# Renovar certificado
sudo certbot renew

# Verificar configuração do Nginx
sudo nginx -t
```

## 📊 Monitoramento de Recursos

### **Uso de CPU e Memória:**
```bash
# Ver uso em tempo real
htop

# Ver uso de memória
free -h

# Ver uso de disco
df -h

# Ver processos
ps aux | grep fiapnet
```

### **Logs de Sistema:**
```bash
# Logs do sistema
sudo journalctl -f

# Logs de boot
sudo journalctl -b

# Logs de kernel
sudo dmesg | tail
```

## 🎯 Comandos Úteis

### **Informações do Sistema:**
```bash
# Versão do sistema
lsb_release -a

# Versão do Python
python3 --version

# Versão do Nginx
nginx -v

# Informações da CPU
lscpu

# Informações da memória
free -h
```

### **Rede:**
```bash
# IP público
curl -s ifconfig.me

# IP local
hostname -I

# Testar conectividade
ping google.com

# Ver rotas
ip route
```

---

**💡 Dica:** Salve estes comandos em um arquivo para referência rápida!

**🔧 Suporte:** Em caso de problemas, verifique sempre os logs primeiro!
