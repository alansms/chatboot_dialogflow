import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# CONFIGURAÇÕES
CREDENTIALS_FILE = "fiap-boot-a239f7750ffc.json"
PROJECT_ID = "fiap-boot"
LANG = "pt-BR"

# Inicializa a aplicação Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Sistema de Suporte de Internet
CHAMADOS_DB: dict[str, dict] = {}
CLIENTES_DB: dict[str, dict] = {}
CONTADOR_CHAMADOS = 1000

# Autenticação com a API Dialogflow
SCOPES = ["https://www.googleapis.com/auth/dialogflow"]
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
GSESSION = AuthorizedSession(credentials)

def detect_intent(text: str, session_id: str = "default") -> dict:
    """Detecta a intenção do usuário usando Dialogflow."""
    url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/sessions/{session_id}:detectIntent"
    
    payload = {
        "queryInput": {
            "text": {
                "text": text,
                "languageCode": LANG
            }
        }
    }
    
    try:
        response = GSESSION.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            intent = result.get("queryResult", {}).get("intent", {}).get("displayName", "Default Fallback Intent")
            params = result.get("queryResult", {}).get("parameters", {})
            params["queryText"] = text
            
            print(f"[DEBUG] detectIntent: texto='{text}' intent='{intent}' params={params}")
            return {"intent": intent, "params": params}
        else:
            print(f"[ERROR] Dialogflow API error: {response.status_code} - {response.text}")
            return {"intent": "Default Fallback Intent", "params": {"queryText": text}}
    except Exception as e:
        print(f"[ERROR] Exception in detect_intent: {e}")
        return {"intent": "Default Fallback Intent", "params": {"queryText": text}}

