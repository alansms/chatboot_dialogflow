# Plataforma RPA-BOT Hamburgueria

## Descrição Geral

Este projeto é uma plataforma completa de chatbot para hamburgueria, integrando Dialogflow, interface web (Streamlit), integração com Telegram e automação de setup do agente Dialogflow (intents e entidades). O sistema permite upload e gerenciamento dinâmico de cardápio, atendimento automatizado via chat e múltiplos canais, além de scripts para facilitar a configuração do agente conversacional.

## Funcionalidades

- **Upload e Gerenciamento de Cardápio**: Upload de arquivos CSV/XLSX com o cardápio, visualização e persistência automática.
- **Chatbot Inteligente**: Atendimento automatizado via Dialogflow, com intents customizadas para pedidos, consulta de cardápio, preços, detalhes, opções vegetarianas, confirmação de pedidos e mais.
- **Interface Web (Streamlit)**: Plataforma centralizada para upload/administração, chat com o bot e visualização do cardápio.
- **Webhook Telegram**: Integração direta com Telegram, permitindo atendimento via app de mensagens.
- **Entidades Dinâmicas**: Atualização automática das entidades do Dialogflow conforme o cardápio carregado.
- **Scripts de Automação**: Scripts Python para importar intents e entidades customizadas para o Dialogflow.

## Estrutura dos Principais Arquivos

- `app.py`: Backend Flask para upload, visualização e manipulação do cardápio, integração com Dialogflow (webhook fulfillment), gerenciamento de carrinho de compras por sessão.
- `streamlit_app.py`: Interface web em Streamlit para chat, upload/administração e visualização do cardápio.
- `webhook_telegram.py`: Webhook Flask para integração Telegram → Dialogflow → Telegram.
- `create_intent.py`, `import_entities.py`, `import_intents.py`, `import_param_intent.py`: Scripts para automação do setup do agente Dialogflow.
- `entities_hamburgueria.json`, `intents_hamburgueria.json`, `intent_PedidoDetalhado.json`: Modelos de entidades e intents customizadas para importação no Dialogflow.
- `cardapio_teste.csv`: Exemplo de cardápio para testes.

## Como Executar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Inicie o backend Flask

```bash
python app.py
```

### 3. Inicie a interface Streamlit

```bash
streamlit run streamlit_app.py
```

Acesse a interface web em `http://localhost:8501`.

### 4. (Opcional) Inicie o webhook do Telegram

```bash
python webhook_telegram.py
```

### 5. (Opcional) Importe intents e entidades para o Dialogflow

```bash
python import_entities.py
python import_intents.py
python import_param_intent.py
```

## Formato do Cardápio (CSV/XLSX)

O arquivo de cardápio deve conter as colunas:
- `categoria` (ex: Burgers, Bebidas, Porções)
- `item` (nome do produto)
- `descricao` (descrição do item)
- `preco` (valor numérico)
- `vegetariano` (sim/não, opcional)
- `sinonimos` (separados por |, opcional)

Exemplo:

```
categoria,item,descricao,preco,vegetariano,sinonimos
Burgers,Cheeseburger,Hambúrguer com queijo,18.90,nao,cheese|x-burguer
Burgers,Vegetariano,Hambúrguer de grão de bico,20.00,sim,veg|veggie
Bebidas,Coca-Cola,Refrigerante lata,6.00,nao,coca|coca-cola
Porções,Batata Frita,Batata frita crocante,12.00,sim,batata|fritas
```

## Segurança
- **NUNCA** compartilhe ou versiona o arquivo de credenciais do Google (Service Account) em repositórios públicos.
- O token do Telegram deve ser mantido em segredo.

## Observações
- O carrinho de compras é mantido em memória por sessão (não persistente).
- O sistema pode ser facilmente expandido para outros canais (WhatsApp, Messenger, etc.).
- Scripts de importação facilitam a automação do setup do Dialogflow.

## Licença
Projeto acadêmico FIAP. Uso livre para fins educacionais.

