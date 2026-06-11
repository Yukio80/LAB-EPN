from fastapi import APIRouter, HTTPException

from app.services.votacao_onchain import implantar, votar, resultado, listar_ativas

router = APIRouter(prefix="/votacao", tags=["votacao"])


@router.get("/propostas")
async def listar_votacoes():
    return await listar_ativas()


@router.get("/propostas/{proposta_id}/resultado")
async def obter_resultado(proposta_id: str):
    try:
        return await resultado(proposta_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/propostas/{proposta_id}/votar")
async def votar_proposta(proposta_id: str, voto: bool = True, creditos: int = 1):
    if creditos < 1:
        raise HTTPException(400, "Creditos devem ser >= 1")
    if creditos > 100:
        raise HTTPException(400, "Maximo 100 creditos por voto")
    try:
        return await votar(proposta_id, voto, creditos)
    except ValueError as e:
        raise HTTPException(404, str(e))
