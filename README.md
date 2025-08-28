# 🍔 ChatBot Hamburgueria - Integração Dialogflow + Streamlit

## 📋 Descrição

Este projeto implementa um chatbot para hamburgueria que utiliza **Google Cloud Dialogflow** como engine principal de NLP, com fallback para processamento local. O bot é executado no Streamlit e oferece funcionalidades completas de atendimento, pedidos e gerenciamento de cardápio.

## 🚀 Funcionalidades

- **Integração com Dialogflow API** para processamento de linguagem natural
- **Fallback local** quando Dialogflow não está disponível
- **Gerenciamento de pedidos** com carrinho de compras
- **Upload de cardápio** via CSV/Excel
- **Interface web responsiva** com Streamlit
- **Sistema de contexto** para conversas inteligentes

## ⚙️ Configuração

### 1. Dependências

```bash
pip install -r requirements.txt
```

### 2. Configuração do Google Cloud Dialogflow

#### Para Desenvolvimento Local:

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a API do Dialogflow
3. Crie uma conta de serviço e baixe o arquivo JSON de credenciais
4. Configure a variável de ambiente:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/suas/credenciais.json"
   ```

#### Para Streamlit Cloud:

1. No painel do Streamlit Cloud, vá em **Settings > Secrets**
2. Adicione as seguintes chaves:
   ```toml
   DIALOGFLOW_PROJECT_ID = "seu-project-id"
   GOOGLE_APPLICATION_CREDENTIALS_JSON = '''
   {
     "type": "service_account",
     "project_id": "seu-project-id",
     "private_key_id": "...",
     "private_key": "...",
     "client_email": "...",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token"
   }
   '''
   ```

### 3. Configuração do Dialogflow

Crie as seguintes intents no seu agent Dialogflow:

#### **Intent: BoasVindas**
- **Training Phrases**: "olá", "oi", "bom dia", "boa tarde"
- **Response**: "Olá! Bem-vindo à nossa hamburgueria! Como posso ajudar?"

#### **Intent: Cardapio**
- **Training Phrases**: "cardápio", "menu", "o que vocês têm"
- **Response**: "Temos hambúrgueres artesanais, bebidas e porções!"

#### **Intent: FazerPedido**
- **Training Phrases**: "quero um hambúrguer", "gostaria de pedir"
- **Parameters**: 
  - `item` (entity: @sys.any)
  - `categoria` (entity: @sys.any)

#### **Intent: Confirmar**
- **Training Phrases**: "sim", "confirmar", "ok"

#### **Intent: Negar**
- **Training Phrases**: "não", "cancelar"

#### **Intent: Despedida**
- **Training Phrases**: "tchau", "obrigado", "até mais"

## 🔧 Como Usar

### Execução Local:
```bash
streamlit run bot_hamburgueria.py
```

### Deploy no Streamlit Cloud:
1. Conecte seu repositório GitHub
2. Configure as secrets (credenciais)
3. Deploy automático

## 📁 Estrutura do Projeto

```
├── bot_hamburgueria.py          # Aplicação principal
├── requirements.txt             # Dependências Python
├── exemplo_dialogflow_api.py    # Exemplo de implementação
├── .gitignore                   # Arquivos ignorados pelo Git
├── README.md                    # Documentação
└── AULAS/2-SEMESTRE/LNP/        # Arquivos do projeto LNP
    ├── entities_hamburgueria.json
    ├── intents_hamburgueria.json
    └── ...
```

## 🛠️ Arquitetura

### Fluxo de Processamento:

1. **Input do usuário** → Streamlit
2. **Dialogflow API** → Detecção de intenção (confiança > 60%)
3. **Processamento local** → Fallback se Dialogflow falhar
4. **Resposta personalizada** → Baseada na intenção detectada
5. **Atualização do contexto** → Para conversas contínuas

### Classes Principais:

- **`DialogflowBot`**: Gerencia comunicação com API
- **`processar_mensagem()`**: Coordena Dialogflow + fallback local
- **Funções auxiliares**: Processamento específico por intenção

## 📊 Monitoramento

O sistema fornece informações em tempo real:

- Status da conexão com Dialogflow
- Confiança das detecções de intenção
- Fallback para processamento local
- Logs de erro para debugging

## 🔒 Segurança

- Credenciais protegidas via Streamlit Secrets
- Arquivo `.gitignore` configurado para evitar vazamentos
- Validação de entrada e tratamento de erros

## 🚨 Troubleshooting

### Erro de Credenciais:
```
⚠️ Credenciais do Dialogflow não configuradas. Usando processamento local.
```
**Solução**: Verifique se as credenciais estão configuradas corretamente.

### Baixa Confiança:
Se Dialogflow retorna confiança < 60%, o sistema usa processamento local automaticamente.

### Erro de API:
```
Erro na comunicação com Dialogflow: [detalhes]
```
**Solução**: Verifique conectividade e cotas da API.

## 📈 Melhorias Futuras

- [ ] Webhook para fulfillment personalizado
- [ ] Integração com sistemas de pagamento
- [ ] Analytics de conversação
- [ ] Suporte multilíngue
- [ ] Interface de administração avançada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido para fins educacionais na FIAP.

---

**Desenvolvido com ❤️ usando Streamlit + Google Cloud Dialogflow**
