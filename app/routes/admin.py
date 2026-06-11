from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.proposta import PropostaORM, PropostaStatus
from app.services.pesos_ods import PESOS_ODS, versao_pesos

router = APIRouter(prefix="/admin", tags=["admin"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Schemas ───────────────────────────────────────────────────

class PesoEntry(BaseModel):
    desigualdade: float = 0.0
    emprego: float = 0.0
    confianca: float = 0.0
    conflito: float = 0.0
    pib: float = 0.0
    sinergia_titulo: list[str] = []
    sinergia_contexto: dict = {}


class PesoODS(BaseModel):
    ods_id: int
    nome: str
    meta_resumo: str
    pesos: PesoEntry


class PesosResponse(BaseModel):
    versao: str
    ods: list[PesoODS]


class PesosUpdate(BaseModel):
    ods_id: int
    pesos: PesoEntry
    justificativa: str


class ValidacaoRequest(BaseModel):
    decisao: str  # "aprovar" | "rejeitar"
    parecer: str = ""


class AuditoriaEntry(BaseModel):
    timestamp: str
    acao: str
    usuario: str
    descricao: str
    dados_anteriores: Optional[dict] = None
    dados_novos: Optional[dict] = None


# ─── In-memory audit log (em produção: tabela SQL) ─────────────

_AUDIT_LOG: list[AuditoriaEntry] = []


# ─── Routes ────────────────────────────────────────────────────

@router.get("/pesos", response_model=PesosResponse)
def listar_pesos():
    ods_list = []
    for ods_id in sorted(PESOS_ODS.keys()):
        entry = PESOS_ODS[ods_id]
        ods_list.append(PesoODS(
            ods_id=ods_id,
            nome=entry["nome"],
            meta_resumo=entry["meta_resumo"],
            pesos=PesoEntry(**entry["pesos"]),
        ))
    return PesosResponse(versao=versao_pesos(), ods=ods_list)


@router.put("/pesos", response_model=PesosResponse)
def atualizar_pesos(update: PesosUpdate):
    if update.ods_id not in PESOS_ODS:
        raise HTTPException(404, f"ODS {update.ods_id} nao encontrado")

    antigo = dict(PESOS_ODS[update.ods_id]["pesos"])
    PESOS_ODS[update.ods_id]["pesos"] = update.pesos.model_dump()

    _AUDIT_LOG.append(AuditoriaEntry(
        timestamp=_now(),
        acao="atualizacao_pesos",
        usuario="comite@lab-epn",
        descricao=f"ODS {update.ods_id}: {update.justificativa[:200]}",
        dados_anteriores={"pesos": antigo},
        dados_novos={"pesos": update.pesos.model_dump()},
    ))

    return listar_pesos()


@router.get("/auditoria", response_model=list[AuditoriaEntry])
def listar_auditoria(limit: int = 50):
    return _AUDIT_LOG[-limit:]


@router.get("/propostas/pendentes", response_model=list[dict])
def listar_pendentes(db: Session = Depends(get_db)):
    orms = db.query(PropostaORM).filter(
        PropostaORM.status.in_(["rascunho", "em_validacao", "simulacao_concluida"])
    ).all()

    result = []
    for o in orms:
        sim = o.simulacao or {}
        result.append({
            "id": o.id,
            "titulo": o.titulo,
            "resumo": o.resumo,
            "status": o.status,
            "orcamento_estimado": o.orcamento_estimado,
            "localizacao": o.localizacao,
            "ods_vinculados": o.ods_vinculados,
            "motor_utilizado": sim.get("motor_utilizado", ""),
            "modelo_versao": sim.get("modelo_versao", ""),
            "metricas": sim.get("metricas", {}),
            "contexto_keys": len(sim.get("contexto_regional", {})),
            "created_at": o.created_at,
            "updated_at": o.updated_at,
        })
    return result


@router.post("/propostas/{proposta_id}/validar", response_model=dict)
def validar_proposta(proposta_id: str, body: ValidacaoRequest, db: Session = Depends(get_db)):
    orm = db.query(PropostaORM).filter(PropostaORM.id == proposta_id).first()
    if not orm:
        raise HTTPException(404, "Proposta nao encontrada")

    if body.decisao not in ("aprovar", "rejeitar"):
        raise HTTPException(400, "Decisao deve ser 'aprovar' ou 'rejeitar'")

    if body.decisao == "aprovar":
        orm.status = PropostaStatus.em_simulacao.value if orm.status == "rascunho" else orm.status
    else:
        orm.status = PropostaStatus.arquivada.value

    orm.updated_at = _now()

    _AUDIT_LOG.append(AuditoriaEntry(
        timestamp=_now(),
        acao=f"validacao_{body.decisao}",
        usuario="comite@lab-epn",
        descricao=f"Proposta {proposta_id}: {body.decisao}. Parecer: {body.parecer[:300] or 'sem parecer'}",
        dados_anteriores={"status": PropostaStatus.rascunho.value if body.decisao == "aprovar" else PropostaStatus.em_validacao.value},
        dados_novos={"status": orm.status},
    ))

    db.commit()
    return {"id": proposta_id, "status": orm.status, "decisao": body.decisao}


@router.get("/votacoes", response_model=list[dict])
def listar_votacoes(db: Session = Depends(get_db)):
    orms = db.query(PropostaORM).filter(
        PropostaORM.status == "em_votacao"
    ).all()
    return [{
        "id": o.id,
        "titulo": o.titulo,
        "resumo": o.resumo,
        "organizacao": o.organizacao,
        "orcamento_estimado": o.orcamento_estimado,
        "metricas": (o.simulacao or {}).get("metricas", {}),
        "created_at": o.created_at,
        "published_at": o.published_at,
    } for o in orms]


@router.get("/dashboard", response_model=dict)
def dashboard(db: Session = Depends(get_db)):
    total = db.query(PropostaORM).count()
    por_status = {}
    for s in PropostaStatus:
        q = db.query(PropostaORM).filter(PropostaORM.status == s.value).count()
        if q:
            por_status[s.value] = q
    em_votacao = db.query(PropostaORM).filter(
        PropostaORM.status == "em_votacao"
    ).count()
    simuladas = db.query(PropostaORM).filter(
        PropostaORM.status == "simulacao_concluida"
    ).count()

    return {
        "total_propostas": total,
        "por_status": por_status,
        "em_votacao": em_votacao,
        "simuladas": simuladas,
        "pesos_ods_versao": versao_pesos(),
        "modelo_versao": "v1.1",
    }
