import streamlit as st
import sys
from pathlib import Path
import os
import requests
import uuid

# Configurações iniciais
sys.path.append(str(Path(__file__).parent.parent))

# Proxy (se necessário)
proxy_user = os.getenv("PROXY_USER")
proxy_pass = os.getenv("PROXY_PASS")
proxy_host = os.getenv("PROXY_HOST")
proxy_port = os.getenv("PROXY_PORT")
proxies = None
if proxy_user and proxy_pass and proxy_host and proxy_port:
    proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    proxies = {"http": proxy_url, "https": proxy_url}

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Desabilita proxy para localhost/127.0.0.1
if "localhost" in API_URL or "127.0.0.1" in API_URL:
    proxies = None
    # Remove variáveis de ambiente de proxy para garantir que requests não usem proxy
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)

st.set_page_config(page_title="Digi Chatbot", page_icon="🤖", layout="centered")

# --- Login/Cadastro simples ---
if "access_token" not in st.session_state:
    st.title("Login Digi")
    aba = st.radio("Escolha uma opção:", ["Login", "Cadastro"], horizontal=True)
    if aba == "Login":
        email = st.text_input("Usuário", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar"):
            try:
                resp = requests.post(f"{API_URL}/user/login", json={"username": email, "password": senha}, proxies=proxies)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["access_token"] = data["access_token"]
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos!")
            except Exception as e:
                st.error(f"Erro ao conectar: {e}")
    else:
        email = st.text_input("Usuário", key="cadastro_email")
        senha = st.text_input("Senha", type="password", key="cadastro_senha")
        if st.button("Cadastrar"):
            try:
                resp = requests.post(f"{API_URL}/user/register", json={"username": email, "password": senha}, proxies=proxies)
                if resp.status_code == 200:
                    st.success("Usuário cadastrado com sucesso! Faça login.")
                elif resp.status_code == 400:
                    st.error("Usuário já existe!")
                else:
                    st.error(f"Erro: {resp.status_code} - {resp.text}")
            except Exception as e:
                st.error(f"Erro ao conectar: {e}")
    st.stop()

# --- Chatbot UI ---

# Função para buscar sessões do usuário
@st.cache_data(show_spinner=False)
def get_sessions(api_url, token, proxies):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{api_url}/chat/sessions", headers=headers, proxies=proxies)
        if resp.status_code == 200:
            return resp.json()
        else:
            return []
    except Exception:
        return []

# Função para buscar histórico de uma sessão
@st.cache_data(show_spinner=False)
def get_history(api_url, token, session_id, proxies):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": "", "session_id": session_id}
    try:
        resp = requests.post(f"{api_url}/chat/", json=payload, headers=headers, proxies=proxies)
        if resp.status_code == 200:
            return resp.json().get("memory", [])
        else:
            return []
    except Exception:
        return []

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

# Sidebar para nova conversa e histórico
st.sidebar.title("Conversas")
if "access_token" in st.session_state:
    sessions = get_sessions(API_URL, st.session_state["access_token"], proxies)
    session_options = [
        f"{s['session_id'][:8]}... ({s['created_at'][:10] if s['created_at'] else ''})" for s in sessions
    ]
    session_map = {opt: s["session_id"] for opt, s in zip(session_options, sessions)}
    if "session_id" not in st.session_state:
        if sessions:
            st.session_state["session_id"] = sessions[-1]["session_id"]
        else:
            st.session_state["session_id"] = str(uuid.uuid4())
    selected = st.sidebar.radio("Selecione uma conversa:", session_options, index=session_options.index(next((k for k,v in session_map.items() if v==st.session_state["session_id"]), session_options[-1])) if session_options else 0)
    if session_map[selected] != st.session_state["session_id"]:
        st.session_state["session_id"] = session_map[selected]
        st.session_state["history"] = get_history(API_URL, st.session_state["access_token"], st.session_state["session_id"], proxies)
        st.rerun()
    if st.sidebar.button("Nova conversa"):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["history"] = []
        st.rerun()
    st.sidebar.markdown(f"<small>ID da sessão: <code>{st.session_state['session_id']}</code></small>", unsafe_allow_html=True)
else:
    st.sidebar.write("Faça login para ver suas conversas.")

if "history" not in st.session_state:
    st.session_state["history"] = get_history(API_URL, st.session_state["access_token"], st.session_state["session_id"], proxies) if "access_token" in st.session_state else []

for msg in st.session_state["history"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte qualquer coisa"):
    st.session_state["history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Digi está pensando..."):
        try:
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            payload = {"question": prompt, "session_id": st.session_state["session_id"]}
            resp = requests.post(f"{API_URL}/chat/", json=payload, headers=headers, proxies=proxies)
            if resp.status_code == 200:
                resposta = resp.json()["answer"]
                # Atualiza histórico com o que veio do backend
                st.session_state["history"] = [
                    {"role": "user", "content": h["question"]} if i%2==0 else {"role": "assistant", "content": h["answer"]}
                    for i, h in enumerate(resp.json().get("memory", []))
                ]
            else:
                resposta = f"Erro: {resp.status_code} - {resp.text}"
        except Exception as e:
            resposta = f"Erro ao conectar: {e}"

    if not st.session_state["history"] or st.session_state["history"][-1]["role"] != "assistant":
        st.session_state["history"].append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.markdown(resposta)

st.markdown('<div class="footer">O Digi usa IA. Verifique se há erros nos dados climáticos. 🤖</div>', unsafe_allow_html=True)
