from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine, SessionLocal
from app.routes.propostas import router as propostas_router
from app.routes.admin import router as admin_router
from app.routes.votacao import router as votacao_router
from app.services.votacao_onchain import carregar_do_banco


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.proposta import PropostaORM
        if db.query(PropostaORM).count() == 0:
            from scripts.seed_demo import seed
            await seed()
        carregar_do_banco(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="LAB-EPN + Pangeia",
    description="Plataforma de simulacao de politicas publicas com motor Pangeia",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "versao": "0.1.0", "motor": "pangeia"}

app.include_router(propostas_router)
app.include_router(admin_router)
app.include_router(votacao_router)

frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
