from fastapi import FastAPI
from .database import Base, engine
import app.models  # Register models

# Routers
from .auth import router as auth_router
from .confession import router as confession_router

# Create tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kiss & Tell API")

# Include Routers (VERY IMPORTANT)
app.include_router(auth_router)
app.include_router(confession_router)

@app.get("/")
def home():
    return {"status": "OK", "message": "Backend running successfully"}
