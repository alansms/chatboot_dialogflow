import streamlit as st
import requests

st.set_page_config(page_title='RPA-BOT', layout='centered')

BACKEND_URL = 'http://localhost:5008'  # Ajuste se rodar em outro host/porta

st.title('Plataforma RPA-BOT')

# Tabs para navegação
aba = st.tabs(["Chat", "Cardápio", "Admin"])

# --- CHAT ---
with aba[0]:
    st.header('Chat com o Bot')
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    user_message = st.text_input('Digite sua mensagem:', key='chat_input', value=st.session_state.get('last_input', ''))
    if st.button('Enviar', key='enviar_chat'):
        if not user_message.strip():
            st.warning('Digite uma mensagem antes de enviar.')
        else:
            # Envia apenas o texto para o backend
            payload = {"text": user_message}
            try:
                resp = requests.post(f"{BACKEND_URL}/dialogflow", json=payload)
                if resp.status_code == 200:
                    reply = resp.json().get('fulfillmentText', 'Desculpe, não entendi.')
                    st.session_state['chat_history'].append((user_message, reply))
                    st.session_state['last_input'] = ''  # Limpa campo após envio
                else:
                    st.error(f"Erro: {resp.status_code}")
            except Exception as e:
                st.error(f"Erro ao conectar: {e}")
    # Limpa o campo de input após envio
    if 'last_input' not in st.session_state:
        st.session_state['last_input'] = ''
    # Exibe histórico
    for user, bot in st.session_state['chat_history']:
        st.markdown(f"**Você:** {user}")
        st.markdown(f"**Bot:** {bot}")

# --- CARDÁPIO ---
with aba[1]:
    st.header('Cardápio Atual')
    try:
        resp = requests.get(f"{BACKEND_URL}/menu")
        if resp.status_code == 200:
            st.markdown(resp.text, unsafe_allow_html=True)
        else:
            st.warning('Nenhum cardápio carregado.')
    except Exception as e:
        st.error(f"Erro ao buscar cardápio: {e}")

# --- ADMIN ---
with aba[2]:
    st.header('Upload de Cardápio (Admin)')
    st.write('Faça upload de um arquivo CSV ou XLSX com as colunas: categoria, item, descricao, preco, vegetariano (opcional), sinonimos (opcional).')
    uploaded_file = st.file_uploader('Escolha o arquivo do cardápio', type=['csv', 'xlsx'])
    if st.button('Enviar Cardápio', key='enviar_cardapio'):
        if uploaded_file is None:
            st.warning('Selecione um arquivo antes de enviar.')
        else:
            file_bytes = uploaded_file.read()
            if not file_bytes:
                st.error('Arquivo vazio ou não pôde ser lido.')
            else:
                files = {'file': (uploaded_file.name, file_bytes)}
                try:
                    resp = requests.post(f"{BACKEND_URL}/upload", files=files, allow_redirects=False)
                    if resp.status_code in (200, 302):
                        st.success('Cardápio enviado com sucesso!')
                    else:
                        st.error(f'Erro ao enviar: {resp.text}')
                except Exception as e:
                    st.error(f'Erro ao conectar: {e}')
