from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import logging

from app.models import User
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "kiss-and-tell-secret"
ALGORITHM = "HS256"

# ------------------------------------------------------------------
# ENABLE FULL LOGGING
# ------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth-debug")

# ------------------------------------------------------------------

class AuthModel(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str):
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    plain = plain[:72]
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=3)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------------------- SIGNUP --------------------------------
@router.post("/signup")
def signup(data: AuthModel, db: Session = Depends(get_db)):
    logger.info(f"Signup called with: {data.dict()}")

    try:
        email = data.email
        password = data.password

        logger.info(f"Checking existing user: {email}")
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        logger.info("Creating new user...")
        new_user = User(
            email=email,
            password=hash_password(password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User created with ID: {new_user.id}")
        token = create_token({"user_id": new_user.id})

        return {"token": token}

    except Exception as e:
        logger.error(f"SIGNUP ERROR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------- LOGIN ---------------------------------
@router.post("/login")
def login(data: AuthModel, db: Session = Depends(get_db)):
    logger.info(f"Login called with: {data.dict()}")

    try:
        email = data.email
        password = data.password

        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        logger.info(f"User authenticated: {user.id}")
        token = create_token({"user_id": user.id})

        return {"token": token}

    except Exception as e:
        logger.error(f"LOGIN ERROR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
