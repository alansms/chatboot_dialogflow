# 🌐 FiapNet - Sistema de Suporte de Internet

## 📋 Descrição

Sistema completo de chatbot para suporte de internet que utiliza **Google Cloud Dialogflow** como engine principal de NLP, integrado com **Telegram** e interface web profissional em **Flask**. O sistema oferece funcionalidades completas de atendimento, abertura de chamados, consulta de status e gerenciamento de intents/entidades.

## 🚀 Funcionalidades

### **Interface Web Profissional**
- ✅ **Chat interativo** com interface moderna
- ✅ **Dashboard administrativo** com estatísticas
- ✅ **Gerenciador de Intents** - Criar, editar, visualizar intents
- ✅ **Gerenciador de Entidades** - Gerenciar entidades do Dialogflow
- ✅ **Sistema de status** de chamados
- ✅ **FAQ integrado** com busca

### **Integração Telegram**
- ✅ **Bot Telegram** (@chat_fiap_bot) totalmente funcional
- ✅ **Webhook configurado** para recebimento de mensagens
- ✅ **Processamento automático** via Dialogflow
- ✅ **Respostas personalizadas** para cada canal

### **Sistema Dialogflow**
- ✅ **15 Intents** configuradas para suporte de internet
- ✅ **7 Entidades** personalizadas
- ✅ **5 Fluxos principais** conforme requisitos da atividade
- ✅ **Contextos e parâmetros** configurados
- ✅ **Fallback inteligente** para casos não cobertos

### **Fluxos de Atendimento**
1. **Saudação e Identificação** - Captura nome e telefone
2. **Abertura de Chamados** - Processo completo de abertura
3. **Consulta de Status** - Verificação de chamados existentes
4. **FAQ e Informações** - Planos, preços, horários
5. **Encaminhamento Humano** - Transferência para atendente

## ⚙️ Configuração

### **1. Dependências**

```bash
pip install -r requirements.txt
```

### **2. Configuração do Google Cloud Dialogflow**

#### **Para Desenvolvimento Local:**

1. Crie um projeto no Google Cloud Console
2. Ative a API do Dialogflow
3. Crie uma conta de serviço e baixe o arquivo JSON de credenciais
4. Configure a variável de ambiente:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/suas/credenciais.json"
```

#### **Para Produção (VPS):**

1. Configure as variáveis de ambiente no servidor
2. Coloque o arquivo de credenciais em local seguro
3. Configure as variáveis do Telegram e webhook

### **3. Configuração do Telegram**

1. Crie um bot com @BotFather no Telegram
2. Configure o token:
```bash
export TELEGRAM_TOKEN="seu_token_do_bot"
```

3. Configure o webhook (para produção):
```bash
export WEBHOOK_URL="https://seu-dominio.com/telegram"
```

## 🔧 Como Usar

### **Execução Local:**

```bash
# Iniciar aplicação
python app_web.py

# Acessar interface web
http://localhost:5023

# Gerenciar intents
http://localhost:5023/intent-manager

# Gerenciar entidades
http://localhost:5023/entity-manager
```

### **Configuração do Telegram:**

```bash
# Ver informações do bot
python telegram_setup.py info

# Configurar webhook
python telegram_setup.py setup

# Testar webhook
python telegram_setup.py test
```

### **Deploy em VPS:**

```bash
# Deploy automático (recomendado)
curl -sSL https://raw.githubusercontent.com/alansms/chatboot_dialogflow/master/AULAS/2-SEMESTRE/LNP/deploy_vps.sh | bash

# Ou deploy manual
chmod +x deploy.sh
./deploy.sh
```

## 📁 Estrutura do Projeto

```
├── AULAS/2-SEMESTRE/LNP/        # Projeto principal FiapNet
│   ├── app_web.py               # Aplicação principal Flask
│   ├── requirements.txt         # Dependências Python
│   ├── deploy_vps.sh           # Script de deploy para VPS
│   ├── telegram_setup.py       # Configuração do Telegram
│   ├── test_telegram_local.py  # Testes locais
│   ├── start_with_ngrok.sh     # Script para desenvolvimento
│   ├── config_example.env      # Exemplo de configuração
│   ├── templates/              # Templates HTML
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── chat.html
│   │   ├── status.html
│   │   ├── faq.html
│   │   ├── admin.html
│   │   ├── intent_manager.html
│   │   └── entity_manager.html
│   ├── static/                 # Arquivos estáticos
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── app.js
│   │   └── images/
│   ├── fiap-boot-a239f7750ffc.json  # Credenciais Dialogflow
│   └── documentação/
│       ├── GERENCIADOR_INTENTS.md
│       ├── INTEGRACAO_TELEGRAM.md
│       ├── CONFIGURACAO_RAPIDA.md
│       ├── CONFIGURACAO_FINAL.md
│       ├── DEPLOY_GUIDE.md
│       └── COMANDOS_VPS.md
└── README.md                   # Este arquivo
```

## 🛠️ Arquitetura

### **Fluxo de Processamento:**

1. **Input do usuário** → Interface Web ou Telegram
2. **Dialogflow API** → Detecção de intenção
3. **Processamento de parâmetros** → Extração de dados
4. **Geração de resposta** → Baseada na intenção
5. **Envio da resposta** → Canal de origem

### **APIs Disponíveis:**

- `GET /` - Interface principal
- `GET /chat` - Interface de chat
- `GET /intent-manager` - Gerenciador de intents
- `GET /entity-manager` - Gerenciador de entidades
- `GET /admin` - Dashboard administrativo
- `POST /telegram` - Webhook do Telegram
- `POST /dialogflow` - Webhook do Dialogflow
- `GET /api/intents` - API de intents
- `GET /api/entities` - API de entidades

## 📊 Intents Configuradas

### **Saudação e Identificação:**
- `Saudacao_Identificacao` - Saudação inicial
- `Capturar_Nome` - Captura do nome do cliente
- `Capturar_Telefone` - Captura do telefone

### **Abertura de Chamados:**
- `Abrir_Chamado` - Início do processo
- `Definir_Tipo_Problema` - Tipo do problema
- `Definir_Urgencia` - Nível de urgência
- `Finalizar_Chamado` - Confirmação e fechamento

### **Consulta de Status:**
- `Consultar_Status` - Consulta de chamados
- `Buscar_Chamado` - Busca específica

### **FAQ e Informações:**
- `FAQ_Informacoes` - Informações gerais
- `Horario_Funcionamento` - Horários de atendimento
- `Planos_Precos` - Planos e preços
- `Solucoes_Rapidas` - Soluções rápidas

### **Suporte e Encerramento:**
- `Encaminhar_Humano` - Transferência para atendente
- `Encerramento` - Encerramento de atendimento

## 🏷️ Entidades Configuradas

- `TipoProblema` - Tipos de problemas técnicos
- `UrgenciaChamado` - Níveis de urgência
- `StatusChamado` - Status de chamados
- `PlanoInternet` - Planos de internet

## 🚀 Deploy em VPS

### **Deploy Automático (Recomendado):**

```bash
# 1. Conectar na VPS
ssh root@seu-ip-da-vps