def handle_intent(intent_name: str, params: dict, session_id: str) -> str:
    """Manipula intents do sistema de suporte de internet."""
    user_text = params.get("queryText", "").lower().strip()
    
    if intent_name == "Saudacao_Identificacao":
        return "Olá! Bem-vindo ao suporte da FiapNet! 🌐\n\nSou seu assistente virtual e posso ajudar com:\n• Abertura de chamados técnicos\n• Consulta de status de chamados\n• Informações sobre planos e serviços\n• Soluções rápidas para problemas comuns\n\nPara começar, preciso do seu nome completo:"
    
    elif intent_name == "Capturar_Nome":
        nome = params.get("nome_cliente", "Cliente")
        return f"Perfeito, {nome}! Agora preciso do seu número de telefone para localizar sua conta:"
    
    elif intent_name == "Capturar_Telefone":
        telefone = params.get("telefone_cliente", "")
        nome = params.get("nome_cliente", "Cliente")
        return f"Obrigado, {nome}! Localizei sua conta. Como posso ajudá-lo hoje?\n\n🔧 Abrir chamado técnico\n📊 Consultar status de chamado\n❓ Informações e FAQ\n👤 Falar com atendente humano"
    
    elif intent_name == "Abrir_Chamado":
        return "Vou abrir um chamado técnico para você. Qual o tipo de problema que está enfrentando?\n\n• Sem internet\n• Internet lenta\n• Problema no WiFi\n• Equipamento com defeito\n• Nova instalação"
    
    elif intent_name == "Definir_Tipo_Problema":
        tipo = params.get("tipo_problema", "problema técnico")
        return f"Entendi, problema com {tipo}. Agora preciso saber qual a urgência deste chamado:\n\n• Baixa (não urgente)\n• Média (normal)\n• Alta (urgente)\n• Crítica (emergência)"
    
    elif intent_name == "Definir_Urgencia":
        urgencia = params.get("urgencia_chamado", "média")
        return "Por favor, descreva detalhadamente o problema que está enfrentando:"
    
    elif intent_name == "Finalizar_Chamado":
        global CONTADOR_CHAMADOS
        CONTADOR_CHAMADOS += 1
        chamado_id = f"CH{CONTADOR_CHAMADOS}"
        
        # Simular dados do chamado
        chamado = {
            "id": chamado_id,
            "nome": params.get("nome_cliente", "Cliente"),
            "telefone": params.get("telefone_cliente", ""),
            "problema": params.get("tipo_problema", "Problema técnico"),
            "urgencia": params.get("urgencia_chamado", "Média"),
            "descricao": params.get("descricao_problema", "Problema reportado"),
            "status": "Aberto",
            "data_abertura": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "previsao": (datetime.now() + timedelta(hours=8)).strftime("%d/%m/%Y %H:%M")
        }
        
        CHAMADOS_DB[chamado_id] = chamado
        
        return f"✅ Chamado aberto com sucesso!\n\n📋 **RESUMO DO CHAMADO**\n🎫 Número: #{chamado_id}\n👤 Cliente: {chamado['nome']}\n📱 Telefone: {chamado['telefone']}\n🔧 Problema: {chamado['problema']}\n⚡ Urgência: {chamado['urgencia']}\n📝 Descrição: {chamado['descricao']}\n\n⏰ **PRAZO DE ATENDIMENTO**\n• Crítica: até 4 horas\n• Alta: até 8 horas\n• Média: até 24 horas\n• Baixa: até 48 horas\n\nVocê receberá atualizações por SMS. Posso ajudar com mais alguma coisa?"
    
    elif intent_name == "Consultar_Status":
        return "Vou consultar o status do seu chamado. Informe o número do chamado (ex: #CH12345) ou posso buscar pelos seus dados:"
    
    elif intent_name == "Buscar_Chamado":
        # Simular busca de chamado
        return "📊 **STATUS DO CHAMADO #CH12345**\n\n🔄 Status: EM ANDAMENTO\n👤 Cliente: Cliente Exemplo\n🔧 Problema: Sem internet\n⚡ Urgência: Alta\n📅 Aberto em: 15/01/2024 14:30\n🕒 Última atualização: 15/01/2024 16:45\n\n📋 **HISTÓRICO:**\n• 14:30 - Chamado aberto\n• 15:20 - Técnico designado\n• 16:45 - Técnico a caminho\n\n⏰ **PREVISÃO:** Resolução até 22:30 hoje\n📱 **TÉCNICO:** João - (11) 99999-8888\n\nPosso ajudar com mais alguma coisa?"
    
    elif intent_name == "FAQ_Informacoes":
        return "📚 **INFORMAÇÕES E FAQ**\n\nSobre o que você gostaria de saber?\n\n🕒 Horário de atendimento\n💰 Planos e preços\n🔧 Soluções rápidas\n📋 Políticas da empresa\n📞 Contatos importantes"
    
    elif intent_name == "Horario_Funcionamento":
        return "🕒 **HORÁRIO DE ATENDIMENTO**\n\n**Suporte Técnico:**\n• Segunda a Sexta: 8h às 22h\n• Sábado: 8h às 18h\n• Domingo: 10h às 16h\n\n**Emergências (sem internet):**\n• 24 horas por dia, todos os dias\n\n**Comercial:**\n• Segunda a Sexta: 9h às 18h\n• Sábado: 9h às 13h\n\n📞 Central: 0800-123-4567"
    
    elif intent_name == "Planos_Precos":
        return "💰 **PLANOS FIAPNET**\n\n🥉 **BÁSICO - 50MB** - R$ 59,90/mês\n• Download: 50 Mbps | Upload: 25 Mbps\n• Ideal para: 2-3 pessoas\n\n🥈 **INTERMEDIÁRIO - 100MB** - R$ 79,90/mês\n• Download: 100 Mbps | Upload: 50 Mbps\n• Ideal para: 4-5 pessoas\n\n🥇 **AVANÇADO - 200MB** - R$ 99,90/mês\n• Download: 200 Mbps | Upload: 100 Mbps\n• Ideal para: 6-8 pessoas\n\n💎 **PREMIUM - 500MB** - R$ 149,90/mês\n• Download: 500 Mbps | Upload: 250 Mbps\n• Ideal para: 10+ pessoas\n\n🚀 **ULTRA - 1GB** - R$ 199,90/mês\n• Download: 1 Gbps | Upload: 500 Mbps\n• Ideal para: empresas\n\n✨ Todos incluem WiFi grátis!"
    
    elif intent_name == "Solucoes_Rapidas":
        return "🔧 **SOLUÇÕES RÁPIDAS**\n\n**Internet Lenta:**\n1. Reinicie o modem (30 segundos)\n2. Teste com cabo ethernet\n3. Verifique quantos dispositivos conectados\n\n**Sem Internet:**\n1. Verifique cabos conectados\n2. Reinicie modem e roteador\n3. Aguarde 2 minutos para sincronizar\n\n**WiFi Fraco:**\n1. Aproxime-se do roteador\n2. Reinicie o WiFi do dispositivo\n3. Esqueça e reconecte à rede\n\n**Modem com Problema:**\n🔴 Luz vermelha = Sem sinal\n🟡 Luz amarela = Sincronizando\n🟢 Luz verde = Funcionando\n\n❌ Se não resolver, abra um chamado!"
    
    elif intent_name == "Encaminhar_Humano":
        nome = params.get("nome_cliente", "Cliente")
        telefone = params.get("telefone_cliente", "")
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        return f"👤 **TRANSFERINDO PARA ATENDENTE HUMANO**\n\nEntendi que precisa de atendimento personalizado. Vou transferir você para nossa equipe:\n\n⏳ Tempo estimado de espera: 3-5 minutos\n📞 Você também pode ligar: 0800-123-4567\n💬 Ou usar nosso chat no site: www.fiapnet.com.br\n\n📋 **RESUMO PARA O ATENDENTE:**\n👤 Cliente: {nome}\n📱 Telefone: {telefone}\n🕒 Atendimento iniciado às: {timestamp}\n\n🔄 Conectando... Aguarde um momento!"
    
    elif intent_name == "Encerramento":
        nome = params.get("nome_cliente", "Cliente")
        duracao = "5 minutos"  # Simular duração
        servicos = "Consulta de informações"
        return f"😊 **ATENDIMENTO FINALIZADO**\n\n📋 **RESUMO DO SEU ATENDIMENTO:**\n👤 Cliente: {nome}\n🕒 Duração: {duracao}\n✅ Serviços utilizados: {servicos}\n\n⭐ **AVALIE NOSSO ATENDIMENTO:**\nEnviaremos uma pesquisa por SMS em alguns minutos.\n\n📞 **PRECISA DE MAIS AJUDA?**\n• Central 24h: 0800-123-4567\n• Site: www.fiapnet.com.br\n• App FiapNet na loja de apps\n\n🌐 **FIAPNET - CONECTANDO VOCÊ AO FUTURO!**\n\nObrigado por escolher a FiapNet! 🚀"
    
    else:
        return "Desculpe, não entendi. Posso ajudar com abertura de chamados, consulta de status ou informações gerais. O que precisa?"

