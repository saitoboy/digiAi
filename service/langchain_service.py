# service/langchain_service.py
"""
Serviço para integração com LangChain e processamento do agente de IA.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from os import getenv, environ
from dotenv import load_dotenv
import yaml
from pathlib import Path
from langchain_core.messages import AIMessage

load_dotenv()

# Nome do modelo DeepSeek V3 0324 (free) no OpenRouter
DEFAULT_MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"

# --- Configuração de proxy corporativo para requests externos ---
proxy_user = getenv("PROXY_USER")
proxy_pass = getenv("PROXY_PASS")
proxy_host = getenv("PROXY_HOST")
proxy_port = getenv("PROXY_PORT")
if proxy_user and proxy_pass and proxy_host and proxy_port:
    proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    environ["HTTP_PROXY"] = proxy_url
    environ["HTTPS_PROXY"] = proxy_url

# Função para criar o LLM do OpenRouter (sem headers customizados)
def get_openrouter_llm(model_name: str = DEFAULT_MODEL_NAME):
    return ChatOpenAI(
        openai_api_key=getenv("OPENROUTER_API_KEY"),
        openai_api_base=getenv("OPENROUTER_BASE_URL"),
        model_name=model_name,
    )

# Função para criar o prompt padrão
def get_default_prompt():
    template = """Question: {question}\nAnswer: Let's think step by step."""
    return PromptTemplate(template=template, input_variables=["question"])

def load_persona_yaml(yaml_path: str = None):
    """Carrega o system_message/persona do arquivo YAML."""
    if yaml_path is None:
        yaml_path = str(Path(__file__).parent.parent / "prompts" / "persona_digi.yaml")
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("system_message", "")

# Função para criar o prompt com persona
def get_persona_prompt():
    system_message = load_persona_yaml()
    template = f"""{{system_message}}\nUsuário: {{question}}\nDigi:"""  # Prompt em pt-BR, com persona
    return PromptTemplate(template=template, input_variables=["question", "system_message"])

# Função para processar uma pergunta
# Corrige para retornar apenas o texto da resposta, sem metadados

def process_question(question: str, model_name: str = DEFAULT_MODEL_NAME):
    llm = get_openrouter_llm(model_name)
    prompt = get_persona_prompt()
    system_message = load_persona_yaml()
    chain = prompt | llm
    resposta = chain.invoke({"question": question, "system_message": system_message})
    # Extrai apenas o texto antes de qualquer 'additional_kwargs' ou metadados
    texto = None
    if isinstance(resposta, dict) and "content" in resposta:
        texto = resposta["content"]
    elif hasattr(resposta, "content"):
        texto = resposta.content
    elif isinstance(resposta, AIMessage):
        texto = resposta.content
    elif isinstance(resposta, str):
        texto = resposta
    else:
        texto = str(resposta)
    # Remove metadados extras se vierem juntos (ex: '\nadditional_kwargs=')
    if "additional_kwargs" in texto:
        texto = texto.split("additional_kwargs")[0].strip()
    return texto

def chat_loop():
    print("\nDigite sua pergunta para o Digi (ou 'sair' para encerrar):")
    while True:
        question = input("Você: ").strip()
        if question.lower() in ("sair", "exit", "quit"):  # comandos para sair
            print("Encerrando o chat. Até logo!")
            break
        resposta = process_question(question)
        conteudo = resposta["content"] if isinstance(resposta, dict) and "content" in resposta else resposta
        print(f"Digi: {conteudo}\n")

# Exemplo de uso (remova ou adapte para produção)
if __name__ == "__main__":
    chat_loop()
