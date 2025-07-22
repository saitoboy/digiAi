from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from model.agent_memory import AgentMemory
from service.langchain_service import process_question
from controller.api import SessionLocal

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    question: str

class ChatResponse(BaseModel):
    answer: str
    memory: Optional[dict] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    # Busca memória existente
    memory = db.query(AgentMemory).filter_by(user_id=req.user_id, session_id=req.session_id).first()
    memory_data = memory.memory_data if memory else {}
    # (Opcional) Passa memória para o LLM futuramente
    answer = process_question(req.question)
    # Atualiza memória (exemplo: salva última pergunta/resposta)
    new_memory = {"last_question": req.question, "last_answer": answer}
    if memory:
        memory.memory_data = new_memory
    else:
        memory = AgentMemory(user_id=req.user_id, session_id=req.session_id, memory_data=new_memory)
        db.add(memory)
    db.commit()
    return ChatResponse(answer=answer, memory=new_memory)
