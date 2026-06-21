"""
Servico de votacao on-chain via QuadraticVote.sol.

Em producao: interage com contrato Solidity implantado via Web3.py.
Em dev: simula o comportamento do contrato em memoria (hash-based).
Com persistencia: dados salvos no banco via PropostaORM.resultado_votacao.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel


class PropostaVotacao(BaseModel):
    id: str
    titulo: str
    hash_proposta: str
    votos_sim: int = 0
    votos_nao: int = 0
    creditos_sim: int = 0
    creditos_nao: int = 0
    ativa: bool = True
    criada_em: str = ""
    deadline: str = ""


# ─── Simulador de contrato (dev) ────────────────────────────────

_votacoes: dict[str, PropostaVotacao] = {}
_proposta_para_votacao: dict[str, str] = {}


def carregar_do_banco(db):
    from app.models.proposta import PropostaORM
    orms = db.query(PropostaORM).filter(
        PropostaORM.status == "em_votacao"
    ).all()
    for o in orms:
        if not o.contrato_endereco:
            continue
        dados = (o.simulacao or {}).get("contrato", {})
        pid = dados.get("proposta_id") or str(uuid4())
        prop = PropostaVotacao(
            id=pid,
            titulo=o.titulo,
            hash_proposta=o.simulacao.get("contrato", {}).get("hash_proposta", ""),
            ativa=True,
            criada_em=o.published_at or o.created_at,
            deadline=o.published_at or o.created_at,
        )
        if o.resultado_votacao:
            prop.votos_sim = o.resultado_votacao.get("votos_sim", 0)
            prop.votos_nao = o.resultado_votacao.get("votos_nao", 0)
            prop.creditos_sim = o.resultado_votacao.get("creditos_sim", 0)
            prop.creditos_nao = o.resultado_votacao.get("creditos_nao", 0)
        _votacoes[pid] = prop
        _proposta_para_votacao[pid] = o.id


def _salvar_resultado(proposta_id: str, prop: PropostaVotacao):
    from app.database import SessionLocal
    from app.models.proposta import PropostaORM
    db = SessionLocal()
    try:
        pid = _proposta_para_votacao.get(proposta_id)
        if not pid:
            return
        orm = db.query(PropostaORM).filter(PropostaORM.id == pid).first()
        if orm:
            orm.resultado_votacao = {
                "votos_sim": prop.votos_sim,
                "votos_nao": prop.votos_nao,
                "creditos_sim": prop.creditos_sim,
                "creditos_nao": prop.creditos_nao,
            }
            db.commit()
    finally:
        db.close()


def _hash_proposta(titulo: str, descricao: str, orcamento: float) -> str:
    raw = f"{titulo.lower().strip()}|{descricao.lower().strip()}|{orcamento}"
    return "0x" + hashlib.sha256(raw.encode()).hexdigest()


async def implantar(titulo: str, descricao: str, orcamento: float, duracao_dias: int = 30) -> dict:
    pid = str(uuid4())
    now = datetime.now(timezone.utc)

    prop = PropostaVotacao(
        id=pid,
        titulo=titulo,
        hash_proposta=_hash_proposta(titulo, descricao, orcamento),
        ativa=True,
        criada_em=now.isoformat(),
        deadline=now.isoformat(),
    )
    _votacoes[pid] = prop

    return {
        "contrato_endereco": "0x" + hashlib.sha256(f"contract_{pid}".encode()).hexdigest()[:40],
        "proposta_id": pid,
        "hash_proposta": prop.hash_proposta,
        "deadline": prop.deadline,
        "network": "simulacao_local",
    }


async def votar(proposta_id: str, voto: bool, creditos: int) -> dict:
    prop = _votacoes.get(proposta_id)
    if not prop:
        raise ValueError("Proposta nao encontrada na votacao on-chain")
    if not prop.ativa:
        raise ValueError("Votacao encerrada para esta proposta")

    if voto:
        prop.votos_sim += 1
        prop.creditos_sim += creditos
    else:
        prop.votos_nao += 1
        prop.creditos_nao += creditos

    custo_eth = creditos * creditos * 0.001
    _salvar_resultado(proposta_id, prop)
    return {
        "proposta_id": proposta_id,
        "voto": voto,
        "creditos": creditos,
        "custo_eth": custo_eth,
        "total_creditos_sim": prop.creditos_sim,
        "total_creditos_nao": prop.creditos_nao,
    }


async def resultado(proposta_id: str) -> dict:
    prop = _votacoes.get(proposta_id)
    if not prop:
        raise ValueError("Proposta nao encontrada")
    aprovada = prop.creditos_sim > prop.creditos_nao
    return {
        "proposta_id": proposta_id,
        "aprovada": aprovada,
        "votos_sim": prop.votos_sim,
        "votos_nao": prop.votos_nao,
        "creditos_sim": prop.creditos_sim,
        "creditos_nao": prop.creditos_nao,
        "diferenca_creditos": prop.creditos_sim - prop.creditos_nao,
    }


async def listar_ativas() -> list[dict]:
    return [
        {
            "id": p.id,
            "titulo": p.titulo,
            "votos_sim": p.votos_sim,
            "votos_nao": p.votos_nao,
            "creditos_sim": p.creditos_sim,
            "creditos_nao": p.creditos_nao,
            "ativa": p.ativa,
            "criada_em": p.criada_em,
        }
        for p in _votacoes.values()
    ]
