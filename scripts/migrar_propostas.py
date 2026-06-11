#!/usr/bin/env python3
"""
Script de migracao: reavalia propostas legadas com o novo motor v1.1.

Protocolo:
  1. Lista propostas com motor_utilizado = pangeia_core ou mock_padrao
  2. Re-simula cada uma com o motor deterministico v1.1
  3. Preserva o historico anterior em simulacao.historico[]
  4. Registra timestamp da reavaliacao

Uso:
  source .venv/bin/activate
  python scripts/migrar_propostas.py [--dry-run]
"""
import asyncio
import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")
from app.database import SessionLocal
from app.models.proposta import PropostaORM
from app.services.simulacao import SimulacaoRequest, chamar_motor_pangeia


MOTORES_LEGADOS = {"pangeia_core", "mock_padrao"}


async def reavaliar(proposta: PropostaORM, dry_run: bool = False) -> dict:
    req = SimulacaoRequest(
        proposta_id=proposta.id,
        titulo=proposta.titulo,
        descricao=proposta.descricao,
        problema=proposta.problema or "",
        solucao=proposta.solucao or "",
        orcamento=proposta.orcamento_estimado,
        localizacao=proposta.localizacao,
        ods=proposta.ods_vinculados,
    )
    resultado = await chamar_motor_pangeia(req)
    return {
        "id": proposta.id,
        "titulo": proposta.titulo[:50],
        "motor_antigo": (proposta.simulacao or {}).get("motor_utilizado", "nenhum"),
        "motor_novo": resultado.motor_usado,
        "metricas_antigas": (proposta.simulacao or {}).get("metricas", {}),
        "metricas_novas": resultado.metricas,
        "ctx_keys_antigo": len((proposta.simulacao or {}).get("contexto_regional", {})),
        "ctx_keys_novo": len(resultado.contexto_regional),
    }


async def main(dry_run: bool):
    db = SessionLocal()
    propostas = db.query(PropostaORM).all()

    a_reavaliar = [
        p for p in propostas
        if (p.simulacao or {}).get("motor_utilizado", "") in MOTORES_LEGADOS
    ]

    now = datetime.now(timezone.utc).isoformat()

    print(f"Total propostas: {len(propostas)}")
    print(f"A reavaliar: {len(a_reavaliar)}")
    print()

    for proposta in a_reavaliar:
        print(f"  [{proposta.status}] {proposta.titulo[:50]}...")
        diff = await reavaliar(proposta, dry_run)

        print(f"    motor: {diff['motor_antigo']} -> {diff['motor_novo']}")
        print(f"    contexto: {diff['ctx_keys_antigo']} -> {diff['ctx_keys_novo']} keys")

        if not dry_run:
            req = SimulacaoRequest(
                proposta_id=proposta.id,
                titulo=proposta.titulo,
                descricao=proposta.descricao,
                problema=proposta.problema or "",
                solucao=proposta.solucao or "",
                orcamento=proposta.orcamento_estimado,
                localizacao=proposta.localizacao,
                ods=proposta.ods_vinculados,
            )
            resultado = await chamar_motor_pangeia(req)

            historico = proposta.simulacao or {}
            historico["reavaliado_em"] = now

            proposta.simulacao = {
                "id_simulacao": str(resultado.id_simulacao),
                "motor_utilizado": resultado.motor_usado,
                "modelo_versao": resultado.modelo_versao,
                "pesos_ods_versao": resultado.pesos_ods_versao,
                "metricas": resultado.metricas,
                "contexto_regional": resultado.contexto_regional,
                "metodologia": resultado.metodologia,
                "timestamp": now,
                "historico": [historico],
            }
            proposta.updated_at = now
            db.commit()
            print(f"    REAVALIADA -> v{resultado.modelo_versao} [{resultado.motor_usado}]")

    db.close()
    status = "DRY RUN - nenhuma alteracao" if dry_run else "Propostas reavaliadas."
    print(f"\nConcluido. {status}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(main(dry))