# ==================== FUNÇÕES AUXILIARES ====================

def _get_intent_category(display_name):
    """Determina a categoria de uma intent baseada no nome."""
    name_lower = display_name.lower()
    
    if any(word in name_lower for word in ['saudacao', 'ola', 'bom dia', 'boa tarde']):
        return 'saudacao'
    elif any(word in name_lower for word in ['chamado', 'abrir', 'problema']):
        return 'chamado'
    elif any(word in name_lower for word in ['consulta', 'status', 'buscar']):
        return 'consulta'
    elif any(word in name_lower for word in ['faq', 'informacao', 'plano', 'preco']):
        return 'faq'
    elif any(word in name_lower for word in ['suporte', 'humano', 'atendente']):
        return 'suporte'
    else:
        return 'outros'

def _get_intent_description(display_name):
    """Gera uma descrição para uma intent baseada no nome."""
    name_lower = display_name.lower()
    
    if 'saudacao' in name_lower:
        return 'Intent para saudação e identificação do cliente'
    elif 'chamado' in name_lower:
        return 'Intent para abertura de chamados técnicos'
    elif 'consulta' in name_lower or 'status' in name_lower:
        return 'Intent para consulta de status de chamados'
    elif 'faq' in name_lower or 'informacao' in name_lower:
        return 'Intent para informações e FAQ'
    elif 'suporte' in name_lower or 'humano' in name_lower:
        return 'Intent para encaminhamento para atendente humano'
    else:
        return 'Intent personalizada'

def _get_entity_category(display_name):
    """Determina a categoria de uma entidade baseada no nome."""
    name_lower = display_name.lower()
    
    if any(word in name_lower for word in ['problema', 'tipo']):
        return 'problema'
    elif any(word in name_lower for word in ['urgencia', 'prioridade']):
        return 'urgencia'
    elif any(word in name_lower for word in ['plano', 'internet']):
        return 'plano'
    elif any(word in name_lower for word in ['status', 'situacao']):
        return 'status'
    else:
        return 'outros'

def _get_entity_description(display_name):
    """Gera uma descrição para uma entidade baseada no nome."""
    name_lower = display_name.lower()
    
    if 'problema' in name_lower:
        return 'Entidade para tipos de problemas técnicos'
    elif 'urgencia' in name_lower:
        return 'Entidade para níveis de urgência de chamados'
    elif 'plano' in name_lower:
        return 'Entidade para planos de internet'
    elif 'status' in name_lower:
        return 'Entidade para status de chamados'
    else:
        return 'Entidade personalizada'

