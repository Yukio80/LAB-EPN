from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.proposta import (
    PropostaInput,
    PropostaORM,
    PropostaResponse,
    PropostaStatus,
)
from app.services.simulacao import SimulacaoRequest, chamar_motor_pangeia
from app.services.votacao_onchain import implantar
from uuid import uuid4

router = APIRouter(prefix="/propostas", tags=["propostas"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("", response_model=PropostaResponse, status_code=201)
def criar_proposta(input: PropostaInput, db: Session = Depends(get_db)):
    now = _now()
    orm = PropostaORM(
        id=str(uuid4()),
        versao=1,
        titulo=input.titulo,
        resumo=input.resumo,
        descricao=input.descricao,
        problema=input.problema,
        solucao=input.solucao,
        orcamento_estimado=input.orcamento_estimado,
        moeda=input.moeda,
        autor_id=input.autor_id,
        autor_tipo=input.autor_tipo,
        organizacao=input.organizacao,
        localizacao=input.localizacao.model_dump(),
        ods_vinculados=input.ods_vinculados,
        status=PropostaStatus.rascunho.value,
        simulacao=None,
        resultado_votacao=None,
        contrato_endereco=None,
        created_at=now,
        updated_at=now,
        published_at=None,
        tags=input.tags,
    )
    db.add(orm)
    db.commit()
    db.refresh(orm)
    return PropostaResponse.from_orm(orm)


@router.get("", response_model=list[PropostaResponse])
def listar_propostas(db: Session = Depends(get_db)):
    orms = db.query(PropostaORM).all()
    return [PropostaResponse.from_orm(o) for o in orms]


@router.get("/{proposta_id}", response_model=PropostaResponse)
def obter_proposta(proposta_id: str, db: Session = Depends(get_db)):
    orm = db.query(PropostaORM).filter(PropostaORM.id == proposta_id).first()
    if not orm:
        raise HTTPException(status_code=404, detail="Proposta nao encontrada")
    return PropostaResponse.from_orm(orm)


@router.post("/{proposta_id}/simular", response_model=PropostaResponse)
async def simular_proposta(proposta_id: str, db: Session = Depends(get_db)):
    orm = db.query(PropostaORM).filter(PropostaORM.id == proposta_id).first()
    if not orm:
        raise HTTPException(status_code=404, detail="Proposta nao encontrada")

    orm.status = PropostaStatus.em_simulacao.value
    db.commit()

    req = SimulacaoRequest(
        proposta_id=proposta_id,
        titulo=orm.titulo,
        descricao=orm.descricao,
        problema=orm.problema or "",
        solucao=orm.solucao or "",
        orcamento=orm.orcamento_estimado,
        localizacao=orm.localizacao,
        ods=orm.ods_vinculados,
    )
    resultado = await chamar_motor_pangeia(req)

    orm.status = PropostaStatus.simulacao_concluida.value
    orm.simulacao = {
        "id_simulacao": str(resultado.id_simulacao),
        "motor_utilizado": resultado.motor_usado,
        "modelo_versao": resultado.modelo_versao,
        "pesos_ods_versao": resultado.pesos_ods_versao,
        "metricas": resultado.metricas,
        "contexto_regional": resultado.contexto_regional,
        "metodologia": resultado.metodologia,
        "relatorio_hash_ipfs": resultado.hash_ipfs,
        "timestamp": _now(),
    }
    orm.updated_at = _now()
    db.commit()
    db.refresh(orm)
    return PropostaResponse.from_orm(orm)


@router.post("/{proposta_id}/publicar", response_model=PropostaResponse)
async def publicar_proposta(proposta_id: str, db: Session = Depends(get_db)):
    orm = db.query(PropostaORM).filter(PropostaORM.id == proposta_id).first()
    if not orm:
        raise HTTPException(status_code=404, detail="Proposta nao encontrada")
    if orm.status != PropostaStatus.simulacao_concluida.value:
        raise HTTPException(
            status_code=400,
            detail="Proposta precisa ter simulacao concluida antes de publicar",
        )
    now = _now()
    orm.status = PropostaStatus.em_votacao.value
    orm.published_at = now
    orm.updated_at = now

    contrato = await implantar(
        titulo=orm.titulo,
        descricao=orm.descricao,
        orcamento=orm.orcamento_estimado,
    )
    orm.contrato_endereco = contrato["contrato_endereco"]
    pid = contrato["proposta_id"]
    from app.services.votacao_onchain import _proposta_para_votacao
    _proposta_para_votacao[pid] = proposta_id
    if orm.simulacao:
        orm.simulacao["contrato"] = contrato

    db.commit()
    db.refresh(orm)
    return PropostaResponse.from_orm(orm)
