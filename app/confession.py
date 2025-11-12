from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .models import Confession
from .database import get_db
from .deps import get_current_user

router = APIRouter(prefix="/confession", tags=["Confession"])

class ConfessionCreate(BaseModel):
    content: str

@router.get("/")
def list_confessions(db: Session = Depends(get_db)):
    return db.query(Confession).order_by(Confession.id.desc()).all()

@router.post("/")
def create_confession(
    body: ConfessionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not body.content or not body.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")

    conf = Confession(content=body.content.strip(), user_id=user.id)
    db.add(conf)
    db.commit()
    db.refresh(conf)
    return conf
