from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import traceback

from app.models import User
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "kiss-and-tell-secret"
ALGORITHM = "HS256"


# Pydantic Request Body
class AuthModel(BaseModel):
    email: EmailStr
    password: str


# Hash password
def hash_password(password: str):
    password = password[:72]
    return pwd_context.hash(password)


# Verify password
def verify_password(plain, hashed):
    plain = plain[:72]
    return pwd_context.verify(plain, hashed)


# Create JWT
def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=3)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# SIGNUP
@router.post("/signup")
def signup(data: AuthModel, db: Session = Depends(get_db)):
    try:
        print("===== SIGNUP CALLED =====")
        print("INPUT DATA:", data.dict())

        email = data.email
        password = data.password

        # 1. Check if email exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("ERROR: Email already exists")
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2. Create user
        new_user = User(
            email=email,
            password=hash_password(password)
        )

        db.add(new_user)
        db.flush()       # <-- IMPORTANT on Render
        db.commit()
        db.refresh(new_user)

        print("NEW USER CREATED:", new_user.id)

        token = create_token({"user_id": new_user.id})
        return {"status": "success", "token": token}

    except Exception as e:
        print("SIGNUP ERROR:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Signup failed: " + str(e))


# LOGIN
@router.post("/login")
def login(data: AuthModel, db: Session = Depends(get_db)):
    try:
        print("===== LOGIN CALLED =====")
        print("INPUT DATA:", data.dict())

        email = data.email
        password = data.password

        # 1. Get user
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print("ERROR: User not found")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # 2. Verify password
        if not verify_password(password, user.password):
            print("ERROR: Wrong password")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token({"user_id": user.id})
        print("LOGIN SUCCESS:", user.id)

        return {"status": "success", "token": token}

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Login failed: " + str(e))
