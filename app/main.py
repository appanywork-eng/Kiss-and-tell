from fastapi import FastAPI
from app.auth import router as auth_router
from app.confession import router as confession_router
from app.database import Base, engine

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Add routers
app.include_router(auth_router)
app.include_router(confession_router)

@app.get("/")
def home():
    return {"status": "OK", "message": "Backend Running ✅"}
