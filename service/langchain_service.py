# service/langchain_service.py
"""
Serviço para integração com LangChain e processamento do agente de IA.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from os import getenv
from dotenv import load_dotenv
import yaml
from pathlib import Path

load_dotenv()

# Nome do modelo DeepSeek V3 0324 (free) no OpenRouter
DEFAULT_MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"

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
def process_question(question: str, model_name: str = DEFAULT_MODEL_NAME):
    llm = get_openrouter_llm(model_name)
    prompt = get_persona_prompt()
    system_message = load_persona_yaml()
    chain = prompt | llm
    return chain.invoke({"question": question, "system_message": system_message})

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
