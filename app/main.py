from fastapi import FastAPI
from .database import Base, engine
import app.models  # ensure models are registered before create_all

# Create tables at startup
Base.metadata.create_all(bind=engine)

from .auth import router as auth_router
from .confession import router as confession_router

app = FastAPI(title="Kiss & Tell API")

app.include_router(auth_router)
app.include_router(confession_router)

@app.get("/")
def home():
    return {"status": "OK", "message": "Backend Running ✅"}
