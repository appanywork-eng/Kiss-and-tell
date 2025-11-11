from fastapi import Depends, HTTPException
from jose import jwt
from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session

SECRET_KEY = "kiss-and-tell-secret"
ALGORITHM = "HS256"

def get_current_user(db: Session = Depends(get_db), token: str = ""):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        user = db.query(User).filter(User.id == user_id).first()
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
