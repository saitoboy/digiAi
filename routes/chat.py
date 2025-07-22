from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from model.agent_memory import AgentMemory  # Usa o model correto
from service.langchain_service import process_question
from db.session import SessionLocal
from middleware.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    question: str

class ChatResponse(BaseModel):
    answer: str
    memory: Optional[List[Dict]] = None

class SessionInfo(BaseModel):
    session_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_id = user["user_id"]
    print(f"[DEBUG] user_id: {user_id}, session_id: {req.session_id}")
    # Busca memória existente usando o model correto
    memory = db.query(AgentMemory).filter_by(user_id=user_id, session_id=req.session_id).first()
    if memory:
        print("[DEBUG] Memória encontrada, atualizando...")
        history = memory.memory_data if isinstance(memory.memory_data, list) else []
    else:
        print("[DEBUG] Memória não encontrada, criando nova...")
        history = []
    # Nova interação
    answer = process_question(req.question)
    new_entry = {"question": req.question, "answer": answer}
    history.append(new_entry)
    if memory:
        memory.memory_data = history
    else:
        memory = AgentMemory(user_id=user_id, session_id=req.session_id, memory_data=history)
        db.add(memory)
    db.commit()
    print(f"[DEBUG] Memória salva! Total de interações: {len(history)}")
    return ChatResponse(answer=answer, memory=history)

@router.get("/sessions", response_model=List[SessionInfo])
def list_sessions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_id = user["user_id"]
    sessions = db.query(AgentMemory).filter_by(user_id=user_id).all()
    return [
        SessionInfo(
            session_id=s.session_id,
            created_at=s.created_at.isoformat() if s.created_at else None,
            updated_at=s.updated_at.isoformat() if s.updated_at else None
        ) for s in sessions
    ]
