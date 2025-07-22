import streamlit as st
import sys
from pathlib import Path
import os

# Configurações iniciais
sys.path.append(str(Path(__file__).parent.parent))
from service.langchain_service import process_question

# Proxy (se necessário)
proxy_user = os.getenv("PROXY_USER")
proxy_pass = os.getenv("PROXY_PASS")
proxy_host = os.getenv("PROXY_HOST")
proxy_port = os.getenv("PROXY_PORT")
if proxy_user and proxy_pass and proxy_host and proxy_port:
    proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url

# Configuração da página
st.set_page_config(page_title="Digi Chatbot", page_icon="🤖", layout="centered")

# CSS customizado (Copilot style)
st.markdown("""
    <style>
        .container {
            text-align: center;
            padding-top: 30px;
        }
        .welcome {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 20px;
            color: #555;
            margin-bottom: 25px;
        }
        .chip-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
        }
        .chip {
            background-color: #f0f0f0;
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 14px;
            color: #333;
            cursor: default;
        }
        .footer {
            margin-top: 40px;
            font-size: 12px;
            color: gray;
        }
    </style>

    <div class="container">
        <div class="welcome">Boa tarde</div>
        <div class="subtitle">Como posso ajudar você hoje?</div>
        <div class="chip-container">
            <div class="chip">Escrever um primeiro rascunho</div>
            <div class="chip">Obter conselhos</div>
            <div class="chip">Aprender algo novo</div>
            <div class="chip">Criar uma imagem</div>
            <div class="chip">Fazer um plano</div>
            <div class="chip">Debate de ideias</div>
            <div class="chip">Praticar um idioma</div>
            <div class="chip">Faça um teste</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Explicação do chatbot
st.markdown("Converse com o Digi! Pergunte sobre clima, ciência ou dados climáticos 🌍")

# Inicializa o histórico
if "history" not in st.session_state:
    st.session_state["history"] = []

# Renderiza histórico de chat
for msg in st.session_state["history"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Pergunte qualquer coisa"):
    st.session_state["history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Digi está pensando..."):
        resposta = process_question(prompt)
        conteudo = resposta["content"] if isinstance(resposta, dict) and "content" in resposta else resposta

    st.session_state["history"].append({"role": "assistant", "content": conteudo})
    with st.chat_message("assistant"):
        st.markdown(conteudo)

# Rodapé
st.markdown('<div class="footer">O Digi usa IA. Verifique se há erros nos dados climáticos. 🤖</div>', unsafe_allow_html=True)
