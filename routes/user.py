from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from model.user import User
import bcrypt
from db.session import SessionLocal
from service.jwt_service import create_access_token

router = APIRouter(prefix="/user", tags=["user"])

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=user.username, password_hash=hashed)
    db.add(new_user)
    db.commit()
    return {"msg": "Usuário criado com sucesso!"}

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    print(f"Tentativa de login: username='{user.username}', password='{user.password}'")
    db_user = db.query(User).filter_by(username=user.username).first()
    print(f"Usuário encontrado no banco: {db_user.username if db_user else None}")
    if not db_user or not bcrypt.checkpw(user.password.encode(), db_user.password_hash.encode()):
        print("Login falhou: usuário não encontrado ou senha inválida.")
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos.")
    # Gera o JWT
    token = create_access_token({"user_id": str(db_user.user_id), "username": db_user.username})
    print("Login bem-sucedido!")
    return {"access_token": token, "token_type": "bearer"}