def _build_training_phrases(phrases):
    """Constrói as frases de treinamento para uma intent."""
    training_phrases = []
    
    for phrase in phrases:
        if phrase.strip():
            training_phrases.append({
                "parts": [{"text": phrase.strip()}],
                "type": "EXAMPLE"
            })
    
    return training_phrases

def _build_parameters(params):
    """Constrói os parâmetros para uma intent."""
    parameters = []
    
    for param in params:
        if param.get("name") and param.get("entityType"):
            parameter = {
                "name": param["name"],
                "displayName": param["name"],
                "entityTypeDisplayName": param["entityType"],
                "mandatory": param.get("required", False),
                "isList": param.get("isList", False)
            }
            parameters.append(parameter)
    
    return parameters

def _build_messages(response_text):
    """Constrói as mensagens de resposta para uma intent."""
    if not response_text.strip():
        return []
    
    return [{
        "text": {
            "text": [response_text.strip()]
        }
    }]

def _build_entity_values(values):
    """Constrói os valores para uma entidade."""
    entity_values = []
    
    for value in values:
        if value.get("value"):
            entity_value = {
                "value": value["value"],
                "synonyms": []
            }
            
            # Adicionar sinônimos se fornecidos
            if value.get("synonyms"):
                synonyms = [s.strip() for s in value["synonyms"].split(",") if s.strip()]
                entity_value["synonyms"] = synonyms
            
            entity_values.append(entity_value)
    
    return entity_values

# ==================== ROTAS WEB ====================

@app.route("/")
def index():
    """Página inicial."""
    return render_template("index.html")

@app.route("/chat")
def chat():
    """Página de chat."""
    return render_template("chat.html")

@app.route("/status")
def status():
    """Página de status de chamados."""
    return render_template("status.html")

@app.route("/faq")
def faq():
    """Página de FAQ."""
    return render_template("faq.html")

@app.route("/admin")
def admin():
    """Página de administração."""
    return render_template("admin.html")

@app.route("/intent-manager")
def intent_manager():
    """Página de gerenciamento de intents."""
    return render_template("intent_manager.html")

@app.route("/entity-manager")
def entity_manager():
    """Página de gerenciamento de entidades."""
    return render_template("entity_manager.html")

# ==================== API ENDPOINTS ====================

