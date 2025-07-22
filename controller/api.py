from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.agent_memory import AgentMemory, Base
from dotenv import load_dotenv
from routes.user import router as user_router
from routes.chat import router as chat_router
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Garante que as tabelas existem
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Libera CORS para facilitar testes locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "ok"}