# 2. Executar deploy automático
curl -sSL https://raw.githubusercontent.com/alansms/chatboot_dialogflow/master/AULAS/2-SEMESTRE/LNP/deploy_vps.sh | bash

# 3. Configurar aplicação
cd /home/usuario/fiapnet/AULAS/2-SEMESTRE/LNP
./configure.sh
```

### **Requisitos do Servidor:**
- Ubuntu 20.04+ ou similar
- Python 3.8+
- Nginx
- SSL Certificate (Let's Encrypt)

### **Processo de Deploy Manual:**

1. **Clone o repositório:**
```bash
git clone https://github.com/alansms/chatboot_dialogflow.git
cd chatboot_dialogflow/AULAS/2-SEMESTRE/LNP
```

2. **Execute o script de deploy:**
```bash
chmod +x deploy.sh
./deploy.sh
```

3. **Configure as variáveis de ambiente:**
```bash
export TELEGRAM_TOKEN="seu_token"
export WEBHOOK_URL="https://seu-dominio.com/telegram"
```

4. **Configure o webhook do Telegram:**
```bash
python telegram_setup.py setup
```

## 🔒 Segurança

- Credenciais protegidas via variáveis de ambiente
- Arquivo `.gitignore` configurado
- Validação de entrada e tratamento de erros
- HTTPS obrigatório para produção
- Firewall configurado no deploy

## 📈 Monitoramento

O sistema fornece:

- Health check endpoint (`/health`)
- Estatísticas em tempo real (`/stats`)
- Logs detalhados de todas as operações
- Monitoramento de performance

## 🚨 Troubleshooting

### **Erro de Credenciais:**
```
⚠️ Credenciais do Dialogflow não configuradas
```
**Solução:** Verifique se as credenciais estão configuradas corretamente.

### **Erro de Webhook:**
```
❌ Erro ao configurar webhook
```
**Solução:** Verifique se a URL é acessível publicamente.

### **Erro de Telegram:**
```
❌ TELEGRAM_TOKEN não encontrado
```
**Solução:** Configure a variável de ambiente com o token correto.

## 🎯 Funcionalidades Avançadas

### **Gerenciador de Intents:**
- Criação de novas intents via interface
- Edição de intents existentes
- Importação/exportação de intents
- Visualização de estatísticas

### **Gerenciador de Entidades:**
- Criação de entidades personalizadas
- Configuração de valores e sinônimos
- Categorização automática
- Testes de funcionamento

### **Sistema de Chamados:**
- Abertura automática de chamados
- Numeração sequencial
- Status em tempo real
- Histórico completo

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido para fins educacionais na FIAP.

## 🎉 Status do Projeto

**✅ COMPLETO E FUNCIONAL**

- Interface Web: ✅ Funcionando
- Telegram Bot: ✅ Funcionando (@chat_fiap_bot)
- Dialogflow: ✅ Integrado
- Gerenciador de Intents: ✅ Funcionando
- Gerenciador de Entidades: ✅ Funcionando
- Deploy VPS: ✅ Scripts prontos
- Documentação: ✅ Completa

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

## 📱 Bot Telegram

**@chat_fiap_bot** - Bot totalmente funcional para suporte de internet

### **Comandos do Bot:**
- `/start` - Iniciar atendimento
- `/help` - Ajuda e informações
- `/status` - Consultar status de chamados
- `/suporte` - Falar com atendente humano

---

**Desenvolvido com ❤️ usando Flask + Google Cloud Dialogflow + Telegram**

**FiapNet - Conectando você ao futuro! 🌐**