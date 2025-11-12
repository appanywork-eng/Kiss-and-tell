from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from .models import User
from .database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "kiss-and-tell-secret"
ALGORITHM = "HS256"

# Request body
class AuthModel(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str):
    # bcrypt max 72 bytes
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain[:72], hashed)

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=3)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup")
def signup(data: AuthModel, db: Session = Depends(get_db)):
    email = data.email
    password = data.password

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=email, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token({"user_id": new_user.id})
    return {"token": token, "message": "Signup successful"}

@router.post("/login")
def login(data: AuthModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"user_id": user.id})
    return {"token": token, "message": "Login successful"}
