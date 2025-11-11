from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Confession
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/confession", tags=["Confession"])


@router.get("/")
def get_confessions(db: Session = Depends(get_db)):
    return db.query(Confession).all()


@router.post("/")
def create_confession(content: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    new_conf = Confession(content=content, user_id=user.id)
    db.add(new_conf)
    db.commit()
    db.refresh(new_conf)
    return new_conf