@app.route("/stats")
def stats():
    """Retorna estatísticas do sistema."""
    chamados_ativos = len([c for c in CHAMADOS_DB.values() if c["status"] in ["Aberto", "Em Andamento"]])
    clientes_cadastrados = len(CLIENTES_DB)
    total_chamados = len(CHAMADOS_DB)
    
    return jsonify({
        "sistema": "FiapNet - Suporte de Internet",
        "chamados_ativos": chamados_ativos,
        "clientes_cadastrados": clientes_cadastrados,
        "total_chamados": total_chamados,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/chat", methods=["POST"])
def chat_api():
    """API para chat em tempo real."""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        
        if not message:
            return jsonify({"response": "Por favor, digite uma mensagem."})
        
        # Detectar intenção
        result = detect_intent(message)
        intent_name = result["intent"]
        params = result["params"]
        
        # Processar resposta
        response = handle_intent(intent_name, params, "web_session")
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"[ERROR] Chat API error: {e}")
        return jsonify({"response": "Desculpe, ocorreu um erro. Tente novamente."}), 500

@app.route("/dialogflow", methods=["POST"])
def dialogflow_webhook():
    """Webhook para Dialogflow."""
    try:
        body = request.get_json()
        
        if 'text' in body:
            # Payload simples do Streamlit
            text = body['text']
            result = detect_intent(text)
            intent_name = result["intent"]
            params = result["params"]
            response = handle_intent(intent_name, params, "streamlit_session")
            
            return jsonify({"fulfillmentText": response})
        
        else:
            # Payload completo do Dialogflow
            intent_name = body.get("queryResult", {}).get("intent", {}).get("displayName", "Default Fallback Intent")
            params = body.get("queryResult", {}).get("parameters", {})
            params["queryText"] = body.get("queryResult", {}).get("queryText", "")
            
            response = handle_intent(intent_name, params, "dialogflow_session")
            
            return jsonify({"fulfillmentText": response})
            
    except Exception as e:
        print(f"[ERROR] Dialogflow webhook error: {e}")
        return jsonify({"fulfillmentText": "Desculpe, ocorreu um erro. Tente novamente."}), 500

@app.route("/chamados")
def listar_chamados():
    """Lista todos os chamados."""
    return jsonify({
        "chamados": list(CHAMADOS_DB.values()),
        "total": len(CHAMADOS_DB)
    })

@app.route("/chamados/<chamado_id>")
def buscar_chamado(chamado_id):
    """Busca um chamado específico."""
    chamado = CHAMADOS_DB.get(chamado_id)
    if chamado:
        return jsonify(chamado)
    else:
        return jsonify({"error": "Chamado não encontrado"}), 404

# ==================== API INTENTS ====================

@app.route("/api/intents")
def listar_intents():
    """Lista todas as intents do Dialogflow."""
    try:
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
        response = GSESSION.get(url)
        
        if response.status_code == 200:
            result = response.json()
            intents = result.get("intents", [])
            
            # Adicionar informações extras para a interface
            for intent in intents:
                intent["category"] = _get_intent_category(intent.get("displayName", ""))
                intent["active"] = intent.get("webhookState") == "WEBHOOK_STATE_ENABLED"
                intent["description"] = _get_intent_description(intent.get("displayName", ""))
            
            return jsonify({"intents": intents, "total": len(intents)})
        else:
            return jsonify({"error": "Erro ao carregar intents"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao listar intents: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/api/intents/<intent_name>")
def buscar_intent(intent_name):
    """Busca uma intent específica."""
    try:
        # Buscar intent por displayName
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
        response = GSESSION.get(url)
        
        if response.status_code == 200:
            result = response.json()
            intents = result.get("intents", [])
            
            # Encontrar intent pelo displayName
            intent = None
            for i in intents:
                if i.get("displayName") == intent_name:
                    intent = i
                    break
            
            if intent:
                intent["category"] = _get_intent_category(intent.get("displayName", ""))
                intent["active"] = intent.get("webhookState") == "WEBHOOK_STATE_ENABLED"
                intent["description"] = _get_intent_description(intent.get("displayName", ""))
                return jsonify(intent)
            else:
                return jsonify({"error": "Intent não encontrada"}), 404
        else:
            return jsonify({"error": "Erro ao buscar intent"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao buscar intent: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/api/intents", methods=["POST"])
def criar_intent():
    """Cria uma nova intent."""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get("displayName"):
            return jsonify({"error": "Nome da intent é obrigatório"}), 400
        
        # Construir payload da intent
        intent_payload = {
            "displayName": data["displayName"],
            "trainingPhrases": _build_training_phrases(data.get("trainingPhrases", [])),
            "parameters": _build_parameters(data.get("parameters", [])),
            "messages": _build_messages(data.get("response", ""))
        }
        
        # Adicionar webhook state apenas se habilitado
        if data.get("webhookEnabled"):
            intent_payload["webhookState"] = "WEBHOOK_STATE_ENABLED"
        
        # Adicionar contextos se fornecidos
        if data.get("contexts"):
            intent_payload["inputContextNames"] = data["contexts"].split(",")
        
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
        response = GSESSION.post(url, json=intent_payload)
        
        if response.status_code == 200:
            return jsonify({"message": "Intent criada com sucesso", "intent": response.json()})
        else:
            return jsonify({"error": f"Erro ao criar intent: {response.text}"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar intent: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/api/intents/<intent_name>", methods=["DELETE"])
def excluir_intent(intent_name):
    """Exclui uma intent."""
    try:
        # Primeiro, buscar o ID da intent
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents"
        response = GSESSION.get(url)
        
        if response.status_code == 200:
            result = response.json()
            intents = result.get("intents", [])
            
            # Encontrar intent pelo displayName
            intent_id = None
            for intent in intents:
                if intent.get("displayName") == intent_name:
                    intent_id = intent.get("name", "").split("/")[-1]
                    break
            
            if intent_id:
                delete_url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/intents/{intent_id}"
                delete_response = GSESSION.delete(delete_url)
                
                if delete_response.status_code == 200:
                    return jsonify({"message": "Intent excluída com sucesso"})
                else:
                    return jsonify({"error": f"Erro ao excluir intent: {delete_response.text}"}), 500
            else:
                return jsonify({"error": "Intent não encontrada"}), 404
        else:
            return jsonify({"error": "Erro ao buscar intent"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao excluir intent: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# ==================== API ENTITIES ====================

@app.route("/api/entities")
def listar_entidades():
    """Lista todas as entidades do Dialogflow."""
    try:
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/entityTypes"
        response = GSESSION.get(url)
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get("entityTypes", [])
            
            # Adicionar informações extras para a interface
            for entity in entities:
                entity["category"] = _get_entity_category(entity.get("displayName", ""))
                entity["description"] = _get_entity_description(entity.get("displayName", ""))
            
            return jsonify({"entities": entities, "total": len(entities)})
        else:
            return jsonify({"error": "Erro ao carregar entidades"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao listar entidades: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/api/entities/<entity_name>")
def buscar_entidade(entity_name):
    """Busca uma entidade específica."""
    try:
        # Buscar entidade por displayName
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/entityTypes"
        response = GSESSION.get(url)
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get("entityTypes", [])
            
            # Encontrar entidade pelo displayName
            entity = None
            for e in entities:
                if e.get("displayName") == entity_name:
                    entity = e
                    break
            
            if entity:
                entity["category"] = _get_entity_category(entity.get("displayName", ""))
                entity["description"] = _get_entity_description(entity.get("displayName", ""))
                return jsonify(entity)
            else:
                return jsonify({"error": "Entidade não encontrada"}), 404
        else:
            return jsonify({"error": "Erro ao buscar entidade"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao buscar entidade: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/api/entities", methods=["POST"])
def criar_entidade():
    """Cria uma nova entidade."""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get("displayName"):
            return jsonify({"error": "Nome da entidade é obrigatório"}), 400
        
        # Construir payload da entidade
        entity_payload = {
            "displayName": data["displayName"],
            "kind": "KIND_MAP",
            "entities": _build_entity_values(data.get("values", [])),
            "autoExpansionMode": "AUTO_EXPANSION_MODE_DEFAULT" if data.get("autoExpand") else "AUTO_EXPANSION_MODE_DISABLED"
        }
        
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/entityTypes"
        response = GSESSION.post(url, json=entity_payload)
        
        if response.status_code == 200:
            return jsonify({"message": "Entidade criada com sucesso", "entity": response.json()})
        else:
            return jsonify({"error": f"Erro ao criar entidade: {response.text}"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar entidade: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/api/entities/<entity_name>", methods=["DELETE"])
def excluir_entidade(entity_name):
    """Exclui uma entidade."""
    try:
        # Primeiro, buscar o ID da entidade
        url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/entityTypes"
        response = GSESSION.get(url)
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get("entityTypes", [])
            
            # Encontrar entidade pelo displayName
            entity_id = None
            for entity in entities:
                if entity.get("displayName") == entity_name:
                    entity_id = entity.get("name", "").split("/")[-1]
                    break
            
            if entity_id:
                delete_url = f"https://dialogflow.googleapis.com/v2/projects/{PROJECT_ID}/agent/entityTypes/{entity_id}"
                delete_response = GSESSION.delete(delete_url)
                
                if delete_response.status_code == 200:
                    return jsonify({"message": "Entidade excluída com sucesso"})
                else:
                    return jsonify({"error": f"Erro ao excluir entidade: {delete_response.text}"}), 500
            else:
                return jsonify({"error": "Entidade não encontrada"}), 404
        else:
            return jsonify({"error": "Erro ao buscar entidade"}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao excluir entidade: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# ==================== TELEGRAM WEBHOOK ====================

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    """Webhook para Telegram."""
    try:
        data = request.get_json()
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        if not text or not chat_id:
            return "OK", 200
        
        # Detectar intenção
        result = detect_intent(text, f"telegram_{chat_id}")
        intent_name = result["intent"]
        params = result["params"]
        
        # Processar resposta
        response = handle_intent(intent_name, params, f"telegram_{chat_id}")
        
        # Enviar resposta para o Telegram
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        if telegram_token:
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            telegram_data = {
                "chat_id": chat_id,
                "text": response,
                "parse_mode": "Markdown"
            }
            
            requests.post(telegram_url, json=telegram_data)
        
        return "OK", 200
        
    except Exception as e:
        print(f"[ERROR] Telegram webhook error: {e}")
        return "OK", 200

# ==================== HEALTH CHECK ====================

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5023))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Iniciando FiapNet - Suporte de Internet")
    print(f"📡 Porta: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"🌐 Acesse: http://localhost:{port}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
