import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .config import settings
from .routers import notes, ai, assets, auth as auth_router

os.makedirs(settings.FILE_DIR, exist_ok=True)
os.makedirs(settings.ASSET_DIR, exist_ok=True)
os.makedirs("./data/chroma", exist_ok=True)


app = FastAPI(title ="Notebook ML API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router.router)
app.include_router(notes.router)
app.include_router(ai.router)
app.include_router(assets.router)

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)