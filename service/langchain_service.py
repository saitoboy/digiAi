# service/langchain_service.py
"""
Serviço para integração com LangChain e processamento do agente de IA.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from os import getenv
from dotenv import load_dotenv

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

# Função para processar uma pergunta
def process_question(question: str, model_name: str = DEFAULT_MODEL_NAME):
    llm = get_openrouter_llm(model_name)
    prompt = get_default_prompt()
    chain = prompt | llm
    return chain.invoke({"question": question})

# Exemplo de uso (remova ou adapte para produção)
if __name__ == "__main__":
    question = "Que foi o primeiro presidente do Brasil?"
    resposta = process_question(question)
    print(resposta["content"] if isinstance(resposta, dict) and "content" in resposta else resposta)
