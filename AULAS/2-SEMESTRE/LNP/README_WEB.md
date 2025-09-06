# 🌐 FiapNet - Suporte de Internet

Sistema completo de chatbot para suporte técnico de internet com interface web profissional, integração com Dialogflow e Telegram.

## 🚀 Características

- **Interface Web Moderna**: Interface responsiva com Bootstrap 5
- **Chat em Tempo Real**: Sistema de chat integrado com Dialogflow
- **Dashboard Administrativo**: Painel de controle com estatísticas e gráficos
- **Integração Multi-Canal**: Web, Telegram e API REST
- **Deploy Automatizado**: Scripts para VPS e ngrok
- **Sistema de Chamados**: Abertura, consulta e acompanhamento de chamados

## 📋 Funcionalidades

### 🎯 Fluxos do Chatbot (5 Obrigatórios)
1. **Saudação e Identificação** - Captura nome e telefone do cliente
2. **Abertura de Chamados** - Fluxo completo para abertura de chamados técnicos
3. **Consulta de Status** - Verificação de status de chamados existentes
4. **FAQ e Informações** - Respostas rápidas sobre planos, horários e soluções
5. **Encaminhamento Humano** - Transferência para atendente quando necessário

### 🔧 Recursos Técnicos
- **15 Intents** personalizadas no Dialogflow
- **4 Entidades** customizadas (TipoProblema, UrgenciaChamado, etc.)
- **Parâmetros Obrigatórios** com prompts de follow-up
- **Fallback Configurado** com recuperação de contexto
- **Contextos** para controle de fluxo conversacional

## 🏗️ Arquitetura

```
FiapNet/
├── app_web.py              # Aplicação Flask principal
├── templates/              # Templates HTML
│   ├── base.html          # Template base
│   ├── index.html         # Página inicial
│   ├── chat.html          # Interface de chat
│   ├── status.html        # Consulta de status
│   ├── faq.html           # FAQ e informações
│   └── admin.html         # Dashboard administrativo
├── static/                # Arquivos estáticos
│   ├── css/style.css      # Estilos customizados
│   └── js/app.js          # JavaScript principal
├── intents_suporte_internet.json  # Intents do Dialogflow
├── entities_suporte_internet.json # Entidades do Dialogflow
├── deploy.sh              # Script de deploy para VPS
├── start_with_ngrok.sh    # Script para ngrok
└── requirements.txt       # Dependências Python
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
```bash
# Python 3.8+
python --version

# Google Cloud Project com Dialogflow habilitado
# Arquivo de credenciais JSON da conta de serviço
```

### 2. Instalação Local
```bash
# Clonar o repositório
git clone <repository-url>
cd fiapnet

# Instalar dependências
pip install -r requirements.txt

# Configurar credenciais do Dialogflow
# Colocar fiap-boot-a239f7750ffc.json no diretório raiz

# Importar intents e entidades
python import_intents.py
python import_entities.py

# Iniciar aplicação
python app_web.py
```

### 3. Deploy em VPS
```bash
# Executar script de deploy
chmod +x deploy.sh
./deploy.sh

# Configurar domínio e SSL
sudo certbot --nginx -d your-domain.com
```

### 4. Desenvolvimento com ngrok
```bash
# Iniciar com ngrok para testes
chmod +x start_with_ngrok.sh
./start_with_ngrok.sh
```

## 🌐 URLs e Endpoints

### Interface Web
- **Página Inicial**: `http://localhost:5008/`
- **Chat**: `http://localhost:5008/chat`
- **Status**: `http://localhost:5008/status`
- **FAQ**: `http://localhost:5008/faq`
- **Admin**: `http://localhost:5008/admin`

### API Endpoints
- **Health Check**: `GET /health`
- **Estatísticas**: `GET /stats`
- **Chat API**: `POST /chat`
- **Listar Chamados**: `GET /chamados`
- **Buscar Chamado**: `GET /chamados/{id}`

### Webhooks
- **Dialogflow**: `POST /dialogflow`
- **Telegram**: `POST /telegram`

## 🔧 Configuração do Dialogflow

### 1. Importar Intents e Entidades
```bash
python import_intents.py
python import_entities.py
```

### 2. Configurar Webhook
- URL: `https://your-domain.com/dialogflow`
- Método: POST
- Ativar para todas as intents

### 3. Configurar Telegram (Opcional)
```bash
# Definir token do bot
export TELEGRAM_TOKEN="your_bot_token"

# Configurar webhook
curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/telegram"}'
```

## 📊 Dashboard Administrativo

O dashboard inclui:
- **Estatísticas em Tempo Real**: Chamados ativos, total, clientes
- **Gráficos Interativos**: Status de chamados, tipos de problema
- **Tabela de Chamados**: Lista com filtros e ações
- **Exportação de Dados**: Relatórios em CSV/JSON

## 🎨 Interface do Usuário

### Design Responsivo
- **Bootstrap 5**: Framework CSS moderno
- **Font Awesome**: Ícones profissionais
- **Animações CSS**: Transições suaves
- **Tema Escuro**: Suporte automático

### Recursos de UX
- **Chat em Tempo Real**: Interface de mensagens moderna
- **Ações Rápidas**: Botões para fluxos comuns
- **Busca Inteligente**: FAQ com filtro em tempo real
- **Feedback Visual**: Indicadores de status e loading

## 🔒 Segurança

- **HTTPS Obrigatório**: SSL/TLS em produção
- **Headers de Segurança**: XSS, CSRF, Clickjacking
- **Validação de Entrada**: Sanitização de dados
- **Rate Limiting**: Proteção contra spam
- **Logs de Auditoria**: Rastreamento de ações

## 📈 Monitoramento

### Logs
- **Aplicação**: `/logs/gunicorn_*.log`
- **Nginx**: `/var/log/nginx/`
- **Systemd**: `journalctl -u fiapnet`

### Métricas
- **Health Check**: `/health`
- **Estatísticas**: `/stats`
- **Performance**: Tempo de resposta, throughput

## 🚀 Deploy em Produção

### VPS (Ubuntu/Debian)
```bash
# Executar script automatizado
./deploy.sh

# Configurações incluídas:
# - Nginx com SSL
# - Gunicorn com múltiplos workers
# - Systemd service
# - Firewall configurado
# - Backup automático
```

### Docker (Opcional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5008
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app_web:app"]
```

## 🧪 Testes

### Testes Manuais
```bash
# Health check
curl http://localhost:5008/health

# Chat API
curl -X POST http://localhost:5008/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Olá"}'

# Estatísticas
curl http://localhost:5008/stats
```

### Testes de Integração
- **Dialogflow**: Testar todas as intents
- **Telegram**: Verificar webhook
- **Interface**: Testar todos os fluxos

## 📝 Logs e Debugging

### Níveis de Log
- **DEBUG**: Desenvolvimento local
- **INFO**: Produção normal
- **WARNING**: Problemas não críticos
- **ERROR**: Erros que precisam atenção

### Comandos Úteis
```bash
# Ver logs da aplicação
sudo journalctl -u fiapnet -f

# Ver logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar serviços
sudo systemctl restart fiapnet nginx

# Status dos serviços
sudo systemctl status fiapnet nginx
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

- **Email**: suporte@fiapnet.com.br
- **Telefone**: 0800-123-4567
- **Documentação**: [Wiki do Projeto](link-para-wiki)

---

**FiapNet - Conectando você ao futuro! 🌐**
