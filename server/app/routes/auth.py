
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
import jwt
from datetime import datetime, timedelta
from ..config import config
from ..database import db

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    role: str
    username: str

def create_token(username: str, role: str) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    user = db.execute_one(
        "SELECT id, username, password_hash, role FROM users WHERE username = %s",
        (req.username,)
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not bcrypt.checkpw(req.password.encode(), user[2].encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token = create_token(user[1], user[3])
    return LoginResponse(token=token, role=user[3], username=user[1])
